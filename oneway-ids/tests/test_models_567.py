"""Tests for category 5-7 model features and optional serving."""
# Bootstrap: tests import core/, training/ and the root entry points, so put the
# repo root and its subpackages on sys.path regardless of the invocation CWD.
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in (_ROOT, _os.path.join(_ROOT, "training")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import os
import tempfile

from collections import defaultdict

from core.models_567 import (Models567, encrypted_metadata_features,
                        exfil_features, flow_sequence_features, scan_features)
from core.packet_sequence_cnn import PacketSequenceCnn, sequence_token
from core.pipeline import FlowAssembler


failures = []


def check(name, condition, detail=""):
    print(f"[{'PASS' if condition else 'FAIL'}] {name} {detail}")
    if not condition:
        failures.append(name)


assembler = FlowAssembler()
assembler.feed(1.0, "10.0.0.5", 40000, "198.51.100.23", 443,
               "tcp", 60, True)
assembler.feed(1.1, "10.0.0.5", 40000, "198.51.100.23", 443,
               "tcp", 120, False)
flow = assembler.finish()[0]
flow["tls_meta"] = {"version": "13", "cipher_count": 6,
                    "ext_count": 3, "sni": "c2.example", "sig_algs": [],
                    "transport": "tls"}

check("flow_retains_packet_sequence",
      flow["packet_sizes"] == [60, 120]
      and flow["packet_times"] == [1.0, 1.1]
      and flow["packet_directions"] == [1, 1])
check("sequence_feature_shape", len(flow_sequence_features(flow)) == 100)
check("metadata_feature_shape", len(encrypted_metadata_features(flow)) == 10)
check("sequence_token_uses_timing",
      sequence_token(flow) != sequence_token(dict(flow, packet_times=[1.0, 2.0])))

window = dict(idx=3, t0=30.0, t1=40.0,
              pairs={"10.0.0.13": {("203.0.113.20", 22),
                                   ("203.0.113.20", 23)}},
              src_bytes=defaultdict(float, {"10.0.0.13": 500}),
              novel_dsts={"203.0.113.20"})
check("scan_feature_shape", len(scan_features(window, "10.0.0.13")[0]) == 5)
check("exfil_feature_shape",
      len(exfil_features(window, "10.0.0.13", "203.0.113.20", 5000)[0]) == 5)


class _AlwaysPositive:
    def predict_proba(self, features):
        return [[0.0, 1.0]]


class _UncalibratedOutlier:
    def decision_function(self, features):
        return [-0.75]


scan_window = dict(idx=4, pairs={"10.0.0.13": {
    (f"198.51.100.{i}", 1000 + i) for i in range(20)}},
    src_bytes={"10.0.0.13": 1000})
scan_bundle = Models567({})
scan_bundle.models = {"scan_rf": _AlwaysPositive(),
                      "scan_iforest": _UncalibratedOutlier()}
scan_without_rule = scan_bundle.score_scan(scan_window, "10.0.0.13")
check("iforest_never_emits_standalone_scan_alert",
      len(scan_without_rule) == 1
      and scan_without_rule[0][2]["model"] == "scan_rf"
      and "iforest_corroboration" not in scan_without_rule[0][2])
scan_bundle.alerted.clear()
scan_with_rule = scan_bundle.score_scan(
    scan_window, "10.0.0.13", rule_corroborated=True)
scan_if_evidence = scan_with_rule[0][2].get("iforest_corroboration", {})
check("iforest_scan_score_is_uncalibrated_corroboration",
      scan_if_evidence.get("anomaly_score") == -0.75
      and scan_if_evidence.get("score_kind") ==
      "uncalibrated_decision_function"
      and scan_if_evidence.get("more_anomalous_when") == "lower")

exfil_window = dict(idx=5, src_bytes={"10.0.0.13": 500_000},
                    novel_dsts={"203.0.113.20"})
exfil_bundle = Models567({})
exfil_bundle.models = {"exfil_xgb": _AlwaysPositive(),
                       "exfil_iforest": _UncalibratedOutlier()}
exfil_without_rule = exfil_bundle.score_exfil(
    exfil_window, "10.0.0.13", "203.0.113.20", 500_000)
check("iforest_never_emits_standalone_exfil_alert",
      len(exfil_without_rule) == 1
      and exfil_without_rule[0][2]["model"] == "exfil_xgb"
      and "iforest_corroboration" not in exfil_without_rule[0][2])
exfil_bundle.alerted.clear()
exfil_bundle.exfil_totals.clear()
exfil_bundle.exfil_novel.clear()
exfil_with_rule = exfil_bundle.score_exfil(
    exfil_window, "10.0.0.13", "203.0.113.20", 500_000,
    rule_corroborated=True)
check("iforest_exfil_score_attaches_to_supervised_alert",
      exfil_with_rule[0][2].get("iforest_corroboration", {}).get(
          "model") == "exfil_iforest")

# Exercise the real window -> rule emission -> model callback path.
from core.pipeline import StreamProcessor
from core.detectors import AlertSink
with tempfile.TemporaryDirectory() as tmp:
    sink = AlertSink(os.path.join(tmp, "alerts.jsonl"))
    integrated = Models567({})
    integrated.models = {"scan_rf": _AlwaysPositive(),
                         "scan_iforest": _UncalibratedOutlier()}
    proc = StreamProcessor(sink, models567=integrated)
    for port in range(20):
        proc.feed((0.01 * port, "10.0.0.13", "203.0.113.20", "tcp",
                   40000 + port, 1000 + port, 60, True, b"", None, 0, None))
    proc.finish()
    model_alerts = [a for a in sink.alerts if a["threat_class"] == "recon_model_scan"]
    check("pipeline_attaches_iforest_only_after_actual_scan_rule",
          len(model_alerts) == 1 and
          "iforest_corroboration" in model_alerts[0]["evidence"])

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "sequence.npz")
    PacketSequenceCnn().save(path)
    bundle = Models567({"sequence_cnn": path})
    score = bundle.models["sequence_cnn"].score(flow)
    check("sequence_model_manifest_load", 0.0 <= score <= 1.0)

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    raise SystemExit(1)
print("all category 5-7 model tests passed")
