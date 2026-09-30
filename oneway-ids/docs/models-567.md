# Category 5-7 Models

This document describes the optional learned model tier added for the three requested threat categories. The existing rule detectors remain enabled because they provide the fast, explainable first signal.

## Overview

| Category | Model | Input | Output |
|---|---|---|---|
| 5. Malware in encrypted sessions | NumPy 1D CNN + XGBoost | packet sizes, timing, one-way direction, TLS/QUIC metadata | `encrypted_session_malware` |
| 6. Reconnaissance / port scanning | Random Forest + Isolation Forest | per-source destination/port fan-out | `recon_model_scan` |
| 7. Data exfiltration | XGBoost + Isolation Forest | transfer volume, source baseline, destination novelty | `data_exfiltration_model` |

The models are served by `core/models_567.py` and integrated at flow-close and window-flush points in `core/pipeline.py`.

## Category 5: encrypted sessions

### Packet-sequence CNN

`core/packet_sequence_cnn.py` converts each closed flow into a compact token sequence:

- packet size buckets
- inter-arrival-time buckets
- outbound direction markers

Because this is a one-way feed, direction is represented explicitly as outbound. There is no fabricated response direction.

The CNN reuses the project’s NumPy convolution implementation from `dga_cnn.py`. It uses parallel Conv1D kernels, masked pooling, dropout, and a dense classifier. It is saved as `sequence_cnn.npz`.

### TLS/QUIC metadata XGBoost

The pipeline attaches parsed ClientHello metadata to the corresponding flow. The XGBoost feature vector includes:

- cipher count
- extension count
- TLS version
- TLS versus QUIC transport
- SNI presence
- signature-algorithm count
- packet count and byte count
- flow duration
- packet-size variation

This model does not decrypt application payloads. QUIC analysis remains limited to decryptable Initial packets.

## Category 6: reconnaissance

The pipeline builds a per-source window feature vector:

- distinct destination/port pairs
- distinct destination IPs
- number of pairs on the most-used destination
- concentration on the most-used destination
- source bytes in the window

The Random Forest provides a supervised scan probability. Isolation Forest provides an unsupervised anomaly score from normal fan-out behavior.

The model tier only evaluates sources that already meet the configured scan fan-out threshold. This prevents ordinary low-volume browsing from creating model alerts and keeps the existing rule detector as the first-stage candidate generator.

## Category 7: data exfiltration

The exfiltration feature vector contains:

- window bytes transferred to the source/destination pair
- current source volume baseline
- transfer-to-baseline ratio
- window index
- destination novelty flag

XGBoost provides a supervised exfiltration probability. Isolation Forest scores anomalous transfer behavior against normal traffic.

The feature vector uses the **per-window** byte total — the same distribution the models are trained and evaluated on. The cumulative total is only an eligibility gate: a destination is evaluated after it is observed as novel and its cumulative transfer reaches `EXFIL_MIN_BYTES`. Pair-level model alerts are deduplicated.

## Training

Install the optional dependencies (scikit-learn and joblib are already main
dependencies; this adds XGBoost only):

```bash
uv sync --extra ml567          # or: pip install '.[ml567]'
```

Generate or refresh the synthetic capture, then train:

```bash
uv run python gen_traffic.py
uv run python training/train_models_567.py --pcap traffic.pcap --out models567
```

Training uses the synthetic generator's labels and a temporal split at 390
seconds. The split point is load-bearing, not arbitrary: the scan attack runs
in two bursts (250 s and 400 s) and exfiltration in two (300 s and 480 s), so
t=390 sits in the gap and gives **every** category malicious rows on both
sides. Earlier the split was 500 s, which placed the entire scan burst in
training and left the holdout with zero malicious scan cases — recall read as
0.000 not because the model failed but because there was nothing to score. The
two-burst generator layout is what makes the split evaluable.

The trainer does not just fit — it **evaluates the temporal holdout and sweeps
the operating threshold** (0.5 … 0.99) for every model, reporting recall,
precision and benign false-positive rate at each point. The shipped threshold
per model is the most sensitive point whose benign FP rate stays within a 0.5%
budget, and it is written into `manifest.json` and read at serve time — so what
was measured is what ships. This is the same discipline as the DGA quorum sweep
in `bench_dga.py`: thresholds are measured constants, never guesses. See
"Measured holdout results" below for what the current capture actually shows.

## Artifacts and manifest

The trained artifacts **ship in the repository**, so `--models-567` works out of
the box exactly like the DGA CNN (`model_dga_cnn.npz`). Re-running the trainer
regenerates them. The trainer creates:

```text
models567/manifest.json      model paths + the measured thresholds
models567/eval.json          holdout evaluation + full threshold sweep
models567/encrypted_xgb.json
models567/scan_rf.joblib
models567/scan_iforest.joblib
models567/exfil_xgb.json
models567/exfil_iforest.joblib
models567/sequence_cnn.npz
```

The manifest maps model names to artifact paths and carries the thresholds. The
runner loads it lazily:

```bash
uv run python run.py --models-567 models567/manifest.json
```

If the manifest is omitted, the optional category 5-7 tier is disabled and the
loaded manifest's absence is reported, not fatal. Rules-only replay does not
require XGBoost or scikit-learn.

## Alert behavior

Model alerts use the standard JSONL schema and include the model name and feature vector in `evidence`. The model tier is a confirmer, not a replacement for the streaming rules:

- rule detectors provide low-latency candidate signals
- learned models add supervised or anomaly-based confirmation
- `FusionEngine` can correlate the resulting alerts with other threat classes
- model alerts are deduplicated per flow, scan window/source, or exfiltration pair

## Measured holdout results

The numbers below are the trainer's own temporal-holdout evaluation (`t >= 390s`)
on the shipped capture, reproduced by `training/train_models_567.py`. `models567/eval.json`
is the machine-readable original, including the full threshold sweep per model.
The raw model is scored over **every** held-out flow and window — not just the
rule-gated subsets the server sees — so the benign FP pressure here
upper-bounds the deployed tier.

| Model | Holdout | Malicious | Threshold | Recall | Precision | Benign FP |
|---|---|---|---|---|---|---|
| `encrypted_xgb` | 1092 | 50 | 0.50 | **1.000** | **1.000** | 0 (0.0%) |
| `sequence_cnn` | 1092 | 50 | 0.50 | **1.000** | **1.000** | 0 (0.0%) |
| `scan_rf` | 321 | 2 | 0.50 | **1.000** | **1.000** | 0 (0.0%) |
| `scan_iforest` | 321 | 2 | 0.99 | **0.000** | — | 0 (0.0%) |
| `exfil_xgb` | 542 | 6 | 0.50 | **1.000** | **1.000** | 0 (0.0%) |
| `exfil_iforest` | 542 | 6 | 0.95 | **0.000** | — | 0 (0.0%) |

**Read this table before presenting the tier.** Four of six models now genuinely
work; the two that do not are a specific, diagnosable failure, not a vague
"ML is hard":

- **Categories 5, 6 and 7 supervised models are genuinely strong.**
  `encrypted_xgb`, `sequence_cnn`, `scan_rf` and `exfil_xgb` all reach 1.000
  recall at 1.000 precision with **zero** benign false positives on held-out
  traffic they never trained on. The earlier 0.000 results for `scan_rf` and
  `exfil_xgb` were **not** model failures — the split placed every malicious
  scan and exfil row in training, so the holdout had nothing to score. Once the
  generator emits bursts on both sides of the split, the same architectures
  score perfectly. That is the difference between "the model cannot learn this"
  and "the evaluation cannot measure this", and it is worth stating on stage:
  the honest reading of the old table was *unmeasurable*, not *broken*.
- **Both IsolationForest models are unfit as classifiers, and the sweep proves why.**
  They *do* detect every malicious row — but only at thresholds where they also
  fire on a large fraction of benign windows (`scan_iforest`: 19 benign FPs at
  0.9, 6.0% of holdout; `exfil_iforest`: 12 at 0.9, 2.2%). Tighten past that and
  they go completely blind. There is **no operating point that is simultaneously
  sensitive and within the 0.5% benign budget**, so the threshold selector
  correctly ships the quiet point (0.99 / 0.95) and reports recall 0.000 rather
  than hiding a noisy one. Unsupervised anomaly detection on this feature space
  does not separate malicious from merely-unusual benign traffic. The supervised
  models are the deployable ones; the IsolationForest pair are retained only
  as uncalibrated evidence on an alert from the matching supervised model.
  They never emit standalone alerts or probabilities. `score_scan` and
  `score_exfil` accept an optional `rule_corroborated=False` flag; when true,
  the raw `decision_function` score is attached to an existing supervised
  alert with `score_kind=uncalibrated_decision_function` and lower scores marked
  as more anomalous. The pipeline passes this flag only when the corresponding deterministic
  scan or exfil rule emitted an alert in the same window. Operator-authorised
  exfil alerts do not qualify.

The classifier sweep remains a negative result for the two IsolationForests.
Their serving role is now ranking evidence, with no extra alert or confidence
increase. This does not demonstrate improved detection or establish a useful
outlier threshold; those still need representative held-out traffic.

## Limitations

- The training data is the repository's synthetic capture, not a public enterprise dataset — the perfect numbers reflect clean synthetic separation and would not survive representative traffic.
- The packet CNN is a one-way outbound sequence model; return-side packet direction is unavailable by design.
- The TLS/QUIC model sees metadata only and never decrypts application payloads.
- XGBoost is an optional dependency (`uv sync --extra ml567`); scikit-learn and joblib are main dependencies.
- The supervised models (`encrypted_xgb`, `sequence_cnn`, `scan_rf`, `exfil_xgb`) validate at 1.000 recall / 0 benign FP on the temporal holdout. Both IsolationForest models remain measured negative results as classifiers: neither has an operating point that is sensitive and within the 0.5% benign budget. In serving, they provide uncalibrated anomaly evidence only when a supervised model alert exists and the caller passes deterministic rule corroboration. The pipeline requires same-window deterministic corroboration.
- The existing rule detectors remain important for transparent evidence and bounded streaming behavior.
