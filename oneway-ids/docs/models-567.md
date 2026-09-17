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

- cumulative bytes transferred to the source/destination pair
- current source volume baseline
- transfer-to-baseline ratio
- window index
- destination novelty flag

XGBoost provides a supervised exfiltration probability. Isolation Forest scores anomalous transfer behavior against normal traffic.

The model tier only evaluates a destination after it has been observed as novel and the cumulative transfer reaches `EXFIL_MIN_BYTES`. Pair-level model alerts are deduplicated.

## Training

Install the optional dependencies:

```bash
.venv/bin/pip install -r requirements-ml.txt
```

Generate or refresh the synthetic capture, then train:

```bash
.venv/bin/python gen_traffic.py
.venv/bin/python train_models_567.py --pcap traffic.pcap --out models567
```

Training uses the synthetic generator’s labels and a temporal split at 500 seconds. This keeps later traffic available for evaluation while ensuring category 7 has both benign and exfiltration examples in training.

## Artifacts and manifest

The trainer creates:

```text
models567/manifest.json
models567/encrypted_xgb.json
models567/scan_rf.joblib
models567/scan_iforest.joblib
models567/exfil_xgb.json
models567/exfil_iforest.joblib
models567/sequence_cnn.npz
```

The manifest maps model names to artifact paths. The runner loads it lazily:

```bash
.venv/bin/python run.py --models-567 models567/manifest.json
```

If the manifest is omitted, the optional category 5-7 tier is disabled. Rules-only operation does not require XGBoost or scikit-learn.

## Alert behavior

Model alerts use the standard JSONL schema and include the model name and feature vector in `evidence`. The model tier is a confirmer, not a replacement for the streaming rules:

- rule detectors provide low-latency candidate signals
- learned models add supervised or anomaly-based confirmation
- `FusionEngine` can correlate the resulting alerts with other threat classes
- model alerts are deduplicated per flow, scan window/source, or exfiltration pair

## Limitations

- The training data is the repository’s synthetic capture, not a public enterprise dataset.
- The packet CNN is a one-way outbound sequence model; return-side packet direction is unavailable by design.
- The TLS/QUIC model sees metadata only and never decrypts application payloads.
- XGBoost, scikit-learn, and joblib are optional dependencies.
- Model quality should be re-evaluated with representative captures before production use.
- The existing rule detectors remain important for transparent evidence and bounded streaming behavior.
