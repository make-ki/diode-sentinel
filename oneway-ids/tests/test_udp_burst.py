"""One-way UDP burst/fan-out behavior at the window boundary."""
import os
import socket
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.detectors import AlertSink
from core.config import SIM_START
from core.pcap_reader import iter_dpkt
from core.pipeline import StreamProcessor
from dashboard import CLASS_TO_PS
from dashboard_signals import describe_alert
import dpkt


class UdpBurstTests(unittest.TestCase):
    def make_processor(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        sink = AlertSink(os.path.join(tmp.name, "alerts.jsonl"))
        return sink, StreamProcessor(sink)

    @staticmethod
    def feed_udp(processor, t, src, dst, dport, size=120):
        processor.feed((t, src, dst, "udp", 53000, dport, size, False,
                        b"", None, 0, 0))

    def test_udp_pcap_parses_and_emits_observed_endpoint_evidence(self):
        sink, processor = self.make_processor()
        with tempfile.TemporaryDirectory() as tmp:
            capture_path = os.path.join(tmp, "udp.pcap")
            capture_file = open(capture_path, "wb")
            writer = dpkt.pcap.Writer(capture_file)
            try:
                for i in range(100):
                    dst = f"198.51.100.{i % 20 + 1}"
                    udp = dpkt.udp.UDP(sport=53000, dport=1000 + i % 20,
                                       data=b"x" * 40)
                    udp.ulen = len(udp)
                    ip = dpkt.ip.IP(src=socket.inet_aton("192.0.2.40"),
                                    dst=socket.inet_aton(dst), p=dpkt.ip.IP_PROTO_UDP,
                                    data=udp)
                    ip.len = len(ip)
                    frame = dpkt.ethernet.Ethernet(
                        src=b"\x00" * 6, dst=b"\x11" * 6,
                        type=dpkt.ethernet.ETH_TYPE_IP, data=ip)
                    writer.writepkt(bytes(frame), ts=SIM_START + i / 10)
            finally:
                writer.close()
            for packet in iter_dpkt(capture_path):
                processor.feed(packet)
        processor.finish()

        alerts = [a for a in sink.alerts
                  if a["threat_class"] == "udp_burst_fanout"]
        self.assertEqual(len(alerts), 1)
        evidence = alerts[0]["evidence"]
        self.assertTrue(alerts[0]["flow_id"].endswith("/udp"))
        self.assertEqual(evidence["udp_packets"], 100)
        self.assertEqual(evidence["distinct_destination_endpoints"], 20)
        self.assertTrue(all(e["protocol"] == "udp"
                            for e in evidence["destination_endpoints_sample"]))
        presented = describe_alert(alerts[0])
        self.assertEqual(presented["kind"], "rule")
        self.assertIn("10.0", presented["summary"])
        self.assertIn("UDP packets per second",
                      {fact["label"] for fact in presented["facts"]})
        self.assertEqual(CLASS_TO_PS[alerts[0]["threat_class"]], "a")

    def test_udp_burst_reports_observed_rate_fanout_and_protocol(self):
        sink, processor = self.make_processor()
        src = "192.0.2.40"
        # 100 datagrams in 10 seconds to 20 distinct observed endpoints.
        for i in range(100):
            dst = f"198.51.100.{i % 20 + 1}"
            dport = 1000 + i % 20
            self.feed_udp(processor, i / 10, src, dst, dport)
        processor.finish()

        alerts = [a for a in sink.alerts
                  if a["threat_class"] == "udp_burst_fanout"]
        self.assertEqual(len(alerts), 1)
        alert = alerts[0]
        ev = alert["evidence"]
        self.assertEqual((alert["src"], alert["threat_class"]),
                         (src, "udp_burst_fanout"))
        self.assertTrue(alert["flow_id"].endswith("/udp"))
        self.assertEqual(ev["udp_packets"], 100)
        self.assertEqual(ev["udp_bytes"], 12000)
        self.assertEqual(ev["udp_packet_rate_per_s"], 10.0)
        self.assertEqual(ev["distinct_destination_ips"], 20)
        self.assertEqual(ev["distinct_destination_endpoints"], 20)
        self.assertTrue(all(item["protocol"] == "udp"
                            for item in ev["destination_endpoints_sample"]))

    def test_low_rate_dns_and_tcp_fanout_do_not_alert(self):
        sink, processor = self.make_processor()
        # Ordinary low-volume DNS-style queries do not pass either gate.
        for i in range(20):
            self.feed_udp(processor, i / 10, "192.0.2.41", "203.0.113.53",
                          53, 90)
        # Broad TCP fan-out is outside this UDP signal.
        for i in range(30):
            processor.feed((3 + i / 10, "192.0.2.42", f"198.51.100.{i + 1}",
                            "tcp", 40000 + i, 443, 100, False,
                            b"", None, 0, 0))
        processor.finish()
        self.assertFalse(any(a["threat_class"].startswith("udp_")
                             for a in sink.alerts))

    def test_many_sources_to_one_udp_endpoint_is_reported_as_burst(self):
        sink, processor = self.make_processor()
        for i in range(50):
            src = f"192.0.2.{i + 1}"
            for n in range(20):
                self.feed_udp(processor, i / 100 + n / 1000, src,
                              "203.0.113.10", 1900, 100)
        processor.finish()

        target_alerts = [a for a in sink.alerts
                         if a["threat_class"] == "udp_target_burst"]
        self.assertEqual(len(target_alerts), 1)
        alert = target_alerts[0]
        self.assertEqual(alert["dst"], "203.0.113.10")
        self.assertTrue(alert["flow_id"].endswith(":1900/udp"))
        self.assertEqual(alert["evidence"]["udp_packets"], 1000)
        self.assertEqual(alert["evidence"]["distinct_source_ips"], 50)
        self.assertIn("does not establish reflection or amplification",
                      alert["evidence"]["why"])
        presented = describe_alert(alert)
        self.assertEqual(presented["kind"], "rule")
        self.assertEqual(CLASS_TO_PS[alert["threat_class"]], "a")


if __name__ == "__main__":
    unittest.main()
