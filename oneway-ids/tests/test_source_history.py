"""Behavior checks for bounded source-relative destination context."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.detectors import ExfilDetector
from core.source_history import SourceDestinationHistory


class Sink:
    def __init__(self):
        self.alerts = []

    def emit(self, t, src, dst, dport, proto, threat, confidence, evidence):
        self.alerts.append({"t": t, "src": src, "dst": dst,
                            "threat_class": threat, "evidence": evidence})


def window(idx, src, dst, amount, fleet_novel=()):
    return {
        "idx": idx, "t0": idx * 10.0, "t1": (idx + 1) * 10.0,
        "pair_bytes": {(src, dst): amount},
        "pair_endpoints": {(src, dst): {("tcp", 8443)}},
        "src_bytes": {src: amount},
        "novel_dsts": set(fleet_novel),
    }


class SourceDestinationHistoryTests(unittest.TestCase):
    def test_ttl_forgets_only_outside_the_declared_lookback(self):
        history = SourceDestinationHistory(max_age_windows=2, max_entries=8)
        self.assertEqual(history.observe("a", "x", 0),
                         (True, "complete_within_lookback"))
        self.assertEqual(history.observe("a", "x", 1),
                         (False, "complete_within_lookback"))
        self.assertEqual(history.observe("a", "x", 4),
                         (True, "complete_within_lookback"))
        self.assertEqual(history.expired_entries, 1)
        self.assertEqual(history.coverage["max_age_windows"], 2)

    def test_capacity_eviction_marks_source_incomplete_and_blocks_novelty(self):
        history = SourceDestinationHistory(max_age_windows=10, max_entries=1)
        self.assertTrue(history.observe("a", "x", 0)[0])
        self.assertTrue(history.observe("b", "y", 1)[0])
        self.assertEqual(history.observe("a", "z", 2),
                         (False, "incomplete_after_capacity_eviction"))
        self.assertEqual(history.coverage["evicted_entries"], 1)
        self.assertEqual(history.coverage["incomplete_sources"], 1)

    def test_coverage_markers_are_bounded_and_fail_closed_when_full(self):
        history = SourceDestinationHistory(max_age_windows=10, max_entries=1)
        history.observe("a", "x", 0)
        history.observe("b", "y", 1)
        history.observe("c", "z", 2)
        self.assertLessEqual(history.coverage["incomplete_sources"], 1)
        self.assertTrue(history.coverage["global_coverage_incomplete"])
        self.assertEqual(history.observe("d", "w", 3),
                         (False, "incomplete_after_capacity_eviction"))

    def test_source_first_contact_survives_fleet_global_seen_destination(self):
        sink = Sink()
        detector = ExfilDetector(sink, source_context=True)
        detector.on_window(window(0, "10.0.0.1", "198.51.100.8", 600_000,
                                  fleet_novel={"198.51.100.8"}))
        detector.on_window(window(1, "10.0.0.2", "198.51.100.8", 600_000))
        second = next(a for a in sink.alerts if a["src"] == "10.0.0.2")
        evidence = second["evidence"]
        self.assertTrue(evidence["source_novel_within_lookback"])
        self.assertFalse(evidence["fleet_destination_novel"])
        self.assertEqual(evidence["source_history_coverage_at_admission"],
                         "complete_within_lookback")
        self.assertEqual(evidence["source_history_lookback_windows"], 8640)

    def test_default_mode_keeps_fleet_global_novelty_gate(self):
        sink = Sink()
        detector = ExfilDetector(sink)
        detector.on_window(window(0, "10.0.0.1", "198.51.100.8", 600_000,
                                  fleet_novel={"198.51.100.8"}))
        detector.on_window(window(1, "10.0.0.2", "198.51.100.8", 600_000))
        self.assertEqual([a["src"] for a in sink.alerts], ["10.0.0.1"])
        self.assertNotIn("source_novel_within_lookback",
                         sink.alerts[0]["evidence"])

    def test_established_pairs_refresh_the_observed_history(self):
        detector = ExfilDetector(Sink(), source_context=True,
                                 source_history_max_age_windows=2)
        for idx in range(4):
            detector.on_window(window(idx, "a", "x", 100))
        self.assertEqual(detector.source_destinations.expired_entries, 0)
        self.assertEqual(detector.source_destinations.coverage["retained_pairs"], 1)


if __name__ == "__main__":
    unittest.main()
