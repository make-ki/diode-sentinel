# HANDOFF for GPT Astra — Diode Sentinel

**Project:** Diode Sentinel — intrusion detection for strictly unidirectional
(one-way / data-diode) network traffic. SIH 2026 problem statement
**PS-26145** (NTRO), "AI-Based Detection of Cyber Threats in Unidirectional IP
Traffic". Repo root is `/home/stark/sih`, the project is the `oneway-ids/`
subdirectory. Branch: `integrate/models-567`.

**Deadline:** idea submission **30 September 2026**.

---

## What the user wants (read this first)

The user is "stark". Preferences learned across sessions:

- **Direct, no fluff.** Wants measured numbers with mandatory qualifiers, not
  adjectives. Asks "does it actually work?" — answer with data.
- **Honesty over hype, explicitly.** The project's biggest self-inflicted
  wound was a deck describing a stack that never existed. The user's own
  standing instruction is: do not reintroduce fictional technology, and if a
  measured number changes, regenerate the deck the same session.
- **Never claim "zero false positives."** The MESSY FP-pressure variant emits
  a critical `data_exfiltration` false positive at 0.95 on a benign
  cloud-backup host. That is the honest cost of a one-way exfil detector.
- **Do not present the ML tier as a robust primary tier.** It is quorum-gated;
  under FP pressure it emits ~74 alerts at confidence 1.0, almost all benign.
- **Do not claim IoT-23 reproducibility.** The numbers are real (measured on
  CTU data) but the scorer scripts lived only in `/tmp` (now gone) and the
  dataset is on an unmounted external drive.
- The user may ask you to "fake it till you make it" or to add impressive-sounding
  technology that is not built. This repo has been burned by exactly that. The
  user respects being told what is real and what is not — that is the whole
  pitch. Prefer building a small real thing over decorating a slide.

---

## The one-sentence pitch

> The statement doesn't ask for a threat detector — it asks for a threat
> detector inside a room with no door. Anyone can run an IDS on a mirror port;
> the difficulty is that we are forbidden from asking the network a single
> question.

The project's actual contribution is **the one-way observability contract**:
an enumeration of every feature PS-26145 requests, marking each OBSERVABLE,
IMPOSSIBLE or SUBSTITUTED on a directional feed. **Five of the problem
statement's own requested features are impossible under its own first
constraint** — JA3S, negotiated cipher + server certificate, round-trip time,
NXDOMAIN ratio, and the outbound-to-inbound byte ratio. That is a finding
about the problem, not a limitation of the code, and it is the deck's headline.

---

## Repo layout (post-refactor)

Entry points stay at the repo root of `oneway-ids/`; library code is packaged.

```
run.py                 end-to-end runner (--live, --parity, --ml, --state)
demo.sh                one-command demo; --fresh regenerates the capture
gen_traffic.py         synthetic one-way pcap (MESSY=1 = FP-pressure variant)
dashboard.py           stdlib SOC dashboard (port 8600)
build_deck.py          PRESENTATION.md -> ../Diode-Sentinel.pptx  (17 slides)
build_contract_image.py  core/observability.py -> contract.png
core/                  the pipeline: pcap_reader, live_source, pipeline,
                       detectors, tls_meta, quic_meta, ml_tier, dga_cnn,
                       observability, metrics, models_567, ...
training/              train_ml, train_dga_cnn, train_models_567, bench_dga
tests/                 10 suites, plain unittest, 336 checks, all green
models567/             shipped category 5-7 artifacts + manifest + eval.json
.regression/           byte-identical alert fixtures (the reproducibility claim)
PRESENTATION.md        the honest deck source (595 lines) -- source of truth
AGENTS.md              working guide + the "what is actually true" list
PS-26145.md            verbatim problem statement, for checking quotes
```

**Build/test commands** (NixOS: `source .env-ml` first, or numpy breaks):

```sh
source .env-ml
.venv/bin/python run.py --ml --dga-cnn --models-567 models567/manifest.json
.venv/bin/python run.py --parity          # dpkt vs scapy must be IDENTICAL
for t in tests/test_*.py; do .venv/bin/python "$t" || break; done
.venv/bin/python build_deck.py            # regenerate slides after any number change
```

---

## What is real and defensible

- **Observability contract** (`core/observability.py`): 21 features — 15
  OBSERVABLE, 5 IMPOSSIBLE, 1 SUBSTITUTED. Enforced by `tests/test_contract.py`,
  which greps detector source for forbidden bidirectional tokens (`ja3s`,
  `server_hello`, `rcode`, `nxdomain`, `ttl`, `rtt`, `bytes_in`, ...) and
  **fails the build** on a hit. Verified: injecting a `rcode` read makes it
  fail; removing it passes. The gate has teeth — it was re-tested after the
  refactor moved modules into `core/`.
- **Throughput:** rules tier ≈48.6k–50.4k pkt/s ≈240 Mbps on one core, pure
  Python, no C extension, no GPU. ML tier ≈24k–31k pkt/s (quoted as a range —
  it is not reproducible as a single number). Mean packet 613.7 B. Do NOT lead
  with "~2,000x real-time" — the capture is sparse (23 pkt/s ≈ 0.11 Mbps), so
  it is one measurement restated; quote it only as repeatability.
- **Reproducibility:** replay reproduces `alerts.jsonl` byte-for-byte against
  `.regression/` fixtures — **46 alerts rules-only, 68 with `--ml`** (the old
  docs said 45/67; corrected). `--parity` asserts dpkt and scapy produce
  identical alert distributions.
- **DGA char-CNN** (`core/dga_cnn.py`): numpy-only 1D conv, 4,930 params,
  analytic gradients match finite differences to 7e-09. Family-held-out: CNN
  1.000 vs rules 0.473 recall on an unseen family, benign FP 0.001 vs 0.003.
  On the external `andrewaeva/DGA` corpus (694k DGA / 1M Alexa) it recovers
  conficker 0.019→0.886 and pushdo 0.000→0.446 where the entropy gate's
  10-char floor blinds it.
- **The quorum is a measured constant.** The CNN alone is not deployable
  (16.5% per-string FP on 1M benign domains). Swept: 17.3 alerts/hour benign
  at k=2 vs 0.46 at k=4 with 7/8 families still detected. Shipped default is
  k=4. **The famous "CNN caught a real DGA query the rules called benign"
  line does NOT fire at the shipped quorum** — quote it as a benchmark
  measurement, never as a live alert.
- **QUIC:** Initial packets are decryptable with no secret (RFC 9001 public
  salt + DCID), so a real JA4 comes out of QUIC on a one-way feed.
  `tests/test_quic.py` proves it byte-identical to the direct TLS parse, and
  a GCM-tampered packet is rejected rather than mis-fingerprinted.
- **IoT-23 validation** (real, but NOT repo-reproducible): per-host scoring
  — Capture-8-1 Hakai 1.000 recall/precision; Capture-1-1 HideNSeek 1.000
  (flagged the infected host, 0 clean FPs); Capture-42-1 Trojan **0.000, a
  total honest miss**; Honeypot-4-1 benign Philips HUE **0.000 precision, a
  real structural FP** (cloud telemetry looks exactly like beaconing one-way).

## What is NOT true — do not put it on a slide

- **"Zero false positives"** — see MESSY above.
- **Zeek / Suricata** — neither is installed, in `flake.nix`, or invoked
  anywhere. The sensor is pure Python. `ZEEK-ONEWAY-FINDINGS.md` records an
  offline Zeek experiment; the shim was never committed. Do not add a Zeek
  build step.
- **Kafka / Flink / ClickHouse / React / ONNX / K8s / Terraform** — none of it
  exists. This was the fictional stack that contaminated the old `.pptx`.
- **`--models-567` as six working models** — it is **four working**
  (`encrypted_xgb`, `sequence_cnn`, `scan_rf`, `exfil_xgb`, all recall 1.000
  at 0 benign FP, temporal split t≥390) **plus two honest failures** (both
  IsolationForests at 0.000 — no operating point is both sensitive and within
  the 0.5% benign budget; a measured negative result, not a tuning bug).
- **MITRE technique IDs** — the alert schema has no such field.
- **"7/7 threat classes"** — the PS names six.

---

## Load-bearing gotchas

1. **`alerts.jsonl` is overwritten by every `run.py` invocation.** Score it
   immediately after a run, or the results are from the wrong scenario.
2. **The contract gate must fail loudly.** `tests/test_contract.py` lists
   modules in `GATED_MODULES` under `core/`. If a module is missing the test
   now fails rather than passing vacuously — a silent pass would disable the
   project's headline claim.
3. **`config.PROJECT_DIR` is `dirname(dirname(__file__))`** so artifact and
   static-asset paths resolve from `core/`. Do not "simplify" this.
4. **The `.pptx` is generated, never hand-edited.** If any measured number
   changes, run `build_deck.py` the same session. That is how the fictional
   stack survived audit for 15 days.
5. Regression fixtures are the reproducibility claim — any detector or
   generator change must keep them byte-identical or be explicitly regenerated.
6. The DGA benchmark needs the external `andrewaeva/DGA` corpus; don't assume
   network access in the enclave.

## Open opportunities (if time allows, in priority order)

1. **Make IoT-23 reproducible.** Re-mount the external drive
   (`udisksctl mount -b /dev/sda1`), re-write the per-host scorer as a
   committed script, and the strongest external validation becomes
   re-runnable. Highest value: it removes the one asterisk from the best
   result.
2. **Test the AF_PACKET socket** against a real interface — it is the only
   unexercised piece of the live driver (the dev container has `CapBnd: 0`).
3. Port the DGA CNN to torch/CUDA if GPU training is wanted (laptop has an
   RTX 3050; `_xgb_device()` in `training/train_models_567.py` probes CUDA).
