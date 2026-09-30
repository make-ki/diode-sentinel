"""Sanctioned uploads stay visible; unrelated or excessive transfers escalate."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tempfile
import unittest
from core.destination_policy import DestinationPolicy
from core.detectors import AlertSink, ExfilDetector, FusionEngine
from core.pipeline import WindowAggregator


ENTRY = dict(name="test backup", source="10.0.0.6/32",
             destination="13.107.42.16/32", protocol="tcp", port=443,
             volume_class="backup", max_bytes=1_000_000)


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.sink = AlertSink(os.path.join(self.tmp.name, 'alerts.jsonl'))
        self.detector = ExfilDetector(self.sink, policy=DestinationPolicy([ENTRY]))
        self.agg = WindowAggregator()
        self.agg.register(self.detector.on_window)

    def send(self, t=0, src='10.0.0.6', dst='13.107.42.16',
             port=443, proto='tcp', size=600_000):
        self.agg.feed(t, src, dst, port, size, False, proto)
        self.agg.flush_current()

    def test_sanctioned_upload_is_visible_medium_with_actual_endpoint(self):
        self.send()
        alert, = self.sink.alerts
        self.assertEqual(alert['severity'], 'medium')
        self.assertEqual(alert['flow_id'], '10.0.0.6:*->13.107.42.16:443/tcp')
        self.assertTrue(alert['evidence']['authorised_destination'])
        self.assertEqual(alert['evidence']['volume_classes'], ['backup'])

    def test_other_hosts_ports_protocols_and_destinations_are_not_authorised(self):
        for override in [dict(src='10.0.0.7'), dict(dst='13.107.42.17'),
                         dict(port=8443), dict(proto='udp')]:
            with self.subTest(override=override):
                detector = ExfilDetector(self.sink, policy=DestinationPolicy([ENTRY]))
                agg = WindowAggregator()
                agg.register(detector.on_window)
                values = dict(t=0, src='10.0.0.6', dst='13.107.42.16',
                              dport=443, size=600_000, is_syn=False, proto='tcp')
                values.update({('dport' if k == 'port' else k): v for k, v in override.items()})
                agg.feed(**values)
                agg.flush_current()
                self.assertEqual(self.sink.alerts[-1]['severity'], 'critical')

    def test_exceeding_cap_escalates_after_demotion(self):
        self.send()
        self.send(t=10, size=500_000)
        self.assertEqual([a['severity'] for a in self.sink.alerts], ['medium', 'critical'])

    def test_new_port_escalates_after_demotion(self):
        self.send()
        self.send(t=10, port=8443, size=1)
        self.assertEqual([a['severity'] for a in self.sink.alerts], ['medium', 'critical'])
        self.assertEqual(self.sink.alerts[-1]['flow_id'], '10.0.0.6:*->13.107.42.16:*/*')

    def test_sanctioned_signal_cannot_create_critical_fusion(self):
        fusion = FusionEngine(self.sink)
        self.sink.subscribe(fusion.on_alert)
        self.sink.emit(0, '10.0.0.6', '13.107.42.16', 443, 'tcp',
                       'tls_novel_fingerprint', .6, {})
        self.send()
        self.assertEqual(len(self.sink.alerts), 2)

    def test_unknown_transport_fails_closed(self):
        self.send(proto=None)
        self.assertEqual(self.sink.alerts[-1]['severity'], 'critical')

    def test_invalid_registry_rejected(self):
        for override in [dict(port=True), dict(max_bytes=-1), dict(protocol='any'),
                         dict(source='invalid'), dict(name='')]:
            with self.subTest(override=override), self.assertRaises(ValueError):
                DestinationPolicy([dict(ENTRY, **override)])


if __name__ == '__main__':
    unittest.main()
