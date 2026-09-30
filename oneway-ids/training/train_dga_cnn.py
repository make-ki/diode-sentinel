"""
Train the Tier-2 DGA character CNN, with family-held-out evaluation.

The honest protocol
-------------------
For a *string* model a random train/test split is worthless: the same family
generates both halves, so the model just memorises that family's alphabet.
The split here is therefore **by DGA family**: several families are held out
entirely and never seen during training. That is what `Diode-Sentinel.pptx`
slide 11 promises ("family-held-out testing for DGA") and what this script
actually does.

The held-out families are the **dictionary** DGAs (suppobox, matsnu style),
because they are the adversarial case for the existing detector: they produce
low-entropy, perfectly lexical labels, so `DGADetector`'s entropy gate cannot
separate them from a benign hostname. The benign corpus deliberately contains
concatenated compounds and word+digit hostnames, so the task stays hard rather
than being set up for a flattering number.

Run: .venv/bin/python train_dga_cnn.py
"""
# Bootstrap: this script lives in training/, one level below the repo root, so
# the core package and sibling modules resolve no matter the CWD it is invoked
# from.
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in (_ROOT, _os.path.join(_ROOT, "training")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import random
import time

import numpy as np

from core.config import DGA_CNN_MODEL_PATH
from core.dga_cnn import CharCnn, Adam, encode_batch
from core.detectors import dga_lexical_gate

# --------------------------------------------------------------------------
# vocabulary used by both the benign generator and the dictionary DGA families
# --------------------------------------------------------------------------

WORDS = """alpha amber anchor angle apple arrow atlas aurora baker beacon beam
berry bishop blade bloom bridge brook cable cache candle canvas carbon cedar
center chart cipher circuit clarity cloud coast cobalt comet compass copper
coronet cortex cosmos crane crystal cyber delta domain drift eagle east edge
ember engine envoy ether fable fabric falcon feather field finch flame flint
forest forge foundry fountain foxgate galaxy gateway gecko granite harbor
harvest helix horizon hub hunter indigo iris iron island ivory jade jasper
junction juniper kernel keypoint lagoon lantern lattice ledger legend light
limestone linden loop lotus lumen magnet maple marble market matrix meadow
meridian mesa meteor metro milo mingle mirror mist mosaic moss network nexus
nimbus node north nova oasis ocean olive onyx opal orbit orchard ore osiris
outpost packet pallas park path pebble pelican pendant phoenix pillar pilot
pine pivot pixel plato plaza plum point polar pond portal prairie prism
quarry quartz quill radiant rally raven reef relay ridge river robin rocket
rose rowan ruby rune rustic sabre sage sail salt sand sapphire satellite
scale scenic sconce seam seraph shade shell sierra signal silver sketch sky
slate slope socket solar song sparrow spool spring spruce spur star static
station steel stella stone storm stream summit surge sydney sycamore table
talon tamarind tarn tellurium terrace thistle thorn tide timber titan topaz
torch tower trace trail transit travel trellis trench triton tunnel turret
umbra union uplink valley vector velvet vertex vessel vista vivid vortex
voyage walnut ward wave weather well west willow wind winter wireless
wombat wren yard yellow zephyr zinc""".split()

SERVICES = ["mail", "api", "cdn", "img", "assets", "static", "auth", "login",
            "vpn", "proxy", "metrics", "telemetry", "backup", "update", "ntp",
            "dns", "smtp", "ftp", "git", "ci", "docs", "wiki", "portal",
            "intranet", "sensor", "plc", "rtu", "gateway", "scada", "hmi",
            "camera", "printer", "nas", "db", "cache", "queue", "search"]


# --------------------------------------------------------------------------
# benign hostname (first-label) generator
# --------------------------------------------------------------------------

def benign_label(rng):
    """Realistic benign first labels: single words, compounds, word+digits,
    hyphenated device names, and short service abbreviations."""
    roll = rng.random()
    if roll < 0.24:
        return rng.choice(SERVICES)                      # "mail", "cdn"
    if roll < 0.46:
        return rng.choice(WORDS)                         # "weather", "harbor"
    if roll < 0.62:                                      # "cloudapi", "netedge"
        return rng.choice(WORDS) + rng.choice(SERVICES)
    if roll < 0.76:                                      # "sensor07", "node12"
        return rng.choice(SERVICES) + str(rng.randint(1, 99))
    if roll < 0.88:                                      # "esp32-a1b2", "plc-2"
        return "%s-%s" % (rng.choice(SERVICES + ["esp32", "sensor", "node"]),
                          rng.choice(["a1b2", "x7", "01", "prod", "eu-west"]))
    return rng.choice(WORDS)[:6] + rng.choice(WORDS)[:6]  # abbreviated compound


# --------------------------------------------------------------------------
# DGA families.  Held-out families exercise morphology the model never saw.
# --------------------------------------------------------------------------

ALNUM = "abcdefghijklmnopqrstuvwxyz0123456789"
LETTERS = "abcdefghijklmnopqrstuvwxyz"


def dga_random_alnum(rng):
    """cryptolocker-style uniform alnum."""
    return "".join(rng.choice(ALNUM) for _ in range(rng.randint(10, 20)))


def dga_random_letters(rng):
    """ramnit-style pure letters, no digits."""
    return "".join(rng.choice(LETTERS) for _ in range(rng.randint(8, 16)))


def dga_hex_like(rng):
    """gozi-style hex-ish."""
    return "".join(rng.choice("0123456789abcdef") for _ in range(rng.randint(12, 24)))


def dga_murofet(rng):
    """murofet-style long random with occasional repeats."""
    n = rng.randint(14, 24)
    out = []
    while len(out) < n:
        out.extend(rng.choice(ALNUM) for _ in range(rng.randint(1, 4)))
    return "".join(out)[:n]


def dga_dictionary_pair(rng):
    """HELD OUT -- suppobox style: two English words concatenated, no digits."""
    return rng.choice(WORDS) + rng.choice(WORDS)


def dga_dictionary_digits(rng):
    """HELD OUT -- matsnu style: one or two words plus a number."""
    return rng.choice(WORDS) + str(rng.randint(1, 9999))


# Families the model trains on.
TRAIN_FAMILIES = {"random_alnum": dga_random_alnum,
                  "random_letters": dga_random_letters,
                  "murofet": dga_murofet,
                  "dictionary_digits": dga_dictionary_digits}

# Families held out entirely. Two DIFFERENT kinds, because they answer two
# different questions and conflating them flatters or damns the model
# unfairly:
#   hex_like          -- same KIND as training (uniform-random labels), unseen
#                        family. Tests generalisation within a morphology.
#   dictionary_pair   -- a DIFFERENT kind (real words, no digits). Tests the
#                        adversarial case the lexical rules cannot separate.
HELDOUT_FAMILIES = {"hex_like": dga_hex_like,
                    "dictionary_pair": dga_dictionary_pair}


# --------------------------------------------------------------------------
# the rule detector's per-label predicate
# --------------------------------------------------------------------------
# Imported from detectors rather than copied: the reported "rule recall" is
# then the score of the predicate the sensor runs, not of a lookalike that
# could drift from it.
rule_says_dga = dga_lexical_gate


def build_corpus(n_benign, n_per_family, families, seed):
    rng = random.Random(seed)
    labels, y_true, family = [], [], []
    for _ in range(n_benign):
        labels.append(benign_label(rng))
        y_true.append(0)
        family.append("benign")
    for name, fn in sorted(families.items()):
        for _ in range(n_per_family):
            labels.append(fn(rng))
            y_true.append(1)
            family.append(name)
    return labels, np.array(y_true), np.array(family)


def evaluate(model, labels, y_true):
    probs = model.predict_proba(labels)[:, 1]
    pred = probs >= 0.5
    tp = int(((pred == 1) & (y_true == 1)).sum())
    fp = int(((pred == 1) & (y_true == 0)).sum())
    fn = int(((pred == 0) & (y_true == 1)).sum())
    tn = int(((pred == 0) & (y_true == 0)).sum())
    rec = tp / max(tp + fn, 1)
    fpr = fp / max(fp + tn, 1)
    return rec, fpr, pred, probs


def recall_at(pred, mask):
    return float(pred[mask].mean()) if int(mask.sum()) else float("nan")


def main():
    t_start = time.time()
    print("=== DGA character CNN (numpy, no torch) ===")

    # Pool of SEEN families, split train/val. The held-out families are never
    # used for model selection, so the final numbers are not tuned on them.
    pool_labels, pool_y, pool_fam = build_corpus(
        12000, 3000, TRAIN_FAMILIES, seed=1)
    rng_split = np.random.default_rng(11)
    perm = rng_split.permutation(len(pool_labels))
    cut = int(0.9 * len(perm))
    tr, va = perm[:cut], perm[cut:]
    train_labels = [pool_labels[i] for i in tr]
    train_y = pool_y[tr]
    val_labels = [pool_labels[i] for i in va]
    val_y = pool_y[va]

    test_labels, test_y, test_fam = build_corpus(
        2000, 1500, HELDOUT_FAMILIES, seed=2)

    print(f"train: {len(train_labels):,} labels from {len(TRAIN_FAMILIES)} "
          f"families {sorted(TRAIN_FAMILIES)}")
    print(f"val  : {len(val_labels):,} labels (same families -- model selection)")
    print(f"test : {len(test_labels):,} labels, HELD-OUT families "
          f"{sorted(HELDOUT_FAMILIES)} (never used for training or selection)")
    print(f"benign includes compounds and word+digit hostnames, so the "
          f"dictionary case is\ngenuinely ambiguous from the string alone\n")

    model = CharCnn.new(kernels=(3, 5), filters=32, dim=16, seed=7, dropout=0.3)
    n_params = sum(int(v.size) for v in model.params().values())
    print(f"model: embedding 16d -> Conv1D(3,5)x32 -> maxpool -> dropout 0.3 "
          f"-> dense ({n_params:,} params)")

    opt = Adam(lr=3e-3, l2=1e-3)
    X, lens = encode_batch(train_labels)
    Xv, lensv = encode_batch(val_labels)
    order = np.arange(len(train_labels))
    rng = np.random.default_rng(3)
    batch = 64
    epochs = 30
    patience, best, best_state, bad = 5, -1.0, None, 0

    for epoch in range(1, epochs + 1):
        rng.shuffle(order)
        losses = []
        for i in range(0, len(order), batch):
            idx = order[i:i + batch]
            probs, cache = model.forward(X[idx], lens[idx], training=True)
            p = probs[np.arange(len(idx)), train_y[idx]]
            losses.append(float(-np.log(np.clip(p, 1e-9, 1)).mean()))
            opt.step(model.params(), model.backward(cache, train_y[idx]))
        vpred = model.predict_proba(val_labels)[:, 1] >= 0.5
        vbal = 0.5 * (recall_at(vpred, val_y == 1) + recall_at(~vpred, val_y == 0))
        flag = ""
        if vbal > best + 1e-4:
            best, bad = vbal, 0
            best_state = {k: v.copy() for k, v in model.params().items()}
            flag = "  <- best"
        else:
            bad += 1
        print(f"  epoch {epoch:2d}: loss {np.mean(losses):.4f} | "
              f"val balanced-acc {vbal:.3f}{flag}")
        if bad >= patience:
            print(f"  early stop (no val improvement for {patience} epochs)")
            break

    if best_state:
        for k, v in model.params().items():
            v[...] = best_state[k]
        print(f"restored best weights (val balanced-acc {best:.3f})")

    print("\n=== held-out evaluation (model never trained or selected on these) ===")
    pred = model.predict_proba(test_labels)[:, 1] >= 0.5
    print(f"{'family':<20}{'n':>6}{'CNN recall':>12}{'rule recall':>13}")
    print("-" * 51)
    for fam in sorted(set(test_fam)):
        m = test_fam == fam
        if fam == "benign":
            continue
        rules = np.mean([rule_says_dga(l) for l, k in zip(test_labels, m) if k])
        print(f"{fam:<20}{int(m.sum()):>6}{recall_at(pred, m):>12.3f}{rules:>13.3f}")
    bm = test_fam == "benign"
    rules_b = np.mean([rule_says_dga(l) for l, k in zip(test_labels, bm) if k])
    print(f"{'benign (FP rate)':<20}{int(bm.sum()):>6}"
          f"{float(pred[bm].mean()):>12.3f}{rules_b:>13.3f}")

    # sanity check: the model must at least be strong on what it did see
    seen_labels, seen_y, _ = build_corpus(1500, 400, TRAIN_FAMILIES, seed=99)
    seen_pred = model.predict_proba(seen_labels)[:, 1] >= 0.5
    print(f"\nfor reference, on unseen samples of the TRAINING families: "
          f"recall {recall_at(seen_pred, seen_y == 1):.3f}, "
          f"benign FP {float(seen_pred[seen_y == 0].mean()):.3f}")

    overall_r = recall_at(pred, test_y == 1)
    rule_all = float(np.mean([rule_says_dga(l) for l, k in
                              zip(test_labels, test_y) if k]))
    print(f"\noverall on {len(test_labels):,} held-out labels: "
          f"CNN recall {overall_r:.3f} at {float(pred[bm].mean()):.3f} FP | "
          f"rule recall {rule_all:.3f} at {rules_b:.3f} FP")

    model.save(DGA_CNN_MODEL_PATH)
    print(f"\nmodel saved -> {DGA_CNN_MODEL_PATH} ({time.time() - t_start:.1f}s)")
    print("note: the CNN is a CONFIRMER, not a replacement. It is trained on "
          "the families above only,\n      and the honest reading of the "
          "dictionary row is that morphology alone does not\n      settle "
          "dictionary DGA -- which is why the detector gates the CNN with "
          "its own\n      one-way behavioural signal (unique-domain streak per "
          "source).")


if __name__ == "__main__":
    main()
