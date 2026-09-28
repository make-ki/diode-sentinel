#!/usr/bin/env python3
"""
Unit tests for the Prometheus exporter (metrics.py).

Plain unittest, run directly:  uv run python test_metrics.py

Covers: exposition well-formedness (HELP/TYPE once per name, label syntax),
label-value escaping, counter monotonicity across alert emissions, tier
attribution from evidence, eager-vs-sampled attach semantics, suppressed
exports, flow-gauge sourcing (FlowAssembler.active_count_by_proto), source
snapshot passthrough, the HTTP endpoint contract, and the run.py hooks
(run_pipeline stats + run_stream on_source attachment).
"""
import os
import re
import sys
import threading
import unittest
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detectors import AlertSink
from metrics import NidsMetrics, _fmt, _mangle
from pipeline import FlowAssembler


def _parse(text):
    """Minimal exposition parser: -> {metric_name: [(labels_dict, value)]}."""
    series = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        name, _, rest = line.partition(" ")
        labels = {}
        if name.endswith("}"):
            name, _, blob = name.partition("{")
            for part in _split_labels(blob[:-1]):
                k, _, v = part.partition("=")
                labels[k] = v.strip('"')
        value = rest
        if value.startswith("{"):
            blob, _, value = value[1:].partition("} ")
            for part in _split_labels(blob):
                k, _, v = part.partition("=")
                labels[k] = v.strip('"')
        series.setdefault(name, []).append((labels, float(value)))
    return series


def _split_labels(blob):
    """Split 'a="1",b="x=1"' on commas outside quotes."""
    out, buf, inq = [], [], False
    for ch in blob:
        if ch == '"':
            inq = not inq
        if ch == "," and not inq:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if buf:
        out.append("".join(buf))
    return out


class FakeAgg:
    flushed = 5


class FakeProc:
    """The slice of StreamProcessor the exporter samples."""

    def __init__(self):
        self.npkt = 1234
        self.ndns = 40
        self.ntls = 7
        self.assembler = FlowAssembler()
        self.assembler.closed_count = 55
        self.agg = FakeAgg()


def _feed(assembler, proto, n=3):
    for i in range(n):
        assembler.feed(1.0 * i, "10.0.0.1", 1000, "10.0.0.2", 80 + i, proto,
                       100, False)


class TestFormatHelpers(unittest.TestCase):
    def test_fmt_integers_and_floats(self):
        self.assertEqual(_fmt(3), "3")
        self.assertEqual(_fmt(3.0), "3")
        self.assertEqual(_fmt(0.5), "0.5")
        self.assertEqual(_fmt(None), "NaN")

    def test_fmt_specials(self):
        self.assertEqual(_fmt(float("inf")), "+Inf")
        self.assertEqual(_fmt(float("-inf")), "-Inf")
        self.assertEqual(_fmt(float("nan")), "NaN")

    def test_mangle(self):
        self.assertEqual(_mangle("ddos_syn_flood"), "ddos_syn_flood")
        self.assertEqual(_mangle("bad/class name"), "bad_class_name")


class TestExposition(unittest.TestCase):
    def setUp(self):
        self.sink = AlertSink(path=os.devnull, truncate=False)
        self.proc = FakeProc()
        self.m = NidsMetrics(self.sink)
        self.m.observe_processor(self.proc)

    def _render(self):
        return self.m.render()

    def test_wellformed_lines(self):
        text = self._render()
        for line in text.splitlines():
            self.assertTrue(line.startswith("#") or " " in line, line)
            if line.startswith("# TYPE "):
                self.assertEqual(len(line.split()), 4, line)
            elif line.startswith("# HELP "):
                self.assertGreater(len(line.split()), 3, line)
            else:
                name, _, value = line.partition(" ")
                self.assertRegex(name, r"^[a-zA-Z_][a-zA-Z0-9_]*"
                                       r"(\{.*\})?$")
                float(value)                      # must parse

    def test_help_type_once_per_name(self):
        text = self._render()
        for name in {ln.split(" ")[2] for ln in text.splitlines()
                     if ln.startswith("# TYPE")}:
            helps = [ln for ln in text.splitlines()
                     if ln.startswith(f"# HELP {name} ")]
            types = [ln for ln in text.splitlines()
                     if ln.startswith(f"# TYPE {name} ")]
            self.assertEqual(len(helps), 1, name)
            self.assertEqual(len(types), 1, name)

    def test_singleton_series_carry_pid_label(self):
        series = _parse(self._render())
        for labels, _ in series["nids_packets_processed_total"]:
            self.assertIn("sensor_pid", labels)

    def test_label_escaping(self):
        self.sink.emit(1.0, '10.0.0."1"', "10.0.0.2", 80, "tcp",
                       'weird\nclass', 0.95, {"why": "x"})
        text = self._render()
        self.assertNotIn('\n', _mangle('weird\nclass'))
        self.assertNotIn('"', _mangle('10.0.0."1"'))
        # the escaped render must still parse cleanly
        parsed = _parse(text)
        self.assertTrue(any(l.get("threat_class") == "weird_class"
                            for l, _ in parsed["nids_alerts_total"]))


class TestCounters(unittest.TestCase):
    def setUp(self):
        self.sink = AlertSink(path=os.devnull, truncate=False)
        self.m = NidsMetrics(self.sink)

    def test_alert_counters_monotonic(self):
        seen = []
        for conf in (0.95, 0.75, 0.55, 0.3):
            self.sink.emit(1.0, "10.0.0.1", "10.0.0.2", 80, "tcp",
                           "ddos_syn_flood", conf, {})
            text = self.m.render()
            total = next(v for l, v in _parse(text)["nids_alerts_total"]
                         if not l.get("threat_class"))
            seen.append(total)
        self.assertEqual(seen, sorted(seen), "counter must not go backwards")
        self.assertEqual(seen[-1], 4)

    def test_severity_split_matches_confidence_thresholds(self):
        # detectors._severity: >=0.9 critical, >=0.7 high, >=0.5 medium
        self.sink.emit(1.0, "a", "b", 1, "tcp", "x", 0.95, {})
        self.sink.emit(1.0, "a", "b", 1, "tcp", "x", 0.75, {})
        self.sink.emit(1.0, "a", "b", 1, "tcp", "x", 0.55, {})
        by_sev = {l["severity"]: v
                  for l, v in _parse(self.m.render())["nids_alerts_total"]
                  if "severity" in l}
        self.assertEqual(by_sev, {"critical": 1, "high": 1, "medium": 1})

    def test_tier_attribution(self):
        self.sink.emit(1.0, "a", "b", 1, "tcp", "ml_flow_suspicious", 0.8,
                       {"tier": "ml"})
        self.sink.emit(1.0, "a", "b", 1, "tcp", "dga_domain", 0.8,
                       {"cnn": True})
        parsed = _parse(self.m.render())
        self.assertEqual(next(v for l, v in parsed["nids_ml_alerts_total"]
                              if l.get("sensor_pid")), 1)
        self.assertEqual(next(v for l, v in parsed["nids_cnn_alerts_total"]
                              if l.get("sensor_pid")), 1)

    def test_suppressed_exported(self):
        self.sink.suppress(3)
        val = next(v for l, v in
                   _parse(self.m.render())["nids_alerts_suppressed_total"]
                   if l.get("sensor_pid"))
        self.assertEqual(val, 3)

    def test_no_sink_no_crash(self):
        m = NidsMetrics(None)
        self.assertIn("nids_process_start_time_seconds", m.render())

    def test_process_stats_exported(self):
        parsed = _parse(self.m.render())
        self.assertIn("nids_process_cpu_seconds_total", parsed)
        self.assertIn("nids_process_resident_memory_bytes", parsed)
        self.assertIn("nids_process_start_time_seconds", parsed)


class TestSampledStats(unittest.TestCase):
    def test_processor_numbers_exported(self):
        m = NidsMetrics(AlertSink(path=os.devnull, truncate=False))
        proc = FakeProc()
        m.observe_processor(proc)
        parsed = _parse(m.render())
        self.assertEqual(parsed["nids_packets_processed_total"][0][1], 1234)
        self.assertEqual(parsed["nids_flows_closed_total"][0][1], 55)
        self.assertEqual(parsed["nids_windows_flushed_total"][0][1], 5)

    def test_active_flow_gauge_per_proto(self):
        m = NidsMetrics(AlertSink(path=os.devnull, truncate=False))
        proc = FakeProc()
        _feed(proc.assembler, "tcp", 2)
        _feed(proc.assembler, "udp", 1)
        m.observe_processor(proc)
        gauges = {l["kind"]: v
                  for l, v in _parse(m.render())["nids_flows_active"]}
        self.assertEqual(gauges, {"tcp": 2, "udp": 1})

    def test_source_snapshot_passthrough(self):
        m = NidsMetrics(AlertSink(path=os.devnull, truncate=False))

        class FakeSource:
            def snapshot(self):
                return {"seen": 100, "kernel_dropped": 4, "sample": 1,
                        "analysed": 96}

        m.observe_source(FakeSource())
        parsed = _parse(m.render())
        self.assertEqual(parsed["nids_frames_seen_total"][0][1], 100)
        self.assertEqual(parsed["nids_kernel_dropped_total"][0][1], 4)
        # keys with no mapping are ignored, mapped-but-absent keys too
        self.assertNotIn("nids_sample", parsed)
        self.assertNotIn("nids_frames_sampled_out_total", parsed)


class TestHttpEndpoint(unittest.TestCase):
    def test_serve_returns_exposition(self):
        m = NidsMetrics(AlertSink(path=os.devnull, truncate=False))
        m.observe_processor(FakeProc())
        # port 0 = kernel-assigned, so the test never collides
        server = m.serve(0, host="127.0.0.1")
        port = server.server_address[1]
        try:
            with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/metrics", timeout=5) as r:
                body = r.read().decode()
                self.assertEqual(r.headers["Content-Type"],
                                 "text/plain; version=0.0.4")
            self.assertIn("nids_packets_processed_total", body)
            self.assertNotIn("Flues", body)     # help text typo guard
        finally:
            server.shutdown()


class TestRunHooks(unittest.TestCase):
    """run.py integration: the exporter must see real pipeline stats."""

    def test_run_pipeline_attaches_stats(self):
        import run as run_mod

        # a two-packet "capture": enough to bump npkt and build one flow.
        # tuple order: (t, src, dst, proto, sport, dport, size, is_syn,
        #               payload, qname, seq, qtype)
        pkts = [(1.0, "10.0.0.1", "10.0.0.2", "tcp", 1000, 80, 100, 1, b"",
                 None, 0, None),
                (1.1, "10.0.0.1", "10.0.0.2", "tcp", 1000, 80, 100, 0, b"",
                 None, 100, None)]
        sink = AlertSink(path=os.devnull, truncate=False)
        metrics = NidsMetrics(sink)
        stats = run_mod.run_pipeline(iter(pkts), sink, metrics=metrics)
        parsed = _parse(metrics.render())
        self.assertEqual(parsed["nids_packets_processed_total"][0][1], 2)
        self.assertGreaterEqual(
            parsed["nids_flows_closed_total"][0][1],
            stats["flows"])

    def test_source_attached_before_processor(self):
        # run_live calls metrics.observe_source(source) the moment the source
        # exists -- before the StreamProcessor is built -- so the exporter must
        # be scrapeable in that window (frames/drops without pipeline stats).
        class FakeSource:
            def snapshot(self):
                return {"seen": 7, "kernel_dropped": 0}

        metrics = NidsMetrics(AlertSink(path=os.devnull, truncate=False))
        metrics.observe_source(FakeSource())
        parsed = _parse(metrics.render())
        self.assertEqual(parsed["nids_frames_seen_total"][0][1], 7)
        self.assertEqual(parsed["nids_kernel_dropped_total"][0][1], 0)
        self.assertNotIn("nids_packets_processed_total", parsed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
