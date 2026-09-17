#!/usr/bin/env python3
"""
Train the Tier-2 ML model (LightGBM) on flows assembled from the synthetic
pcap, with generator-derived ground truth labels and a TEMPORAL split
(train = flows starting before t=420s, test = after) -- the honest split.

Run: .venv/bin/python train_ml.py
"""
import lgb_env  # noqa: F401  (NixOS: preloads libstdc++ before lightgbm)
import lightgbm as lgb
try:
    from sklearn.metrics import classification_report, confusion_matrix
except ImportError as e:
    raise SystemExit(
        f"missing ML deps ({e}). pip install lightgbm scikit-learn numpy")

from config import PCAP_PATH, ML_MODEL_PATH
from pcap_reader import iter_dpkt
from pipeline import FlowAssembler
from ml_tier import flow_features, label_flow, FEATURE_NAMES


def collect_flows(path):
    """Assemble closed flows (same lazy-timeout loop as run.py)."""
    assembler = FlowAssembler()
    flows = []
    last_flush_t = -1.0
    for (t, src, dst, proto, sport, dport, size, is_syn, payload, qname,
         seq) in iter_dpkt(path):
        assembler.feed(t, src, sport, dst, dport, proto, size, is_syn)
        if t - last_flush_t >= 0.5:
            flows.extend(assembler.emit_ready(t))
            last_flush_t = t
    flows.extend(assembler.finish())
    return flows


def main(path=PCAP_PATH):
    flows = collect_flows(path)
    print(f"flows assembled: {len(flows):,}")

    X, y, t0s = [], [], []
    for f in flows:
        src, sport, dst, dport, proto = f["key"]
        X.append(flow_features(f))
        y.append(label_flow(src, dst, dport, proto, f["t0"]))
        t0s.append(f["t0"])

    split_t = 420.0                                   # temporal split
    tr = [i for i in range(len(X)) if t0s[i] < split_t]
    te = [i for i in range(len(X)) if t0s[i] >= split_t]
    Xtr = [X[i] for i in tr]; ytr = [y[i] for i in tr]
    Xte = [X[i] for i in te]; yte = [y[i] for i in te]

    n_mal_tr, n_mal_te = sum(ytr), sum(yte)
    print(f"temporal split at t={split_t}s: train={len(Xtr):,} flows "
          f"({n_mal_tr} malicious), test={len(Xte):,} flows "
          f"({n_mal_te} malicious)")

    clf = lgb.LGBMClassifier(n_estimators=200, num_leaves=31,
                             class_weight="balanced", verbose=-1,
                             random_state=42)
    clf.fit(Xtr, ytr)
    prob = clf.predict_proba(Xte)[:, 1]
    pred = (prob >= 0.5).astype(int)

    print("\n=== TEST SET (t >= 420s, unseen time window) ===")
    print(classification_report(yte, pred, target_names=["benign", "malicious"],
                                digits=4, zero_division=0))
    print("confusion matrix [ benign  malicious ] (rows=true):")
    print(confusion_matrix(yte, pred))

    # rule-detector comparison on the same test window
    mal_flow_srcs = {f["key"][0] for i, f in enumerate(flows)
                     if t0s[i] >= split_t and y[i] == 1}
    print(f"malicious sources active in test window: {sorted(mal_flow_srcs)}")

    print("\nfeature importance (gain):")
    booster = clf.booster_
    for name, gain in sorted(zip(FEATURE_NAMES, booster.feature_importance("gain")),
                             key=lambda kv: -kv[1]):
        print(f"  {name:14s} {gain:10.1f}")

    booster.save_model(ML_MODEL_PATH)
    print(f"\nmodel saved -> {ML_MODEL_PATH}")


if __name__ == "__main__":
    main()
