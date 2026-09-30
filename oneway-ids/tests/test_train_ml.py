"""Behavior checks for explicit benign-replay labeling."""
import unittest
import os
import sys
import json
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from training.train_ml import build_rows, select_replay_rows, evaluate_predictions


def flow(src, dst="93.184.216.1", dport=443, proto="tcp", t0=10.0):
    return {"key": (src, 50000, dst, dport, proto), "t0": t0,
            "t1": t0 + 1, "npkt": 2, "nbytes": 1200, "nsyn": 1}


class BenignReplayLabelTests(unittest.TestCase):
    def test_selected_benign_source_is_present_and_benign(self):
        flows = [flow("10.0.0.6")]
        rows = select_replay_rows(flows, build_rows(flows), ["10.0.0.6"])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][1], 0)

    def test_known_attack_is_not_relabelled_benign(self):
        # This is a generator-known C2 destination even if its source is selected.
        flows = [flow("10.0.0.6", dst="198.51.100.23")]
        rows = select_replay_rows(flows, build_rows(flows), ["10.0.0.6"])
        self.assertEqual(rows[0][1], 1)

    def test_unselected_source_does_not_enter_benign_replay_rows_by_selection(self):
        flows = [flow("10.0.0.6"), flow("10.0.0.7")]
        rows = build_rows(flows)
        selected = select_replay_rows(flows, rows, ["10.0.0.6"])
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0][1], 0)

    def test_holdout_report_serializes_numpy_prediction_counts(self):
        result = evaluate_predictions([0, 0, 1], np.array([0.99, 0.2, 0.97]))
        self.assertEqual(result["heldout_benign_false_positives"], 1)
        self.assertEqual(result["heldout_malicious_detected"], 1)
        self.assertEqual(json.loads(json.dumps(result)), result)


if __name__ == "__main__":
    unittest.main()
