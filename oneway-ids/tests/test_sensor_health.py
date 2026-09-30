"""Health sidecar reports measured counts and live-source lifecycle honestly."""
import json
import os
import tempfile
import time
import unittest
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from core.sensor_health import atomic_write_json, health_snapshot
from core.live_source import AfPacketSource, CaptureConfigError, PcapStreamSource
from core.detectors import AlertSink
import run


class Source:
    iface = "demo0"
    def snapshot(self):
        return {
            "seen": 8, "analysed": 3, "sampled_out": 2,
            "malformed": 1, "kernel_dropped": None, "sample": 4,
            "last_packet_observed_at": time.time() - 1,
        }


class EmptySource(Source):
    anchor = 1_700_000_000.0
    eof = True
    def default_clock(self):
        return None
    def drain(self, batch):
        return None
    def close(self):
        self.closed = True


class BrokenSource(EmptySource):
    eof = False
    def drain(self, batch):
        raise RuntimeError("synthetic read failure")


class SensorHealthTests(unittest.TestCase):
    def test_idle_and_active_states_keep_unknown_distinct_from_zero(self):
        source = Source()
        active = health_snapshot(source, status="active", mode="interface",
                                 started_at="start", now=time.time())
        self.assertEqual(active["status"], "active")
        self.assertEqual(active["counts"]["seen"], 8)
        self.assertIsNone(active["counts"]["kernel_drops"])
        self.assertEqual(active["interface"], "demo0")
        idle = health_snapshot(source, status="active", mode="interface",
                               started_at="start",
                               now=time.time() + 6)
        self.assertEqual(idle["status"], "idle")

    def test_terminal_state_and_atomic_json_are_readable(self):
        health = health_snapshot(Source(), status="completed",
                                 mode="pcap_stream", started_at="start")
        health["path"] = "/tmp/demo.pcap"
        self.assertEqual(health["status"], "completed")
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "run_stats.json")
            atomic_write_json(path, {"health": health})
            with open(path) as stream:
                loaded = json.load(stream)
            self.assertEqual(loaded["health"]["counts"]["kernel_drops"], None)
            self.assertEqual(os.listdir(folder), ["run_stats.json"])

    def test_live_eof_marks_completed_and_keeps_unknown_drop_count(self):
        with tempfile.TemporaryDirectory() as folder:
            stats_path = os.path.join(folder, "run_stats.json")
            alert_path = os.path.join(folder, "alerts.jsonl")
            with patch.object(run, "ALERTS_PATH", alert_path):
                source = EmptySource()
                run.run_live("unused", AlertSink(alert_path), source=source,
                             state_path=None, verbose=False)
            with open(stats_path) as stream:
                health = json.load(stream)["health"]
            self.assertEqual(health["status"], "completed")
            self.assertIsNone(health["counts"]["kernel_drops"])
            self.assertTrue(source.closed)

    def test_live_read_error_marks_failed_and_closes_source(self):
        with tempfile.TemporaryDirectory() as folder:
            stats_path = os.path.join(folder, "run_stats.json")
            alert_path = os.path.join(folder, "alerts.jsonl")
            with patch.object(run, "ALERTS_PATH", alert_path):
                source = BrokenSource()
                with self.assertRaisesRegex(RuntimeError, "synthetic read"):
                    run.run_live("unused", AlertSink(alert_path), source=source,
                                 state_path=None, verbose=False)
            with open(stats_path) as stream:
                health = json.load(stream)["health"]
            self.assertEqual(health["status"], "failed")
            self.assertIn("synthetic read failure", health["error"])
            self.assertTrue(source.closed)

    def test_live_open_error_is_written_as_failed(self):
        with tempfile.TemporaryDirectory() as folder:
            stats_path = os.path.join(folder, "run_stats.json")
            alert_path = os.path.join(folder, "alerts.jsonl")
            missing = os.path.join(folder, "missing.pcap")
            with patch.object(run, "ALERTS_PATH", alert_path):
                with self.assertRaises(CaptureConfigError):
                    run.run_live(missing, AlertSink(alert_path),
                                 source=PcapStreamSource(missing),
                                 state_path=None, verbose=False)
            with open(stats_path) as stream:
                health = json.load(stream)["health"]
            self.assertEqual(health["status"], "failed")
            self.assertEqual(health["mode"], "pcap_stream")
            self.assertEqual(health["path"], missing)

    def test_socket_errors_escape_drain_and_drops_stay_unknown(self):
        source = AfPacketSource("mock0")
        self.assertIsNone(source.snapshot()["kernel_dropped"])
        class FailedSocket:
            def settimeout(self, _timeout):
                pass
            def recvmsg(self, _size):
                raise OSError("mock socket failure")
        source.sock = FailedSocket()
        with self.assertRaisesRegex(OSError, "mock socket failure"):
            source.drain()

    def test_socket_drop_deltas_reach_health_as_cumulative_measurements(self):
        import socket
        import struct
        source = AfPacketSource("mock0")
        class MeasuredSocket:
            drops = iter((3, 5))
            def settimeout(self, _timeout):
                pass
            def recvmsg(self, _size):
                raise socket.timeout()
            def getsockopt(self, *_args):
                return struct.pack("II", 10, next(self.drops))
        source.sock = MeasuredSocket()
        source.drain()
        first = health_snapshot(source, status="active", mode="interface", started_at="start")
        self.assertEqual(first["counts"]["kernel_drops"], 3)
        source.drain()
        second = health_snapshot(source, status="active", mode="interface", started_at="start")
        self.assertEqual(second["counts"]["kernel_drops"], 8)


if __name__ == "__main__":
    unittest.main()
