"""Dashboard health reflects writer lifecycle and missing heartbeats."""
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dashboard


class HealthTests(unittest.TestCase):
    def load(self, health):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "run_stats.json")
            with open(path, "w") as handle:
                json.dump({"health": health}, handle)
            with patch.object(dashboard, "STATS_PATH", path):
                return dashboard._load_sensor()["health"]

    def test_stale_heartbeat_does_not_claim_active(self):
        old = (datetime.now(timezone.utc) - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        health = self.load({"status": "active", "heartbeat_at": old})
        self.assertEqual(health["status"], "stale")
        self.assertGreaterEqual(health["heartbeat_age_seconds"], 30)

    def test_quiet_sensor_with_fresh_heartbeat_is_idle(self):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        health = self.load({"status": "idle", "heartbeat_at": now,
                            "counts": {"kernel_drops": None, "seen": 0}})
        self.assertEqual(health["status"], "idle")
        self.assertIsNone(health["counts"]["kernel_drops"])
        self.assertEqual(health["counts"]["seen"], 0)

    def test_terminal_status_survives_old_heartbeat(self):
        for status in ("completed", "stopped", "failed"):
            with self.subTest(status=status):
                self.assertEqual(self.load({"status": status, "heartbeat_at": "2020-01-01T00:00:00Z"})["status"], status)

    def test_missing_heartbeat_is_unknown(self):
        self.assertEqual(self.load({"status": "active"})["status"], "unknown")

    def test_demo_provenance_is_explicit(self):
        with patch.dict(os.environ, {"DIODESENTINEL_DEMO": "1"}):
            self.assertTrue(dashboard._stats([], {})["synthetic_demo"])


if __name__ == "__main__":
    unittest.main()
