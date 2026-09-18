# Category 5-7 Models

This document describes the optional learned model tier added for the three requested threat categories. The existing rule detectors remain enabled because they provide the fast, explainable first signal.

## Overview

| Category | Model | Input | Output |
|---|---|---|---|
| 5. Malware in encrypted sessions | NumPy 1D CNN + XGBoost | packet sizes, timing, one-way direction, TLS/QUIC metadata | `encrypted_session_malware` |
| 6. Reconnaissance / port scanning | Random Forest + Isolation Forest | per-source destination/port fan-out | `recon_model_scan` |
| 7. Data exfiltration | XGBoost + Isolation Forest | transfer volume, source baseline, destination novelty | `data_exfiltration_model` |

The models are served by `models_567.py` and integrated at flow-close and window-flush points in `pipeline.py`.

## Category 5: encrypted sessions

### Packet-sequence CNN

`packet_sequence_cnn.py` converts each closed flow into a compact token sequence:

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
uv run python train_models_567.py --pcap traffic.pcap --out models567
```

Training uses the synthetic generator's labels and a temporal split at 500
seconds. This keeps later traffic available for evaluation while ensuring
category 7 has both benign and exfiltration examples in training.

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

The numbers below are the trainer's own temporal-holdout evaluation (`t >= 500s`)
on the shipped capture, reproduced by `train_models_567.py`. `models567/eval.json`
is the machine-readable original, including the full threshold sweep per model.
The raw model is scored over **every** held-out flow and window — not just the
rule-gated subsets the server sees — so the benign FP pressure here
upper-bounds the deployed tier.

| Model | Holdout | Malicious | Threshold | Recall | Precision | Benign FP |
|---|---|---|---|---|---|---|
| `encrypted_xgb` | 262 | 23 | 0.50 | **1.000** | **1.000** | 0 (0.0%) |
| `sequence_cnn` | 262 | 23 | 0.50 | **1.000** | **1.000** | 0 (0.0%) |
| `scan_rf` | 144 | **0** | 0.80 | — | — | 0 (0.0%) |
| `scan_iforest` | 144 | **0** | 0.80 | — | — | **46 (31.9%)** |
| `exfil_xgb` | 252 | 4 | 0.50 | **0.000** | — | 0 (0.0%) |
| `exfil_iforest` | 252 | 4 | 0.95 | **0.000** | — | 0 (0.0%) |

**Read this table before presenting the tier.** It is not uniformly good news,
and saying otherwise on stage is the one thing a judge can check:

- **Category 5 (encrypted sessions) is genuinely strong.** Both models reach
  1.000 recall at 1.000 precision with zero benign false positives on 239
  held-out benign flows — including 23 malicious flows they never trained on.
  This is the tier's defensible result.
- **Category 6 (recon) is unmeasurable on this capture, and one of its models
  is noisy.** The temporal split at t=500 puts *all* scanning activity in the
  training window, so the holdout contains zero malicious scan cases — the
  supervised model's recall is undefined, not 1.000. Worse, `scan_iforest`
  fires on **31.9% of benign windows** even with no positives to find. The
  sweep ships 0.8 for both, but the honest statement is that this capture
  cannot validate category 6 and the anomaly model has an unsolved
  false-positive problem.
- **Category 7 (exfil) fails the holdout.** `exfil_xgb` detects **none** of the
  4 held-out exfiltration events at *any* threshold in the sweep. `exfil_iforest`
  does detect all four — but only at thresholds ≤ 0.9, where its benign FP rate
  exceeds the 0.5% budget; at the quiet shipped point (0.95) it is blind. No
  operating point on this capture is simultaneously sensitive and quiet.
  The rule `ExfilDetector` remains the deployable category-7 detector.

Consequently the category 6 and 7 models are **shipped as measured-but-not-
deployable**: they load and score, but the evidence above is what a judge
should be shown, not a claim that they work. Making them good is open work —
the plausible route is a capture where each attack class spans the temporal
split (so the holdout actually contains positives), plus per-source baseline
weighting for the anomaly models.

## Limitations

- The training data is the repository's synthetic capture, not a public enterprise dataset — the perfect category-5 numbers reflect clean synthetic separation and would not survive representative traffic.
- The packet CNN is a one-way outbound sequence model; return-side packet direction is unavailable by design.
- The TLS/QUIC model sees metadata only and never decrypts application payloads.
- XGBoost is an optional dependency (`uv sync --extra ml567`); scikit-learn and joblib are main dependencies.
- Categories 6 and 7 are measured but **not deployable** on the shipped capture (see "Measured holdout results"): category 6 has no malicious holdout examples and a 31.9%-benign-FP anomaly model; category 7's supervised model has 0 holdout recall. The rule detectors remain the deployable detectors for those classes.
- The existing rule detectors remain important for transparent evidence and bounded streaming behavior.
