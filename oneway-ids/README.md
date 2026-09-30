# One-Way NIDS — SIH 2026 PS-26145 Prototype

AI-based detection of cyber threats in **unidirectional IP traffic** — the
receive side of a hardware data diode. Every detector runs on a single
direction of traffic: no responses, no completed handshakes, no payload
decryption, no probes, no return path. QUIC v1 Initial protection is removed
only to expose the ClientHello metadata public by protocol design. Traffic
windows close on a clock; completed-flow model scoring can still wait for flow
closure, so no end-to-end alert-latency bound is claimed for every model.

## Product walkthrough

[Watch the 7:34 Diode Sentinel explainer](diode-sentinel-launch/out/diode-sentinel-explainer.mp4)
(1080p, 30 fps). It follows observed packets through flows, detection models,
correlation and an evidence export, with Indian English narration and a live
dashboard walkthrough. The displayed replay is synthetic; its counts are demo
data, not accuracy or throughput claims. Production notes and claim trace are
in [the video project](diode-sentinel-launch/README.md).

## Proof snapshot (each result is tied to its stated input)

| Metric | Value | Notes |
|---|---|---|
| Throughput (rules only) | **≈48.6k–50.4k pkt/s · ≈240 Mbps** | repeated one-core pure-Python measurements; Mbps uses the synthetic capture's mean packet size |
| Throughput (with ML tier) | **≈24k–31k pkt/s · ≈120–155 Mbps** | measured range; LightGBM scores closed flows |
| Real-time factor | **≈2,000×** | sparse 23 pkt/s synthetic capture; repeatability statement only, not a headline capability measure |
| Alert timing | 2s flow idle / 10s windows | design intervals, not measured end-to-end latency; continuous-flow model scoring can wait for closure |
| Threat classes covered | **6 / 6** | PS-26145 names classes (a)–(f); fusion is not a seventh class |
| DGA char-CNN vs entropy gate | **1.00 vs 0.47 recall** | held-out DGA family, 0.1% vs 0.3% FP |
| External-corpus DGA (as shipped) | conficker 0.886 / pushdo 0.446 vs gate 0.019 / 0.000 | andrewaeva/DGA: 694k real DGA / 1M benign; benign host 0.46 alerts/h at shipped quorum — `BENCH-DGA.md` |
| False-positive pressure | **1 critical rules FP; 59 benign-host ML alerts** | observed on the MESSY capture; no zero-FP claim |
| Backend parity | **complete alert-record parity** | dpkt and scapy matched on the current archived capture |

The current archived `traffic.pcap` has 14,049 packets and emits 45 rules-tier
alerts / 67 with `--ml`. The preserved historical regression files contain 46
/ 68: exactly one `tls_known_malware` alert from the old synthetic QUIC fixture
is absent because that fixture used invalid QUIC Initial protection. Fixture
migration is pending. The old reference files have not been rewritten, so the
byte-identical regression gate currently reports this known difference; the
other alert records are unchanged.

## Architecture

```
data diode (one-way feed)
   │
   ├─► core/pcap_reader.py  dpkt (hot path) or scapy (parity reference)  [replay]
   └─► core/live_source.py  AF_PACKET raw socket                          [live]
   │  uniform packet tuples (same schema, same dpkt dissection)
   ▼
core/pipeline.py    FlowAssembler (5-tuple, idle timeout)
                    WindowAggregator (10s windows: rates, entropy, fan-out,
                                     novel destinations, per-pair bytes)
   │
   ├─► Tier-0  config allowlist (operator-curated, zero cost)
   ├─► Tier-1  streaming detectors (core/detectors.py):
   │      DDoS        window rate + src-IP Shannon entropy + SYN ratio
   │      beaconing   inter-flow IAT mean/CV per (src,dst,dport),
   │                  evidence-scaled CV gate (0.15 small-n / 0.25 n>=10)
   │      DGA/DNS     char entropy + vowel/digit lexical profile + streak
   │      recon/scan  per-src fan-out cardinality + dominant-dst classifier
   │      exfil       per-(src,dst) cumulative bytes vs source baseline,
   │                  pair-age guard
   │      TLS/QUIC (d) ClientHello parse -> JA4/JA3 (tls_meta.py for TCP,
   │                  quic_meta.py supports RFC-verified QUIC v1 Initials;
   │                  its JA4 transport prefix is q, versus t for TLS):
   │                  known-bad intel match (t=0) +
   │                  two-tier inventory novelty (global=high/per-host=medium),
   │                  transport-aware dedupe (channel migration re-alerts)
   ├─► Tier-2  MLScorer (ml_tier.py): LightGBM on flow features,
   │            micro-batched per flush tick, bare-SYN excluded (tier boundary)
   │            + DgaCnnScorer (dga_cnn.py): 1D character CNN on the qname,
   │            numpy-only, family-held-out trained, quorum-gated
  │            + Models567 (models_567.py): optional category-specific
  │              XGBoost, Random Forest, Isolation Forest, and packet CNN
   ▼
FusionEngine        noisy-OR over exponentially decayed confidences,
                    fire-on-escalation dedupe, scenario tags
   ▼
AlertSink           standardized JSONL: timestamp, src, dst, flow_id,
                    threat_class, confidence, severity, evidence{why, ...}
   ▼
dashboard.py        zero-dependency live SOC dashboard (stdlib HTTP server;
                    daisyUI + Chart.js components vendored locally)
```

## The seven requested threat classes — how each is detected one-way

| PS class | Detector | One-way signal |
|---|---|---|
| (a) DDoS / SYN floods / spoofed floods | window rate + entropy | pkt rate, src-IP entropy collapse, SYN ratio |
| (b) C2 beaconing | IAT periodicity | inter-flow arrival regularity (CV), no request/response pairing |
| (c) DGA / DNS tunnelling | lexical + behavioral | qname entropy, vowel/digit profile, streaks |
| (d) malware in encrypted sessions | JA4/JA3 + novelty | ClientHello metadata over TLS and RFC-verified QUIC v1 Initials; JA4 uses `t` for TLS and `q` for QUIC |
| (6) recon / port scan | fan-out | distinct (dst,port) pairs per src per window, classified as vertical or horizontal |
| (7) data exfiltration | volume + novelty | cumulative bytes to destinations first observed in the stream, compared with the source baseline |

## Layout

```
pyproject.toml       pinned interpreter deps (exact versions the results were
                      measured with) -- `uv sync` reproduces .venv from uv.lock
uv.lock              locked dependency graph incl. hashes; `--extra ml567` adds
                      the category 5-7 model deps (xgboost)
flake.nix            NixOS dev shell: pinned nixpkgs provides uv + libstdc++
                      (numpy/scipy/lightgbm need it; Nix keeps it off the loader
                      path) -- `nix develop`
.env-ml              same libstdc++ shim without flakes (`source .env-ml`)

run.py               end-to-end runner (--live, --parity, --ml, --state)
gen_traffic.py       synthetic one-way pcap: benign + attacks (MESSY=1 for
                      the FP-pressure variant)
dashboard.py         stdlib live SOC dashboard
demo.sh              one-command demo: capture -> all tiers -> dashboard
core/                the pipeline (one detection path, shared by replay+live)
  config.py            thresholds, allowlist, label ground truth, paths
  pcap_reader.py       dpkt/scapy backends -> uniform packet tuples
  live_source.py       live ingest -> the SAME packet tuples as pcap_reader:
                        AfPacketSource (AF_PACKET raw socket) and
                        PcapStreamSource (unprivileged FIFO/pcap-stream
                        reader), sharing one dissector (kernel timestamps,
                        drop stats, deterministic 1-in-N line-rate guard)
  pipeline.py          FlowAssembler + WindowAggregator + StreamProcessor
  detectors.py         6 detectors + FusionEngine + AlertSink
  tls_meta.py          ClientHello parser, JA4/JA3, record reassembly,
                        TCP seq tracker (retransmit/gap safe)
  quic_meta.py         RFC 9001 QUIC v1 Initial derivation -> q-prefixed JA4;
                        independent Appendix A.1/A.2 fixtures
  hello_profiles.py    synthetic TLS stack profiles (single source of truth
                        for traffic + intel seed)
  ml_tier.py           flow features + LightGBM scorer (train/serve parity
                        by construction)
  metrics.py           stdlib Prometheus exporter (nids_* on /metrics)
  observability.py     the one-way observability contract (the headline
                        finding: 5 requested features are impossible)
  dga_cnn.py           1D character CNN + Adam, numpy only (no torch/ONNX)
  packet_sequence_cnn.py  category-6 packet-sequence CNN
  models_567.py        category 5-7 scorers + manifest IO
training/            trainers + the external benchmark (write model artifacts)
  train_ml.py          temporal-split training + honest evaluation
  train_dga_cnn.py     family-held-out training + honest evaluation vs rules
  train_models_567.py  category 5-7 trainers + threshold sweep + holdout eval
  bench_dga.py         cross-dataset benchmark on andrewaeva/DGA (external,
                        unmodified; model loaded as shipped) -> dga_bench.json
tests/               the 10 suites (plain unittest scripts; no pytest dep)
  test_tls_meta.py     parsing, JA4/JA3 golden vectors, reassembly,
                        seq tracking, detector units
  test_fusion.py       noisy-OR, dedupe semantics, decay, scenario gates
  test_live.py         live/offline parity, FIFO streaming, idle-window
                        scoring, timestamp rendering, warm start, socket
                        plumbing, interface validation, privilege denial
  test_dashboard.py    API contracts, filters, timeline, static serving,
                        path-traversal guard, live tail, asset integrity
  test_dga_cnn.py      encoder, finite-difference gradient check on the
                        hand-written backprop, training, save/load, held-out
                        generalisation, tier boundaries
  test_metrics.py      exposition format, counters, HTTP, run hooks
  test_contract.py     the observability-contract gate (fails the build if a
                        detector reads a bidirectional field)
  test_bench_dga.py    fixture-corpus loader, sampling guarantees,
                        sorted-stream ordering, quorum-sweep math
  test_models_567.py   category 5-7 scorers + sequence CNN
model_ml.txt         trained LightGBM flow model
model_dga_cnn.npz    trained CNN weights (4,930 params, 42 KB)
models567/           shipped category 5-7 artifacts + manifest + eval.json
monitoring/          dockerized Prometheus + Grafana: provisioned dashboard,
                      alert rules -- see docs/monitoring.md
BENCH-DGA.md         full-corpus results: per-family TPR, FP, quorum sweep
core/models_567.py   optional Tier-2 models for PS classes (d) encrypted
                    sessions, (e) recon, (f) exfil: XGBoost / forests / a
                    packet-sequence CNN reusing core/dga_cnn.py's numpy conv
training/train_models_567.py  trains that bundle AND evaluates the temporal
                    holdout, sweeping each model's threshold against benign
                    traffic; results -> models567/eval.json (see docs/models-567.md)
models567/           trained artifacts + manifest (shipped, so --models-567
                    works out of the box) + eval.json holdout results
docs/               run-simulation walkthrough; models-567 measured results
static/index.html  dashboard page
static/app.css     layout + SOC palette (daisyUI tokens, dark/light)
static/app.js      polling client: KPIs, charts, filters, evidence modal
static/vendor/     daisyUI 5.7.38 CSS + Chart.js 4.5.0 (both MIT)
alerts.jsonl       standardized alert stream (dashboard input)
```

## Reproducing the environment

The interpreter dependencies are pinned to the exact versions the benchmark
and every documented result were produced with. With
[uv](https://docs.astral.sh/uv/) installed:

```bash
uv sync          # creates .venv bit-for-bit from uv.lock (numpy, scipy,
                 # scikit-learn, lightgbm, scapy, dpkt, cryptography + deps)
uv sync --extra ml567   # + optional category 5-7 model deps (xgboost)
```

`dga_bench.json` also records the model sha256 and both corpus-file digests, so
the benchmark run itself is reproducible, not just the environment.

**On NixOS only**, numpy/scipy/lightgbm link `libstdc++.so.6`, which Nix keeps
off the default loader path — the venv builds but the C extensions fail to
import until it is on `LD_LIBRARY_PATH`. `flake.nix` handles this:

```bash
nix develop     # pinned nixpkgs (flake.lock) provides uv + libstdc++, then:
uv sync         # inside the dev shell, imports work with no extra steps
```

Without flakes, `source .env-ml` resolves the same library paths dynamically
(the previous hardcoded store hash broke on every nixos-rebuild that touched
gcc). On a normal FHS distro neither shim is needed — plain `uv sync` works.

## Run it

Detailed walkthroughs:

- [Running the simulation](docs/run-simulation.md)
- [Category 5-7 models](docs/models-567.md)

```bash
uv sync                 # one-time: reproduce the pinned environment
uv sync --extra ml567   # + category 5-7 model deps (xgboost)

uv run python gen_traffic.py          # synthetic one-way capture
uv run python run.py                  # full pipeline + report
uv run python run.py --parity         # dpkt vs scapy parity check
uv run python training/train_ml.py             # train ML tier (temporal split)
uv run python run.py --ml             # pipeline + ML tier
uv run python tests/test_tls_meta.py        # 42 unit tests (TLS/JA4)
uv run python tests/test_fusion.py          # 15 unit tests (fusion)
uv run python tests/test_quic.py            # RFC fixtures + malformed-input checks
uv run python tests/test_live.py            # 64 unit tests (live capture path)
uv run python training/train_dga_cnn.py        # train the DGA character CNN
uv run python tests/test_dga_cnn.py         # 49 unit tests (CNN + backprop)
uv run python run.py --dga-cnn        # pipeline + DGA CNN confirmer
uv run python training/train_models_567.py     # train category 5-7 model bundle
uv run python run.py --models-567 models567/manifest.json
uv run python training/bench_dga.py            # external-corpus benchmark (~6 min)
uv run python training/bench_dga.py --quick    # 20k subsample, ~40 s
uv run python tests/test_bench_dga.py       # 31 unit tests (benchmark harness)
uv run python tests/test_dashboard.py       # dashboard API + asset tests
uv run python dashboard.py            # live dashboard on :8600
uv run python run.py --metrics-port 9100   # + Prometheus /metrics
                                       # then: docker compose -f
                                       # monitoring/docker-compose.yml up -d
                                       # (Grafana :3000, docs/monitoring.md)
MESSY=1 uv run python gen_traffic.py  # FP-pressure traffic variant

# live capture by reading the socket directly (needs CAP_NET_RAW)
sudo uv run python run.py --live eth0
sudo uv run python run.py --live eth0 --sample 4 --duration 300

# live capture WITHOUT privileges: a privileged helper writes a pcap stream,
# this process only reads it (and so never needs to run as root)
mkfifo /tmp/nids.pcap
dumpcap -i eth0 -P -U -w /tmp/nids.pcap &
uv run python run.py --pipe /tmp/nids.pcap
uv run python run.py --list-interfaces   # find the right interface name
#   --sample N   analyse 1 packet in N (line-rate guard above the ~45k
#                pkt/s single-core ceiling; losses are reported, not hidden)
#   --duration S stop after S seconds of stream time
#   --state P    JA4 inventory checkpoint (default nids_state.json)
#   --no-state   disable persistence: cold start every run
sudo setcap cap_net_raw,cap_net_admin+eip $(readlink -f .venv/bin/python)
```

## Live capture (Item 8)

`live_source.AfPacketSource` is an AF_PACKET raw socket (stdlib only -- no
libpcap binding, no new dependency). It emits the same 11-field packet tuple
as `pcap_reader` and dissects with the same dpkt calls, so live and replay
share one parser rather than two that drift.

```
data diode (one-way feed)
   |
   +-- offline:  pcap_reader.py  (dpkt / scapy)   \
   +-- live:     live_source.py  (AF_PACKET raw)   >-- pipeline.StreamProcessor
                                                      |  flows, windows,
                                                      v  6 detectors, fusion
```

Three things a file reader never needs and a live socket always does:

- **Idle-aware clock.** `WindowAggregator.tick()` closes a completed window
  even when no packet arrives. Without it, a flood followed by silence would
  sit unscored until the next unrelated packet showed up -- unbounded alert
  latency, on a sensor whose whole claim is bounded latency.
- **Drop accounting.** `PACKET_STATISTICS` is read each drain and reported.
  Loss on a one-way feed is invisible by definition, so unreported drops
  would silently bias every rate estimate.
- **Kernel receive timestamps** (`SO_TIMESTAMP` via `recvmsg`). Under load,
  `time.time()` at drain time stamps a whole batch with the drain clock,
  which directly corrupts the inter-arrival statistics that C2 beaconing
  detection is built on.

Stream time is anchored to the wall clock at capture start, so `t=0` is
"capture start" and the existing `BASELINE_SECONDS` window keeps meaning
"the first 3 minutes". `config.set_time_anchor()` decides whether alert
timestamps render that way (live) or as the synthetic 2025 sim dates
(offline replay).

### Two ways to get live traffic

The socket path is the direct one. The stream path exists because opening a
capture socket needs `CAP_NET_RAW` while *reading* a capture stream does not,
so the privileged part can be kept to a small audited tool and the analysis
stack never has to run as root:

```
mkfifo /run/nids/feed.pcap
dumpcap -i eth0 -P -U -w /run/nids/feed.pcap   # privileged (or file-capped)
run.py --pipe /run/nids/feed.pcap              # this side needs nothing
```

`-P` forces classic pcap (pcapng cannot be streamed) and `-U` makes the writer
packet-buffered -- without `-U` the writer buffers whole seconds of traffic,
which silently breaks the latency budget. `--pipe` also accepts a regular
file that is still growing, so it can tail a capture in progress.

The stream source picks its own clock: wall clock when the records are
timestamped about now (a live feed), otherwise packet timestamps (an archive
replay, where the wall clock would race ahead of the frames being processed
and close every window early). It prints which one it chose.

**The AF_PACKET socket path is still unverified against a real interface.**
The development container has `CapBnd: 0`, so no capability can be acquired
there at all -- not by root and not even via a file-capped helper (`dumpcap
-failed to inherit capabilities: Operation not permitted`). What is verified:
the whole analysis path end to end, driven by a real FIFO written in chunks
by another process, reproducing the offline alert stream **byte-for-byte**;
plus dissection, drop accounting, sampling, interface validation and both
privilege/config failure paths. What is not: `AF_PACKET` socket setup itself,
which is only exercised up to the point where it fails with
`CapturePermissionError`.

**Warm-start semantics.** `--state` persists the fingerprint inventory *and*
the per-incident dedupe clocks. A restart therefore does not re-announce an
incident it has already reported (the TLS re-alert window is 300s), which is
the intended fire-on-escalation behaviour. One consequence to be aware of:
replaying the *same* capture twice against the same state file suppresses the
second run's known-bad alerts, because the replayed timeline never advances
past the saved dedupe times. On a live sensor time only moves forward, so the
window expires normally.

## DGA tier (Item 10): a character CNN, and why it earns its place

The Tier-1 DGA detector is a scalar heuristic: character entropy plus
vowel/digit ratios. It is cheap and always on. It also has a measured blind
spot, and the blind spot is one this project documented before the model
existed (README lesson 1): **empirical Shannon entropy on short labels is
biased low**, so uniform-random labels walk under a 3.3-bit gate.

Measured on the shipped demo traffic: `8yuxczaumapqpp` scored **3.182 bits**
against a `DGA_MIN_ENTROPY` of 3.3. The rules called it benign. It is a real
query from the botnet DGA host. Across 60 fresh cryptolocker-style labels,
**17 (28%) are rejected** by the lexical gate.

`core/dga_cnn.py` is a 1D character CNN over the label (embedding → Conv1D(k=3,5)
×32 → ReLU → masked global max-pool → dropout → dense → softmax), trained and
served entirely in numpy. It adds **no dependency**: numpy is already present
transitively via LightGBM, and there is no torch, keras or ONNX anywhere.
4,930 parameters, ~60 s to train, CPU only.

## Category 5-7 model tier

`models_567.py` adds an optional learned tier for the three requested threat
categories. `FlowAssembler` retains bounded packet sizes, timestamps, and the
one-way outbound direction. Category 5 uses a NumPy 1D CNN over those sequence
tokens plus XGBoost over TLS/QUIC metadata. Category 6 uses Random Forest and
Isolation Forest over scan fan-out features. Category 7 uses XGBoost and
Isolation Forest over transfer volume, baseline, and destination novelty.

Train the bundle with `train_models_567.py`; it writes a JSON manifest, the
model artifacts, and a holdout evaluation under `models567/` (all shipped in
the repo, so `--models-567` works out of the box). Serving is opt-in via
`--models-567`; without the manifest, the original rules and existing ML tier
continue unchanged. The trainer evaluates the temporal holdout and sweeps each
model's threshold against benign traffic — the measured results are published
in `docs/models-567.md`, and they are not uniformly good news: category 5 is
genuinely strong, categories 6 and 7 are measured-but-not-deployable on this
capture. Read that table before quoting the tier.

**Family-held-out evaluation** (the protocol the deck's slide 11 claims, and
the only honest one for a string model — a random split lets the same family
sit on both sides and just measures memorisation):

| Held-out family | n | CNN recall | rule recall |
|---|---|---|---|
| `hex_like` (same kind, unseen family) | 1500 | **1.000** | 0.473 |
| `dictionary_pair` (different kind) | 1500 | 0.007 | 0.004 |
| benign (false-positive rate) | 2000 | **0.001** | 0.003 |

The benign corpus deliberately contains concatenated compounds and
word+digit hostnames, so the task is not set up for a flattering number.

**Why it is a Tier-2 confirmer and not a replacement.** Dictionary DGA
families (suppobox, matsnu) build low-entropy, perfectly lexical labels —
`drivercenter`, `helpdeskupdate` — that no entropy threshold and, as the
table shows, no morphological model can separate from a benign hostname from
the string alone. That is a finding, not a tuning failure: the detector
therefore gates the CNN behind a per-source quorum (`DGA_CNN_MIN_STREAK`) and
caps its unaided confidence below 0.90, so a morphology-only verdict can
never outrank a lexical alert the host is also actively beaconing from.

**On someone else's corpus.** `bench_dga.py` scores the shipped detector
against `andrewaeva/DGA` — 694,173 real DGA domains across 8 named families
and 1,000,000 Alexa domains, unmodified, model loaded as shipped. Two
findings (`BENCH-DGA.md`): the entropy gate's `DGA_MIN_LEN = 10` floor blinds
it on conficker and pushdo (median labels 8 chars) where the CNN scores
0.886 / 0.446; and the CNN's own per-string FP rate on real benign domains is
16.5% — which is why the quorum is a measured constant, swept on the full
corpus: 17.3 benign alerts/h at k=2, 0.46 at k=4, 7/8 families still
detected.

**Regression safety.** The CNN is opt-in (`--dga-cnn`); with `cnn=None` the
detector is unchanged. Current dpkt/scapy records match on the archived
capture. The historical `.regression` refs remain at 46/68 while the current
capture produces 45/67 because one invalid synthetic-QUIC-derived
`tls_known_malware` record was removed. Do not describe the frozen-reference
gate as passing until the reviewed fixture migration is complete.

## Dashboard (Item 5, rebuilt on a component library)

`dashboard.py` is still stdlib-only Python -- `ThreadingHTTPServer` serving a
static page plus JSON, no Flask, no npm. The front end is one page built from
[daisyUI](https://daisyui.com) components (badge, table, progress, btn,
modal) and [Chart.js](https://www.chartjs.org). Both are **vendored** under
`static/vendor/`: this dashboard sits on the receive side of a data diode, so
a CDN `<link>` would simply never resolve.

Panels: six KPI cards (alerts, critical, high, medium, PS coverage,
allowlisted), a stacked severity timeline, a threat-class mix ring, the
filterable alert stream with an evidence drawer (click a row), top offending
sources, and a PS-26145 (a)-(f) coverage panel. Dark/light toggle, pause,
search over src/dst/class/evidence, and severity/class filters.

| Endpoint | Returns |
|---|---|
| `GET /` | the dashboard page |
| `GET /static/...` | app + vendored assets (path-traversal guarded) |
| `GET /api/alerts?limit=&severity=&cls=&q=` | filtered alerts + full stats + severity timeline + top talkers |
| `GET /api/stats` | counts by class/severity, coverage, sensor sidecar |

Filtering, time-bucketing and aggregation all happen server-side; the browser
only renders, so the polling cost per tick is one request. Every `/api/*`
request re-reads `alerts.jsonl`, which is why a pipeline appending to the
file streams straight to the browser (a torn last line is skipped, not
crashed on). KPI counts describe the whole file; the timeline, stream and top
talkers follow the active filters.

Verification: `test_dashboard.py` asserts the API contracts, the filter and
bucket invariants, the traversal guard and the live-tail behaviour. Because
the page cannot be eyeballed from a terminal, it also asserts that no asset
is remote, that every class used in the markup resolves to a rule in the
vendored CSS or `app.css`, and that every element id the client grabs exists.
The layout itself was checked in headless Chromium over CDP (KPI row and both
grids at desktop width, charts painted, modal opens, filter focuses, theme
swap) -- see the loop log.

## Validation approach (honest version)

- **Temporal splits everywhere**: ML trains on t<420s, tests on t>=420s —
  no temporal leakage. Test results: benign recall 100% (0 FP), malicious
  recall 85.7% — and the 10 "misses" are documented label noise (the model
  is right, the generator-derived labels are wrong on benign DNS from an
  attack host).
- **Backend parity**: dpkt and scapy readers produce identical alert
  distributions; asserted in `--parity` mode.
- **External corpus**: the shipped DGA policy scored on andrewaeva/DGA
  (694k real DGA domains / 1M benign) without retraining — per-family TPR,
  FP rates and the quorum sweep in `BENCH-DGA.md`; the benchmark harness
  itself is unit-tested offline against a fixture corpus
  (`test_bench_dga.py`).
- **Live/offline parity**: the same capture replayed through the live driver
  (injected source, frame-synchronised clock) yields an identical alert
  distribution to the offline path -- asserted in `test_live.py`.
- **Idle-window scoring**: a flood followed by silence is proven to score
  during the capture rather than waiting for the next packet.
- **Current archive vs historical references**: the current 14,049-packet
  archive emits 45/67 alerts (rules/ML). Preserved refs contain 46/68; the
  single difference is `tls_known_malware` from an invalid historical
  synthetic QUIC Initial. Reference migration is pending and the byte-identical
  gate is therefore known to fail; no refs have been overwritten.
- **Ground truth**: labels derive from generator knowledge (src/dst/time
  predicates in config), never from the detectors themselves.
- **FP pressure test** (MESSY=1): IoT periodic telemetry, first-time 3MB
  cloud-backup, CDN-style subdomains. Outcomes: DGA held (0 FP), beacon
  FPs on unlearned periodic services resolved by operator-curated
  allowlist (the same workflow as RITA/AC-Hunter), backup upload fires one
  genuinely-ambiguous exfil alert (documented limitation: novel-dst +
  large transfer needs a UEBA feedback loop).
- **QUIC protocol proof**: `tests/fixtures/quic/rfc9001_a2_client_initial.hex`
  is the independent RFC 9001 Appendix A.2 packet; `test_quic.py` checks the
  Appendix A.1 client key/IV/HP values and expected ClientHello metadata. QUIC
  uses JA4 prefix `q` while TLS uses `t`, so only the ClientHello metadata
  fields are compared. GCM-tampered packets fail closed.

## Lessons baked in (each one was a real bug we hit)

1. **Entropy on short strings is biased low** — 14-char random labels score
   ~3.4–4.2 bits, not log2(36)=5.17 (sample collisions). Raw entropy alone
   cannot separate DGA from long English words; composite lexical features
   (vowel/digit ratios) are required.
2. **"Novel destination" must be tracked per (src,dst) with an age guard** —
   window-scoped novelty lets sustained transfers evade after window one.
3. **Sample CV at n=6 is statistically noisy** — a benign exponential
   process dips below any fixed gate by luck (~2%/test). Evidence-scaled
   gates: tight for small n, standard for n≥10.
4. **Retransmits silently corrupt stream reassembly** — one-way feeds have
   no ACK clock, so duplicate/gapped segments must be detected by TCP seq
   tracking. A wrong fingerprint is worse than no fingerprint.
5. **First-alert gates must not be shadowed by re-alert gates** — a naive
   `n - last < 10` check blocked ALL first alerts for series <10 flows.
6. **Exact-set dedupe on fusions causes alert storms** — an ongoing
   incident re-fires critical every window; fire-on-escalation semantics
   fix it (a growing class-set escalates; a stable one stays silent).
7. **Tier boundaries matter as much as detectors** — per-flow ML on bare
   SYN packets produced 3,000 alerts; the aggregate detectors own those.
8. **Allowlists are operator-curated, not auto-learned** — auto-learning
   periodic traffic whitelists existing botnets.
9. **Determinism and order are different requirements** — a sorted corpus is
   reproducible *and wrong* when the consumer is order-sensitive. A prefix of
   a sorted domain list is a lexicographic slice (0.83 vs 0.165 measured FP),
   and a sorted query feed lets each digit-leading benign label complete the
   previous one's CNN quorum (9.9 vs 0.43 benign alerts/h from the same
   corpus). Seed the shuffle; pin provenance with a digest instead.

## Known limitations (stated, not hidden)

- QUIC: only RFC-verified v1 Initial packets are supported and decryptable
  one-way (by protocol design); Handshake/1-RTT payloads stay opaque. Other
  QUIC versions are rejected.
- Live capture has not been run against real traffic or a real interface
  (see "Live capture" above): the container used for development has no
  CAP_NET_RAW. Socket setup, drops, sampling and idle handling are unit
  tested through an injected source; the socket itself is not.
- Live capture has no kernel BPF filter (Python-side `port_filter` runs
  post-dissection, so it saves detector work but not parse work), and
  sustained ingest is capped by pure-Python dissection. `--sample N` is the
  guard, and it trades coverage for stability.
- JA4 inventory persistence is implemented (`--state`), but the Tier-0
  allowlist is still a hand-edited constant rather than operator tooling.
- ML labels are generator-derived; real-efficacy training needs public
  datasets (CTU-13, CIC-IDS, CESNET-TLS22) — the pipeline ingests them via
  the same flow-feature path.
- Spoofed-source attribution is weaker one-way (entropy-based suspicion,
  not proof).
- JA3S / server certificates are structurally invisible one-way; the TLS
  detector documents this in every alert's evidence.
