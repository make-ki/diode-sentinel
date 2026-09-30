"""
Tier-2 DNS confirmer: a 1D character CNN over the first DNS qname label.

Why a CNN on top of the lexical rules
-------------------------------------
`DGADetector` is a scalar heuristic: character entropy plus vowel/digit ratios.
That catches *random-looking* labels, and it catches them cheaply. It walks
straight past **dictionary** DGA families (suppobox, matsnu), which build
domains by concatenating real English words -- "helpdeskupdate", "drivercenter"
-- because such labels are perfectly lexical and low entropy by construction.
No threshold on entropy can separate them from a benign hostname.

A character CNN learns sub-word morphology instead of one scalar, so the
decision is over letter *sequences*. That is also what the PS asks for
literally: "Entropy/n-gram analysis of DNS query names" -- the n-gram half.

Zero new dependencies
---------------------
The network is numpy only. numpy is already present as a LightGBM dependency,
so this adds no package to the venv: no torch, no keras, no ONNX. ~5k
parameters, trained and served on CPU.

Train/serve parity by construction
----------------------------------
`encode_label()` is the ONLY place a domain string becomes a tensor. It is
imported by both train_dga_cnn.py and DgaCnnScorer, so the encoder cannot
drift between training and serving -- the same guarantee `flow_features()`
gives the LightGBM tier.
"""
import json
import math

import numpy as np

# ---- encoder: single source of truth for both training and serving --------

_PAD, _UNK = "<pad>", "<unk>"
CHARS = list("0123456789abcdefghijklmnopqrstuvwxyz-_")
PAD_IDX, UNK_IDX = 0, 1
VOCAB = len(CHARS) + 2
MAX_LEN = 32                      # labels are truncated/padded to this

_CHAR_TO_IDX = {c: i + 2 for i, c in enumerate(CHARS)}


def encode_label(label: str):
    """(ids, length) for one label. Lowercased; unknown chars -> <unk>.

    An empty label becomes a single <unk> token rather than a run of them, so
    "no label" stays one character wide instead of five.
    """
    text = (label or "").lower()
    ids = [_CHAR_TO_IDX.get(ch, UNK_IDX) for ch in text[:MAX_LEN]]
    if not ids:
        ids = [UNK_IDX]
    length = len(ids)
    if length < MAX_LEN:
        ids += [PAD_IDX] * (MAX_LEN - length)
    return ids, length


def encode_batch(labels):
    """(X, lens) tensors for a list of labels."""
    pairs = [encode_label(l) for l in labels]
    return (np.array([p[0] for p in pairs], dtype=np.int64),
            np.array([p[1] for p in pairs], dtype=np.int64))


def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


# ---- the network ----------------------------------------------------------

class CharCnn:
    """Embedding -> parallel Conv1D(k=3, k=5) -> ReLU -> global max-pool ->
    dense -> softmax. Kim-CNN style, length-invariant by construction.

    Global max-pooling over positions means the classifier does not care where
    in the label a suspicious n-gram sits, and padding is masked out of the
    pool so a short label cannot win the max on its pad embeddings.
    """

    def __init__(self, kernels=(3, 5), filters=32, dim=16, seed=0, dropout=0.3):
        rng = np.random.default_rng(seed)
        self.kernels = tuple(kernels)
        self.filters = int(filters)
        self.dim = int(dim)
        self.dropout = float(dropout)
        self.E = rng.normal(0, 0.1, (VOCAB, self.dim))
        self.W = [rng.normal(0, 1.0, (self.filters, k, self.dim))
                  * math.sqrt(2.0 / (k * self.dim)) for k in self.kernels]
        self.b = [np.zeros(self.filters) for _ in self.kernels]
        self.Wd = rng.normal(0, 0.1, (2, self.filters * len(self.kernels)))
        self.bd = np.zeros(2)

    # -- parameter plumbing (flat names -> arrays, so Adam is generic) -------

    def params(self):
        out = {"E": self.E, "Wd": self.Wd, "bd": self.bd}
        for i, w in enumerate(self.W):
            out[f"W{i}"] = w
        for i, b in enumerate(self.b):
            out[f"b{i}"] = b
        return out

    # -- forward ------------------------------------------------------------

    def _conv(self, emb, Wk, bk, k, lens):
        B, T, D = emb.shape
        P = T - k + 1
        # windows[b, p] = emb[b, p:p+k] flattened in (j, d) order
        win = np.lib.stride_tricks.sliding_window_view(emb, k, axis=1)
        win = np.transpose(win, (0, 1, 3, 2)).reshape(B, P, k * D)
        pre = win @ Wk.reshape(self.filters, k * D).T + bk      # (B,P,C)
        pre = np.transpose(pre, (0, 2, 1))                      # (B,C,P)
        # a position is valid only if its whole window is real characters
        eff = np.maximum(lens, k)
        pos = np.arange(P)[None, :]
        pad = pos > (eff[:, None] - k)
        act = np.where(pre > 0, pre, 0.0)
        act = np.where(pad[:, None, :], -1e9, act)
        idx = act.argmax(axis=2)
        g = np.take_along_axis(act, idx[:, :, None], axis=2)[:, :, 0]
        return g, {"win": win, "pre": pre, "pad": pad, "idx": idx}

    def forward(self, X, lens, training=False):
        emb = self.E[X]
        gs, convs = [], []
        for Wk, bk, k in zip(self.W, self.b, self.kernels):
            g, c = self._conv(emb, Wk, bk, k, lens)
            gs.append(g)
            convs.append(c)
        gcat = np.concatenate(gs, axis=1)
        # Dropout on the pooled features. Without it this model memorises the
        # training families (train loss -> 0.006) and generalises to none of
        # the held-out ones -- the whole point of the family split.
        mask = None
        if training and self.dropout > 0:
            keep = 1.0 - self.dropout
            mask = (np.random.random(gcat.shape) < keep) / keep
            gcat_d = gcat * mask
        else:
            gcat_d = gcat
        probs = softmax(gcat_d @ self.Wd.T + self.bd)
        return probs, {"emb": emb, "convs": convs, "gcat": gcat_d,
                       "X": X, "probs": probs, "mask": mask}

    # -- backward -----------------------------------------------------------

    def _conv_backward(self, dg, cache, Wk, k, emb):
        B, C, P = cache["pre"].shape
        D = Wk.shape[2]
        dz = np.zeros_like(cache["pre"])
        np.put_along_axis(dz, cache["idx"][:, :, None], dg[:, :, None], axis=2)
        dz = np.where(cache["pre"] > 0, dz, 0.0)          # ReLU
        dz = np.where(cache["pad"][:, None, :], 0.0, dz)  # masked positions
        dzT = np.transpose(dz, (0, 2, 1))                 # (B,P,C)
        dW = np.einsum("bpc,bpk->ck", dzT, cache["win"]).reshape(Wk.shape)
        db = dzT.sum(axis=(0, 1))
        dwin = (dzT @ Wk.reshape(self.filters, k * D)).reshape(B, P, k, D)
        demb = np.zeros_like(emb)
        for j in range(k):
            demb[:, j:j + P, :] += dwin[:, :, j, :]
        return dW, db, demb

    def backward(self, cache, y):
        B = len(y)
        dlogits = cache["probs"].copy()
        dlogits[np.arange(B), y] -= 1.0
        dlogits /= B
        grads = {"Wd": dlogits.T @ cache["gcat"], "bd": dlogits.sum(axis=0)}
        dgcat = dlogits @ self.Wd
        if cache["mask"] is not None:                # dropout backward
            dgcat = dgcat * cache["mask"]
        F = self.filters
        demb_total = np.zeros_like(cache["emb"])
        for i, k in enumerate(self.kernels):
            dW, db, demb = self._conv_backward(
                dgcat[:, i * F:(i + 1) * F], cache["convs"][i], self.W[i], k,
                cache["emb"])
            grads[f"W{i}"], grads[f"b{i}"] = dW, db
            demb_total += demb
        dE = np.zeros_like(self.E)
        np.add.at(dE, cache["X"], demb_total)
        grads["E"] = dE
        return grads

    # -- inference ----------------------------------------------------------

    def predict_proba(self, labels):
        X, lens = encode_batch(list(labels))
        probs, _ = self.forward(X, lens, training=False)
        return probs

    def score(self, label) -> float:
        """P(label comes from a DGA family)."""
        return float(self.predict_proba([label])[0, 1])

    # -- persistence --------------------------------------------------------

    def save(self, path):
        payload = {f"p_{k}": v for k, v in self.params().items()}
        payload["meta"] = np.array(json.dumps({
            "kernels": list(self.kernels), "filters": self.filters,
            "dim": self.dim, "dropout": self.dropout, "vocab": VOCAB,
            "max_len": MAX_LEN, "chars": CHARS}))
        np.savez(path, **payload)

    @classmethod
    def load(cls, path):
        z = np.load(path, allow_pickle=False)
        meta = json.loads(str(z["meta"]))
        if meta["vocab"] != VOCAB or meta["max_len"] != MAX_LEN:
            raise ValueError("model was trained on a different encoder "
                             "(vocab/max_len mismatch) -- retrain it")
        model = cls(kernels=tuple(meta["kernels"]), filters=meta["filters"],
                    dim=meta["dim"], dropout=meta.get("dropout", 0.0))
        for name, arr in model.params().items():
            arr[...] = z[f"p_{name}"]
        return model

    @classmethod
    def new(cls, **kw):
        return cls(**kw)


class Adam:
    """Adam with global-norm gradient clipping and decoupled weight decay
    (applied to the weights, never to the biases)."""

    def __init__(self, lr=3e-3, b1=0.9, b2=0.999, eps=1e-8, clip=5.0, l2=1e-3):
        self.lr, self.b1, self.b2, self.eps, self.clip = lr, b1, b2, eps, clip
        self.l2 = l2
        self.t, self.m, self.v = 0, {}, {}

    def step(self, params, grads):
        self.t += 1
        norm = math.sqrt(sum(float((g * g).sum()) for g in grads.values()))
        scale = 1.0 if norm <= self.clip else self.clip / (norm + 1e-12)
        for name, p in params.items():
            g = grads[name] * scale
            if self.l2 and not name.startswith("b"):
                p -= self.lr * self.l2 * p          # decoupled decay
            self.m[name] = self.b1 * self.m.get(name, np.zeros_like(p)) + (1 - self.b1) * g
            self.v[name] = self.b2 * self.v.get(name, np.zeros_like(p)) + (1 - self.b2) * g * g
            mh = self.m[name] / (1 - self.b1 ** self.t)
            vh = self.v[name] / (1 - self.b2 ** self.t)
            p -= self.lr * mh / (np.sqrt(vh) + self.eps)


# ---- serving wrapper (mirrors ml_tier.MLScorer.from_file) -----------------

class DgaCnnScorer:
    """Scores DNS labels; deliberately does NOT emit. The DNS detector owns
    alerting, dedupe and streak state, so the confirmer stays a pure function
    of the label."""

    def __init__(self, model, threshold=0.5):
        self.model = model
        self.threshold = threshold

    @classmethod
    def from_file(cls, path, threshold=0.5):
        return cls(CharCnn.load(path), threshold=threshold)

    def score(self, label: str) -> float:
        return self.model.score(label)

    def score_many(self, labels):
        return self.model.predict_proba(labels)[:, 1].tolist()
