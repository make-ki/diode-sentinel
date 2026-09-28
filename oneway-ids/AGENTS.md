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
  reproducibility claim. They were regenerated against the post-realism
  generator and re-verified byte-identical for both tiers (45 rules / 67 ML);
  the earlier staleness is resolved. Re-verify after any detector or generator
  change.

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

- Throughput, re-measured over repeated runs on one core: rules tier
  ~48.6k pkt/s (47.9k-49.0k, tight) ~= 205 Mbps; ML tier 23k-31k pkt/s
  (quoted as a range -- it is not reproducible as a single number); 2,377x
  real-time on the sparse synthetic capture. Mean packet 527.3 B.
- dpkt and scapy backends produce byte-identical alert distributions.
- The DGA char-CNN is a genuine numpy `conv1d` whose analytic gradients match
  finite differences to 7e-09. Family-held-out evaluation against a real
  694k-domain corpus. This is the strongest ML artifact in the repo.
- Zeek 7.2.2 correctly parses a TLS ClientHello from a strictly one-direction
  capture, including with the SYN present. Verified on real OpenSSL traffic.
- **The one-way observability contract is the project's real contribution.**
  `observability.py` enumerates every feature PS-26145 names and states
  whether it is `OBSERVABLE`, `IMPOSSIBLE`, or `SUBSTITUTED` on a directional
  feed. 21 features: 15 observable, 5 structurally impossible (JA3S, negotiated
  cipher, server certificate, RTT, NXDOMAIN ratio, in/out byte ratio), 1
  substituted. `test_contract.py` is the gate: it fails the build if a
  detector reads a forbidden bidirectional field. Five of the PS's own
  requested features are unsatisfiable under the PS's own constraint (a) --
  that finding is the deck's headline, not a config trick.

Results that are NOT true — do not put them on a slide:

- **"Zero false positives"** — false. The MESSY run emits a critical
  `data_exfiltration` FP at 0.95 on the benign cloud-backup host (10.0.0.6).
  Verified: regenerating with `MESSY=1` and running rules-only puts exactly one
  critical FP plus one medium `tls_novel_fingerprint` on designated-benign
  hosts. The rules FP is the honest cost of a one-way exfil detector.
- **The ML tier collapses under FP pressure** — also verified. On the same
  MESSY capture `--ml` adds ~74 `ml_flow_suspicious` alerts at confidence 1.0,
  almost all on benign hosts (IoT telemetry, backup, ordinary browsing). The
  supervised flow model does not generalise to benign traffic shapes absent
  from its training capture. Never present `--ml` as a robust primary tier;
  it is quorum-gated for this reason.
- **`--models-567` is not a headline** — `models567/eval.json`: `encrypted_xgb`
  and `sequence_cnn` reach recall 1.000 at 0 FP, but `scan_rf`/`scan_iforest`
  have zero malicious holdout examples (untestable) and `exfil_xgb`/
  `exfil_iforest` miss all 4 malicious windows (recall 0.000).
- **"7 / 7 threat classes"** — the PS names six. The seventh conflates the
  fusion layer with a detector.
- **DNS tunnelling detection** — **now exists** (`DGADetector._tunnel_check`).
  Uses qtype anomaly, query length and max label length; all three are written
  by the client into the query, so all are one-way observable. The previous
  note here ("does not exist, and the dashboard labels the class as though it
  does") is superseded as of the qtype plumbing through `pcap_reader.py`,
  `live_source.py` and `pipeline.py`. The old gap is closed, do not report it
  as open.
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
