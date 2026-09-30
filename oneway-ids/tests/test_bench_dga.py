"""Tests for the cross-dataset DGA benchmark harness (bench_dga.py).

Everything here runs OFFLINE against a fixture corpus written into a temp
dir: `fetch_corpus` must serve from cache without ever touching the network,
which is asserted directly by poisoning urlopen.

The regression this suite exists to pin is Result 4's cousin: the corpus
lists are kept SORTED for reproducibility, and feeding a per-source query
stream in sorted order clusters morphology (every digit-leading benign label
arrives back to back), which completes CNN quorums that a uniform ordering
never does. Measured on the full corpus at the shipped k=4: 9.9 benign
alerts/h from the sorted list vs 0.46/h from the same corpus shuffled.

Run: .venv/bin/python test_bench_dga.py
"""
# Bootstrap: tests import core/, training/ and the root entry points, so put the
# repo root and its subpackages on sys.path regardless of the invocation CWD.
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in (_ROOT, _os.path.join(_ROOT, "training")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import argparse
import os
import tempfile
import urllib.request

import numpy as np

from core import config
from training import bench_dga as bd
from training.bench_dga import (load_corpus, fetch_corpus, sample, rule_scores,
                       cnn_scores, compute, report, stream_scenarios,
                       quorum_sweep)
from core.detectors import DGADetector, dga_label_of

failures = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        failures.append(name)


class Sink:
    """Stub matching AlertSink's emit signature (no file writes)."""

    def __init__(self):
        self.alerts = []

    def emit(self, t, src, dst, dport, proto, threat, conf, ev):
        self.alerts.append({"t": t, "src": src, "threat_class": threat,
                            "confidence": conf, "evidence": ev})


class StubCnn:
    """predict_proba-compatible stand-in with a rule we control.

    DGADetector calls .score(label); bench_dga's cnn_scores calls
    predict_proba. Real model quality is the job of the benchmark itself --
    these tests pin harness behaviour, which must not depend on weights.
    """

    def __init__(self, fn):
        self.fn = fn

    def score(self, label):
        return float(self.fn(label))

    def predict_proba(self, labels):
        p = np.array([float(self.fn(l)) for l in labels])
        return np.stack([1.0 - p, p], axis=1)


POSITIVE = StubCnn(lambda l: 0.99)                      # always CNN-positive
DIGIT_LEADING = StubCnn(lambda l: 0.99 if l[0].isdigit() else 0.01)

# ------------------------------------------------------------ fixture corpus --
# Counts are exact and asserted below: 14 unique DGA domains in 2 named
# families + 3 unattributed (+1 duplicated line), 41 benign (1 shared with
# the DGA set -> overlap 1), and a wordlist with zero overlap that the
# loader must REPORT rather than silently include.


def build_fixture(root):
    corpus = os.path.join(root, "corpus")
    wl = os.path.join(corpus, "dga_wordlists")
    os.makedirs(wl)

    alpha = [f"alpha{i:04d}.example.com" for i in range(1, 7)]   # len-9 labels
    beta = [f"beta{i:04d}.beta.example.com" for i in range(1, 6)]
    unattr = ["zz9unattr1.example.com", "zz9unattr2.example.net",
              "0shared4both.example.org"]
    dga = alpha + beta + unattr

    benign = ([f"{w}{n:02d}.example.com"
               for w in ("mailserver", "cloudbackup", "filestore")
               for n in range(1, 11)]
              + [f"{d}warehouse.example.com" for d in (0, 3, 6, 9)]
              + ["0shared4both.example.org"])

    with open(os.path.join(corpus, "all_dga.txt"), "w") as fh:
        fh.write("\n".join(dga + [dga[0]]) + "\n")   # +1 duplicated line
    with open(os.path.join(corpus, "all_legit.txt"), "w") as fh:
        fh.write("\n".join(benign) + "\n")
    with open(os.path.join(wl, "alpha.txt"), "w") as fh:
        fh.write("\n".join(alpha) + "\n")
    with open(os.path.join(wl, "beta.txt"), "w") as fh:
        fh.write("\n".join(beta) + "\n")
    with open(os.path.join(wl, "ghost.txt"), "w") as fh:
        fh.write("\n".join(f"ghost{i}.nowhere.com" for i in range(4)) + "\n")
    return len(dga) + 1, len(benign)


def feed_tier2(order, src="10.9.9.9"):
    """Feed qnames (already labelled) through the shipping detector; return
    the tier2_cnn_only alerts. One query per second, one source."""
    sink = Sink()
    det = DGADetector(sink, cnn=DIGIT_LEADING)
    for i, label in enumerate(order):
        det.on_dns(float(i), src, label + ".example.com")
    return [a for a in sink.alerts
            if a["evidence"].get("detector_tier") == "tier2_cnn_only"]


with tempfile.TemporaryDirectory() as tmp:
    # -------------------------------------------- fetch serves from cache --
    real_urlopen = urllib.request.urlopen

    def _no_network(*a, **k):
        raise AssertionError("network access attempted with a warm cache")

    urllib.request.urlopen = _no_network
    try:
        n_dga_lines, n_benign_lines = build_fixture(tmp)
        corpus_dir = fetch_corpus(tmp)               # must not raise
    finally:
        urllib.request.urlopen = real_urlopen
    check("fetch_corpus_uses_cache_offline",
          os.path.isfile(os.path.join(corpus_dir, "all_dga.txt")))

    # ----------------------------------------------------- family attrib. --
    corpus = load_corpus(tmp)
    man = corpus["manifest"]
    check("families_recovered_by_membership_join",
          man["families"] == {"alpha": 6, "beta": 5}, man["families"])
    check("wordlist_with_zero_overlap_is_reported",
          man["wordlists_not_in_corpus"]
          == [{"list": "ghost.txt", "domains": 4, "in_all_dga": 0}],
          man["wordlists_not_in_corpus"])
    check("unattributed_counted_not_dropped", man["unattributed"] == 3)
    check("corpus_counts_lines_vs_unique",
          (man["dga_lines"], man["dga_unique"], man["benign_lines"],
           man["benign_unique"], man["overlap"])
          == (n_dga_lines, 14, n_benign_lines, n_benign_lines, 1),
          (man["dga_lines"], man["dga_unique"], man["benign_lines"],
           man["benign_unique"], man["overlap"]))
    check("corpus_lists_are_sorted_deterministic",
          corpus["dga"] == sorted(corpus["dga"])
          and corpus["benign"] == sorted(corpus["benign"]))

    # --------------------------------------- sampling: index, not position --
    xs = [f"{i:04d}dom" for i in range(1000)]        # lexicographically sorted
    full_a, full_b = sample(xs, None, seed=7), sample(xs, None, seed=7)
    check("full_corpus_draw_deterministic", full_a == full_b)
    check("full_corpus_draw_is_permutation",
          sorted(full_a) == xs and len(full_a) == len(xs))
    check("full_corpus_draw_is_shuffled", full_a != xs)

    sub = sample(xs, 200, seed=1)
    check("subsample_right_size_and_members",
          len(sub) == 200 and len(set(sub)) == 200 and set(sub) <= set(xs))
    check("subsample_reaches_the_tail",                # NOT items[:200]
          max(int(x[:4]) for x in sub) > 800)
    check("subsample_deterministic", sub == sample(xs, 200, seed=1))

    # ------------------------------ regression: sorted stream completes ----
    # CNN quorums that a uniform ordering never does (see module docstring).
    # Same corpus, same detector, same stub -- only the feed order differs.
    clustered = feed_tier2(["0a", "1a", "2a", "3a"])
    check("clustered_order_completes_quorum", len(clustered) == 1,
          len(clustered))
    spread = feed_tier2(["0a", "x1", "1a", "x2", "2a", "x3", "3a", "x4"])
    check("interleaved_benign_breaks_quorum", len(spread) == 0, len(spread))

    benign_sorted = feed_tier2(corpus["benign"])          # the artifact feed
    benign_mixed = feed_tier2(
        sample(corpus["benign"], None, seed=101))         # what the harness
    check("sorted_feed_fires_benign_alerts",
          len(benign_sorted) >= 1, len(benign_sorted))
    check("shuffled_feed_is_quieter_than_sorted",
          len(benign_mixed) < len(benign_sorted),
          f"{len(benign_mixed)} vs {len(benign_sorted)}")

    # --------------------------------------------- quorum default & sweep --
    det_default = DGADetector(Sink())
    check("cnn_min_streak_defaults_to_config_constant",
          det_default.cnn_min_streak == config.DGA_CNN_MIN_STREAK
          and config.DGA_CNN_MIN_STREAK >= 4,
          det_default.cnn_min_streak)

    SW = quorum_sweep(POSITIVE, corpus, rows=300, per_family=100, qps=1.0,
                      ks=(2, 4))
    # Constant-positive stub: the first alert lands exactly at the quorum-th
    # query, so queries_to_first_alert == k is a sharp assertion of the math.
    check("sweep_first_alert_at_exactly_k",
          all(SW[str(k)]["per_family"]["alpha"]["queries_to_first_alert"] == k
              for k in (2, 4)),
          {k: SW[str(k)]["per_family"]["alpha"]["queries_to_first_alert"]
           for k in (2, 4)})
    check("sweep_families_detected_both_quora",
          all(SW[str(k)]["families_detected"] == 2 for k in (2, 4)))
    check("sweep_benign_never_increases_with_k",
          SW["4"]["benign_alerts"] <= SW["2"]["benign_alerts"],
          (SW["2"]["benign_alerts"], SW["4"]["benign_alerts"]))

    # ------------------------------------- per-string metrics & batching --
    # cnn_scores' docstring promises batching is a pure speedup; this is the
    # verification that promise refers to. A real (untrained) CharCnn, three
    # batch sizes, one answer.
    from core.dga_cnn import CharCnn
    real = CharCnn(kernels=(3, 5), filters=4, dim=6, seed=11, dropout=0.0)
    labels = ([f"lab{i:03d}x" for i in range(300)]
              + [l for l in corpus["benign"][:20]]
              + [l for l in corpus["dga"][:20]])
    labels = [dga_label_of(d) for d in labels]
    by_one = cnn_scores(real, labels, batch=1)
    by_997 = cnn_scores(real, labels, batch=997)
    worst = max(abs(a - b) for a, b in zip(by_one, by_997))
    check("cnn_batching_is_pure_speedup", worst <= 1e-12, f"max delta {worst:.2e}")

    results = compute(corpus, POSITIVE)
    bl = results["bench_labels"]
    n_b = len(bl["benign"])
    check("bench_labels_aligned",
          len(bl["rule"]) == len(bl["cnn"]) == n_b == len(corpus["benign"]))
    check("bench_labels_are_first_labels",
          bl["benign"] == [dga_label_of(d) for d in corpus["benign"]])
    check("rule_scores_are_booleans",
          all(isinstance(r, bool) or r in (0, 1) for r in bl["rule"]))

    # ------------------------------------------------------------ report --
    results["stream"] = stream_scenarios(
        POSITIVE, corpus, limit={"benign": 30, "dga_per_family": 4,
                                 "mixed": 200})
    text, out = report(results, corpus, POSITIVE,
                       argparse.Namespace(quick=False), limit={
                           "benign": 30, "dga_per_family": 4, "mixed": 200})
    check("report_fp_rates_match_the_arrays",
          abs(out["per_string"]["benign_rule_fp"] - sum(bl["rule"]) / n_b)
          < 1e-12
          and abs(out["per_string"]["benign_cnn_fp_0.5"]
                  - sum(p >= 0.5 for p in bl["cnn"]) / n_b) < 1e-12)
    check("report_sweep_fpr_consistent_with_per_string",
          abs(out["sweep"]["0.5"]["fpr"]
              - out["per_string"]["benign_cnn_fp_0.5"]) < 1e-12)
    results["quorum_sweep"] = quorum_sweep(POSITIVE, corpus, rows=50,
                                           per_family=50, qps=1.0, ks=(2,))
    text, out = report(results, corpus, POSITIVE,
                       argparse.Namespace(quick=False), limit={
                           "benign": 30, "dga_per_family": 4, "mixed": 200})
    check("report_text_has_the_sections",
          all(s in text for s in ("=== corpus ===",
                                  "=== per-string discrimination",
                                  "=== CNN threshold sweep",
                                  "=== end-to-end through the shipping",
                                  "=== Tier-2 quorum sweep")))
    fam_rows = out["per_string"]["families"]
    check("report_family_rows_complete",
          set(fam_rows) == {"alpha", "beta"}
          and all(fam_rows[f]["n"] == len(corpus["families"][f])
                  for f in fam_rows))
    check("stream_mixed_reports_ambiguous_labels",
          out["stream"]["mixed_host"]["ambiguous_labels"] == 1,
          out["stream"]["mixed_host"]["ambiguous_labels"])
    check("stream_benign_host_shape",
          out["stream"]["benign_host"]["queries"] == 30
          and out["stream"]["benign_host"]["alerts_per_hour"] >= 0)

# ------------------------------------------------- shipped-model sanity -------
# Not a benchmark number -- just pins that the harness reads the model the
# pipeline ships (same file path, loadable, deterministic scores).
if os.path.exists(config.DGA_CNN_MODEL_PATH):
    from core.dga_cnn import DgaCnnScorer
    scorer = DgaCnnScorer.from_file(config.DGA_CNN_MODEL_PATH)
    a = scorer.score("8yuxczaumapqpp")
    b = scorer.score("8yuxczaumapqpp")
    check("shipped_model_loads_and_scores_deterministically",
          0.0 <= a <= 1.0 and a == b, f"{a:.4f}")
else:
    print(f"[SKIP] {config.DGA_CNN_MODEL_PATH} not found")

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    raise SystemExit(1)
print("all bench_dga tests passed")
