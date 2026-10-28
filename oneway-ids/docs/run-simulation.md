# Running the Simulation

This guide runs the synthetic one-way traffic generator, replays the capture through the IDS, optionally trains the ML tiers, and starts the dashboard. All commands use the existing entry points; no service-stack deployment is required.

[Project overview](../../README.md) · [Prototype reference](../README.md) · [Demo lifecycle](demo.md)

## Fastest path: live synthetic dashboard

Prerequisites: **Linux**, **Python 3.14+**, **uv**, and **Bash 5.1+** for the demo script. From the repository root:

```bash
cd oneway-ids
uv sync --locked
./demo.sh
```

Open **http://localhost:8600**. The script uses fresh temporary capture/alert files, starts the dashboard first, then streams 600 seconds of synthetic traffic at 10× speed with rules and the shipped DGA CNN. The completed view remains open until **Ctrl+C**, which stops the children and removes the temporary files. No training, raw-socket privileges, GPU, Node.js, or Docker is needed.

Use `./demo.sh --speed=25` for a shorter replay, or `./demo.sh --port=8601` if port 8600 is busy. On NixOS, run `nix develop` before `uv sync --locked`; without flakes, use `source .env-ml` before manual Python commands. Other Linux distributions do not need this loader setup.

The manual workflow below keeps generated files in the project directory for inspection.

## 1. Enter the project

```bash
cd oneway-ids
```

This path is relative to the repository root. From outside a fresh clone, use `cd diode-sentinel/oneway-ids` instead.

## 2. Create the virtual environment

Run this once on a fresh checkout (see the README's "Reproducing the
environment" for the NixOS `nix develop` variant):

```bash
uv sync --locked
```

Every command below uses the project interpreter via `uv run`, so the required
packages are found consistently. Dependencies are pinned in `pyproject.toml`
and `uv.lock`; installation needs internet access or an available offline
package cache. Model weights are committed, so training is optional. Add
`uv sync --locked --extra ml567` when using the specialist bundle; the demo,
rules, DGA CNN, and LightGBM paths do not need that extra.

## 3. Generate synthetic traffic

```bash
uv run python gen_traffic.py
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
MESSY=1 uv run python gen_traffic.py
```

## 4. Run the rules and existing metadata detectors

```bash
uv run python run.py
```

The report includes packet and flow counts, processing rate, alert counts, and alert classes. Alerts are written to `alerts.jsonl`; dashboard statistics are written to `run_stats.json`.

Useful variants:

```bash
uv run python run.py --parity
uv run python run.py --ml
uv run python run.py --dga-cnn
```

`--parity` compares the dpkt and scapy readers. `--ml` enables the existing LightGBM flow scorer. `--dga-cnn` enables the DNS character CNN and requires `model_dga_cnn.npz`.

For independent repeated replays, add `--no-state`. By default, `nids_state.json` preserves fingerprint inventory and incident deduplication clocks, so replaying the same timeline against saved state can suppress alerts from earlier runs. The demo already disables persistent state.

These options enable experimental learned tiers; synthetic output counts are not measures of real-world accuracy. See [ML replay findings](ml-replay.md) and [specialist model evaluation](models-567.md).

## 5. Optional: train the category 5-7 models

The shipped bundle can be used without retraining. To regenerate it:

```bash
uv sync --locked --extra ml567
uv run python training/train_models_567.py --pcap traffic.pcap --out models567
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

The shipped artifacts are tracked despite ignore patterns for generated model files. Training overwrites the corresponding artifacts and `eval.json`; it is not a prerequisite for running them. The training script uses a temporal split and keeps attack examples on both sides so the holdout can evaluate each category.

The other optional trainers are also under `training/`:

```bash
uv run python training/train_ml.py
uv run python training/train_dga_cnn.py
```

## 6. Run all category 5-7 models

```bash
uv sync --locked --extra ml567
uv run python run.py --models-567 models567/manifest.json
```

The model tier is optional. Without this flag, the rules and existing LightGBM/DGA CNN paths continue to work unchanged.

Model alerts are intentionally gated by the existing rules:

- scan models evaluate sources with scan-sized fan-out
- exfiltration models evaluate novel destinations after the byte threshold
- repeated model alerts are deduplicated

## 7. Run the tests

Focused model and detector tests:

```bash
uv run python tests/test_models_567.py
uv run python tests/test_fusion.py
uv run python tests/test_tls_meta.py
uv run python tests/test_quic.py
```

Live-path regression tests:

```bash
uv run python tests/test_live.py
```

The live test uses injected/FIFO sources for most coverage and does not require raw-socket privileges.

To verify the paced demo itself, including mid-replay alerts and Ctrl+C cleanup:

```bash
DIODESENTINEL_DEMO_SMOKE=1 uv run python tests/test_demo_smoke.py
```

The suite uses Python `unittest`, not pytest. The documented historical `.regression` fixtures have a known single-alert QUIC migration difference from the later archived capture; backend parity is a separate check. See the [latest handoff](../HANDOFF.md).

## 8. Start the dashboard

In a separate terminal, after a replay or live run:

```bash
cd oneway-ids                         # from the repository root
uv run python dashboard.py
```

Open `http://127.0.0.1:8600`.

The dashboard uses Python's standard library and locally vendored assets. It is independent of the Remotion video project and needs no `npm install` or frontend build. For another port, use `uv run python dashboard.py 8601`.

## 9. Live capture options

Direct capture requires the appropriate Linux capability:

```bash
uv run python run.py --list-interfaces
sudo .venv/bin/python run.py --live eth0
sudo .venv/bin/python run.py --live eth0 --sample 4 --duration 300
```

Replace `eth0` with the explicitly selected diode receive-side or test interface. Real-interface AF_PACKET validation remains outstanding; automated tests exercise injected and FIFO sources. Live capture requires Linux `CAP_NET_RAW` or equivalent privileges. Install dependencies as your normal user before invoking the existing virtual-environment interpreter with `sudo`.

A lower-privilege pipe workflow uses a capture helper:

```bash
mkfifo /tmp/nids.pcap
dumpcap -i eth0 -P -U -w /tmp/nids.pcap &
uv run python run.py --pipe /tmp/nids.pcap
```

The same model bundle can be enabled for live capture:

```bash
sudo .venv/bin/python run.py --live eth0 --models-567 models567/manifest.json
```

## 10. Optional: Prometheus + Grafana

Expose the sensor's internals as metrics and get the provisioned Grafana
dashboard + alert rules (needs Docker; full details in
[monitoring.md](monitoring.md)):

```bash
uv run python run.py --metrics-port 9100          # sensor + /metrics
```

In another terminal, from `oneway-ids/`:

```bash
docker compose -f monitoring/docker-compose.yml up -d
```

Grafana: <http://localhost:3000> (admin / admin) -- the "NIDS Overview"
dashboard is loaded automatically. Works for live capture and replay alike;
see [monitoring.md](monitoring.md) for remote/multiple sensors. The exporter lives only while the sensor process runs, so a short offline replay may finish before Prometheus scrapes it. Use a running live/stream workflow for continuous monitoring. This stack monitors sensor metrics; it is not a ClickHouse alert-history backend.

## Troubleshooting

### Missing virtual environment or unsupported Python

Run from `oneway-ids/` and check the interpreter requirement:

```bash
python3 --version
uv sync --locked
```

The project requires Python 3.14+. Its uv configuration prefers a system interpreter. If your Linux distribution has an older Python, install a compatible interpreter, or explicitly select uv's managed interpreter on a standard Linux distribution:

```bash
uv python install 3.14
uv sync --locked --python 3.14 --managed-python
```

On NixOS, use the provided `nix develop` environment instead. Do not change `requires-python`, dependency pins, or the lockfile to follow this guide.

### `libstdc++.so.6` or another native library is missing

On NixOS use `nix develop`, or `source .env-ml`. On other distributions, provide the runtime library named in the import error using the distribution's packages. The shipped Python wheel dependencies include native components even though the sensor pipeline itself is Python.

### The demo exits because port 8600 is in use

Use `./demo.sh --port=8601` and open `http://localhost:8601`. The script checks the port before starting child processes.

### Missing XGBoost or scikit-learn

Install the optional model dependency (scikit-learn is already a main
dependency; this adds XGBoost only):

```bash
uv sync --locked --extra ml567
```

### Model manifest cannot be loaded

Run from `oneway-ids/`, ensure the optional extra is installed, and use `models567/manifest.json`; the manifest contains paths relative to that directory. If artifacts are missing, generate `traffic.pcap`, then retrain:

```bash
uv sync --locked --extra ml567
uv run python gen_traffic.py
uv run python training/train_models_567.py --out models567
uv run python run.py --models-567 models567/manifest.json
```

### Reset generated output

The generator and runner overwrite the primary simulation outputs:

```bash
uv run python gen_traffic.py
uv run python run.py
```
