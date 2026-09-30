import os
import sys
import tempfile
import unittest
from pathlib import Path

# Direct test-file invocation sets sys.path[0] to tests/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from training.score_iot23 import read_conn_log, one_way_packets, score_hosts


CONN = """#separator \\x09
#set_separator ,
#empty_field (empty)
#unset_field -
#fields\tts\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tproto\tlabel\tdetailed-label
1.0\t192.0.2.10\t40000\t198.51.100.7\t443\ttcp\tMalicious\tHakai
2.0\t192.0.2.20\t40001\t198.51.100.8\t443\ttcp\tBenign\t-
3.0\t192.0.2.20\t443\t198.51.100.8\t40001\ttcp\tBenign\t-
"""


class IoT23ScorerTests(unittest.TestCase):
    def test_conn_labels_and_direction_are_parsed(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "conn.log")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(CONN)
            directions, labels = read_conn_log(path)
        self.assertEqual(len(directions), 3)
        self.assertEqual(labels["192.0.2.10"], {"malicious"})
        self.assertEqual(labels["192.0.2.20"], {"benign"})

    def test_whitespace_combined_label_suffix_is_supported(self):
        conn = """#separator \\x09
#fields\tts\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tproto\tlabel   detailed-label
1.0\t192.0.2.10\t40000\t198.51.100.7\t443\ttcp\tMalicious   C&C-FileDownload
2.0\t192.0.2.20\t40001\t198.51.100.8\t443\ttcp\tBenign   -
"""
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "conn.log")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(conn)
            directions, labels = read_conn_log(path)
        self.assertEqual(len(directions), 2)
        self.assertEqual(labels["192.0.2.10"], {"malicious"})
        self.assertEqual(labels["192.0.2.20"], {"benign"})

    def test_only_originator_direction_is_replayed(self):
        directions = {("192.0.2.10", 40000, "198.51.100.7", 443, "tcp")}
        originator = (1.0, "192.0.2.10", "198.51.100.7", "tcp", 40000,
                      443, 100, False, b"", None, 0, None)
        responder = (1.1, "198.51.100.7", "192.0.2.10", "tcp", 443,
                     40000, 100, False, b"", None, 0, None)
        self.assertEqual(list(one_way_packets([originator, responder], directions),),
                         [originator])

    def test_bidirectionally_ambiguous_conn_tuples_are_dropped(self):
        a_to_b = ("192.0.2.10", 40000, "198.51.100.7", 443, "tcp")
        b_to_a = ("198.51.100.7", 443, "192.0.2.10", 40000, "tcp")
        packet_a = (1.0, a_to_b[0], a_to_b[2], "tcp", a_to_b[1], a_to_b[3],
                    100, False, b"", None, 0, None)
        packet_b = (1.1, b_to_a[0], b_to_a[2], "tcp", b_to_a[1], b_to_a[3],
                    100, False, b"", None, 0, None)
        self.assertEqual(list(one_way_packets([packet_a, packet_b], {a_to_b, b_to_a})), [])

    def test_zero_accepted_packets_fails(self):
        from training.score_iot23 import require_packets
        with self.assertRaisesRegex(ValueError, "no pcap packets matched"):
            require_packets(0)

    def test_unknown_detailed_label_does_not_create_ground_truth(self):
        conn = "#fields\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tproto\tlabel\tdetailed-label\n" \
               "192.0.2.1\t10\t198.51.100.1\t443\ttcp\t-\tUnfamiliar-Classification\n"
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "conn.log")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(conn)
            with self.assertRaisesRegex(ValueError, "no recognized primary labels"):
                read_conn_log(path)

    def test_host_metrics_count_hosts_once_and_prefer_malicious_label(self):
        labels = {"mal": {"malicious"}, "ben": {"benign"},
                  "mixed": {"benign", "malicious"}}
        alerts = [{"src": "mal", "threat_class": "c2_beaconing"},
                  {"src": "mixed", "threat_class": "c2_beaconing"},
                  {"src": "ben", "threat_class": "c2_beaconing"},
                  {"src": "ben", "threat_class": "scan"}]
        result = score_hosts(alerts, labels)
        self.assertEqual(result["counts"], {"tp": 2, "fp": 1, "fn": 0, "tn": 0,
                                             "malicious_hosts": 2, "benign_hosts": 1,
                                             "alerted_hosts": 3})
        self.assertAlmostEqual(result["precision"], 2 / 3)
        self.assertEqual(result["recall"], 1.0)
        self.assertEqual(result["alert_classes"], {"c2_beaconing": 3, "scan": 1})

    def test_missing_recognized_labels_fails_closed(self):
        conn = "#fields\tid.orig_h\tid.orig_p\tid.resp_h\tid.resp_p\tproto\n" \
               "192.0.2.1\t10\t198.51.100.1\t443\ttcp\n"
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "conn.log")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(conn)
            with self.assertRaisesRegex(ValueError, "no recognized primary labels"):
                read_conn_log(path)


if __name__ == "__main__":
    unittest.main()
