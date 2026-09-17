#!/usr/bin/env python3
"""
Live SOC dashboard for the one-way NIDS (stdlib only -- no Flask/FastAPI/npm).

Serves:
  GET /                          -- single-page dashboard
  GET /static/...                -- app.css, app.js, vendored daisyUI/Chart.js
  GET /api/alerts?limit=&severity=&cls=&q=
                                 -- filtered alert stream + full stats
  GET /api/stats                 -- counts by class/severity + coverage

Every /api/* request re-reads alerts.jsonl, so a running pipeline (run.py)
appending to the file streams straight to the browser. Replay works the same
way: the file IS the replay buffer.

The front end is a static page (static/index.html + app.css + app.js) built
on daisyUI components and Chart.js. Both are vendored under static/vendor/ so
the dashboard renders on an enclave host with no route to a CDN.

Run:  .venv/bin/python dashboard.py [port]     (default 8600)
"""
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

from config import ALERTS_PATH, PROJECT_DIR

STATIC_DIR = os.path.join(PROJECT_DIR, "static")
STATS_PATH = os.path.join(os.path.dirname(ALERTS_PATH) or ".", "run_stats.json")

SEVERITIES = ("critical", "high", "medium", "low")
SEV_RANK = {s: i for i, s in enumerate(reversed(SEVERITIES), start=1)}

# The six threat classes of PS-26145, in problem-statement order.
PS_CLASSES = [
    ("a", "DDoS / SYN flood"),
    ("b", "C2 beaconing"),
    ("c", "DGA / DNS tunnelling"),
    ("d", "Encrypted-session malware"),
    ("e", "Recon / port scan"),
    ("f", "Data exfiltration"),
]

# Every class the pipeline can emit, mapped to its PS class. Fusion verdicts
# and ML verdicts are cross-signal tiers, so they get their own coverage key.
CLASS_TO_PS = {
    "ddos_volumetric_spoofed": "a",
    "ddos_syn_flood":          "a",
    "ddos_udp_amplification":  "a",
    "c2_beaconing":            "b",
    "dga_domain":              "c",
    "dns_tunneling":           "c",
    "tls_known_malware":       "d",
    "tls_novel_fingerprint":   "d",
    "recon_vertical_scan":     "e",
    "recon_horizontal_scan":   "e",
    "data_exfiltration":       "f",
    "confirmed_exfiltration":  "fused",
    "confirmed_c2_implant":    "fused",
    "botnet_c2_with_dga":      "fused",
    "multi_signal_fusion":     "fused",
    "ml_flow_suspicious":      "ml",
}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".txt": "text/plain; charset=utf-8",
    ".md": "text/plain; charset=utf-8",
}

_BUCKET_LADDER = (1, 2, 5, 10, 15, 30, 60, 120, 300, 600, 1800, 3600)


# ---------------------------------------------------------------- loading ---

def _load():
    """Read every parseable alert from alerts.jsonl (the tail is re-read on
    each poll, so a partially written last line is simply skipped)."""
    if not os.path.exists(ALERTS_PATH):
        return []
    out = []
    with open(ALERTS_PATH) as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def _load_sensor():
    """Sidecar written by run.py: suppressed count, parser, throughput, mode."""
    if not os.path.exists(STATS_PATH):
        return {}
    try:
        with open(STATS_PATH) as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _parse_ts(value):
    """ISO-8601 with a trailing Z -> aware datetime, or None."""
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=timezone.utc)
    except ValueError:
        pass
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc)
    except ValueError:
        return None


# ------------------------------------------------------------------ stats ---

def _coverage(by_class):
    counts = Counter()
    for cls, n in by_class.items():
        counts[CLASS_TO_PS.get(cls, "other")] += n
    return [{"key": key, "label": label, "count": counts.get(key, 0)}
            for key, label in PS_CLASSES]


def _stats(alerts, sensor):
    sev = Counter(a.get("severity") for a in alerts)
    by_class = Counter(a.get("threat_class") for a in alerts)
    hosts = {a.get("src") for a in alerts if a.get("src") not in (None, "*")}
    times = [t for t in (_parse_ts(a.get("timestamp")) for a in alerts)
             if t is not None]
    return {
        "total": len(alerts),
        "critical": sev.get("critical", 0),
        "high": sev.get("high", 0),
        "medium": sev.get("medium", 0),
        "low": sev.get("low", 0),
        # kept for the original /api/stats contract
        "classes": sorted(by_class),
        "suppressed": int(sensor.get("suppressed") or 0),
        "by_class": dict(by_class.most_common()),
        "by_severity": {s: sev.get(s, 0) for s in SEVERITIES},
        "hosts": len(hosts),
        "coverage": _coverage(by_class),
        "first_alert": times[0].isoformat() if times else None,
        "last_alert": times[-1].isoformat() if times else None,
        "span_seconds": round((times[-1] - times[0]).total_seconds(), 1)
                        if len(times) > 1 else 0.0,
        "sensor": sensor,
    }


def _top_sources(alerts, limit=6):
    agg = {}
    for a in alerts:
        src = a.get("src") or "*"
        entry = agg.setdefault(src, {"src": src, "n": 0, "classes": Counter(),
                                     "worst": "low", "confidence": 0.0})
        entry["n"] += 1
        entry["classes"][a.get("threat_class")] += 1
        if SEV_RANK.get(a.get("severity"), 0) > SEV_RANK.get(entry["worst"], 0):
            entry["worst"] = a.get("severity")
        entry["confidence"] = max(entry["confidence"],
                                  float(a.get("confidence") or 0.0))
    top = sorted(agg.values(), key=lambda e: (-e["n"], e["src"]))[:limit]
    out = []
    for e in top:
        dom, dom_n = e["classes"].most_common(1)[0]
        e["classes"] = dict(e["classes"])
        e["dominant"] = dom
        e["dominant_count"] = dom_n
        e["confidence"] = round(e["confidence"], 3)
        out.append(e)
    return out


def _pick_bucket(span):
    for size in _BUCKET_LADDER:
        if span / size <= 36:
            return size
    return _BUCKET_LADDER[-1]


def _timeline(alerts, max_buckets=36):
    """Stacked severity counts over uniform time buckets.

    Buckets are aligned to the first alert (not to a wall-clock grid) so a
    short capture still fills the whole chart instead of leaving one bar."""
    pairs = [(t, a.get("severity")) for t, a in
             ((_parse_ts(a.get("timestamp")), a) for a in alerts) if t]
    if not pairs:
        return {"labels": [], "series": {}, "bucket_seconds": 0, "count": 0}
    t0 = min(t for t, _ in pairs)
    t1 = max(t for t, _ in pairs)
    size = _pick_bucket(max((t1 - t0).total_seconds(), 1.0))
    n = int((t1 - t0).total_seconds() // size) + 1
    while n > max_buckets:
        size *= 2
        n = int((t1 - t0).total_seconds() // size) + 1
    series = {s: [0] * n for s in SEVERITIES}
    for t, sev in pairs:
        idx = min(int((t - t0).total_seconds() // size), n - 1)
        # setdefault returns the *list*, so index it directly (an unknown
        # severity -- a hand-edited alert file -- must not crash the poll).
        series.setdefault(sev, [0] * n)[idx] += 1
    labels = [
        ((t0 + timedelta(seconds=i * size)).strftime("%H:%M:%S")
         if size < 60 else (t0 + timedelta(seconds=i * size)).strftime("%H:%M"))
        for i in range(n)
    ]
    return {"labels": labels, "series": series, "bucket_seconds": size,
            "count": len(pairs)}


# ---------------------------------------------------------------- filters ---

def _multi(qs, key):
    raw = []
    for value in qs.get(key, []):
        raw.extend(part for part in value.split(",") if part)
    return {p.strip() for p in raw if p.strip()}


def _filter(alerts, sev_filter, cls_filter, needle):
    out = alerts
    if sev_filter:
        out = [a for a in out if a.get("severity") in sev_filter]
    if cls_filter:
        out = [a for a in out if a.get("threat_class") in cls_filter]
    if needle:
        low = needle.lower()

        def hit(a):
            blob = " ".join(str(a.get(k, "")) for k in
                            ("src", "dst", "threat_class", "severity", "flow_id"))
            blob += " " + json.dumps(a.get("evidence") or {})
            return low in blob.lower()
        out = [a for a in out if hit(a)]
    return out


def _payload(qs):
    alerts = _load()
    sensor = _load_sensor()
    sev_filter = _multi(qs, "severity")
    cls_filter = _multi(qs, "cls")
    needle = (qs.get("q", [""])[0] or "").strip()
    try:
        limit = max(1, min(2000, int(qs.get("limit", ["400"])[0])))
    except ValueError:
        limit = 400

    view = _filter(alerts, sev_filter, cls_filter, needle)
    return {
        "alerts": view[-limit:],
        "matched": len(view),
        "stats": _stats(alerts, sensor),
        "timeline": _timeline(view),
        "sources": _top_sources(view),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


# --------------------------------------------------------------- handlers ---

class Handler(BaseHTTPRequestHandler):
    server_version = "OneWayNIDS/1.0"

    def _send(self, code, body, ctype, cache="no-cache"):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", cache)
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_file(self, path, cache="no-cache"):
        ext = os.path.splitext(path)[1].lower()
        try:
            with open(path, "rb") as fh:
                body = fh.read()
        except OSError:
            return self._send(404, "not found", "text/plain")
        self._send(200, body, CONTENT_TYPES.get(ext, "application/octet-stream"),
                   cache)

    def _serve_static(self, url_path):
        rel = unquote(url_path[len("/static/"):])
        target = os.path.realpath(os.path.join(STATIC_DIR, rel))
        # Path traversal guard: never step outside static/.
        if not (target == STATIC_DIR or target.startswith(STATIC_DIR + os.sep)):
            return self._send(403, "forbidden", "text/plain")
        cache = ("public, max-age=86400" if os.sep + "vendor" + os.sep in target
                 else "no-cache")
        self._send_file(target, cache)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html"):
            return self._send_file(os.path.join(STATIC_DIR, "index.html"))
        if path.startswith("/static/"):
            return self._serve_static(path)
        if path == "/api/alerts":
            return self._send(200, json.dumps(_payload(parse_qs(parsed.query))),
                              "application/json")
        if path == "/api/stats":
            return self._send(200, json.dumps(_stats(_load(), _load_sensor())),
                              "application/json")
        if path == "/favicon.ico":
            return self._send(204, b"", "image/x-icon")
        self._send(404, "not found", "text/plain")

    def log_message(self, *a):     # silence per-request logging
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8600
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"dashboard: http://localhost:{port}  (tailing {ALERTS_PATH})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
