"""Category-specific model adapters for encrypted sessions, scanning, and exfil.

The rule detectors remain the fast Tier-1 path. These models are optional Tier-2
confirmers trained and served from explicit artifacts:
  - XGBoost for encrypted-session metadata and exfiltration
  - Random Forest + Isolation Forest for reconnaissance
  - XGBoost + Isolation Forest for exfiltration
  - PacketSequenceCNN for packet-size/timing sequences

Imports are lazy so rules-only replay remains usable without ML dependencies.
"""
import json
import math
import os

from core.config import EXFIL_MIN_BYTES, SCAN_MIN_PAIRS


class Model567DependencyError(RuntimeError):
    pass


def _require_sklearn():
    try:
        from joblib import load
        from sklearn.ensemble import IsolationForest, RandomForestClassifier
        return load, IsolationForest, RandomForestClassifier
    except ImportError as exc:
        raise Model567DependencyError(
            "category 5-7 tree models require scikit-learn and joblib; "
            "install requirements-ml.txt") from exc


def _require_xgboost():
    try:
        import xgboost as xgb
        return xgb
    except ImportError as exc:
        raise Model567DependencyError(
            "category 5-7 XGBoost models require xgboost; "
            "install requirements-ml.txt") from exc


def _safe_cv(values):
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean <= 0:
        return 0.0
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance) / mean


def flow_sequence_features(flow, max_packets=32):
    """Fixed-size packet-shape vector for category 5.

    The feed is one-way, so direction is explicitly represented as outbound
    ones rather than pretending response-side direction exists. The vector
    contains packet sizes, inter-arrival times, and aggregate burst features.
    """
    sizes = list(flow.get("packet_sizes", ()))[:max_packets]
    times = list(flow.get("packet_times", ()))[:max_packets]
    sizes += [0.0] * (max_packets - len(sizes))
    iats = [max(0.0, times[i] - times[i - 1])
            for i in range(1, min(len(times), max_packets))]
    iats += [0.0] * (max_packets - 1 - len(iats))
    directions = [1.0 if value else 0.0
                  for value in flow.get("packet_directions", ())[:max_packets]]
    directions += [0.0] * (max_packets - len(directions))
    real_sizes = [value for value in sizes if value > 0]
    real_iats = [value for value in iats if value > 0]
    return (sizes + iats + directions + [
        float(flow.get("npkt", 0)),
        float(flow.get("nbytes", 0)),
        float(flow.get("t1", 0) - flow.get("t0", 0)),
        _safe_cv(real_sizes),
        _safe_cv(real_iats),
    ])


def encrypted_metadata_features(flow):
    """Numeric TLS/QUIC metadata vector for the category-5 XGBoost model."""
    meta = flow.get("tls_meta", {})
    version = {"10": 10, "11": 11, "12": 12, "13": 13}.get(
        str(meta.get("version", "")), 0)
    transport = 1 if meta.get("transport", "tls") == "quic" else 0
    return [
        float(meta.get("cipher_count", 0)),
        float(meta.get("ext_count", 0)),
        float(version),
        transport,
        1.0 if meta.get("sni") else 0.0,
        float(len(meta.get("sig_algs", ()))),
        float(flow.get("npkt", 0)),
        float(flow.get("nbytes", 0)),
        float(flow.get("t1", 0) - flow.get("t0", 0)),
        _safe_cv(flow.get("packet_sizes", ())),
    ]


def scan_features(window, src):
    pairs = window.get("pairs", {}).get(src, set())
    by_dst = {}
    for dst, _ in pairs:
        by_dst[dst] = by_dst.get(dst, 0) + 1
    counts = list(by_dst.values())
    return [[
        float(len(pairs)),
        float(len(by_dst)),
        float(max(counts, default=0)),
        float(max(counts, default=0) / max(len(pairs), 1)),
        float(window.get("src_bytes", {}).get(src, 0)),
    ]]


def exfil_features(window, src, dst, total_bytes=0.0):
    baseline = float(window.get("src_bytes", {}).get(src, 0))
    return [[
        float(total_bytes),
        baseline,
        float(total_bytes / max(baseline, 1.0)),
        float(window.get("idx", 0)),
        1.0 if dst in window.get("novel_dsts", set()) else 0.0,
    ]]


def _probability(model, features):
    if hasattr(model, "predict_proba"):
        return float(model.predict_proba(features)[0][1])
    score = float(model.decision_function(features)[0])
    return 1.0 / (1.0 + math.exp(-score))


def _anomaly_probability(model, features):
    score = float(model.decision_function(features)[0])
    return 1.0 / (1.0 + math.exp(10.0 * score))


class Models567:
    """Optional serving bundle for category-specific model artifacts."""

    def __init__(self, paths, thresholds=None):
        self.paths = dict(paths)
        # Operating points are measured per model by train_models_567.py's
        # sweep and shipped in the manifest; defaulting to 0.8 keeps an
        # old manifest working.
        self.thresholds = dict(thresholds or {})
        self.models = {}
        self.alerted = set()
        self.exfil_totals = {}
        self.exfil_novel = set()
        self._load()

    def _load(self):
        load = None
        xgb = None
        for name, path in self.paths.items():
            if not path:
                continue
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            if name.endswith("_xgb"):
                xgb = xgb or _require_xgboost()
                model = xgb.XGBClassifier()
                model.load_model(path)
            elif name == "sequence_cnn":
                from core.packet_sequence_cnn import PacketSequenceCnn
                model = PacketSequenceCnn.load(path)
            else:
                if load is None:
                    load, _, _ = _require_sklearn()
                model = load(path)
            self.models[name] = model

    def score_flow(self, flow):
        alerts = []
        if "encrypted_xgb" in self.models:
            score = _probability(self.models["encrypted_xgb"],
                                 [encrypted_metadata_features(flow)])
            key = ("encrypted", flow["key"])
            if score >= self.thresholds.get("encrypted_xgb", 0.8) \
                    and key not in self.alerted:
                self.alerted.add(key)
                alerts.append(("encrypted_session_malware", score, {
                    "model": "xgboost",
                    "metadata_features": encrypted_metadata_features(flow),
                }))
        if "sequence_cnn" in self.models:
            score = self.models["sequence_cnn"].score(flow)
            key = ("sequence", flow["key"])
            if score >= self.thresholds.get("sequence_cnn", 0.8) \
                    and key not in self.alerted:
                self.alerted.add(key)
                alerts.append(("encrypted_session_malware", score, {
                    "model": "1d-cnn",
                    "sequence_score": round(score, 4),
                }))
        return alerts

    def score_scan(self, window, src):
        features = scan_features(window, src)
        if len(window.get("pairs", {}).get(src, set())) < SCAN_MIN_PAIRS:
            return []
        alerts = []
        for name in ("scan_rf", "scan_iforest"):
            if name not in self.models:
                continue
            score = (_anomaly_probability(self.models[name], features)
                     if name.endswith("iforest") else
                     _probability(self.models[name], features))
            key = (name, "scan", window.get("idx"), src)
            if score >= self.thresholds.get(name, 0.8) \
                    and key not in self.alerted:
                self.alerted.add(key)
                alerts.append(("recon_model_scan", score,
                               {"model": name, "features": features[0]}))
        return alerts

    def score_exfil(self, window, src, dst, total_bytes):
        pair = (src, dst)
        self.exfil_totals[pair] = self.exfil_totals.get(pair, 0.0) + total_bytes
        if dst in window.get("novel_dsts", set()):
            self.exfil_novel.add(pair)
        cumulative = self.exfil_totals[pair]
        if pair not in self.exfil_novel or cumulative < EXFIL_MIN_BYTES:
            return []
        # Features use the per-window bytes -- the SAME distribution the model
        # was trained and evaluated on. The cumulative total is only the
        # eligibility gate; feeding it as a feature would shift the served
        # vector outside the training range (tree models cannot extrapolate,
        # which is what the holdout sweep exposed).
        features = exfil_features(window, src, dst, total_bytes)
        alerts = []
        for name in ("exfil_xgb", "exfil_iforest"):
            if name not in self.models:
                continue
            score = (_anomaly_probability(self.models[name], features)
                     if name.endswith("iforest") else
                     _probability(self.models[name], features))
            key = (name, "exfil", src, dst)
            if score >= self.thresholds.get(name, 0.8) \
                    and key not in self.alerted:
                self.alerted.add(key)
                alerts.append(("data_exfiltration_model", score,
                               {"model": name, "features": features[0]}))
        return alerts


def save_manifest(path, paths):
    with open(path, "w") as fh:
        json.dump({"version": 1, "models": paths}, fh, indent=2)
