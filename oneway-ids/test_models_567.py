"""Tests for category 5-7 model features and optional serving."""
import os
import tempfile

from collections import defaultdict

from models_567 import (Models567, encrypted_metadata_features,
                        exfil_features, flow_sequence_features, scan_features)
from packet_sequence_cnn import PacketSequenceCnn, sequence_token
from pipeline import FlowAssembler


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
