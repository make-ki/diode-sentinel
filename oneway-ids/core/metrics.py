#!/usr/bin/env python3
"""
Prometheus exporter for the one-way NIDS (stdlib only -- no prometheus_client).

Exposes the sensor's live internals in the Prometheus text exposition format:

  GET /metrics    all NIDS metrics (counter/gauge lines, one HELP+TYPE pair)

Two attach points, both dependency-free:

  NidsMetrics(sink, ...)
      attaches to the AlertSink. An alert is too rare an event to wait for a
      scrape, so emits are counted eagerly via sink.subscribe(); everything
      else is sampled from the processor / source at scrape time.

  run.py --metrics-port 9100
      starts the HTTP server in a daemon thread and passes in live objects.
      Replay mode still works: process stats land at the end of the run, so
      Prometheus can watch a batch job as easily as a live sensor.

Design notes
------------
- Severity is a *property* of a class's confidence (detectors._severity), so
  nids_alerts_total carries both labels; severity-only views are plain
  sums. The allowlisted (suppressed) count is only reachable via
  sink.suppressed -- it never appears in alerts.jsonl -- so it is exported
  explicitly, keeping the exporter's numbers identical to the SOC
  dashboard's.
- Source stats (kernel drops, sampler, ring counters) are exported when a
  live source is attached. Loss on a one-way feed is invisible by definition;
  the README already refuses to hide it on the terminal -- the same refusal
  belongs in the time-series store, where it can page someone at 3am.
- Gauges that make no sense mid-run (parse time, wall clock) are exported
  as-is rather than skipped: a scrape of a live sensor should never see
  STALE series come and go.

Run:  .venv/bin/python -c "from metrics import ..."      (used by run.py)
      .venv/bin/python metrics.py                        (self-test server)
"""
import os
import re
import threading
import time
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------------------
# metric names / labels (single source of truth -- also imported by tests)
# ---------------------------------------------------------------------------

NAMESP = "nids"

# ---------------------------------------------------------------------------
# exposition helpers
# ---------------------------------------------------------------------------

# Prometheus metric name charset; anything else is replaced (defensive: the
# pipeline's class names are already identifiers, but a hand-edited alert
# file must not be able to poison the exposition).
_SANITIZE = re.compile(r"[^a-zA-Z0-9_]")


def _mangle(value: str) -> str:
    return _SANITIZE.sub("_", value)


def _fmt(value) -> str:
    if value is None:
        return "NaN"
    try:
        f = float(value)
    except (TypeError, ValueError):
        return "NaN"
    if f != f or f in (float("inf"), float("-inf")):
        return "+Inf" if f > 0 else ("-Inf" if f < 0 else "NaN")
    if f.is_integer() and abs(f) < 2 ** 53:
        return str(int(f))
    return repr(f)


def _labels(**kwargs) -> str:
    parts = ",".join(f'{k}="{_mangle(str(v))}"' for k, v in kwargs.items())
    return "{" + parts + "}" if parts else ""


class _Sample:
    """One exported series (name, fixed label dict, value)."""

    __slots__ = ("name", "labels", "value", "help", "kind")

    def __init__(self, name, labels, value, help="", kind="gauge"):
        self.name = name
        self.labels = labels
        self.value = value
        self.help = help
        self.kind = kind


class NidsMetrics:
    """Collects NIDS state into Prometheus text exposition on /metrics."""

    def __init__(self, sink, processor=None, source=None, proc=None,
                 start_time=None):
        """
        sink       AlertSink            (required; alert counters attach here)
        processor  StreamProcessor     sampled per scrape (npkt, ndns, ...)
        source     AfPacketSource /
                   PcapStreamSource    sampled per scrape (drops, frames)
        proc       os reference        sampled per scrape (RSS, CPU time)
        """
        self.sink = sink
        self.processor = processor
        self.source = source
        self._proc = proc or os
        self._start = start_time or time.time()
        self.pid = os.getpid()

        # Eager counters, bumped by the AlertSink subscription: an alert is
        # too rare to reconstruct by diffing sink.alerts on every scrape, and
        # a replay driver truncates the list per run, so a cumulative counter
        # must be ours.
        self._by_class = Counter()          # (threat_class, severity) -> n
        self._ml_total = 0                  # Tier-2 LightGBM verdicts
        self._cnn_total = 0                 # Tier-2 DGA-CNN confirmations
        if sink is not None:
            sink.subscribe(self._on_alert)

        self._lock = threading.Lock()

    # ------------------------------------------------------------ attaching --

    def observe_processor(self, processor):
        """Attach (or re-attach) the StreamProcessor sampled at scrape time."""
        self.processor = processor

    def observe_source(self, source):
        """Attach the capture source so socket/drop stats are exported.

        run.py calls this the moment a live source exists, so the exporter
        reports frames/drops from the first scrape even while the pipeline is
        still being constructed.
        """
        self.source = source

    # ------------------------------------------------------------ sink hook --

    def _on_alert(self, _t, rec):
        cls = rec.get("threat_class") or "unknown"
        sev = rec.get("severity") or "unknown"
        with self._lock:
            self._by_class[(cls, sev)] += 1
            evidence = rec.get("evidence") or {}
            if evidence.get("tier") == "ml":
                self._ml_total += 1
            elif evidence.get("cnn"):
                self._cnn_total += 1

    # ----------------------------------------------------------- collection --

    def _proc_stats(self):
        """RSS bytes + CPU seconds from /proc (Linux; [] elsewhere)."""
        out = []
        try:
            with open(f"/proc/self/stat") as fh:
                fields = fh.read().split()
            utime, stime = float(fields[11 + 2]), float(fields[12 + 2])
            ticks = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100
            out.append(_Sample(f"{NAMESP}_process_cpu_seconds_total", {},
                               (utime + stime) / ticks,
                               "User + system CPU time spent by the sensor.",
                               "counter"))
        except (OSError, IndexError, ValueError):
            pass
        try:
            with open("/proc/self/statm") as fh:
                rss_pages = int(fh.read().split()[1])
            page = os.sysconf("SC_PAGE_SIZE") if hasattr(os, "sysconf") else 4096
            out.append(_Sample(f"{NAMESP}_process_resident_memory_bytes", {},
                               rss_pages * page,
                               "Resident memory of the sensor process.",
                               "gauge"))
        except (OSError, IndexError, ValueError):
            pass
        return out

    def _samples(self):
        s = []

        # --- ingest (sampled from the StreamProcessor at scrape time) ---
        p = self.processor
        if p is not None:
            s.append(_Sample(f"{NAMESP}_packets_processed_total", {}, p.npkt,
                             "Packets fed into the pipeline.", "counter"))
            s.append(_Sample(f"{NAMESP}_dns_queries_total", {}, p.ndns,
                             "DNS qnames dissected.", "counter"))
            s.append(_Sample(f"{NAMESP}_clienthellos_parsed_total", {}, p.ntls,
                             "TLS/QUIC ClientHellos parsed (TCP + QUIC "
                             "Initial).", "counter"))
            s.append(_Sample(f"{NAMESP}_flows_closed_total", {},
                             p.assembler.closed_count,
                             "Idle-closed flows handed to scoring.",
                             "counter"))
            for kind, n in p.assembler.active_count_by_proto.items():
                s.append(_Sample(f"{NAMESP}_flows_active", {("kind", kind)}, n,
                                 "Flows not yet idle-closed, per protocol.",
                                 "gauge"))
            s.append(_Sample(f"{NAMESP}_windows_flushed_total", {},
                             p.agg.flushed,
                             "10 s detection windows flushed.", "counter"))

        # --- alert counters (eager, via AlertSink.subscribe) ---
        if self.sink is not None:
            s.append(_Sample(f"{NAMESP}_alerts_total", {},
                             sum(self._by_class.values()),
                             "Alerts emitted by the fusion engine.",
                             "counter"))
            for (cls, sev), n in self._by_class.items():
                s.append(_Sample(
                    f"{NAMESP}_alerts_total",
                    {"threat_class": cls, "severity": sev}, n, "", "counter"))
            s.append(_Sample(f"{NAMESP}_alerts_suppressed_total", {},
                             self.sink.suppressed,
                             "Alerts squashed by the Tier-0 operator "
                             "allowlist.", "counter"))
            s.append(_Sample(f"{NAMESP}_ml_alerts_total", {},
                             self._ml_total,
                             "Alerts attributed to the Tier-2 LightGBM flow "
                             "scorer.", "counter"))
            s.append(_Sample(f"{NAMESP}_cnn_alerts_total", {},
                             self._cnn_total,
                             "Alerts confirmed by the Tier-2 DGA character "
                             "CNN.", "counter"))

        # --- capture-source stats (live only) ---
        if self.source is not None and hasattr(self.source, "snapshot"):
            snap = self.source.snapshot()
            mapping = (
                ("seen", "frames_seen_total", "counter",
                 "Ethernet frames pulled off the socket."),
                ("analysed", "frames_analysed_total", "counter",
                 "Frames that survived the sampler and got dissected."),
                ("sampled_out", "frames_sampled_out_total", "counter",
                 "Frames skipped by the 1-in-N line-rate guard."),
                ("non_ipv4", "frames_non_ipv4_total", "counter",
                 "ARP/LLDP/IPv6 frames -- not parsed."),
                ("other_ip", "frames_other_ip_total", "counter",
                 "ICMP/GRE/ESP -- no detector consumes these."),
                ("malformed", "frames_malformed_total", "counter",
                 "Frames that failed dissection."),
                ("kernel_dropped", "kernel_dropped_total", "counter",
                 "Kernel ring-buffer drops: traffic LOST before analysis "
                 "(one-way feeds cannot retransmit)."),
            )
            for key, name, kind, help_ in mapping:
                if key in snap and snap[key] is not None:
                    s.append(_Sample(f"{NAMESP}_{name}", {}, snap[key],
                                     help_, kind))

        # --- process (so a batch-mode replay is scrapeable too) ---
        s.extend(self._proc_stats())
        s.append(_Sample(f"{NAMESP}_process_start_time_seconds", {},
                         self._start,
                         "Unix time the sensor started.", "gauge"))

        return s

    # ----------------------------------------------------------- rendering --

    def render(self) -> str:
        out = []
        seen = set()
        pid_label = {"sensor_pid": self.pid}
        for sample in self._samples():
            head = f"# HELP {sample.name} {sample.help}\n" \
                   f"# TYPE {sample.name} {sample.kind}\n"
            if sample.name not in seen:
                seen.add(sample.name)
                out.append(head)
            labels = dict(sample.labels or {})
            if not labels and sample.kind in ("counter", "gauge"):
                # singleton series still get a pid label so several sensors on
                # one host remain distinguishable
                labels = dict(pid_label)
            out.append(f"{sample.name}{_labels(**labels)} {_fmt(sample.value)}\n")
        return "".join(out)

    # ------------------------------------------------------------- server --

    def serve(self, port=9100, host="0.0.0.0") -> ThreadingHTTPServer:
        metrics = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.split("?")[0] in ("/metrics", "/"):
                    body = metrics.render().encode()
                    self.send_response(200)
                    self.send_header("Content-Type",
                                     "text/plain; version=0.0.4")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    try:
                        self.wfile.write(body)
                    except (BrokenPipeError, ConnectionResetError):
                        pass
                else:
                    self.send_error(404)

            def log_message(self, *a):
                pass

        server = ThreadingHTTPServer((host, port), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True,
                                  name="nids-metrics")
        thread.start()
        return server


if __name__ == "__main__":
    import sys
    from core.detectors import AlertSink

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9100
    m = NidsMetrics(AlertSink(path="/dev/null", truncate=False))
    m.serve(port)
    print(f"self-test exporter on :{port} -- Ctrl-C to stop")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass
