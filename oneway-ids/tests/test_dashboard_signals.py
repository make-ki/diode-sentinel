"""Behavior checks for the dashboard-only alert presentation adapter."""
import copy
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from dashboard_signals import describe_alert, summarize_alerts
from core.config import SCAN_MIN_PAIRS
from core.detectors import AlertSink, ScanDetector


class DashboardSignalTests(unittest.TestCase):
    def test_c2_fixture_arithmetic_and_zero_is_preserved(self):
        alert = {"threat_class": "c2_beaconing", "confidence": 0.8,
                 "evidence": {"flows_in_series": 6, "mean_interval_s": 0.0,
                             "iat_cv": 0.12, "cv_gate": 0.15}}
        result = describe_alert(alert)
        self.assertEqual(result["kind"], "rule")
        self.assertIn("flows 6", result["summary"])
        self.assertIn("mean interval (s) 0.0", result["summary"])
        self.assertEqual([f["value"] for f in result["facts"]], [6, 0.0, 0.12, 0.15])

    def test_exfil_registry_and_dns_volume_are_named_carefully(self):
        exfil = describe_alert({"threat_class": "data_exfiltration", "evidence": {
            "bytes_to_new_dst": 900, "src_baseline_bytes_median": 0,
            "ratio_vs_baseline": 900.0, "pair_age_windows": 0,
            "authorised_destination": True, "registry_entries": ["backup"],
        }})
        self.assertIn("operator registry match", exfil["summary"])
        self.assertEqual(exfil["facts"][1]["value"], 0)
        dns = describe_alert({"threat_class": "dns_tunneling", "evidence": {
            "query_bytes": 90, "qtype": 16, "tunnel_queries_from_src": 5,
            "cumulative_tunnel_bytes": 450,
        }})
        self.assertIn("not verified exfil volume", dns["summary"])

    def test_cnn_only_has_model_kind_and_does_not_invent_entropy(self):
        result = describe_alert({"threat_class": "dga_domain", "evidence": {
            "detector_tier": "tier2_cnn_only", "qname_label": "abcxyz",
            "label_length": 6, "dga_cnn_prob": 0.91,
        }})
        self.assertEqual(result["kind"], "model")
        self.assertEqual(result["score_label"], "Model score")
        self.assertIn("CNN-only", result["summary"])
        self.assertNotIn("entropy", " ".join(f["label"].lower() for f in result["facts"]))

    def test_model_vector_is_displayed_as_raw_numeric_values(self):
        result = describe_alert({"threat_class": "ml_flow_suspicious", "evidence": {
            "model": "lightgbm", "flow_features": {"npkt": 2, "duration": 0.0,
                                                        "is_udp": 0, "dport": 443}}})
        self.assertEqual(result["kind"], "model")
        self.assertEqual([f["value"] for f in result["facts"] if f["label"] != "Model"],
                         [2, 0.0, 0, 443])
        self.assertIn("packets=2", result["summary"])

    def test_known_model_vector_uses_exact_feature_order_and_units(self):
        result = describe_alert({"threat_class": "encrypted_session_malware", "evidence": {
            "model": "xgboost",
            "metadata_features": [0, 2, 13, 1, 0, 3, 40, 10000, 12.5, 0.25],
        }})
        self.assertEqual([f["label"] for f in result["facts"] if f["label"] != "Model"], [
            "ClientHello cipher-suite count (count)",
            "ClientHello extension count (count)",
            "ClientHello offered TLS version (code: 10=TLS 1.0; 11=TLS 1.1; 12=TLS 1.2; 13=TLS 1.3; 0=unknown)",
            "Transport code (0 = TLS, 1 = QUIC)",
            "SNI-present flag (0/1)",
            "Signature-algorithm count (count)",
            "Flow packet count (packets)", "Flow bytes (bytes)",
            "Flow duration (seconds)",
            "Packet-size coefficient of variation (unitless)",
        ])
        # Recorded zero remains a measured vector value; no availability flag
        # exists in this legacy record to interpret it as absent metadata.
        self.assertEqual(result["facts"][1]["value"], 0)
        self.assertIn("no metadata-availability flags", result["caveat"])

    def test_scan_and_exfil_vectors_have_named_serving_order(self):
        scan = describe_alert({"threat_class": "recon_model_scan", "evidence": {
            "model": "scan_rf", "features": [20, 5, 8, 0.4, 9000]}})
        self.assertEqual([f["label"] for f in scan["facts"] if f["label"] != "Model"], [
            "Distinct destination/port pairs (pairs)", "Distinct destination IPs (IPs)",
            "Maximum ports on one destination (ports)",
            "Maximum per-destination share of pairs (unitless ratio)",
            "Source bytes in window (bytes)",
        ])
        exfil = describe_alert({"threat_class": "data_exfiltration_model", "evidence": {
            "model": "exfil_xgb", "features": [5000, 10000, 0.5, 4, 1]}})
        self.assertEqual([f["value"] for f in exfil["facts"] if f["label"] != "Model"],
                         [5000, 10000, 0.5, 4, 1])

    def test_rolling_scan_is_presented_as_bounded_rule_evidence(self):
        src, dst = "10.0.0.4", "198.51.100.2"
        per_window = max(1, (SCAN_MIN_PAIRS + 1) // 2)
        with tempfile.TemporaryDirectory() as folder:
            sink = AlertSink(os.path.join(folder, "alerts.jsonl"))
            detector = ScanDetector(sink, rolling_window=60)

            def window(t0, first_port):
                pairs = {(dst, first_port + i) for i in range(per_window)}
                return {
                    "t0": t0, "t1": t0 + 10,
                    "pairs": {src: pairs},
                    "pair_endpoints": {
                        (src, dst): {("tcp", port) for _, port in pairs}},
                }

            detector.on_window(window(0, 1000))
            detector.on_window(window(10, 2000))
            alert = next(a for a in sink.alerts
                         if a["threat_class"] == "recon_rolling_vertical_scan")
        result = describe_alert(alert)
        evidence = alert["evidence"]
        self.assertIn("Rolling-window port scan", result["label"])
        facts = {fact["label"]: fact["value"] for fact in result["facts"]}
        self.assertEqual(evidence["rolling_distinct_dst_port_pairs"], 2 * per_window)
        self.assertEqual(facts["Distinct destination/port pairs in rolling history"],
                         2 * per_window)
        self.assertEqual(facts["Rolling horizon (s)"], 60.0)
        self.assertEqual(facts["Pairs in current window"], per_window)
        self.assertEqual(facts["Observed endpoint sample"], evidence["observed_endpoints_sample"])
        self.assertEqual(facts["History evictions"], evidence["history_evictions"])
        self.assertIn("rolling horizon (s) 60.0", result["summary"])
        self.assertIn("observed_endpoints_truncated", evidence)

    def test_unknown_or_incomplete_model_vector_stays_raw(self):
        result = describe_alert({"threat_class": "recon_model_scan", "evidence": {
            "model": "scan_rf", "features": [[1.0, 2.0, 3.0]]}})
        self.assertEqual(result["kind"], "model")
        self.assertIn([[1.0, 2.0, 3.0]], [f["value"] for f in result["facts"]])
        self.assertTrue(any(f["label"] == "Unmapped numeric feature vector"
                            for f in result["facts"]))
        self.assertIn("Raw numeric model vector", result["summary"])

    def test_correlation_related_signals_use_only_observed_values(self):
        alert = {"threat_class": "confirmed_c2_implant", "evidence": {
            "contributing_signals": [
                {"threat_class": "tls_known_malware", "age_s": 0,
                 "dst": "198.51.100.23", "dport": 0},
                {"threat_class": "c2_beaconing", "age_s": 12.5,
                 "dst": "*", "dport": 443},
            ]}}
        result = describe_alert(alert)
        self.assertEqual(result["kind"], "correlation")
        self.assertIn("not confirmation", result["summary"])
        self.assertEqual(result["related"], [
            {"label": "tls_known_malware", "age_seconds": 0, "effective_score": None, "destination": "198.51.100.23"},
            {"label": "c2_beaconing", "age_seconds": 12.5, "effective_score": None, "destination": None},
        ])
        self.assertTrue(all("port" not in r and "dport" not in r for r in result["related"]))

    def test_missing_evidence_unknown_has_no_invented_investigation(self):
        result = describe_alert({"threat_class": "future_detector", "evidence": {"x": None}})
        self.assertEqual(result["kind"], "unknown")
        self.assertEqual(result["summary"], "Measurements not recorded")
        self.assertEqual(result["facts"], [])
        self.assertIsNone(result["next_step"])

    def test_summary_partitions_without_double_counting_correlation_as_rule(self):
        alerts = [
            {"src": "10.0.0.1", "severity": "critical", "threat_class": "data_exfiltration",
             "evidence": {"authorised_destination": True}},
            {"src": "10.0.0.2", "severity": "critical", "threat_class": "ml_flow_suspicious",
             "evidence": {}},
            {"src": "10.0.0.1", "severity": "critical", "threat_class": "confirmed_exfiltration",
             "evidence": {"contributing_signals": []}},
            {"src": "*", "severity": "high", "threat_class": "ddos_syn_flood", "evidence": {}},
            {"src": "10.0.0.3", "threat_class": "unknown_alert", "evidence": {}},
        ]
        before = copy.deepcopy(alerts)
        result = summarize_alerts(alerts)
        self.assertEqual(result, {"raw_records": 5, "rule_records": 2,
                                  "model_records": 1, "correlation_records": 1,
                                  "unknown_records": 1, "critical_rule_records": 1,
                                  "authorised_records": 1, "source_count": 3})
        self.assertEqual(alerts, before)

    def test_real_ml_regression_records_have_presented_evidence(self):
        path = os.path.join(ROOT, ".regression", "alerts_ml.reference.jsonl")
        with open(path) as stream:
            alerts = [json.loads(line) for line in stream if line.strip()]
        classes = set()
        for alert in alerts:
            result = describe_alert(alert)
            classes.add(alert["threat_class"])
            self.assertTrue(result["facts"] or result["related"], alert["threat_class"])
            self.assertTrue(result["summary"])
            self.assertLessEqual(len(result["summary"]), 160)
            self.assertNotIn("?", result["summary"])
        expected_values = {"c2_beaconing": "4.98", "data_exfiltration": "933800",
                           "dns_tunneling": "70", "recon_vertical_scan": "202"}
        for threat, value in expected_values.items():
            alert = next(a for a in alerts if a["threat_class"] == threat)
            self.assertIn(value, describe_alert(alert)["summary"])
        self.assertIn("data_exfiltration", classes)


if __name__ == "__main__":
    unittest.main()
