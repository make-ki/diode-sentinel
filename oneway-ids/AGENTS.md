# AGENTS.md

Guidance for AI coding agents working in this repository. Per the
[agents.md](https://agents.md) convention there is no formal schema; the
nearest `AGENTS.md` to a file wins, and explicit user instruction overrides
everything. Keep this file short — bloated instruction files get ignored.

## Project overview

**Diode Sentinel** — intrusion detection for *strictly unidirectional* network
traffic: the receive side of a hardware data diode. The sensor sees one
direction of every conversation. There are no replies, no handshakes, no
FIN/RST from the far end, and no decryption of payload content.

The problem statement is SIH 2026 **PS-26145** (NTRO), "AI-Based Detection of
Cyber Threats in Unidirectional IP Traffic". Deadline for idea submission is
**30 September 2026**.

The core constraint shapes every detector: anything that requires a response
is unavailable. JA3S, server certificates, negotiated ciphers, RTT, DNS reply
codes (NXDOMAIN ratio) and in/out byte ratio are *structurally unobservable*,
not merely hard. Do not add a detector that depends on them.

## Build and test commands

```sh
# NixOS: get libstdc++/zlib onto the loader path FIRST, or numpy breaks.
source .env-ml

# Generate the synthetic diode capture.
.venv/bin/python gen_traffic.py            # -> traffic.pcap (12k pkts, 600s)
MESSY=1 .venv/bin/python gen_traffic.py    # FP-pressure variant

# Run the pipeline.
.venv/bin/python run.py                    # rules only
.venv/bin/python run.py --ml               # + LightGBM tier
.venv/bin/python run.py --parity           # dpkt vs scapy must agree byte-for-byte
.venv/bin/python run.py --models-567 models567/manifest.json

# Zeek dissection layer (Tier-1).
zeek -r traffic.pcap local zeek/oneway.zeek

# Tests are plain unittest scripts. There is NO pytest dependency.
for t in test_*.py; do .venv/bin/python "$t" || break; done
```

Environment: `uv sync` reproduces `.venv` from `uv.lock`; `nix develop` gives
the same plus the loader-path shim. `python-preference = "system"` in
`pyproject.toml` is a NixOS workaround — on other distros you may need to
relax `requires-python`.

## Code style

- Pure Python, no C extensions, no CGO. The whole point is that it deploys
  inside an air-gapped enclave with no toolchain.
- **No GPU, no deep learning.** LightGBM/XGBoost/sklearn and a ~5k-parameter
  numpy char-CNN are the ceiling. They train in seconds on CPU. Do not reach
  for torch/transformers/VAEs — the deck's claims about them were fiction and
  the laptop cannot validate them anyway.
- Every detector must state, in a docstring, which features it consumes and
  confirm they are one-way observable.
- Thresholds carry a comment explaining *why*, not just what. Unexplained
  magic numbers are the smell that made the scan detector look like a toy.

## Testing instructions

- Write a test for a behaviour, not for an implementation detail. The worst
  bug in this repo was `test_metrics.py` asserting on evidence keys the
  pipeline never emits — a test that validated a mock.
- Regression gates: `.regression/alerts_rules.reference.jsonl` and
  `alerts_ml.reference.jsonl` must stay **byte-identical**. They are the
  reproducibility claim.
- The generator change in this session altered packet counts; those reference
  files are now stale and must be regenerated before any claim is repeated.

## Security considerations

- `nids_state.json` and `alerts.jsonl` are *outputs*. They previously leaked a
  real LAN host's JA4 inventory and 354 rows of private traffic. They are
  gitignored now; do not un-ignore them casually.
- `ALLOWLIST` in `config.py` is operator-curated. It currently contains the
  same three telemetry IPs the generator emits, which makes "zero false
  positives after allowlisting" circular. Do not present that as a result.
- Never point the AF_PACKET source at a production interface without
  explicit intent. It is read-only, but treat captures as sensitive.

## What is actually true (read before quoting any number)

Results that are real and defensible:

- ~44k pkt/s rules-only on one core, ~24k with the ML tier; 2,113x real-time.
- dpkt and scapy backends produce byte-identical alert distributions.
- The DGA char-CNN is a genuine numpy `conv1d` whose analytic gradients match
  finite differences to 7e-09. Family-held-out evaluation against a real
  694k-domain corpus. This is the strongest ML artifact in the repo.
- Zeek 7.2.2 correctly parses a TLS ClientHello from a strictly one-direction
  capture, including with the SYN present. Verified on real OpenSSL traffic.

Results that are NOT true — do not put them on a slide:

- **"Zero false positives"** — false. The MESSY run emits a critical
  `data_exfiltration` FP at 0.95 on the benign cloud-backup host.
- **"7 / 7 threat classes"** — the PS names six. The seventh conflates the
  fusion layer with a detector.
- **DNS tunnelling detection** — does not exist. There is no `qtype` parsing
  anywhere, and the dashboard labels the class as though it does.
- **MITRE technique IDs** — the deck promises them four times; the alert
  schema has no such field.
- **The 13 public datasets on slide 16** — none were used. Only
  `andrewaeva/DGA` + Alexa top-1M. Everything else is `gen_traffic.py`.
- **Kafka/Flink/ClickHouse/React/ONNX/K8s/Terraform stack** — none of it
  exists. The deck described a different project.
- **"Zeek cannot work one-way, we fixed it"** — my own testing disproved this.
  Vanilla Zeek works once the traffic generator emits realistic TCP.
  `ZEEK-ONEWAY-FINDINGS.md` records the measurement.

## How to work here

- Read `ZEEK-ONEWAY-FINDINGS.md` before touching Zeek or the generator. It
  records three days of wrong hypotheses so you do not repeat them.
- The single most valuable unclaimed asset is the **IoT-23 validation** in
  `HANDOFF.md` at the repo root: real CTU captures, real Zeek ground truth,
  including an honest miss and a genuine one-way false positive. Nothing in
  the deck uses it.
- When a hypothesis fails, record *why* before moving on. The findings file
  exists because negative results were getting lost.
- Do not trust markdown claims in this repo — verify against the code. The
  docs have several times drifted from the implementation.
