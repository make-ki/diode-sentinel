# `Diode-Sentinel.pptx` vs the prototype — reconciliation

> **⚠ SUPERSEDED — kept as an audit record, not a current to-do.**
> This review was written against the **Sep 14 2026** `.pptx`, which described
> a Kafka/Flink/ClickHouse/React/ONNX/K8s/Terraform stack that does not exist
> in this repo. That deck was replaced on **29 Sep 2026** by one built from the
> honest source (`build_deck.py` → 17 slides). Every "fix before you present"
> item in §C and §E below has been addressed by the rebuild, and the fictional
> stack named in §B is now absent from the shipped deck.
>
> Read this for the *negative findings* that stay true regardless of the deck:
> §B.1 (the project is multi-model, not multimodal), and §F's warning that the
> CNN's live rescue does **not** fire at the shipped quorum (k=4) — quote it as
> a benchmark measurement, never as a live alert. Do not action §C/§E; they are
> done.

Checked `../Diode-Sentinel.pptx` (16 slides) against the code in this
directory. **Short answer: the architecture matches, the technology stack does
not — and the deck never mentions the thing you actually built.**

Two separate problems, and they cut in opposite directions:

1. **The deck claims ~30 named technologies the repo does not contain.** If a
   judge says "show me the Kafka topic", there is nothing to show.
2. **The deck never says you have a working prototype.** 16 slides, and not one
   sentence is spent on the repo that already runs. At the idea stage, most
   teams have a slide deck *and nothing else* — that is your biggest unused
   asset, and the deck currently discards it.

The deck is for the **IDEA** round (it follows the official
`SIH2026-IDEA-Presentation-Format`), where a target architecture is expected
and legitimate. So the fix is not to rewrite the idea — it is to **label the
stack as the target** and **add one slide for what runs today**.

---

## A. The same architecture — keep this, it is your strongest through-line

The deck's *structural* idea and the code agree closely. These are the parts a
judge can be shown and which are genuinely implemented:

| Deck claim (slide) | In the code | Status |
|---|---|---|
| Optical TAP → flow metadata → windows → **Tier-0 → Tier-1 → Tier-2** → fused alerts (1, 5, 8) | `config.ALLOWLIST` → 6 streaming detectors → LightGBM `ml_tier.py` → `FusionEngine` | ✅ same 3-tier shape |
| **Allowlist-first**; known-good OT traffic never reaches ML (5, 11) | Tier-0 checked with zero detector cost | ✅ |
| Fingerprint inventory **never auto-learned from attacker traffic** (11) | known-bad handshakes are excluded from inventory — documented "prevents baseline poisoning" | ✅ |
| Fusion, **storm dedup**, one evolving incident (5, 11) | fire-on-escalation dedupe + noisy-OR decayed confidence | ✅ |
| **Metadata-only, no decryption, compliant by construction** (1, 5) | TLS/QUIC ClientHello parsing only; `tls_meta.py`, `quic_meta.py` | ✅ |
| **JA4 + QUIC-aware** per-flow verdicts (4) | JA4/JA3 from TLS **and** from QUIC Initials | ✅ **and better than the deck — see §D** |
| Time-based splits, no leakage (11) | `train_ml.py`: train t<420 s, test t≥420 s | ✅ |
| Dashboard with **severity and confidence** (5, 8) | rebuilt dashboard: severity, confidence, per-alert evidence | ✅ |
| Demo on recorded pcaps, **no diode hardware** (7, 9) | `run.py`, `--parity`, `--ml` on `traffic.pcap` | ✅ (minus Docker) |
| Per-device baselines (4, 11) | per-**source** byte baselines (`src_baseline_bytes_median`) | ⚠️ partial |
| Versioned communication matrix: peers, ports, polling periods, resolvers, JA4 (8, 11) | 4-entry hand-edited `(dst_ip, dst_port)` allowlist + JA4 inventory persisted via `--state` | ⚠️ partial |

---

## B. The stack the deck names but the repo does not contain

Roughly **30 named technologies; 5 are present.** Verified by grep, not by
impression.

| Deck claim | Reality in the repo |
|---|---|
| C/C++ capture with **DPDK / PF_RING** ring buffers (6) | Python `AF_PACKET` raw socket (`live_source.py`) and `dpkt`/`scapy` (`pcap_reader.py`) |
| **Zeek and Suricata** in parser-only mode (6) | neither is used; hand-written ClientHello/DNS dissectors |
| **Kafka / Redpanda** partitioned by flow key, **Redis Streams**, Schema Registry with **Protobuf/Avro**, **Flink** exactly-once checkpoints (6) | one Python process; `FlowAssembler` + `WindowAggregator`; JSONL on disk |
| **Flink + Polars** event-time windowing at **5 s / 60 s / 10 min** (6, 8) | pure Python, **one window size: 10 s** (`config.WINDOW`) |
| Feature list: entropy ✅, IAT ✅, JA3/JA4 ✅, byte ratios ✅, plus **FFT inputs** ✗, **HLL fan-out** ✗, **SPLT sequences** ✗ (6) | exact `set`/`Counter` cardinality, IAT mean/CV — no FFT, no HyperLogLog, no packet-length/time sequences |
| Six models: **Random Forest, XGBoost, 1D-CNN, LightGBM, Isolation Forest, VAE**, all exported to **ONNX**, served on **ONNX Runtime / Triton** (4, 6, 8, 9) | **two** models: LightGBM (`model_ml.txt`) and a numpy 1D **character CNN** for DGA (`model_dga_cnn.npz`, added after this review — see §F). No Random Forest, XGBoost, Isolation Forest or VAE. `sklearn` is imported only for `classification_report` |
| **"p99 under 10 ms"** inference budget (6) | no latency distribution is measured; only throughput (44,269 pkt/s) |
| **Go/Python fusion service** → **ClickHouse** with materialized views and TTL tiering (7) | Python fusion ✅; **JSONL file**, no ClickHouse |
| **React + strict TypeScript** dashboard, **Grafana + Prometheus + OpenTelemetry**, async **webhook dispatch to SIEM/PagerDuty/Slack** (7) | stdlib `ThreadingHTTPServer` + daisyUI/Chart.js static page; no React, no TS, no metrics stack, no webhooks |
| **DVC**, **Docker + Compose**, **Kubernetes + Terraform** (7, 9) | venv + README commands. No Dockerfile, no compose, no manifests |
| Trained on **CIC-DDoS2019, CTU-13, UNSW-NB15, DGArchive, ISCXVPN2016, ToN-IoT, UQ NetFlow-v3** (7, 9, 16) | **one synthetic generator** (`gen_traffic.py`). No public dataset is ingested anywhere |
| **MITRE technique IDs** persisted (5, 8, 11) | scenario tags only (`confirmed_c2_implant`) — no T-IDs. `architecture.svg` correctly calls these "MITRE-**style** tags" |
| **Sketches + EWMA/CUSUM**, flood decided **inline at line rate in sub-seconds** (5, 8) | threshold detector per **10 s window** — decided per window, not inline |

Two size checks that make the gap concrete:

- The deck's Feature-engineering stage names **7** feature families; the code
  implements **4**.
- The deck's ML stage names **6** models; the code implements **2** (one of them — the DGA CNN — is genuinely one of the six named).

### B.1 "Multimodal" — no, and it is worth being precise about this

The repo is **not multimodal.** As of the DGA CNN it is now genuinely
**multi-model (two)**, over **two** input types. Verified by dependency
inspection, not by impression:

- The project source imports six non-stdlib packages: `dpkt`, `scapy`,
  `lightgbm`, `cryptography`, `numpy`, and `sklearn` (used only for
  `classification_report` / `confusion_matrix` — no sklearn estimator is
  instantiated).
- The venv contains: cffi, cloudpickle, cryptography, dpkt, joblib, lightgbm,
  narwhals, numpy, pycparser, scipy, scikit-learn, threadpoolctl.
  **No torch, no keras, no tensorflow, no onnx, no polars, no pandas.**
- `train_ml.py` instantiates one estimator:
  `lgb.LGBMClassifier(n_estimators=200, num_leaves=31)` → `model_ml.txt`,
  consuming **10 tabular flow statistics** (`ml_tier.py` → `FEATURE_NAMES`):
  `npkt, nbytes, duration, nsyn, bytes_per_pkt, pkts_per_sec, is_udp, dport,
  sport_priv, dst_internal`.
- `dga_cnn.py` is a second, independently trained model: a 1D **character**
  CNN over the DNS label (embedding → Conv1D(k=3,5)×32 → ReLU → masked global
  max-pool → dropout → dense), 4,930 parameters, written in numpy. It consumes
  the **string** modality, which the flow model never sees.

So there are now **two models over two different input types** — but that is
still not "multimodal ML": nothing fuses the two representations. The other
signal families remain *deterministic* code:

| Signal family | Handled by | Learned? |
|---|---|---|
| Packet timing / flags / sizes | `FlowAssembler`, `BeaconDetector` (IAT mean+CV) | ❌ rules |
| Aggregate statistics (window rate, Shannon entropy, fan-out, per-pair bytes) | `DDosDetector`, `ScanDetector`, `ExfilDetector` | ❌ rules |
| **Lexical** — DNS qname strings | `DgaDetector` (entropy, vowel/digit ratios, streak) | ❌ rules |
| **Protocol metadata** — TLS/QUIC ClientHello → JA4/JA3 | `TlsDetector` | ❌ rules |
| Multivariate per-flow deviation | `MLScorer` — LightGBM | ✅ **the only model** |

**Multi-signal fusion is still not multimodal ML.** `FusionEngine` correlates
*verdicts* (noisy-OR over decayed confidences); it does not fuse *features*
into a shared representation. The deck's "1D-CNN over SPLT packet-shape
metadata" (a *timing* modality) is still absent.

**"Where is the AI in your DGA detection?" is now answerable.** A learned
character model exists (`dga_cnn.py`), it is trained with a family-held-out
split, and it is measurably better than the rules on an unseen family: 1.000
recall vs 0.473, at a lower false-positive rate (0.001 vs 0.003). It also
rescues a real query on the shipped demo traffic. Lead with that; see §F for
the numbers and for what it does *not* do.

---

## C. Eight present-tense sentences to fix before you present

The rest of the deck reads as a plan and is fine. These eight assert something
as *already done*, which is what invites "show me":

| Slide | Sentence | Problem |
|---|---|---|
| **16** | *"Our models **are** rigorously trained and validated using publicly available, high-fidelity datasets"* | Most dangerous line in the deck. The model is trained on `gen_traffic.py` output; `README.md` says so explicitly. |
| **4** | *"Tier-0 communication matrix **encodes** legitimate polling periods, peers, and JA4 fingerprints"* | Present tense. You have a 4-entry IP/port allowlist plus a JA4 inventory. |
| **5** | *"terminal Tier-1 detector ... **decides floods inline at line rate in sub-seconds**"* | Your windows are 10 s. Decisions are per window, not inline. |
| **11** | *"polling protocols and maintenance schedules **are** explicit negative classes in training"* | Not true of the current model. |
| **9** | Public datasets *"**is mapped** to every model"* | True as a plan, not as a fact. |
| **6** | *"every model **exported to ONNX** ... **p99 under 10 ms**"* | No ONNX export exists; no p99 measured. |
| **9** | *"the full pipeline **runs** on recorded pcaps via one replay script"* | True in spirit, but via Python venv, not Docker — and "full pipeline" overstates one model vs six. |
| **1** | *"5s/60s/10m feature windows"* | One window size (10 s). It also contradicts your own `architecture.svg`, which says "10s windows". |

**The internal contradiction to watch for:** if you show slide 1 next to
`architecture.svg`, the audience sees "5s/60s/10m windows" and "10s windows",
and "Tier-2 confirmers" (plural) against "LightGBM scorer" (singular). Fix one
of the two.

Cheapest repair, if you want to touch nothing else: put **"Target
architecture"** in the header of slides 6, 7, 8 and 9, and change slide 16's
opening from *"Our models are trained on…"* to *"We will train and validate
on…"*. That converts every falsifiable claim into a roadmap item without
touching the substance.

---

## D. What the deck undersells — put these on a slide

The deck spends 16 slides describing a system you have not built yet and
**zero slides** describing the one you have. That is backwards for an idea
round, where a working slice is rare. Everything below is in the repo and
verifiable in the demo:

- **JA4 out of QUIC, with no secret.** The deck says "QUIC-aware (4)".
  What actually exists is stronger: QUIC **Initial** packets are decryptable
  because RFC 9001 derives keys from a **public version salt + connection ID**,
  so you extract a real JA4 on a one-way feed with no key material — and
  `test_quic.py` proves it byte-identical against the direct TLS parse. The
  deck's own §b constraint ("no payload decryption") stays satisfied.
- **The clock closes detection windows, not the traffic.** Flood-then-silence
  would otherwise sit unscored forever — unbounded latency on a sensor whose
  only claim is bounded latency. Proven by contrast in `test_live.py`.
  Slide 8 mentions bounded latency; this is the *mechanism* that delivers it.
- **Self-auditing loss accounting.** A one-way feed cannot report its own
  drops, so you audit your own capture path — including a real bug where
  ICMP/GRE/ESP frames were discarded without incrementing any counter, making
  dropped frames look processed. Directly answers the deck's own slide-10 risk
  "Line-rate pressure … any slow stage drops packets permanently".
- **Forensic reproducibility.** Offline replay and `--ml` reproduce the alert
  files **byte-for-byte** against committed fixtures, and `--parity` asserts
  dpkt and scapy produce **identical** alert distributions. That is what
  "clean chain of custody" means in practice, and it is not in the deck.
- **Baseline-poisoning prevention.** Known-bad handshakes never enter the
  inventory. Deck slide 11 says "never auto-learned from attacker traffic" —
  this is the code that does it.
- **A measured throughput number the deck lacks.** Slide 9 asserts "one CPU-only
  appliance" but never states a rate; the PS explicitly requires one
  ("Defined throughput target"). You have it: **44,269 pkt/s ≈ 188 Mbps
  sustained, single core, pure Python** (24,687 pkt/s with the ML tier).
- **Operator-curated allowlist, deliberately** — auto-learning periodic traffic
  whitelists existing botnets, the same reason RITA/AC-Hunter force analysts to
  curate.
- **Six PS threat classes covered, 0 false positives after allowlisting, 295
  test checks green across seven suites.** One line, and it is the scoreboard.

---

## E. Suggested slide edits, in order of value per minute

1. **Add one slide: "What runs today (and what is a roadmap item)."** Two
   columns. Left: the working pipeline, the measured rate, 6/6 classes, **the
   two trained models incl. the DGA CNN and its held-out numbers**, the
   dashboard, the test count, the PS constraints satisfied. Right: the target
   stack (Kafka/Flink/ClickHouse/React/the remaining models) marked *planned*.
   This single slide resolves the entire §B table and turns your biggest risk
   into your biggest differentiator.
2. **Mark slides 6–9 "Target architecture"** in the header.
3. **Fix the eight sentences in §C**, starting with slide 16.
4. **Align slide 1 with `architecture.svg`** — say "10 s detection windows
   (5 s/60 s/10 min planned)" so the deck and the figure agree.
5. **Add the throughput number** to slide 9: 44,269 pkt/s ≈ 188 Mbps sustained.
6. **Refresh `architecture.svg`'s footer**: it says "58 unit tests" — it is now
   295 (42+15+10+64+82+51+31, seven suites).
7. **Decide the MITRE story before a judge does.** Either add real technique IDs
   to the fused verdicts, or say "MITRE-style scenario tags" consistently —
   the SVG and the deck currently use different words for the same thing.

---

## F. The biggest code-side gap is now partly closed — the DGA CNN

**DONE (this session):** the deck's *"1D-CNN + LightGBM (DGA)"* and
*"family-held-out testing for DGA"* are now real, not roadmap.

| Deck claim | Before | Now |
|---|---|---|
| slide 4: "1D-CNN + LightGBM (DGA)" | no CNN anywhere | `dga_cnn.py`, numpy 1D char-CNN, 4,930 params |
| slide 11: "family-held-out testing for DGA" | none | families held out, one of each kind |
| slide 6/9: "ONNX, p99 < 10 ms" | absent | still absent — but no longer needed to make slide 4 true |

**Numbers to quote** (from `train_dga_cnn.py`, reproducible):

| Held-out family | n | CNN recall | rule recall |
|---|---|---|---|
| `hex_like` — same kind, unseen family | 1500 | **1.000** | 0.473 |
| `dictionary_pair` — different kind | 1500 | 0.007 | 0.004 |
| benign — false-positive rate | 2000 | **0.001** | 0.003 |

**And the single best demo line in the whole project — read this before you
use it.** The CNN's rescue *used* to be a live alert. At the original quorum
`DGA_CNN_MIN_STREAK = 2`, `--ml --dga-cnn` emitted 56 alerts vs 55 for `--ml`
alone, the extra one being a **true DGA query the entropy rules called benign**:

- label `8yuxczaumapqpp`, from `10.0.0.9` (ground-truth role `botnet_dga`)
- character entropy **3.182** against a `DGA_MIN_ENTROPY` gate of **3.3**
- rules: benign. CNN: **1.000**. Emitted at `high`, conf 0.85, zero new FPs.

**That line no longer fires at the shipped quorum, and quoting it as current
would be the one thing a judge can check and break.** The external corpus
(`BENCH-DGA.md`) measured the CNN's per-string FP rate at **16.5% on 1M real
benign labels**, which made k=2 cry wolf **17.3 alerts/hour on a purely benign
host**; `DGA_CNN_MIN_STREAK = 4` is the shipped default for that measured
reason. Verified on this capture: `--ml --dga-cnn` emits the **same 55 alerts
as `--ml`, byte-identical** — the CNN corroborates 8 existing lexical alerts at
prob 1.0 (`tier1_lexical+cnn_confirmed`), emits **zero** `tier2_cnn_only`
alerts, and `8yuxczaumapqpp` sits one label short of the quorum and stays
quiet.

So tell the story as a **measurement on the benchmark, not a live alert**:
on the external corpus the CNN recovers conficker **0.019 → 0.886** and pushdo
**0.000 → 0.446** where the entropy gate's 10-character floor blinds it. That
is stronger evidence than one demo packet ever was. If the live rescue matters
for the demo, run it with an explicit `cnn_min_streak=2` **for the demo only**
and *say* the shipped default is 4 — do not silently revert the default to make
a nicer screenshot.

**What it does NOT do — say this before a judge asks.** The held-out
*dictionary* family scores 0.007 for the CNN and 0.004 for the rules: neither
works. Dictionary DGA (suppobox/matsnu) produces low-entropy, perfectly
lexical labels, so morphology alone cannot settle it. That negative result is
the honest reason the CNN is a **quarantined Tier-2 confirmer** (per-source
quorum, confidence capped at 0.85 so it can never be labelled critical),
not a replacement for the rules. Presenting it as "we solve DGA" would be the
one claim a judge can dismantle.

**Still open, in priority order:** Random Forest / XGBoost / Isolation Forest
(the rest of the model zoo), ClickHouse/Kafka/Flink (infrastructure), the
public flow datasets (CIC-DDoS2019, CTU-13, UNSW-NB15) for the **flow**-feature
model, and real MITRE technique IDs. DGArchive-equivalent DGA data is no longer
on the "still open" list — see §G.

---

## G. The deck's riskiest slide-16 sentence became true today — the external corpus

Slide 16 says: *"Our models **are** rigorously trained and validated using
publicly available, high-fidelity datasets"* — flagged in §C as the most
dangerous line in the deck, because until now every label came from this
repo's own generator. That sentence is now **partly true, measurably**, and
the part that is true is on the DGA side:

| Slide-16 implication | Status after `bench_dga.py` |
|---|---|
| "publicly available datasets" | **True for DGA**: scored as-shipped on andrewaeva/DGA — 694,173 real DGA domains across 8 named malware families (conficker, zeus, cryptolocker, pushdo, ramdo, rovnix, tinba, matsnu) vs 1,000,000 Alexa domains. External, citable, unmodified; model sha256 and corpus digests recorded in `dga_bench.json`. |
| "validated" | **True and unflattering where it should be**: rules 0.019/0.000 TPR on conficker/pushdo vs CNN 0.886/0.446; CNN per-string FP 16.5% on 1M benign — published, and used to *derive* the shipped quorum (17.3→0.46 alerts/h from k=2→4). |
| "our models are trained on…" | **Still false for the flow model.** LightGBM is still trained on generator output; CTU-13/CIC-IDS remain roadmap. Keep slide 16's verb honest for that half. |

Two more §C-adjacent sentences this closes or sharpens:

- **"Where is the AI in your DGA detection?"** (§B.1) now has an
  external-corpus answer, not just a synthetic one: on someone else's
  corpus the learned model recovers exactly the families the scalar gate is
  structurally blind to.
- **§C slide-4 sentence** ("Tier-0 communication matrix encodes…") stays on
  the fix list — the external corpus does not touch that claim.

The two sampling bugs the benchmark surfaced are themselves stage material:
a 0.83-vs-0.165 FP swing from sampling a sorted list by position, and 9.9-vs-
0.43 benign alerts/hour from *feeding* a sorted stream to a quorum detector.
Both are documented in `BENCH-DGA.md` §Result 4 with the fix and the
test that pins them — evidence the evaluation is adversarial toward itself,
which is the thing slide 16 is actually claiming.
