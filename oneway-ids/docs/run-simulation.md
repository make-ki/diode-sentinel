# Running the Simulation

This guide runs the synthetic one-way traffic generator, replays the capture through the IDS, trains the optional ML tiers, and runs the dashboard.

## 1. Enter the project

```bash
cd diode-ids/oneway-ids
```

## 2. Create the virtual environment

Run this once on a fresh checkout:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install scapy dpkt lightgbm cryptography
.venv/bin/pip install -r requirements-ml.txt
```

The first command creates `.venv`. Every command below uses the virtual-environment interpreter, so the required packages are found consistently.

## 3. Generate synthetic traffic

```bash
.venv/bin/python gen_traffic.py
```

This writes `traffic.pcap`. The generator includes benign traffic and these scenarios:

- spoofed SYN flood
- periodic C2 beaconing
- DGA DNS queries
- TLS and QUIC encrypted-session malware
- vertical port scanning
- data exfiltration to a novel destination

For the false-positive pressure variant:

```bash
MESSY=1 .venv/bin/python gen_traffic.py
```

## 4. Run the rules and existing metadata detectors

```bash
.venv/bin/python run.py
```

The report includes packet and flow counts, processing rate, alert counts, and alert classes. Alerts are written to `alerts.jsonl`; dashboard statistics are written to `run_stats.json`.

Useful variants:

```bash
.venv/bin/python run.py --parity
.venv/bin/python run.py --ml
.venv/bin/python run.py --dga-cnn
```

`--parity` compares the dpkt and scapy readers. `--ml` enables the existing LightGBM flow scorer. `--dga-cnn` enables the DNS character CNN and requires `model_dga_cnn.npz`.

## 5. Train the category 5-7 models

```bash
.venv/bin/python train_models_567.py
```

The command reads `traffic.pcap` and creates:

```text
models567/
  encrypted_xgb.json
  scan_rf.joblib
  scan_iforest.joblib
  exfil_xgb.json
  exfil_iforest.joblib
  sequence_cnn.npz
  manifest.json
```

The generated directory is ignored by git. The training script uses a temporal split and keeps part of the generated exfiltration period in training so the category-7 classifiers contain both classes.

## 6. Run all category 5-7 models

```bash
.venv/bin/python run.py --models-567 models567/manifest.json
```

The model tier is optional. Without this flag, the rules and existing LightGBM/DGA CNN paths continue to work unchanged.

Model alerts are intentionally gated by the existing rules:

- scan models evaluate sources with scan-sized fan-out
- exfiltration models evaluate novel destinations after the byte threshold
- repeated model alerts are deduplicated

## 7. Run the tests

Focused model and detector tests:

```bash
.venv/bin/python test_models_567.py
.venv/bin/python test_fusion.py
.venv/bin/python test_tls_meta.py
.venv/bin/python test_quic.py
```

Live-path regression tests:

```bash
.venv/bin/python test_live.py
```

The live test uses injected/FIFO sources for most coverage and does not require raw-socket privileges.

## 8. Start the dashboard

In a separate terminal, after a replay or live run:

```bash
cd diode-ids/oneway-ids
.venv/bin/python dashboard.py
```

Open `http://127.0.0.1:8600`.

## 9. Live capture options

Direct capture requires the appropriate Linux capability:

```bash
sudo .venv/bin/python run.py --live eth0
sudo .venv/bin/python run.py --live eth0 --sample 4 --duration 300
```

A lower-privilege pipe workflow uses a capture helper:

```bash
mkfifo /tmp/nids.pcap
dumpcap -i eth0 -P -U -w /tmp/nids.pcap &
.venv/bin/python run.py --pipe /tmp/nids.pcap
```

The same model bundle can be enabled for live capture:

```bash
.venv/bin/python run.py --live eth0 --models-567 models567/manifest.json
```

## Troubleshooting

### `.venv/bin/python: No such file or directory`

The virtual environment has not been created. Run:

```bash
python3 -m venv .venv
```

Then install the dependencies from step 2.

### Missing XGBoost or scikit-learn

Install the optional model dependencies:

```bash
.venv/bin/pip install -r requirements-ml.txt
```

### Model manifest cannot be loaded

Retrain the artifacts and use the generated manifest path:

```bash
.venv/bin/python train_models_567.py --out models567
.venv/bin/python run.py --models-567 models567/manifest.json
```

### Reset generated output

The generator and runner overwrite the primary simulation outputs:

```bash
.venv/bin/python gen_traffic.py
.venv/bin/python run.py
```
