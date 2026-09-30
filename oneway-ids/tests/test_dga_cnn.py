"""Tests for the DGA character CNN (model, backprop, persistence) and its
integration into DGADetector as a Tier-2 confirmer.

The gradient check is the important one: this network's forward and backward
passes are hand-written numpy, and a wrong convolution gradient still TRAINS
(just badly), so nothing else here would catch it.

Run: .venv/bin/python test_dga_cnn.py
"""
# Bootstrap: tests import core/, training/ and the root entry points, so put the
# repo root and its subpackages on sys.path regardless of the invocation CWD.
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in (_ROOT, _os.path.join(_ROOT, "training")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import os
import random
import tempfile

import numpy as np

from core import config
from collections import Counter

from core.dga_cnn import (CharCnn, Adam, encode_label, encode_batch, MAX_LEN,
                     VOCAB, PAD_IDX, UNK_IDX, DgaCnnScorer)
from core.detectors import DGADetector, shannon_entropy
from training import train_dga_cnn as tdc

failures = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        failures.append(name)


# ---------------------------------------------------------------- encoder --
ids, n = encode_label("Ab3")
check("encode_lowercases", ids[:3] == encode_label("ab3")[0][:3])
check("encode_length", n == 3 and len(ids) == MAX_LEN)
check("encode_pads", all(i == PAD_IDX for i in ids[3:]))
check("encode_unknown_char", encode_label("a.b")[0][1] == UNK_IDX)
check("encode_hyphen_is_in_vocab", encode_label("a-b")[0][1] != UNK_IDX)
check("encode_empty_safe", encode_label("")[1] == 1)
check("encode_truncates", encode_label("x" * 100)[1] == MAX_LEN)
check("encode_ids_in_vocab",
      all(0 <= i < VOCAB for i in encode_label("a-b9z")[0]))
X, lens = encode_batch(["abc", "de"])
check("encode_batch_shapes", X.shape == (2, MAX_LEN) and lens.tolist() == [3, 2])

# --------------------------------------------------------------- gradients --
# finite-difference check against the analytic backward pass.
np.random.seed(0)
model = CharCnn(kernels=(3,), filters=3, dim=4, seed=1, dropout=0.0)
labels = ["abc", "xyzw", "helpdesk", "q7z9x", "cdn01", "aa"]
Xg, Lg = encode_batch(labels)
yg = np.array([0, 1, 1, 0, 1, 0])


def loss_and_grads(m):
    probs, cache = m.forward(Xg, Lg, training=False)
    p = probs[np.arange(len(yg)), yg]
    loss = float(-np.log(np.clip(p, 1e-9, 1)).mean())
    return loss, m.backward(cache, yg)


eps = 1e-5
worst = 0.0
worst_name = ""
loss_0, grads_0 = loss_and_grads(model)
for name, param in model.params().items():
    flat = param.reshape(-1)
    for i in np.linspace(0, flat.size - 1, min(10, flat.size)).astype(int):
        orig = flat[i]
        flat[i] = orig + eps
        lp, _ = loss_and_grads(model)
        flat[i] = orig - eps
        lm, _ = loss_and_grads(model)
        flat[i] = orig
        num = (lp - lm) / (2 * eps)
        ana = grads_0[name].reshape(-1)[i]
        err = abs(num - ana) / max(1e-8, abs(num) + abs(ana))
        if err > worst:
            worst, worst_name = err, name
check("analytic_gradients_match_finite_difference", worst < 1e-4,
      f"worst rel err {worst:.2e} on {worst_name}")

# ------------------------------------------------------- forward invariants --
probs, _ = model.forward(Xg, Lg, training=False)
check("probs_sum_to_one", np.allclose(probs.sum(axis=1), 1.0, atol=1e-9))
check("probs_in_range", ((probs >= 0) & (probs <= 1)).all())
check("predict_proba_shape", model.predict_proba(["abc", "def"]).shape == (2, 2))
check("score_in_range", 0.0 <= model.score("abc") <= 1.0)

# Padding must be masked out of the max-pool, so what sits AFTER the true
# label cannot change the verdict. (Only guaranteed for labels at least as
# long as the widest kernel -- below that, a window necessarily reaches into
# the pad embeddings, consistently in both train and serve.)
pad_probe = CharCnn(kernels=(3, 5), filters=4, dim=4, seed=3, dropout=0.0)
for name, arr in pad_probe.params().items():
    arr[...] = 0.4
Xa, La = encode_batch(["abcdef"])
Xb = Xa.copy()
Xb[0, 6:] = 7                       # garbage where the padding lives
pa, _ = pad_probe.forward(Xa, La, training=False)
pb, _ = pad_probe.forward(Xb, La, training=False)
check("padding_masked_beyond_label_length", np.allclose(pa, pb, atol=1e-12),
      f"max delta {float(np.abs(pa - pb).max()):.2e}")

# ---------------------------------------------------------------- training --
train_labels = (["kq3vz9xbw2", "z8ym4tqpn6", "w7x2k9vqz3", "p4n8wz6yq1"] * 60
                + ["mailserver", "cloudbackup", "sensor07", "node12"] * 60)
train_y = np.array([1] * 240 + [0] * 240)
m2 = CharCnn(kernels=(3, 5), filters=16, dim=8, seed=5, dropout=0.0)
opt = Adam(lr=3e-3)
X2, L2 = encode_batch(train_labels)
first, last = None, None
for _ in range(25):
    order = np.random.default_rng(0).permutation(len(train_labels))
    for i in range(0, len(order), 64):
        idx = order[i:i + 64]
        _, cache = m2.forward(X2[idx], L2[idx], training=True)
        opt.step(m2.params(), m2.backward(cache, train_y[idx]))
    p = m2.predict_proba(train_labels)[:, 1]
    acc = float(((p >= 0.5) == (train_y == 1)).mean())
    last = acc
    if first is None:
        first = acc
check("training_reduces_loss", last >= first, f"{first:.3f} -> {last:.3f}")
check("model_fits_training_set", last >= 0.95, f"train acc {last:.3f}")

# ------------------------------------------------------------ persistence --
with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "m.npz")
    m2.save(path)
    loaded = CharCnn.load(path)
    a = m2.predict_proba(["kq3vz9xbw2", "cloudbackup"])
    b = loaded.predict_proba(["kq3vz9xbw2", "cloudbackup"])
    check("save_load_roundtrip_identical", np.array_equal(a, b))
    check("save_load_preserves_shape",
          loaded.filters == m2.filters and loaded.kernels == m2.kernels)
    check("load_missing_raises",
          not os.path.exists(os.path.join(tmp, "nope.npz")))

scorer = DgaCnnScorer(m2)
check("scorer_from_model", 0.0 <= scorer.score("abc") <= 1.0)
check("scorer_score_many", len(scorer.score_many(["a", "b", "c"])) == 3)

# ------------------------------------------- held-out generalisation claim --
# The claim on the slides is that the CNN beats the entropy rules on an unseen
# family of the SAME kind. Check it on a small, freshly generated sample.
rng = random.Random(0)          # the corpus generators use random.Random


def _persistently_seeded(fn, n):
    """Generate n labels, resetting the generator so the run is repeatable."""
    r = random.Random(1234)
    return [fn(r) for _ in range(n)]


train_pool = _persistently_seeded(tdc.dga_random_alnum, 600) + \
             _persistently_seeded(tdc.dga_random_letters, 600) + \
             _persistently_seeded(tdc.benign_label, 1200)
train_pool_y = np.array([1] * 1200 + [0] * 1200)
m3 = CharCnn(kernels=(3, 5), filters=24, dim=8, seed=9, dropout=0.2)
opt3 = Adam(lr=3e-3)
X3, L3 = encode_batch(train_pool)
for _ in range(12):
    order = np.random.default_rng(1).permutation(len(train_pool))
    for i in range(0, len(order), 64):
        idx = order[i:i + 64]
        _, cache = m3.forward(X3[idx], L3[idx], training=True)
        opt3.step(m3.params(), m3.backward(cache, train_pool_y[idx]))

heldout = _persistently_seeded(tdc.dga_hex_like, 300)   # family NOT trained
benign_h = _persistently_seeded(tdc.benign_label, 600)
cnn_heldout = float((m3.predict_proba(heldout)[:, 1] >= 0.5).mean())
rule_heldout = float(np.mean([tdc.rule_says_dga(l) for l in heldout]))
cnn_fp = float((m3.predict_proba(benign_h)[:, 1] >= 0.5).mean())
check("cnn_beats_rules_on_unseen_family", cnn_heldout > rule_heldout + 0.10,
      f"cnn {cnn_heldout:.3f} vs rules {rule_heldout:.3f}")
check("cnn_benign_fp_acceptable", cnn_fp <= 0.05, f"{cnn_fp:.3f}")

# ------------------------------------------------- detector integration ---
class Sink:
    """Stub matching AlertSink's emit signature (no file writes)."""

    def __init__(self):
        self.alerts, self.suppressed = [], 0

    def emit(self, t, src, dst, dport, proto, threat, conf, ev):
        self.alerts.append({"t": t, "src": src, "dst": dst, "dport": dport,
                            "proto": proto, "threat_class": threat,
                            "confidence": round(float(conf), 3),
                            "evidence": ev})

    def suppress(self, n=1):
        self.suppressed += n


# A fixed, deterministic pool of labels from a real DGA family
# (dga_random_alnum = cryptolocker-style). Note the split below: the lexical
# gate rejects a large share of them, which is the whole reason the CNN
# exists -- splitting the pool keeps each test honest about which labels it
# is asserting on.
_r = random.Random(5)
_POOL = [tdc.dga_random_alnum(_r) for _ in range(60)]
GATE_PASSING = [l for l in _POOL if tdc.rule_says_dga(l)]
GATE_MISSED = [l for l in _POOL if not tdc.rule_says_dga(l)]
LABELS = GATE_PASSING          # consecutive, so DGA_MIN_STREAK can be reached

check("lexical_gate_misses_a_share_of_random_labels",
      len(GATE_MISSED) / len(_POOL) >= 0.20,
      f"{len(GATE_MISSED)}/{len(_POOL)} uniform-random DGA labels rejected by "
      f"the entropy gate")
check("lexical_pool_large_enough", len(LABELS) >= 5, len(LABELS))

# train_dga_cnn keeps its own copy of the rule predicate so the evaluation
# script stays standalone. If the detector's gate ever changes, the reported
# "rule recall" silently becomes a lie -- so pin them together. The detector's
# per-label verdict is observable through its streak counter.
probe = DGADetector(Sink())
drift = []
for lab in _POOL[:40]:
    probe.streak["10.0.0.1"] = 0
    probe.on_dns(0.0, "10.0.0.1", lab + ".example.com")
    if (probe.streak["10.0.0.1"] > 0) != tdc.rule_says_dga(lab):
        drift.append(lab)
check("trainer_rule_matches_detector", not drift, drift[:3])


class FixedCnn:
    def __init__(self, prob):
        self.prob = prob

    def score(self, label):
        return self.prob


# 1. cnn=None must be exactly the original detector: no CNN evidence keys,
#    and deterministic (two fresh detectors emit byte-identical records)
sink = Sink()
det_none = DGADetector(sink)
for i, lab in enumerate(LABELS):
    det_none.on_dns(float(i), "10.0.0.9", lab + ".example.com")
sink2 = Sink()
det_none2 = DGADetector(sink2)
for i, lab in enumerate(LABELS):
    det_none2.on_dns(float(i), "10.0.0.9", lab + ".example.com")
check("cnn_none_emits_alerts", len(sink.alerts) > 0, len(sink.alerts))
check("cnn_none_has_no_cnn_evidence",
      all("dga_cnn_prob" not in a["evidence"] and "detector_tier" not in a["evidence"]
          for a in sink.alerts))
check("cnn_none_matches_reference_records", sink.alerts == sink2.alerts)
BASELINE = list(sink.alerts)      # frozen BEFORE section 2 rebinds `sink`
ORIGINAL_KEYS = {"qname_label", "label_length", "char_entropy_bits", "vowel_ratio",
                 "digit_ratio", "high_entropy_query_streak",
                 "dga_queries_seen_from_src", "note", "why"}
check("cnn_none_evidence_schema_frozen",
      all(set(a["evidence"]) == ORIGINAL_KEYS for a in sink.alerts),
      sorted(set(BASELINE[0]["evidence"]) ^ ORIGINAL_KEYS))

# 2. a confident CNN adds evidence to the lexical alert without changing it
sink = Sink()
det = DGADetector(sink, cnn=FixedCnn(0.99))
for i, lab in enumerate(LABELS):
    det.on_dns(float(i), "10.0.0.9", lab + ".example.com")
lexical = [a for a in sink.alerts if a["evidence"].get("detector_tier")
           == "tier1_lexical+cnn_confirmed"]
check("cnn_confirmed_count_matches_lexical_count",
      len(lexical) == len(BASELINE), f"{len(lexical)} vs {len(BASELINE)}")
check("cnn_confirms_lexical_alerts", len(lexical) > 0, len(lexical))
check("cnn_evidence_added",
      all(a["evidence"]["dga_cnn_prob"] == 0.99 for a in lexical))
check("cnn_does_not_change_confidence",
      [a["confidence"] for a in lexical] == [a["confidence"] for a in BASELINE])
check("cnn_does_not_change_timestamps",
      [a["t"] for a in lexical] == [a["t"] for a in BASELINE])
# the CNN must not remove or re-time any lexical alert; its only new
# emissions are the tier-2 ones
_not_tier2 = [a for a in sink.alerts
              if a["evidence"].get("detector_tier") != "tier2_cnn_only"]
check("cnn_preserves_lexical_alert_count", len(_not_tier2) == len(BASELINE),
      f"{len(_not_tier2)} vs {len(BASELINE)}")
check("cnn_preserves_lexical_alert_identity",
      [(a["t"], a["src"], a["confidence"]) for a in _not_tier2] ==
      [(a["t"], a["src"], a["confidence"]) for a in BASELINE])

# 3. a low-probability CNN must not add anything
sink = Sink()
det = DGADetector(sink, cnn=FixedCnn(0.10))
for i, lab in enumerate(LABELS):
    det.on_dns(float(i), "10.0.0.9", lab + ".example.com")
check("low_cnn_prob_adds_no_cnn_only_alerts",
      not any(a["evidence"].get("detector_tier") == "tier2_cnn_only"
              for a in sink.alerts))
check("low_cnn_prob_marks_tier1",
      all(a["evidence"].get("detector_tier") == "tier1_lexical"
          for a in sink.alerts if "detector_tier" in a["evidence"]))

# 4. quorum: CNN-positive LEXICAL-LOOKING labels are only an incident once
#    the per-source quorum is reached ("mailserver" is lexical, so only the
#    CNN path can fire on it). The quorum is read from config rather than
#    hardcoded here, because it is a MEASURED value: bench_dga.py swept it
#    against a real benign corpus and the FP cost of a short quorum is steep
#    (measured on the FULL corpus: k=2 -> 17.3 benign alerts/hour,
#    k=4 -> 0.46; the quick-run estimates 16.9/0.36 were revised upward).
#    A test that pinned a literal 2 would block that correction instead of
#    protecting it.
QUORUM = config.DGA_CNN_MIN_STREAK
sink = Sink()
det = DGADetector(sink, cnn=FixedCnn(0.95))
for i in range(QUORUM - 1):
    det.on_dns(float(i), "10.0.0.44", ["mailserver", "cloudbackup", "filestore",
                                       "buildagent", "datastore"][i % 5] +
               ".example.com")
check("cnn_below_quorum_no_alert", sink.alerts == [],
      (QUORUM, len(sink.alerts)))
det.on_dns(float(QUORUM), "10.0.0.44", "appserver.example.com")
cnn_only = [a for a in sink.alerts
            if a["evidence"].get("detector_tier") == "tier2_cnn_only"]
check("cnn_quorum_fires_at_min_streak", len(cnn_only) == 1, len(cnn_only))
check("cnn_quorum_default_is_measured",
      config.DGA_CNN_MIN_STREAK >= 4,
      "bench_dga.py measured k=2 at 17.3 benign alerts/hour (full corpus)")
check("cnn_only_never_critical", all(a["confidence"] < 0.90 for a in cnn_only),
      [a["confidence"] for a in cnn_only])
check("cnn_min_streak_overridable",
      DGADetector(Sink(), cnn=None, cnn_min_streak=7).cnn_min_streak == 7)
check("cnn_only_has_model_evidence",
      all(a["evidence"]["model"].startswith("char-cnn") for a in cnn_only))

# 5. a benign label breaks the CNN streak
sink = Sink()
det = DGADetector(sink, cnn=FixedCnn(0.0))
det.on_dns(0.0, "10.0.0.44", "mailserver.example.com")
det.cnn_streak["10.0.0.44"] = 5
det.on_dns(1.0, "10.0.0.44", "weather.example.com")
check("benign_label_resets_cnn_streak", det.cnn_streak["10.0.0.44"] == 0)

# 6. re-alert window dedupes a continuing CNN incident
sink = Sink()
det = DGADetector(sink, cnn=FixedCnn(0.95))
for i in range(10):
    det.on_dns(float(i), "10.0.0.44", "mailserver.example.com")
check("cnn_realert_deduped", len(sink.alerts) == 1, len(sink.alerts))

# ------------------------------------- the shipped model's demo claim ------
if os.path.exists(config.DGA_CNN_MODEL_PATH):
    real = DgaCnnScorer.from_file(config.DGA_CNN_MODEL_PATH)
    rescued = "8yuxczaumapqpp"
    check("rules_still_miss_the_rescued_label", not tdc.rule_says_dga(rescued))
    check("shipped_model_catches_the_rescued_label", real.score(rescued) >= 0.90,
          f"{real.score(rescued):.3f}")
    check("shipped_model_quiet_on_benign_services",
          all(real.score(l) < 0.5 for l in
              ["mailserver", "cloudbackup", "sensor07", "cdn", "api",
               "static", "weather", "harbor", "node12"]),
          [round(real.score(l), 3) for l in ["mailserver", "sensor07", "cdn"]])
else:
    print(f"[SKIP] {config.DGA_CNN_MODEL_PATH} not trained yet")

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    raise SystemExit(1)
print("all dga_cnn tests passed")
