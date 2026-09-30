#!/usr/bin/env python3
"""Train the Tier-2 flow model with an explicit temporal evaluation split.

Optional benign replay rows are accepted only for operator-selected source
IPs, and known generator-labelled attacks are never relabelled as benign.
"""
import argparse
import ipaddress
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, "training")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from core import lgb_env  # noqa: F401
import lightgbm as lgb

from core.config import PCAP_PATH
from core.pcap_reader import iter_dpkt
from core.pipeline import FlowAssembler
from core.ml_tier import flow_features, label_flow

DEFAULT_OUTPUT = os.path.join(_ROOT, "training", "model_ml_experiment.txt")
SPLIT_T = 420.0
DEPLOYED_THRESHOLD = 0.95


def collect_flows(path):
    """Assemble flows from the one-way packet reader's 12-field tuple stream."""
    assembler = FlowAssembler()
    flows = []
    last_flush_t = -1.0
    for (t, src, dst, proto, sport, dport, size, is_syn, payload, qname,
         seq, qtype) in iter_dpkt(path):
        assembler.feed(t, src, sport, dst, dport, proto, size, is_syn)
        if t - last_flush_t >= 0.5:
            flows.extend(assembler.emit_ready(t))
            last_flush_t = t
    flows.extend(assembler.finish())
    return flows


def build_rows(flows):
    """Return (features, generator labels, times), preserving known attacks."""
    rows = []
    for f in flows:
        src, sport, dst, dport, proto = f["key"]
        # Preserve synthetic ground truth: selected replay sources receive the
        # default benign label, but known attacks retain their malicious label.
        label = label_flow(src, dst, dport, proto, f["t0"])
        rows.append((flow_features(f), label, f["t0"]))
    return rows


def select_replay_rows(flows, rows, benign_sources):
    """Keep only flows whose source was explicitly selected for benign replay."""
    selected = {str(ipaddress.ip_address(ip)) for ip in benign_sources}
    return [row for row, flow in zip(rows, flows) if flow["key"][0] in selected]


def evaluate_predictions(labels, probabilities, threshold=DEPLOYED_THRESHOLD):
    """Build JSON-safe holdout counts at the serving threshold."""
    benign = [p for p, label in zip(probabilities, labels) if label == 0]
    malicious = [p for p, label in zip(probabilities, labels) if label == 1]
    false_positives = int(sum(bool(p >= threshold) for p in benign))
    detected = int(sum(bool(p >= threshold) for p in malicious))
    return {
        "heldout_benign_flows": int(len(benign)),
        "heldout_benign_false_positives": false_positives,
        "heldout_benign_false_positive_rate": (
            false_positives / len(benign) if benign else None),
        "heldout_malicious_detected": detected,
        "heldout_malicious_flows": int(len(malicious)),
    }


def train(training_pcap=PCAP_PATH, benign_replay_pcap=None,
          benign_sources=(), output=DEFAULT_OUTPUT, split_t=SPLIT_T):
    """Fit on pre-split flows and report held-out benign FP rate at 0.95."""
    rows = build_rows(collect_flows(training_pcap))
    selected = {str(ipaddress.ip_address(ip)) for ip in benign_sources}
    if benign_replay_pcap:
        if not selected:
            raise ValueError("--benign-replay-pcap requires at least one --benign-source-ip")
        replay = collect_flows(benign_replay_pcap)
        replay_rows = build_rows(replay)
        selected_rows = select_replay_rows(replay, replay_rows, selected)
        if not selected_rows:
            raise ValueError("selected benign source IPs produced no replay flows")
        rows.extend(selected_rows)

    train_rows = [r for r in rows if r[2] < split_t]
    test_rows = [r for r in rows if r[2] >= split_t]
    if not train_rows or not test_rows:
        raise ValueError(f"temporal split at {split_t}s needs rows on both sides")
    Xtr, ytr = [r[0] for r in train_rows], [r[1] for r in train_rows]
    Xte, yte = [r[0] for r in test_rows], [r[1] for r in test_rows]
    if len(set(ytr)) < 2:
        raise ValueError("training partition needs both benign and malicious flows")

    clf = lgb.LGBMClassifier(n_estimators=200, num_leaves=31,
                             class_weight="balanced", verbose=-1,
                             random_state=42, n_jobs=1)
    clf.fit(Xtr, ytr)
    probs = clf.predict_proba(Xte)[:, 1]
    report = {
        "training_pcap": os.path.abspath(training_pcap),
        "benign_replay_pcap": os.path.abspath(benign_replay_pcap) if benign_replay_pcap else None,
        "benign_source_ips": sorted(selected),
        "temporal_split_seconds": split_t,
        "threshold": DEPLOYED_THRESHOLD,
        "train_flows": len(train_rows), "test_flows": len(test_rows),
        "train_malicious": sum(ytr), "test_malicious": sum(yte),
        **evaluate_predictions(yte, probs),
    }
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    clf.booster_.save_model(output)
    report_path = output + ".report.json"
    with open(report_path, "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"model saved -> {output}\nreport saved -> {report_path}")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pcap", default=PCAP_PATH, help="labelled training pcap")
    parser.add_argument("--benign-replay-pcap", help="optional replay pcap containing selected benign sources")
    parser.add_argument("--benign-source-ip", action="append", default=[],
                        help="source IP explicitly approved as benign; repeat for multiple IPs")
    parser.add_argument("--output", default=DEFAULT_OUTPUT,
                        help="experiment model path (default does not overwrite shipped model)")
    parser.add_argument("--split", type=float, default=SPLIT_T,
                        help="relative event-time split in seconds")
    args = parser.parse_args(argv)
    if args.benign_source_ip and not args.benign_replay_pcap:
        parser.error("--benign-source-ip requires --benign-replay-pcap")
    train(args.pcap, args.benign_replay_pcap, args.benign_source_ip,
          args.output, args.split)


if __name__ == "__main__":
    main()
