# One-Way NIDS — SIH 2026 PS-26145 Prototype

AI-based detection of cyber threats in **unidirectional IP traffic** — the
receive side of a hardware data diode. Every detector runs on a single
direction of traffic: no responses, no handshakes, no decryption, no probes,
no return path. Streaming, not batch: alerts fire within seconds of the
traffic, with bounded latency by construction.

## Headline results (all measured, not claimed)

| Metric | Value | Notes |
|---|---|---|
| Throughput (rules only) | **44,269 pkt/s · 18,077 flow/s** | dpkt backend, 1 CPU core, pure Python |
| Throughput (with ML tier) | **24,687 pkt/s · 10,081 flow/s** | LightGBM scoring every closed flow |
| Real-time factor | **2,113×** (rules) / 1,179× (with ML) | 600s capture processed in 0.28s |
| Alert latency | ≤ 2s flow-idle + ≤ 10s window | bounded by design, not measured tail |
| Threat classes covered | **6 / 6** | (a)–(f) of PS-26145 |
| DGA char-CNN vs entropy gate | **1.00 vs 0.47 recall** | held-out DGA family, 0.1% vs 0.3% FP |
| External-corpus DGA (as shipped) | conficker 0.886 / pushdo 0.446 vs gate 0.019 / 0.000 | andrewaeva/DGA: 694k real DGA / 1M benign; benign host 0.46 alerts/h at shipped quorum — `BENCH-DGA.md` |
| False positives | **0** (after operator allowlisting) | pressure-tested on messy benign traffic |
| Backend parity | IDENTICAL | dpkt vs scapy produce byte-identical alert distributions |

## Architecture

```
data diode (one-way feed)
   │
   ├─► pcap_reader.py   dpkt (hot path) or scapy (parity reference)  [replay]
   └─► live_source.py   AF_PACKET raw socket                          [live]
   │  uniform packet tuples (same schema, same dpkt dissection)
   ▼
pipeline.py         FlowAssembler (5-tuple, idle timeout)
                    WindowAggregator (10s windows: rates, entropy, fan-out,
                                     novel destinations, per-pair bytes)
   │
   ├─► Tier-0  config allowlist (operator-curated, zero cost)
   ├─► Tier-1  streaming detectors (detectors.py):
   │      DDoS        window rate + src-IP Shannon entropy + SYN ratio
   │      beaconing   inter-flow IAT mean/CV per (src,dst,dport),
   │                  evidence-scaled CV gate (0.15 small-n / 0.25 n>=10)
   │      DGA/DNS     char entropy + vowel/digit lexical profile + streak
   │      recon/scan  per-src fan-out cardinality + dominant-dst classifier
   │      exfil       per-(src,dst) cumulative bytes vs source baseline,
   │                  pair-age guard
   │      TLS/QUIC (d) ClientHello parse -> JA4/JA3 (tls_meta.py for TCP,
   │                  quic_meta.py decrypts QUIC Initial packets -- keys are
   │                  public (version salt + DCID), so one-way QUIC analysis
   │                  needs no secrets): known-bad intel match (t=0) +
   │                  two-tier inventory novelty (global=high/per-host=medium),
   │                  transport-aware dedupe (channel migration re-alerts)
   ├─► Tier-2  MLScorer (ml_tier.py): LightGBM on flow features,
   │            micro-batched per flush tick, bare-SYN excluded (tier boundary)
   │            + DgaCnnScorer (dga_cnn.py): 1D character CNN on the qname,
   │            numpy-only, family-held-out trained, quorum-gated
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

## The six PS threat classes — how each is detected one-way

| PS class | Detector | One-way signal |
|---|---|---|
| (a) DDoS / SYN floods / spoofed floods | window rate + entropy | pkt rate, src-IP entropy collapse, SYN ratio |
| (b) C2 beaconing | IAT periodicity | inter-flow arrival regularity (CV), no request/response pairing |
| (c) DGA / DNS tunnelling | lexical + behavioral | qname entropy, vowel/digit profile, streaks |
| (d) encrypted-session malware | JA4/JA3 + novelty | ClientHello metadata over **TLS and QUIC** (QUIC Initials are decryptable one-way — keys are public) |
| (e) recon / port scan | fan-out | distinct (dst,port) pairs per src per window |
| (f) data exfiltration | volume + novelty | cumulative bytes to young (src,dst) pairs vs baseline |

## Layout

```
pyproject.toml     pinned interpreter deps (exact versions the results were
                   measured with) -- `uv sync` reproduces .venv from uv.lock
uv.lock            locked dependency graph incl. hashes
flake.nix          NixOS dev shell: pinned nixpkgs provides uv + libstdc++
                   (numpy/scipy/lightgbm need it; Nix keeps it off the loader
                   path) -- `nix develop`
.env-ml            same libstdc++ shim without flakes (`source .env-ml`)
config.py          thresholds, allowlist, label ground truth, paths
gen_traffic.py     synthetic one-way pcap: benign + attacks (MESSY=1 for
                   the FP-pressure variant)
pcap_reader.py     dpkt/scapy backends -> uniform packet tuples
live_source.py     live ingest -> the SAME packet tuples as pcap_reader:
                   AfPacketSource (AF_PACKET raw socket) and
                   PcapStreamSource (unprivileged FIFO/pcap-stream reader),
                   sharing one dissector (kernel timestamps, drop stats,
                   deterministic 1-in-N line-rate guard)
pipeline.py        FlowAssembler + WindowAggregator + StreamProcessor
                   (one detection path, shared by replay and live)
detectors.py       6 detectors + FusionEngine + AlertSink
tls_meta.py        ClientHello parser, JA4/JA3, record reassembly,
                   TCP seq tracker (retransmit/gap safe)
hello_profiles.py  synthetic TLS stack profiles (single source of truth
                   for traffic + intel seed)
ml_tier.py         flow features + LightGBM scorer (train/serve parity
                   by construction)
train_ml.py        temporal-split training + honest evaluation
dashboard.py       stdlib live SOC dashboard
run.py             end-to-end runner (--live, --parity, --ml, --state)
test_tls_meta.py   42 tests: parsing, JA4/JA3 golden vectors, reassembly,
                   seq tracking, detector units
test_fusion.py     15 tests: noisy-OR, dedupe semantics, decay,
                   scenario gates, SYN-flood attribution
test_live.py       64 tests: live/offline parity, FIFO streaming,
                   idle-window scoring, timestamp rendering,
                   inventory warm start, socket plumbing, interface
                   validation, privilege denial
test_dashboard.py  82 checks: API contracts, filters, timeline bucketing,
                   static serving, path-traversal guard, live tail of a
                   half-written line, and asset integrity (no CDN, every
                   class resolves, every element id exists)
test_dga_cnn.py    49 checks: encoder, finite-difference gradient check on
                   the hand-written backprop, training, save/load, held-out
                   generalisation, and detector tier boundaries
dga_cnn.py        1D character CNN + Adam, numpy only (no torch/keras/ONNX)
train_dga_cnn.py   family-held-out training + honest evaluation vs the rules
model_dga_cnn.npz trained CNN weights (4,930 params, 42 KB)
bench_dga.py        cross-dataset benchmark on andrewaeva/DGA (external,
                    unmodified; model loaded as shipped) -> dga_bench.json
test_bench_dga.py   31 checks: fixture-corpus loader, sampling guarantees,
                    sorted-stream ordering regression, quorum-sweep math
BENCH-DGA.md        full-corpus results: per-family TPR, FP, quorum sweep
BENCH-DGA-FINDINGS.md  superseded pre-full-run note; kept for the quick->full
                   deltas (what scaling confirmed and what it revised)
static/index.html  dashboard page
static/app.css     layout + SOC palette (daisyUI tokens, dark/light)
static/app.js      polling client: KPIs, charts, filters, evidence modal
static/vendor/     daisyUI 5.7.38 CSS + Chart.js 4.5.0 (both MIT)
alerts.jsonl       standardized alert stream (dashboard input)
PLAN.md            build loop log: every design, review, and fix
```

## Reproducing the environment

The interpreter dependencies are pinned to the exact versions the benchmark
and every documented result were produced with. With
[uv](https://docs.astral.sh/uv/) installed:

```bash
uv sync          # creates .venv bit-for-bit from uv.lock (numpy, scipy,
                 # scikit-learn, lightgbm, scapy, dpkt, cryptography + deps)
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

```bash
uv sync                 # one-time: reproduce the pinned environment

uv run python gen_traffic.py          # synthetic one-way capture
uv run python run.py                  # full pipeline + report
uv run python run.py --parity         # dpkt vs scapy parity check
uv run python train_ml.py             # train ML tier (temporal split)
uv run python run.py --ml             # pipeline + ML tier
uv run python test_tls_meta.py        # 42 unit tests (TLS/JA4)
uv run python test_fusion.py          # 15 unit tests (fusion)
uv run python test_quic.py            # 10 unit tests (QUIC)
uv run python test_live.py            # 64 unit tests (live capture path)
uv run python train_dga_cnn.py        # train the DGA character CNN
uv run python test_dga_cnn.py         # 49 unit tests (CNN + backprop)
uv run python run.py --dga-cnn        # pipeline + DGA CNN confirmer
uv run python bench_dga.py            # external-corpus benchmark (~6 min)
uv run python bench_dga.py --quick    # 20k subsample, ~40 s
uv run python test_bench_dga.py       # 31 unit tests (benchmark harness)
uv run python test_dashboard.py       # dashboard API + asset tests
uv run python dashboard.py            # live dashboard on :8600
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

`dga_cnn.py` is a 1D character CNN over the label (embedding → Conv1D(k=3,5)
×32 → ReLU → masked global max-pool → dropout → dense → softmax), trained and
served entirely in numpy. It adds **no dependency**: numpy is already present
transitively via LightGBM, and there is no torch, keras or ONNX anywhere.
4,930 parameters, ~60 s to train, CPU only.

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
detector is unchanged, and the audit is mechanical: offline replay and `--ml`
still reproduce their reference alert files **byte-for-byte**, and `--parity`
is still IDENTICAL.

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
- **No regressions**: after the refactor, offline replay and `--ml` still
  reproduce the original alert files byte-for-byte.
- **Ground truth**: labels derive from generator knowledge (src/dst/time
  predicates in config), never from the detectors themselves.
- **FP pressure test** (MESSY=1): IoT periodic telemetry, first-time 3MB
  cloud-backup, CDN-style subdomains. Outcomes: DGA held (0 FP), beacon
  FPs on unlearned periodic services resolved by operator-curated
  allowlist (the same workflow as RITA/AC-Hunter), backup upload fires one
  genuinely-ambiguous exfil alert (documented limitation: novel-dst +
  large transfer needs a UEBA feedback loop).
- **Two independent adversarial code reviews** absorbed during development
  (spec-verified against FoxIO/Salesforce docs); findings and fixes logged
  in PLAN.md.
- **QUIC round-trip proof**: the JA4 extracted from a decrypted QUIC
  Initial is byte-identical to the direct TLS parse (test_quic.py), and a
  GCM-tampered packet is rejected rather than mis-fingerprinted.

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

- QUIC: only Initial packets are decryptable one-way (by protocol design);
  Handshake/1-RTT payloads stay opaque. Only QUIC v1 salt implemented.
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
