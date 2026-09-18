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
from models_567 import (_anomaly_probability, _probability,
                        encrypted_metadata_features, exfil_features,
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
            "missing category 5-7 ML dependencies; install the 'ml567' extra: "
            "uv sync --extra ml567  (or: pip install '.[ml567]')") from exc


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
    return model


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
    }, {
        "encrypted_xgb": encrypted,
        "scan_rf": scan_rf,
        "scan_iforest": scan_if,
        "exfil_xgb": exfil,
        "exfil_iforest": exfil_if,
    }


# Operating-point sweep and the benign false-positive budget used to pick the
# shipped threshold. Same discipline as the DGA CNN quorum sweep in
# bench_dga.py: the threshold is a measured constant, and the sweep is
# published rather than asserted. The chosen point is written into the manifest
# and read at serve time, so what is measured is what ships.
SWEEP = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
BENIGN_FP_BUDGET = 0.005      # max tolerable benign FP rate (0.5%)


def _score_sweep(scores, labels):
    """Detection rate / benign-FP tradeoff per threshold, plus the chosen point.

    Returns (rows, chosen, note). Ships the most sensitive threshold whose
    benign FP rate stays within budget; if none qualifies, ships the least
    noisy point and says so rather than hiding the miss.
    """
    malicious = [s for s, y in zip(scores, labels) if y == 1]
    benign = [s for s, y in zip(scores, labels) if y == 0]
    rows = [{
        "threshold": thr,
        "detection_rate": sum(s >= thr for s in malicious) / max(len(malicious), 1),
        "benign_fp": sum(s >= thr for s in benign),
        "benign_fp_rate": sum(s >= thr for s in benign) / max(len(benign), 1),
    } for thr in SWEEP]
    if not malicious:
        return rows, 0.8, "no malicious examples in the temporal holdout; default kept"
    if not benign:
        return rows, 0.8, "no benign examples in the temporal holdout; default kept"
    in_budget = [r for r in rows if r["benign_fp_rate"] <= BENIGN_FP_BUDGET]
    if in_budget:
        best = max(in_budget, key=lambda r: (r["detection_rate"], -r["threshold"]))
        return rows, best["threshold"], \
            "most sensitive point with benign FP <= %.3f" % BENIGN_FP_BUDGET
    quietest = min(rows, key=lambda r: (r["benign_fp_rate"], -r["threshold"]))
    return rows, quietest["threshold"], \
        "no threshold met the FP budget on this capture; least-noisy point shipped"


def _summarise(name, scores, labels, rows, chosen, note):
    at = next(r for r in rows if r["threshold"] == chosen)
    malicious_n = sum(labels)
    tp = sum(s >= chosen for s, y in zip(scores, labels) if y == 1)
    fp = sum(s >= chosen for s, y in zip(scores, labels) if y == 0)
    return {
        "holdout_n": len(labels),
        "malicious_n": malicious_n,
        "benign_n": len(labels) - malicious_n,
        "at_threshold": {
            "threshold": chosen,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": malicious_n - tp,
            "recall": tp / max(malicious_n, 1),
            "precision": tp / max(tp + fp, 1),
            "benign_fp_rate": at["benign_fp_rate"],
        },
        "sweep": rows,
        "why_this_threshold": note,
    }


def evaluate(flows, windows, models, split_t):
    """Score the temporal holdout (t >= split_t) with the trained models.

    Measures the RAW model over the full held-out distribution -- every closed
    flow and every window, not just the rule-gated subsets the server scores --
    so the benign FP pressure here UPPER-BOUNDS what the deployed tier sees:
    serving additionally requires the scan/exfil candidate gates (SCAN_MIN_PAIRS,
    destination novelty + EXFIL_MIN_BYTES). Same separation as bench_dga.py's
    per-string scoring vs its quorum layer: model quality here, deployed
    behaviour in the regression suite.

    Returns (report, thresholds); thresholds is the shipped operating point per
    model, recorded in the manifest and read at serve time.
    """
    holdout_flows = [f for f in flows if f["t0"] >= split_t]
    holdout_windows = [w for w in windows if w["t0"] >= split_t]
    report, thresholds = {}, {}

    # ---- category 5: encrypted sessions (two independent scorers) ----
    for name in ("encrypted_xgb", "sequence_cnn"):
        if name not in models:
            continue
        model = models[name]
        scores, labels = [], []
        for flow in holdout_flows:
            scores.append(_probability(model, [encrypted_metadata_features(flow)])
                          if name == "encrypted_xgb" else model.score(flow))
            labels.append(int(flow["key"][2] in C2_IPS))
        rows, chosen, note = _score_sweep(scores, labels)
        report[name] = _summarise(name, scores, labels, rows, chosen, note)
        thresholds[name] = chosen

    # ---- categories 6 and 7: window-level scorers ----
    scan_cases = []           # (features, label) per (window, src)
    exfil_cases = []          # (features, label) per (window, src, dst)
    for window in holdout_windows:
        for src in window["pairs"]:
            scan_cases.append((scan_features(window, src)[0],
                               int(src in ATTACK_HOST_ROLES and
                                   SCAN_TARGET_IP in
                                   {d for d, _ in window["pairs"][src]})))
        for (src, dst), total in window["pair_bytes"].items():
            exfil_cases.append((exfil_features(window, src, dst, total)[0],
                                int(dst == EXFIL_DST_IP)))

    window_jobs = [("scan_rf", scan_cases), ("scan_iforest", scan_cases),
                   ("exfil_xgb", exfil_cases), ("exfil_iforest", exfil_cases)]
    for name, cases in window_jobs:
        if name not in models:
            continue
        is_anomaly = name.endswith("iforest")
        scores, labels = [], []
        for features, label in cases:
            scores.append(_anomaly_probability(models[name], [features])
                         if is_anomaly else _probability(models[name], [features]))
            labels.append(label)
        rows, chosen, note = _score_sweep(scores, labels)
        report[name] = _summarise(name, scores, labels, rows, chosen, note)
        thresholds[name] = chosen

    return report, thresholds


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
    sequence_model = fit_sequence(flows, sequence_path, split_t)
    paths, models = fit_tree_models(flows, windows, args.out, split_t)
    paths["sequence_cnn"] = sequence_path
    models["sequence_cnn"] = sequence_model

    report, thresholds = evaluate(flows, windows, models, split_t)
    eval_path = os.path.join(args.out, "eval.json")
    with open(eval_path, "w") as fh:
        json.dump({"split_t": split_t, "benign_fp_budget": BENIGN_FP_BUDGET,
                   "models": report}, fh, indent=2)

    manifest = os.path.join(args.out, "manifest.json")
    with open(manifest, "w") as fh:
        json.dump({"version": 1, "models": paths,
                   "thresholds": thresholds}, fh, indent=2)

    print(f"trained category 5-7 models -> {manifest}")
    print(f"holdout evaluation (t >= {split_t:g}s) -> {eval_path}\n")
    print(f"{'model':16s} {'thr':>4s} {'recall':>7s} {'prec':>7s} {'FP':>4s} "
          f"{'benignFP':>9s}  why")
    for name, row in report.items():
        a = row["at_threshold"]
        print(f"{name:16s} {a['threshold']:>4g} {a['recall']:>7.3f} "
              f"{a['precision']:>7.3f} {a['false_positives']:>4d} "
              f"{a['benign_fp_rate'] * 100:>8.2f}%  {row['why_this_threshold']}")


if __name__ == "__main__":
    main()
