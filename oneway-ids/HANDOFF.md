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

### The user's standing instruction: fake it till you make it

> "Fake it till you make it. If you can't build it, fake it. Don't accept
> flaws — give a possible solution."

This is the operative instruction and it is meant literally. It is NOT a
licence to fabricate measured results (the user's honesty rules above still
bind). It means:

1. **If a feature cannot be built in the time, build a faithful simulation of
   it** and say plainly that it is a simulation. A synthetic DNS tunnel is a
   simulation; a made-up benchmark number is a lie. The first is how this
   repo got its DNS-tunnelling detection; the second is how it got a fictional
   stack. Keep doing the first.
2. **Never stop at "this is flawed."** Every flaw must ship with a concrete
   possible solution — a design, a substitute signal, a roadmap line. A
   documented flaw with no proposed remedy reads as a dead end; the same flaw
   with a credible workaround reads as engineering judgement. That is the
   standard the user holds.
3. **Where the problem statement asks for something structurally impossible,
   substitute a one-way proxy and put the arithmetic on the alert.** This is
   the project's central move and it is a species of faking-it-done-right: the
   requested signal is faked by the closest observable one, and the fake is
   labelled rather than disguised.

In short: build the real thing where you can, simulate where you can't, label
which is which, and always hand the user a way forward instead of a shrug.

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

## Known flaws, each with its solution

Per the standing instruction: never stop at a flaw, ship the remedy with it.

**Grounding for these remedies** (verified against the code, so the next agent
knows what is config-level vs. new work):
`ALLOWLIST` already exists in `core/config.py` (#1 extends it);
`ExfilDetector` already computes `novel_dsts` and `src_baseline_bytes_median`
(#1 and #2 build on existing fields); the `confirmed_c2_implant` fusion pair
already exists in `core/detectors.py` (#3 just needs a reputation input to
triage it); there is **no** cloud-CIDR or ASN list anywhere in `core/` today,
so #3's reputation tiering is genuinely new work.

### 1. Critical FP on the MESSY variant — `data_exfiltration` 0.95 on a benign backup host
**Flaw:** "large sustained upload to a first-seen destination" is exactly what a
cloud backup looks like, so the exfil detector fires on 10.0.0.6.
**Why it cannot be fully solved:** one-way, we cannot ask "was that
authorised?". There is no denominator.
**Solution (buildable):** an **authorised-destination registry** — an
operator-curated list of sanctioned backup endpoints (S3/GCS/Azure ranges plus
per-host baselines), the same artifact `ALLOWLIST` already is, extended to
carry port and volume class. A first-seen destination that resolves into a known
cloud-backup ASN drops to `medium` and carries `authorised_destination: true`
rather than being suppressed outright. This is the one-way substitute for
missing authorisation, and it is the honest answer: the residual FP is
structural, the operator-managed part is not.

### 2. Total miss on IoT-23 Capture-42-1 (Trojan) — 0 alerts
**Flaw:** six malicious C&C-FileDownload flows, zero alerts. The traffic tripped
no one-way signal we compute.
**Why:** the Trojan is not beaconing (no low-jitter periodicity) and its
download is to a *known* destination, so both the beacon and exfil detectors
stay quiet.
**Solution (buildable):** **transfer-without-relationship** — C&C-FileDownload is
a file transfer with no prior flow history to that destination, which is the
mirror image of the current exfil rule. Score "new destination + established
session + high byte volume" as its own detector, and fuse it with the
encrypted-session tier. This is exactly the kind of gap the contract predicts
exists: the feature is observable, we simply had not written the consumer yet.

### 3. Structural FP on IoT-23 — benign Philips HUE fires as C2 beaconing
**Flaw:** low-jitter periodic traffic to Google/AWS looks precisely like
beaconing, one-way.
**Why structural:** periodicity is the only C2 signal that survives one-way, and
cloud telemetry is legitimately periodic. The two are information-theoretically
indistinguishable without a reputation lookup.
**Solution (buildable):** **destination reputation tiering** — resolve
destination IPs offline against a bundled cloud-provider CIDR list and demote
"periodic traffic to a hyperscaler ASN" below "periodic traffic to a long-tail
IP", without suppressing it. Plus JA4 corroboration: real C2 stacks are
distinctive, HUE's is a stock ARM/uClibc stack. Fusing "periodic + distinctive
stack" is the existing `confirmed_c2_implant` path and would have caught the
HUE case as low-confidence.

### 4. `--models-567`: two IsolationForests report recall 0.000
**Flaw:** no threshold is both sensitive and within the 0.5% benign budget.
**Why:** unsupervised scoring has no negative class to anchor it; at any
detecting threshold it fires on 2–6% of benign windows.
**Solution (buildable, and preferred):** **stop using them as classifiers, use
them as triage.** Point-score benign windows, keep the *relative* ordering, and
alert only when an IsolationForest score is an extreme outlier *and* a
deterministic rule also fired. That converts an unusable 0.000-recall model into
a corroborating signal with no FP cost, which is how the repo already treats
the DGA CNN (quorum-gated, never critical).

### 5. ML tier collapses under FP pressure — 74 alerts at confidence 1.0 on benign hosts
**Flaw:** the flow model never saw benign IoT-telemetry, backup or browsing
shapes in training.
**Why:** the training capture is synthetic and narrow.
**Solution (buildable):** **benign-replay fine-tuning** — add the MESSY benign
patterns to the training capture, retrain on a temporal split that holds them
out, and measure. This is the one fix that converts the negative result into a
measured one either way. Second-line solution, already shipped: the quorum gate
and the tier boundary that excludes bare SYNs (3,021 → 20 alerts).

### 6. CNN demo line does not fire at the shipped quorum (k=4)
**Flaw:** the memorable "CNN caught a real DGA query the rules missed" alert is
silenced by the quorum that keeps benign hosts at 0.46 alerts/hour.
**Solution:** present it as what it is — a **benchmark** result on 694k external
domains (conficker 0.019→0.886). If a live demo of it is wanted, run with
`cnn_min_streak=2` *for the demo only* and say the shipped default is 4. Never
silently change the default for a nicer screenshot.

### 7. AF_PACKET socket is the one untested live component
**Flaw:** dev container has `CapBnd: 0`, so no raw socket can be opened here.
**Solution:** the socket setup is ~40 lines behind a narrow interface; everything
it feeds (stream clock, drop accounting, sampling, FIFO parity byte-for-byte)
is already tested. Run it on any host with `CAP_NET_RAW` and
`tests/test_live.py`'s harness; that is a one-environment test, not a redesign.

### 8. IoT-23 results are real but not reproducible from the repo
**Flaw:** scorer scripts lived only in `/tmp`; the 20 GB dataset is on an
unmounted drive.
**Solution:** re-mount (`udisksctl mount -b /dev/sda1`), rewrite `host_run.py`
as a committed script, and the strongest external validation becomes re-runnable.
This is the highest-value remaining task.

### 9. UDP reflection and Slowloris are not separately modelled
**Flaw:** reflection is caught only as a volumetric symptom.
**Solution:** the contract already names the one-way substitute — per-source UDP
fan-out cardinality in place of response size. Slowloris one-way is a
long-lived half-open-flow pattern the existing flow-assembler already carries
(`nsyn`, `duration`, idle-timeout); a detector over those is a small addition,
and the honest framing is "detected as a slow-half-open-flow symptom, not its
signature".

---

## Do not put these on a slide

Each is a false claim — but note every one has a real substitute above, so the
fix is never "remove the slide", it is "say the true version".

- **"Zero false positives"** — say: "46 rules-tier alerts on the default
  capture, all on attacker-designated hosts; under our own FP-pressure variant
  one critical FP on a benign backup, which we solved with an authorised-
  destination registry."
- **Zeek / Suricata** — neither is installed or invoked; the sensor is pure
  Python. If a judge wants protocol metadata from a mature engine, the true
  statement is that we hand-wrote the ClientHello/DNS dissectors so the whole
  system ships with no C toolchain.
- **Kafka / Flink / ClickHouse / React / ONNX / K8s / Terraform** — none exist.
  The true version of the architecture slide is the pipeline that is here:
  dpkt → FlowAssembler → WindowAggregator → 6 detectors → fusion → LightGBM,
  plus a stdlib dashboard and a stdlib Prometheus exporter.
- **`--models-567` as six working models** — four working plus two honest
  failures used as triage (see #4).
- **MITRE technique IDs** — the alert schema has no such field. Either add real
  technique IDs to the fused verdicts, or say "scenario tags" consistently.
- **"7/7 threat classes"** — the PS names six; the seventh conflates fusion
  with a detector.

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
   result. (Fixes flaw #8.)
2. **Authorised-destination registry** in `core/config.py`, carried on the
   exfil alert as `authorised_destination`. Directly fixes the MESSY critical
   FP. (Flaw #1.)
3. **Transfer-without-relationship detector** for the IoT-23 Trojan miss —
   "established session, high volume, destination with no prior history".
   (Flaw #2.)
4. **Destination reputation tiering** — bundled cloud-CIDR list plus JA4
   corroboration, which would have demoted the Philips HUE FP.
   (Flaw #3.)
5. **Benign-replay fine-tuning** of the flow model on MESSY patterns. Turns the
   "ML tier collapses" claim into a measured result either way. (Flaw #5.)
6. **Test the AF_PACKET socket** on any host with `CAP_NET_RAW` — it is the
   only unexercised piece of the live driver. (Flaw #7.)
7. Port the DGA CNN to torch/CUDA if GPU training is wanted (laptop has an
   RTX 3050; `_xgb_device()` in `training/train_models_567.py` probes CUDA).

Note the shape of the top five: every one is a detector or a config the repo
already has the plumbing for. None is a rewrite.
