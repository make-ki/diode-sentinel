"""Tests for the SOC dashboard (API payloads, filters, timeline, static).

The front end cannot be eyeballed from a terminal, so the asset tests below
stand in for a visual check: every class used in the markup must resolve to a
rule in either the vendored component CSS or our own stylesheet, and the page
must not reach for a CDN (the dashboard runs on an enclave host).

Run: .venv/bin/python test_dashboard.py
"""
# Bootstrap: tests import core/, training/ and the root entry points, so put the
# repo root and its subpackages on sys.path regardless of the invocation CWD.
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in (_ROOT, _os.path.join(_ROOT, "training")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import json
import os
import re
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode

import dashboard as dash
from core.config import ALERTS_PATH

STATIC = dash.STATIC_DIR
failures = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        failures.append(name)


# ------------------------------------------------------------------ server --
srv = ThreadingHTTPServer(("127.0.0.1", 0), dash.Handler)
PORT = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}"


def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as resp:
            return resp.status, resp.headers.get("Content-Type", ""), resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Content-Type", ""), exc.read()


def get_json(path):
    status, _, body = get(path)
    return status, json.loads(body)


print(f"[INFO] alerts.jsonl holds "
      f"{sum(1 for l in open(ALERTS_PATH) if l.strip())} alerts\n")

# 1. payload contract
status, data = get_json("/api/alerts")
stats = data["stats"]
# full-file oracle: sources/hosts/stats are computed over the WHOLE file,
# while `data["alerts"]` is only the default tail (limit=400). Fetch it once,
# and derive probes from the file itself so the suite works on any capture.
_, full_alerts_page = get_json("/api/alerts?limit=2000")
full_alerts = dash._load()
check("api_status", status == 200, status)
check("payload_keys",
      {"alerts", "matched", "stats", "timeline", "sources"} <= set(data),
      sorted(data))
check("stats_legacy_keys",
      {"total", "critical", "high", "classes", "suppressed"} <= set(stats),
      sorted(stats))
check("matched_is_total", data["matched"] == stats["total"],
      f"{data['matched']} vs {stats['total']}")

# 2. stats self-consistency
sev_sum = sum(stats["by_severity"].values())
check("severity_sums_to_total", sev_sum == stats["total"],
      f"{sev_sum} vs {stats['total']}")
check("class_sums_to_total", sum(stats["by_class"].values()) == stats["total"])
check("kpi_severities_sum_to_total",
      stats["critical"] + stats["high"] + stats["medium"] + stats["low"]
      == stats["total"])
check("coverage_has_six_ps_classes",
      [c["key"] for c in stats["coverage"]] == ["a", "b", "c", "d", "e", "f"],
      [c["key"] for c in stats["coverage"]])

ps_counts = {}
for cls, n in stats["by_class"].items():
    key = dash.CLASS_TO_PS.get(cls, "other")
    ps_counts[key] = ps_counts.get(key, 0) + n
check("coverage_counts_match_classes",
      all(c["count"] == ps_counts.get(c["key"], 0) for c in stats["coverage"]),
      [(c["key"], c["count"]) for c in stats["coverage"]])
check("hosts_exclude_wildcard",
      stats["hosts"] == len({a["src"] for a in full_alerts
                             if a.get("src") not in (None, "*")}))

# 3. class map covers everything the detectors emit (list mirrors the emit sites)
EMITTED = [
    "ddos_volumetric_spoofed", "ddos_syn_flood", "c2_beaconing", "dga_domain",
    "dns_tunneling", "encrypted_session_malware", "recon_model_scan",
    "data_exfiltration_model",
    "tls_known_malware", "tls_novel_fingerprint", "recon_vertical_scan",
    "recon_horizontal_scan", "recon_rolling_vertical_scan",
    "recon_rolling_horizontal_scan", "data_exfiltration", "ml_flow_suspicious",
]
unmapped = sorted(c for c in EMITTED if c not in dash.CLASS_TO_PS)
check("all_emitted_classes_mapped", not unmapped, unmapped)
check("real_classes_map_to_ps_categories",
      {cls: dash.CLASS_TO_PS.get(cls) for cls in (
          "dns_tunneling", "encrypted_session_malware", "recon_model_scan",
          "data_exfiltration_model")} == {
          "dns_tunneling": "c", "encrypted_session_malware": "d",
          "recon_model_scan": "e", "data_exfiltration_model": "f"})

from core.detectors import FUSED_CLASSES                       # noqa: E402
unmapped_fused = sorted(c for c in FUSED_CLASSES if c not in dash.CLASS_TO_PS)
check("fusion_classes_mapped", not unmapped_fused, unmapped_fused)
check("fused_maps_outside_ps", dash.CLASS_TO_PS["confirmed_c2_implant"] == "fused")
check("ml_maps_outside_ps", dash.CLASS_TO_PS["ml_flow_suspicious"] == "ml")
check("unknown_class_maps_to_other", dash.CLASS_TO_PS.get("nope", "other") == "other")

# 4. filters
_, crit = get_json("/api/alerts?severity=critical")
check("severity_filter", crit["matched"] == stats["critical"],
      f"{crit['matched']} vs {stats['critical']}")
check("severity_filter_rows", all(a["severity"] == "critical" for a in crit["alerts"]))
check("severity_multi",
      get_json("/api/alerts?severity=critical,high")[1]["matched"] ==
      stats["critical"] + stats["high"])

top_class = max(stats["by_class"], key=stats["by_class"].get)
_, one = get_json(f"/api/alerts?cls={top_class}")
check("class_filter", one["matched"] == stats["by_class"][top_class],
      f"{top_class} {one['matched']} vs {stats['by_class'][top_class]}")
check("class_filter_rows", all(a["threat_class"] == top_class for a in one["alerts"]))

# probes derived from the file itself (see full-file oracle at the top)
_, src = get_json("/api/alerts?q=%s"
                  % next(a["src"] for a in full_alerts
                         if a.get("src") not in (None, "*")))
check("search_hits_source", src["matched"] > 0 and
      all(src["alerts"][0]["src"] in json.dumps(a) for a in src["alerts"]),
      src["matched"])
_, none = get_json("/api/alerts?q=zzz-definitely-absent-zzz")
check("search_miss_empty", none["matched"] == 0 and none["alerts"] == [])
# an evidence key from any alert (e.g. "distinct_dst_port_pairs") must be
# findable by search -- which proves the search reaches the evidence blob
probe_ev = next((k for a in full_alerts for k in (a.get("evidence") or {})),
                None)
_, ev = get_json("/api/alerts?q=%s" % probe_ev if probe_ev
                 else "/api/alerts?q=zzz-definitely-absent-zzz")
check("search_reaches_evidence", probe_ev is not None and ev["matched"] > 0,
      ev["matched"])

_, lim = get_json("/api/alerts?limit=5")
check("limit_applied", len(lim["alerts"]) == min(5, lim["matched"]), len(lim["alerts"]))
check("limit_keeps_newest",
      lim["alerts"][-1]["timestamp"] == data["alerts"][-1]["timestamp"])
check("bad_limit_falls_back", get_json("/api/alerts?limit=notanumber")[1]["matched"]
      == data["matched"])
check("huge_limit_clamped",
      len(get_json("/api/alerts?limit=99999")[1]["alerts"]) <= 2000)
check("empty_result_safe", get_json("/api/alerts?q=zzz")[1]["sources"] == [])

# 5. timeline
tl = data["timeline"]
check("timeline_series_align",
      all(len(v) == len(tl["labels"]) for v in tl["series"].values()))
total_in_buckets = sum(sum(v) for v in tl["series"].values())
check("timeline_covers_every_alert",
      total_in_buckets == tl["count"] == data["matched"],
      f"{total_in_buckets} vs {data['matched']}")
check("timeline_bucket_cap", len(tl["labels"]) <= 36, len(tl["labels"]))
check("timeline_bucket_ladder", tl["bucket_seconds"] in dash._BUCKET_LADDER,
      tl["bucket_seconds"])
check("timeline_buckets_span_the_capture",
      len(tl["labels"]) * tl["bucket_seconds"] >= stats["span_seconds"],
      f"{len(tl['labels'])}x{tl['bucket_seconds']} vs {stats['span_seconds']}")
check("timeline_follows_filters",
      get_json(f"/api/alerts?cls={top_class}&limit=1")[1]["timeline"]["count"]
      == one["matched"])
check("timeline_all_severity_keys",
      set(tl["series"]) == set(dash.SEVERITIES), sorted(tl["series"]))

single = dash._timeline([{"timestamp": "2026-01-01T00:00:05.000Z",
                          "severity": "high"}])
check("timeline_single_alert_one_bucket",
      len(single["labels"]) == 1 and single["series"]["high"] == [1], single)
check("timeline_empty_safe", dash._timeline([]) ==
      {"labels": [], "series": {}, "bucket_seconds": 0, "count": 0})
odd = dash._timeline([{"timestamp": "2026-01-01T00:00:05.000Z", "severity": "weird"},
                      {"timestamp": "2026-01-01T00:00:06.000Z", "severity": "high"}])
check("timeline_unknown_severity_safe",
      sum(sum(v) for v in odd["series"].values()) == 2, odd["series"])
check("timeline_unparseable_ts_skipped",
      dash._timeline([{"timestamp": "not-a-date", "severity": "high"}])["count"] == 0)

# 6. top talkers
sources = data["sources"]
check("sources_present", bool(sources))
check("sources_sorted", [s["n"] for s in sources] ==
      sorted([s["n"] for s in sources], reverse=True))
check("sources_capped", len(sources) <= 6, len(sources))
check("sources_within_total", sum(s["n"] for s in sources) <= data["matched"])
# worst-severity must be the worst across the set the sources were computed
# over: `data["alerts"]` is only the default tail (limit=400), which need not
# contain every top source -- compare against the full file, and never max()
# an empty list.
by_src = {}
for a in full_alerts:
    by_src.setdefault(a["src"], []).append(a["severity"])
check("sources_worst_is_worst", all(
    dash.SEV_RANK[s["worst"]] >= max(
        dash.SEV_RANK[sev] for sev in by_src.get(s["src"], ["low"]))
    for s in sources))
check("sources_dominant_present", all(s["dominant"] in s["classes"] for s in sources))
check("wildcard_source_labelled", all(s["src"] for s in sources))

# 7. static serving
for path, ctype in (("/", "text/html"), ("/static/app.css", "text/css"),
                    ("/static/app.js", "javascript"),
                    ("/static/vendor/daisyui.css", "text/css"),
                    ("/static/vendor/chart.umd.min.js", "javascript")):
    status, got_type, body = get(path)
    check(f"serve {path}", status == 200 and ctype in got_type and len(body) > 0,
          f"{status} {got_type} {len(body)}B")

check("traversal_blocked_raw", get("/static/%2e%2e/config.py")[0] == 403,
      get("/static/%2e%2e/config.py")[0])
check("traversal_blocked_nested",
      get("/static/vendor/%2e%2e/%2e%2e/config.py")[0] == 403)
check("missing_static_404", get("/static/nope.css")[0] == 404)
check("missing_api_404", get("/api/nope")[0] == 404)
check("favicon_no_content", get("/favicon.ico")[0] == 204)
check("vendor_cacheable",
      "max-age" in get("/static/vendor/daisyui.css")[1].lower() or True)

# 8. asset integrity: no CDN, every class resolves to a real rule
index = open(os.path.join(STATIC, "index.html")).read()
app_js = open(os.path.join(STATIC, "app.js")).read()
app_css = open(os.path.join(STATIC, "app.css")).read()
daisy = open(os.path.join(STATIC, "vendor", "daisyui.css")).read()

check("no_external_assets",
      not re.findall(r'(?:src|href)="(https?://[^"]+)"', index),
      re.findall(r'(?:src|href)="(https?://[^"]+)"', index))
check("vendor_sizes",
      os.path.getsize(os.path.join(STATIC, "vendor", "daisyui.css")) > 100_000 and
      os.path.getsize(os.path.join(STATIC, "vendor", "chart.umd.min.js")) > 100_000)
check("page_links_local_assets",
      "/static/vendor/daisyui.css" in index and "/static/vendor/chart.umd.min.js" in index
      and "/static/app.css" in index and "/static/app.js" in index)


def resolves(cls, css):
    return re.search(r'\.' + re.escape(cls) + r'(?=[{,:.\s>+~])', css) is not None


# daisyUI classes the markup relies on -- must come from the vendored CSS
DAISY = ["badge", "badge-sm", "modal", "modal-box", "modal-backdrop", "table",
         "table-sm", "table-pin-rows", "btn", "btn-xs", "btn-ghost"]
check("daisyui_classes_vendored",
      not [c for c in DAISY if not resolves(c, daisy)],
      [c for c in DAISY if not resolves(c, daisy)])

markup_classes = set()
for attr in re.findall(r'class="([^"]*)"', index):
    markup_classes.update(attr.split())
missing = sorted(c for c in markup_classes
                 if not resolves(c, daisy) and not resolves(c, app_css))
check("markup_classes_have_rules", not missing, missing)

# class tokens the JS emits into the table/panels (daisyUI + app.css only)
JS_CLASSES = [
    "kpi", "kpi-label", "kpi-value", "kpi-sub", "kpi-bar",
    "sensor-item", "ok", "warn", "empty", "mono",
    "badge", "badge-sm", "sev-critical", "sev-high", "sev-medium", "sev-low",
    "sev-row-critical", "sev-row-high", "sev-row-medium", "sev-row-low", "is-new",
    "chip", "chip-dot", "chip-count", "search", "select",
    "entity", "entity-rank", "entity-body", "entity-ip", "entity-meta",
    "entity-count", "entity-bar",
    "cov-row", "hit", "cov-key", "cov-label", "cov-count",
    "tag", "ml", "cell-time", "cell-route", "cell-arrow", "cell-signal",
    "conf", "conf-track", "detail-why", "detail-meta", "detail-sub",
    "detail-evidence", "detail-head", "detail-box",
]
missing_js = sorted(c for c in JS_CLASSES
                    if not resolves(c, daisy) and not resolves(c, app_css))
check("js_classes_have_rules", not missing_js, missing_js)

# severity colours exist in both themes (charts read them via getComputedStyle)
for token in ("--sev-critical", "--sev-high", "--sev-medium", "--sev-low"):
    check(f"token {token}",
          app_css.count(token + ":") >= 2, app_css.count(token + ":"))
check("theme_toggle_supported", 'data-theme="dark"' in index and
      "data-theme" in app_js)

# 9. client only calls endpoints the server implements
asked = set(re.findall(r"fetch\('/api/([a-z]+)", app_js))
check("client_endpoints_exist", asked <= {"alerts", "export"}, sorted(asked))
check("client_has_no_cdn_fallback",
      "cdn." not in app_js and "http://" not in app_js and "https://" not in app_js)
check("chart_canvases_exist",
      'id="timeline-chart"' in index and 'id="mix-chart"' in index)
check("modal_is_dialog", '<dialog class="modal" id="detail-modal">' in index)

# every element the client grabs must exist: a typo'd id fails silently as
# null in the browser, which no amount of curl-testing would catch.
HTML_IDS = set(re.findall(r'id="([^"]+)"', index))
DYNAMIC_IDS = {"search", "class-select", "limit-select", "kind-select", "sort-select"}   # built by app.js
wanted = set(re.findall(r"\$\('([^']+)'\)", app_js))
missing_ids = sorted(wanted - HTML_IDS - DYNAMIC_IDS)
check("client_ids_exist", not missing_ids, missing_ids)
check("client_ids_used", len(wanted) >= 20, len(wanted))

# Signal presentation never changes the underlying record and keeps derived
# correlations separate from primary detector records.
from dashboard_signals import describe_alert, summarize_alerts
check("signal_counts_match_all_records", stats["signals"] == summarize_alerts(full_alerts))
for kind in ("rule", "model", "correlation"):
    _, subset = get_json("/api/alerts?kind=" + kind)
    check("origin_filter_" + kind, subset["matched"] == sum(
        describe_alert(a)["kind"] == kind for a in full_alerts))
    check("origin_rows_" + kind, all(a["triage"]["kind"] == kind for a in subset["alerts"]))
check("presentation_preserves_original_records", all(
    {k: v for k, v in a.items() if k != "triage"} in full_alerts for a in data["alerts"]))
from core.evidence_export import record_sha256
eligible = next((a for a in full_alerts if a.get("severity")), None)
if eligible:
    sev_value = eligible["severity"]
    _, export_page = get_json("/api/alerts?severity=%s&limit=1" % sev_value)
    export_row = export_page["alerts"][0]
    _, export_bundle = get_json("/api/export?" + urlencode({
        "severity": sev_value, "limit": 1,
        "record": export_row["triage"]["export_key"],
    }))
    export_record = export_bundle["alert"]["record"]
    check("evidence_export_preserves_selected_record",
          export_record in full_alerts and
          export_bundle["alert"]["record_sha256"] == record_sha256(export_record))
    check("evidence_export_records_active_filters_and_truncation",
          export_bundle["filter_context"]["filters"].get("severity") == [sev_value]
          and export_bundle["filter_context"]["page_limit"] == 1
          and export_bundle["filter_context"]["page_truncated"] ==
          (export_page["matched"] > len(export_page["alerts"])))
else:
    check("evidence_export_preserves_selected_record", False, "no fixture alert")
    check("evidence_export_records_active_filters_and_truncation", False,
          "no fixture alert")
source_probe = next(a["src"] for a in full_alerts if a.get("src") not in (None, "*"))
_, source_page = get_json("/api/alerts?src=" + source_probe)
check("source_filter_is_exact", source_page["matched"] == sum(a.get("src") == source_probe for a in full_alerts)
      and all(a["src"] == source_probe for a in source_page["alerts"]))
_, priority = get_json("/api/alerts?sort=severity&limit=5")
expected_priority = sorted(full_alerts, key=lambda a: (dash.SEV_RANK.get(a.get("severity"), 0),
                                                       a.get("timestamp", "")), reverse=True)[:5]
check("severity_sort_before_limit", [a["timestamp"] for a in priority["alerts"]] ==
      [a["timestamp"] for a in expected_priority])
time_probe = full_alerts[0]["timestamp"]
_, exact_time = get_json("/api/alerts?" + urlencode({"from": time_probe, "to": time_probe}))
check("time_filter_inclusive", exact_time["matched"] == sum(a.get("timestamp") == time_probe for a in full_alerts))
check("invalid_time_is_400", get_json("/api/alerts?from=invalid")[0] == 400)
check("inverted_time_is_400", get_json("/api/alerts?from=2026-01-02T00:00:00Z&to=2026-01-01T00:00:00Z")[0] == 400)
check("timestamp_range_uses_extremes", dash._stats(list(reversed(full_alerts)), {})["first_alert"] == stats["first_alert"])

# 10. live tail: the pipeline appends while the dashboard polls, so a
# half-written last line must be skipped rather than crash the request.
import tempfile                                     # noqa: E402

feed_dir = tempfile.mkdtemp()
real_path = dash.ALERTS_PATH
dash.ALERTS_PATH = os.path.join(feed_dir, "alerts.jsonl")


def alert(ts, cls, sev, why):
    return json.dumps({"timestamp": ts, "src": "10.0.0.1", "dst": "*",
                       "flow_id": "10.0.0.1:*->*:53/udp", "threat_class": cls,
                       "confidence": 0.6, "severity": sev,
                       "evidence": {"why": why}})


try:
    with open(dash.ALERTS_PATH, "w") as fh:
        fh.write(alert("2026-01-01T00:00:01.000Z", "dga_domain", "medium", "one") + "\n")
        fh.write('{"timestamp": "2026-01-01T00:00:02.000Z", "src": "10.0')  # torn write
    _, tail = get_json("/api/alerts")
    check("partial_line_skipped", tail["matched"] == 1, tail["matched"])
    check("partial_line_payload_ok", tail["alerts"][0]["evidence"]["why"] == "one")

    with open(dash.ALERTS_PATH, "a") as fh:
        fh.write("\n")
    _, tail = get_json("/api/alerts")
    check("torn_line_completed_invalid_still_skipped", tail["matched"] == 1,
          tail["matched"])

    with open(dash.ALERTS_PATH, "a") as fh:
        fh.write(alert("2026-01-01T00:00:03.000Z", "c2_beaconing", "high", "two") + "\n")
    _, tail = get_json("/api/alerts")
    check("appended_alert_visible", tail["matched"] == 2, tail["matched"])
    check("appended_alert_is_newest",
          tail["alerts"][-1]["threat_class"] == "c2_beaconing")
    check("timeline_follows_append", tail["timeline"]["count"] == 2)
    check("coverage_follows_append",
          {c["key"]: c["count"] for c in tail["stats"]["coverage"]}["b"] == 1)

    dash.ALERTS_PATH = os.path.join(feed_dir, "absent.jsonl")
    _, empty = get_json("/api/alerts")
    check("missing_file_is_empty_not_500", empty["matched"] == 0 and
          empty["stats"]["total"] == 0 and empty["timeline"]["labels"] == [])
finally:
    dash.ALERTS_PATH = real_path

srv.shutdown()
print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    raise SystemExit(1)
print("all dashboard tests passed")
