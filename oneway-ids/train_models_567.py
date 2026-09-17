#!/usr/bin/env python3
"""Train the optional category 5-7 model bundle.

Usage:
    python train_models_567.py --pcap traffic.pcap --out models567
    python run.py --models-567 models567/manifest.json

The split is temporal: flows/windows before t=500 train the models and later
traffic evaluates them. The rule detectors remain enabled during serving.
"""
import argparse
import json
import os

import numpy as np

from config import (ATTACK_HOST_ROLES, C2_IPS, EXFIL_DST_IP, PCAP_PATH,
                    SCAN_TARGET_IP, WINDOW)
from detectors import ExfilDetector
from models_567 import (encrypted_metadata_features, exfil_features,
                        scan_features)
from packet_sequence_cnn import PacketSequenceCnn, sequence_token
from dga_cnn import Adam, encode_batch
from pcap_reader import iter_dpkt
from pipeline import FlowAssembler, WindowAggregator


def _deps():
    try:
        import joblib
        import xgboost as xgb
        from sklearn.ensemble import IsolationForest, RandomForestClassifier
        return joblib, xgb, IsolationForest, RandomForestClassifier
    except ImportError as exc:
        raise SystemExit(
            "missing category 5-7 ML dependencies; install "
            "requirements-ml.txt") from exc


def collect(path):
    assembler = FlowAssembler()
    aggregator = WindowAggregator()
    flows, windows = [], []
    aggregator.register(windows.append)
    last_tick = -1.0
    for packet in iter_dpkt(path):
        t, src, dst, proto, sport, dport, size, is_syn, payload, qname, seq = packet
        assembler.feed(t, src, sport, dst, dport, proto, size, is_syn)
        if t - last_tick >= 0.5:
            flows.extend(assembler.emit_ready(t))
            aggregator.tick(t)
            last_tick = t
        aggregator.feed(t, src, dst, dport, size, is_syn)
    flows.extend(assembler.finish())
    aggregator.flush_current()
    return flows, windows


def fit_sequence(flows, out_path, split_t):
    model = PacketSequenceCnn()
    labels = [sequence_token(flow) for flow in flows]
    y = np.array([int(flow["key"][2] in C2_IPS) for flow in flows])
    train = np.array([flow["t0"] < split_t for flow in flows])
    if not train.any() or len(set(y[train])) < 2:
        raise RuntimeError("category-5 sequence training needs both labels")
    x, lens = encode_batch(labels)
    order = np.flatnonzero(train)
    optimizer = Adam(lr=3e-3, l2=1e-3)
    for _ in range(12):
        rng = np.random.default_rng(7)
        rng.shuffle(order)
        for start in range(0, len(order), 64):
            batch = order[start:start + 64]
            _, cache = model.model.forward(x[batch], lens[batch], training=True)
            optimizer.step(model.model.params(),
                           model.model.backward(cache, y[batch]))
    model.save(out_path)


def fit_tree_models(flows, windows, out_dir, split_t):
    joblib, xgb, IsolationForest, RandomForestClassifier = _deps()
    os.makedirs(out_dir, exist_ok=True)

    flow_train = [flow for flow in flows if flow["t0"] < split_t]
    encrypted_x = np.asarray([encrypted_metadata_features(flow)
                              for flow in flow_train])
    encrypted_y = np.asarray([int(flow["key"][2] in C2_IPS)
                              for flow in flow_train])
    if len(set(encrypted_y)) < 2:
        raise RuntimeError("category-5 metadata training needs both labels")
    encrypted = xgb.XGBClassifier(n_estimators=120, max_depth=4,
                                  learning_rate=0.08, eval_metric="logloss",
                                  random_state=42)
    encrypted.fit(encrypted_x, encrypted_y)
    encrypted_path = os.path.join(out_dir, "encrypted_xgb.json")
    encrypted.save_model(encrypted_path)

    scan_rows, scan_y = [], []
    exfil_rows, exfil_y = [], []
    for window in windows:
        if window["t0"] >= split_t:
            continue
        for src in window["pairs"]:
            scan_rows.append(scan_features(window, src)[0])
            scan_y.append(int(src in ATTACK_HOST_ROLES and
                              SCAN_TARGET_IP in {d for d, _ in
                                                 window["pairs"][src]}))
        for (src, dst), total in window["pair_bytes"].items():
            exfil_rows.append(exfil_features(window, src, dst, total)[0])
            exfil_y.append(int(dst == EXFIL_DST_IP))

    scan_x, scan_y = np.asarray(scan_rows), np.asarray(scan_y)
    scan_rf = RandomForestClassifier(n_estimators=120, class_weight="balanced",
                                     random_state=42)
    scan_rf.fit(scan_x, scan_y)
    scan_rf_path = os.path.join(out_dir, "scan_rf.joblib")
    joblib.dump(scan_rf, scan_rf_path)
    scan_if = IsolationForest(n_estimators=120, contamination="auto",
                              random_state=42)
    scan_if.fit(scan_x[scan_y == 0])
    scan_if_path = os.path.join(out_dir, "scan_iforest.joblib")
    joblib.dump(scan_if, scan_if_path)

    exfil_x, exfil_y = np.asarray(exfil_rows), np.asarray(exfil_y)
    exfil = xgb.XGBClassifier(n_estimators=120, max_depth=4,
                              learning_rate=0.08, eval_metric="logloss",
                              random_state=42)
    exfil.fit(exfil_x, exfil_y)
    exfil_path = os.path.join(out_dir, "exfil_xgb.json")
    exfil.save_model(exfil_path)
    exfil_if = IsolationForest(n_estimators=120, contamination="auto",
                               random_state=42)
    exfil_if.fit(exfil_x[exfil_y == 0])
    exfil_if_path = os.path.join(out_dir, "exfil_iforest.joblib")
    joblib.dump(exfil_if, exfil_if_path)

    return {
        "encrypted_xgb": encrypted_path,
        "scan_rf": scan_rf_path,
        "scan_iforest": scan_if_path,
        "exfil_xgb": exfil_path,
        "exfil_iforest": exfil_if_path,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pcap", default=PCAP_PATH)
    parser.add_argument("--out", default="models567")
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)
    flows, windows = collect(args.pcap)
    # Keep a slice of the generated exfiltration (480-540s) in training while
    # retaining later traffic for temporal evaluation.
    split_t = 500.0
    sequence_path = os.path.join(args.out, "sequence_cnn.npz")
    fit_sequence(flows, sequence_path, split_t)
    paths = fit_tree_models(flows, windows, args.out, split_t)
    paths["sequence_cnn"] = sequence_path
    manifest = os.path.join(args.out, "manifest.json")
    with open(manifest, "w") as fh:
        json.dump({"version": 1, "models": paths}, fh, indent=2)
    print(f"trained category 5-7 models -> {manifest}")


if __name__ == "__main__":
    main()
