"""
ML tier (Item 4): flow-feature extraction + LightGBM scoring.

Feature parity guarantee: flow_features() is the ONLY place features are
built -- imported by both train_ml.py (training) and MLScorer (serving),
so train/serve skew is structurally impossible.

Labels (train_ml.py only) derive from generator ground truth via
label_flow(); known noise documented there.
"""
import time

from core.config import ATTACK_HOST_ROLES, VICTIM_IP, FLOOD_WINDOW, \
    SCAN_TARGET_IP, EXFIL_DST_IP, C2_IPS, ML_PROBA_THRESHOLD, \
    ML_REAlert_SECS

FEATURE_NAMES = ["npkt", "nbytes", "duration", "nsyn", "bytes_per_pkt",
                 "pkts_per_sec", "is_udp", "dport", "sport_priv",
                 "dst_internal"]


def flow_features(f: dict) -> list:
    """f = closed flow dict from FlowAssembler."""
    dur = max(f["t1"] - f["t0"], 0.001)
    npkt = max(f["npkt"], 1)
    src, sport, dst, dport, proto = f["key"]
    return [
        f["npkt"],
        f["nbytes"],
        f["t1"] - f["t0"],
        f["nsyn"],
        f["nbytes"] / npkt,
        f["npkt"] / dur,
        1 if proto == "udp" else 0,
        dport,
        1 if sport < 1024 else 0,
        1 if dst.startswith("10.") else 0,
    ]


def label_flow(src, dst, dport, proto, t0) -> int:
    """Ground-truth binary label from generator knowledge.

    Documented label noise: host 10.0.0.9's ~30 benign DNS queries are
    labeled malicious (indistinguishable one-way from DGA queries without
    response-side NXDOMAIN info).
    """
    if dst in C2_IPS:
        return 1
    if src in ATTACK_HOST_ROLES:
        if src == "10.0.0.9" and proto == "udp" and dport == 53:
            return 1
        if src == "10.0.0.11" and dst == EXFIL_DST_IP:
            return 1
        if src == "10.0.0.13" and dst == SCAN_TARGET_IP:
            return 1
    if dst == VICTIM_IP and FLOOD_WINDOW[0] <= t0 < FLOOD_WINDOW[1]:
        return 1
    return 0


class MLScorer:
    """Tier-2 ML confirmer: scores closed flows; alerts on high malicious
    probability. Tier boundaries:
      - bare SYN-only flows (npkt==1, nsyn==1) are skipped: individual
        probe/flood packets are the aggregate detectors' domain (fan-out,
        DDoS windows) -- per-flow ML on them only produces storms.
    Performance: flows are micro-batched and scored on flush (called within
    the same 0.5s stream tick), keeping bounded latency while amortizing
    LightGBM's per-call overhead. Deduped per source (ML_REAlert_SECS).
    """

    def __init__(self, sink, booster, threshold=ML_PROBA_THRESHOLD):
        self.sink = sink
        self.booster = booster
        self.threshold = threshold
        self.last_alert = {}
        self._buffer = []

    @classmethod
    def from_file(cls, sink, path):
        from core import lgb_env  # noqa: F401  (NixOS: preloads libstdc++ before lightgbm)
        import lightgbm as lgb
        return cls(sink, lgb.Booster(model_file=path))

    def on_flow(self, f: dict):
        if f["npkt"] == 1 and f["nsyn"] == 1:
            return                                    # bare SYN: rules' domain
        self._buffer.append(f)

    def flush(self):
        if not self._buffer:
            return
        feats = [flow_features(f) for f in self._buffer]
        probs = self.booster.predict(feats)
        for f, prob in zip(self._buffer, probs):
            prob = float(prob)
            if prob < self.threshold:
                continue
            src = f["key"][0]
            t = f["t1"]
            if t - self.last_alert.get(src, -1e18) < ML_REAlert_SECS:
                continue
            self.last_alert[src] = t
            fdict = dict(zip(FEATURE_NAMES,
                             [round(v, 2) if isinstance(v, float) else v
                              for v in flow_features(f)]))
            self.sink.emit(t, src, f["key"][2], f["key"][3], f["key"][4],
                           "ml_flow_suspicious", prob, {
                               "malicious_probability": round(prob, 4),
                               "model": "lightgbm (temporal split)",
                               "flow_features": fdict,
                               "why": "supervised model flags this flow's "
                                      "feature vector as highly likely "
                                      "malicious",
                           })
        self._buffer = []
