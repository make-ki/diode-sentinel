"""Independent behavior checks for the opt-in rolling scan rule."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.detectors import ScanDetector


class Sink:
    def __init__(self):
        self.alerts = []

    def emit(self, t, src, dst, dport, proto, threat, confidence, evidence):
        self.alerts.append({"t": t, "src": src, "dst": dst, "dport": dport,
                            "proto": proto, "threat_class": threat,
                            "confidence": confidence, "evidence": evidence})


def window(start, src_to_pairs):
    pairs = {src: set(items) for src, items in src_to_pairs.items()}
    endpoints = {}
    for src, items in pairs.items():
        for dst, port in items:
            endpoints[(src, dst)] = {("tcp", port)}
    return {"t0": start, "t1": start + 10, "pairs": pairs,
            "pair_endpoints": endpoints}


def vertical_ports(first, count, dst="203.0.113.8"):
    return {(dst, first + offset) for offset in range(count)}


class RollingScanTests(unittest.TestCase):
    def test_adjacent_partial_windows_accumulate_one_vertical_alert(self):
        sink = Sink()
        detector = ScanDetector(sink, rolling_window=60)
        detector.on_window(window(0, {"10.0.0.1": vertical_ports(1000, 10)}))
        detector.on_window(window(10, {"10.0.0.1": vertical_ports(1010, 10)}))
        rolling = [a for a in sink.alerts
                   if a["threat_class"] == "recon_rolling_vertical_scan"]
        self.assertEqual(len(rolling), 1)
        self.assertEqual(rolling[0]["dst"], "203.0.113.8")
        ev = rolling[0]["evidence"]
        self.assertEqual(ev["rolling_distinct_dst_port_pairs"], 20)
        self.assertEqual(ev["current_window_distinct_pairs"], 10)

    def test_repeated_endpoint_retries_do_not_inflate_distinct_count(self):
        sink = Sink()
        detector = ScanDetector(sink, rolling_window=60)
        repeated = vertical_ports(1000, 10)
        for start in (0, 10, 20, 30):
            detector.on_window(window(start, {"10.0.0.1": repeated}))
        self.assertFalse(any(a["threat_class"].startswith("recon_rolling_")
                             for a in sink.alerts))

    def test_pairs_older_than_horizon_do_not_accumulate(self):
        sink = Sink()
        detector = ScanDetector(sink, rolling_window=60)
        detector.on_window(window(0, {"10.0.0.1": vertical_ports(1000, 10)}))
        detector.on_window(window(70, {"10.0.0.1": vertical_ports(1010, 10)}))
        self.assertFalse(any(a["threat_class"].startswith("recon_rolling_")
                             for a in sink.alerts))

    def test_sources_do_not_share_fanout_history(self):
        sink = Sink()
        detector = ScanDetector(sink, rolling_window=60)
        detector.on_window(window(0, {"10.0.0.1": vertical_ports(1000, 10),
                                      "10.0.0.2": vertical_ports(2000, 10)}))
        detector.on_window(window(10, {"10.0.0.1": vertical_ports(1010, 10)}))
        rolling = [a for a in sink.alerts
                   if a["threat_class"].startswith("recon_rolling_")]
        self.assertEqual([a["src"] for a in rolling], ["10.0.0.1"])

    def test_default_mode_preserves_single_window_only_behavior(self):
        sink = Sink()
        detector = ScanDetector(sink)
        detector.on_window(window(0, {"10.0.0.1": vertical_ports(1000, 20)}))
        self.assertEqual([a["threat_class"] for a in sink.alerts],
                         ["recon_vertical_scan"])

    def test_rolling_mode_does_not_duplicate_a_full_window_rule_alert(self):
        sink = Sink()
        detector = ScanDetector(sink, rolling_window=60)
        detector.on_window(window(0, {"10.0.0.1": vertical_ports(1000, 20)}))
        self.assertEqual([a["threat_class"] for a in sink.alerts],
                         ["recon_vertical_scan"])

    def test_rolling_horizontal_fanout_is_classified(self):
        sink = Sink()
        detector = ScanDetector(sink, rolling_window=60)
        first = {(f"198.51.100.{i}", 443) for i in range(1, 11)}
        second = {(f"203.0.113.{i}", 443) for i in range(1, 11)}
        detector.on_window(window(0, {"10.0.0.1": first}))
        detector.on_window(window(10, {"10.0.0.1": second}))
        rolling = [a for a in sink.alerts
                   if a["threat_class"] == "recon_rolling_horizontal_scan"]
        self.assertEqual(len(rolling), 1)
        self.assertEqual(rolling[0]["dst"], "*")

    def test_pair_cap_is_visible_and_sample_truncation_is_exact(self):
        sink = Sink()
        detector = ScanDetector(sink, rolling_window=60)
        detector.ROLLING_MAX_PAIRS_PER_SOURCE = 25
        detector.on_window(window(0, {"10.0.0.1": vertical_ports(1000, 19)}))
        detector.on_window(window(10, {"10.0.0.1": vertical_ports(1019, 19)}))
        alert, = [a for a in sink.alerts
                  if a["threat_class"] == "recon_rolling_vertical_scan"]
        ev = alert["evidence"]
        self.assertEqual(ev["rolling_distinct_dst_port_pairs"], 25)
        self.assertEqual(ev["history_evictions"]["pairs_for_source"], 13)
        self.assertEqual(len(ev["observed_endpoints_sample"]), 20)
        self.assertTrue(ev["observed_endpoints_truncated"])

    def test_source_cap_eviction_is_reported(self):
        sink = Sink()
        detector = ScanDetector(sink, rolling_window=60)
        detector.ROLLING_MAX_SOURCES = 1
        detector.on_window(window(0, {"10.0.0.1": vertical_ports(1000, 10)}))
        detector.on_window(window(10, {"10.0.0.2": vertical_ports(2000, 10)}))
        detector.on_window(window(20, {"10.0.0.2": vertical_ports(2010, 10)}))
        rolling, = [a for a in sink.alerts
                    if a["threat_class"] == "recon_rolling_vertical_scan"]
        self.assertEqual(rolling["evidence"]["history_evictions"]["source_entries"], 1)


if __name__ == "__main__":
    unittest.main()
