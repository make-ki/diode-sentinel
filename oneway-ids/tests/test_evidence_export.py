"""Behavior for single-alert offline evidence bundles."""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import dashboard
from core.evidence_export import record_sha256
REAL_ALERT_LOADER = dashboard._load


class EvidenceExportTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"timestamp": "2026-09-30T10:00:00Z", "src": "10.0.0.1",
             "dst": "198.51.100.1", "flow_id": "10.0.0.1:*->198.51.100.1:443/tcp",
             "threat_class": "ml_flow_suspicious", "confidence": 0.72,
             "severity": "high", "evidence": {"flow_features": {"npkt": 10}}},
            {"timestamp": "2026-09-30T10:01:00Z", "src": "10.0.0.2",
             "dst": "198.51.100.2", "flow_id": "10.0.0.2:*->198.51.100.2:443/tcp",
             "threat_class": "c2_beaconing", "confidence": 0.8,
             "severity": "high", "evidence": {"flows_in_series": 5}},
        ]
        self.load_patch = patch.object(dashboard, "_load", return_value=self.records)
        self.sensor_patch = patch.object(dashboard, "_load_sensor", return_value={})
        self.load_patch.start()
        self.sensor_patch.start()
        self.addCleanup(self.load_patch.stop)
        self.addCleanup(self.sensor_patch.stop)

    def test_export_preserves_original_and_marks_page_truncation(self):
        query = {"severity": ["high"], "limit": ["1"], "sort": ["newest"]}
        page = dashboard._payload(query)
        self.assertEqual(page["matched"], 2)
        selected = page["alerts"][0]
        params = dict(query, record=[selected["triage"]["export_key"]])
        bundle, _ = dashboard._export_payload(params)
        self.assertEqual(bundle["schema_version"], "diode-sentinel-alert-evidence/v1")
        self.assertEqual(bundle["filter_context"]["filters"]["severity"], ["high"])
        self.assertEqual(bundle["filter_context"]["matched_alerts"], 2)
        self.assertEqual(bundle["filter_context"]["page_limit"], 1)
        self.assertTrue(bundle["filter_context"]["page_truncated"])
        record = bundle["alert"]["record"]
        self.assertEqual(record, self.records[1])
        self.assertEqual(bundle["alert"]["record_sha256"], record_sha256(record))
        self.assertEqual(bundle["integrity"]["scope"], "alert.record only")
        self.assertFalse(bundle["integrity"]["legal_custody_claim"])
        self.assertEqual(bundle["provenance_availability"]["capture_identity"],
                         "not recorded in alert")
        self.assertNotIn("path", bundle)

    def test_export_rejects_alert_excluded_by_active_filter(self):
        key = record_sha256(self.records[0])
        with self.assertRaises(LookupError):
            dashboard._export_payload({"severity": ["critical"], "record": [key]})

    def test_alert_loader_skips_malformed_lines_and_keeps_neighbors(self):
        first = {"timestamp": "2026-09-30T10:00:00Z", "threat_class": "first"}
        last = {"timestamp": "2026-09-30T10:02:00Z", "threat_class": "last"}
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "alerts.jsonl")
            with open(path, "w", encoding="utf-8") as stream:
                stream.write(json.dumps(first) + "\n")
                stream.write("not-json\n")
                stream.write("[]\nnull\n\"primitive\"\n")
                stream.write('{"confidence": NaN}\n')
                stream.write('{"confidence": Infinity}\n')
                stream.write('{"confidence": 1e999}\n')
                stream.write(json.dumps(last) + "\n")
            # Call the real loader rather than setUp's fixture stub used by
            # the export-selection tests.
            with patch.object(dashboard, "ALERTS_PATH", path):
                self.assertEqual(REAL_ALERT_LOADER(), [first, last])


if __name__ == "__main__":
    unittest.main()
