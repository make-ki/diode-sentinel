"""Behavior gates for model admission, QUIC recovery, and opt-in CLI paths."""
import copy
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.detectors import AlertSink
from core.models_567 import Models567
from core.pipeline import StreamProcessor
from run import _cli, run_pipeline


class MetadataModel:
    def __init__(self):
        self.calls = []

    def predict_proba(self, values):
        self.calls.append(values)
        return [[0.01, 0.99]]


class SequenceModel:
    def score(self, flow):
        return 0.99


def flow():
    return dict(key=("10.0.0.1", 40000, "198.51.100.1", 443, "tcp"),
                t0=0.0, t1=1.0, npkt=3, nbytes=1200,
                packet_sizes=[60, 570, 570], packet_times=[0.0, 0.5, 1.0],
                packet_directions=[1, 1, 1])


def packet(t, src, dst, size=600, *, sport=40000, dport=443,
           proto="tcp", payload=b""):
    return (t, src, dst, proto, sport, dport, size, False,
            payload, None, 0, None)


class HourFixTests(unittest.TestCase):
    def test_missing_handshake_skips_metadata_model_but_keeps_sequence_model(self):
        metadata = MetadataModel()
        models = Models567({})
        models.models = {"encrypted_xgb": metadata, "sequence_cnn": SequenceModel()}
        alerts = models.score_flow(flow())
        self.assertEqual(metadata.calls, [])
        self.assertEqual(models.metadata_skipped, 1)
        self.assertEqual([e[2]["model"] for e in alerts], ["1d-cnn"])

    def test_recorded_empty_sni_and_signature_list_are_valid_inputs(self):
        metadata = MetadataModel()
        models = Models567({})
        models.models = {"encrypted_xgb": metadata}
        observed = flow()
        observed["tls_meta"] = dict(cipher_count=2, ext_count=3, version="13",
                                    sni=None, sig_algs=[], transport="tls")
        alerts = models.score_flow(observed)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(len(metadata.calls), 1)
        self.assertEqual(metadata.calls[0][0][:6], [2.0, 3.0, 13.0, 0, 0.0, 0.0])
        self.assertEqual(models.metadata_skipped, 0)

    def test_partial_handshake_does_not_invent_missing_fields(self):
        metadata = MetadataModel()
        models = Models567({})
        models.models = {"encrypted_xgb": metadata}
        observed = flow()
        observed["tls_meta"] = {"version": "13", "cipher_count": 2}
        self.assertEqual(models.score_flow(observed), [])
        self.assertEqual(metadata.calls, [])

    def test_failed_initial_does_not_hide_later_valid_packet_and_keys_expire(self):
        fixture = ROOT / "tests/fixtures/quic/rfc9001_a2_client_initial.hex"
        valid = bytes.fromhex("".join(
            line for line in fixture.read_text().splitlines()
            if line and not line.startswith("#")))
        malformed = bytearray(valid)
        malformed[-1] ^= 1
        with tempfile.TemporaryDirectory() as tmp:
            proc = StreamProcessor(AlertSink(os.path.join(tmp, "alerts.jsonl")))
            proc.feed(packet(0.0, "10.0.0.1", "198.51.100.1", proto="udp",
                             payload=bytes(malformed)))
            self.assertEqual(proc.ntls, 0)
            self.assertEqual(len(proc.quic_seen), 0)
            proc.feed(packet(0.5, "10.0.0.1", "198.51.100.1", proto="udp", payload=valid))
            self.assertEqual(proc.ntls, 1)
            self.assertEqual(len(proc.quic_seen), 1)
            proc.tick(5.0)
            self.assertEqual(len(proc.quic_seen), 0)
            proc.feed(packet(6.0, "10.0.0.1", "198.51.100.1", proto="udp", payload=valid))
            self.assertEqual(proc.ntls, 2)
            proc.finish()
            self.assertEqual(len(proc.quic_seen), 0)

    def test_source_context_reaches_actual_streaming_detector(self):
        packets = [packet(0.0, "10.0.0.1", "198.51.100.1"),
                   packet(0.1, "10.0.0.2", "198.51.100.2")]
        packets += [packet(10.1 + i / 1000, "10.0.0.2", "198.51.100.1", size=6000)
                    for i in range(100)]
        with tempfile.TemporaryDirectory() as tmp:
            default = AlertSink(os.path.join(tmp, "default.jsonl"))
            contextual = AlertSink(os.path.join(tmp, "contextual.jsonl"))
            run_pipeline(iter(copy.deepcopy(packets)), default)
            run_pipeline(iter(copy.deepcopy(packets)), contextual, source_context=True)
            default_transfers = [a for a in default.alerts if a["threat_class"] == "data_exfiltration"]
            contextual_transfers = [a for a in contextual.alerts if a["threat_class"] == "data_exfiltration"]
            self.assertEqual(default_transfers, [])
            self.assertEqual(len(contextual_transfers), 1)
            self.assertEqual(contextual_transfers[0]["src"], "10.0.0.2")
            self.assertFalse(contextual_transfers[0]["evidence"]["fleet_destination_novel"])

    def test_rolling_scan_reaches_actual_streaming_detector(self):
        packets = [packet(0.1 + i / 100, "10.0.0.1", "198.51.100.1",
                          sport=40000 + i, dport=1000 + i) for i in range(10)]
        packets += [packet(10.1 + i / 100, "10.0.0.1", "198.51.100.1",
                           sport=40010 + i, dport=1010 + i) for i in range(10)]
        with tempfile.TemporaryDirectory() as tmp:
            sink = AlertSink(os.path.join(tmp, "alerts.jsonl"))
            run_pipeline(iter(packets), sink, rolling_scan=True)
            rolling = [a for a in sink.alerts if a["threat_class"].startswith("recon_rolling_")]
            self.assertEqual(len(rolling), 1)
            self.assertEqual(rolling[0]["evidence"]["rolling_distinct_dst_port_pairs"], 20)

    def test_new_cli_modes_are_explicit_opt_ins(self):
        parser = _cli()
        defaults = parser.parse_args([])
        self.assertFalse(defaults.source_context)
        self.assertFalse(defaults.rolling_scan)
        selected = parser.parse_args(["--source-context", "--rolling-scan"])
        self.assertTrue(selected.source_context)
        self.assertTrue(selected.rolling_scan)


if __name__ == "__main__":
    unittest.main()
