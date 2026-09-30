# Diode Sentinel — Video Brief

> **Give this whole file to the video generator.** It is self-contained: it
> explains what the project is, the handful of things that are genuinely
> unique, the exact numbers that may be quoted, and — just as important — a
> list of claims the video must **not** make. Everything here was verified
> against the source in this repo, not copied from marketing copy. Where a
> number needs a caveat, the caveat is written next to it and is not optional.

---

## 0. 30-second orientation (for the writer, not the audience)

**Project name:** Diode Sentinel
**Problem statement:** SIH 2026 **PS-26145** (NTRO) — *"AI-Based Detection of
Cyber Threats in Unidirectional IP Traffic."*
**What it actually is:** an intrusion-detection sensor for the receive side of a
**hardware data diode**. It sees exactly one direction of every conversation —
no replies, no handshakes, no FIN/RST from the far end, no decryption.
**How it's built:** pure Python. No GPU, no deep-learning frameworks, no C
extensions, no Zeek/Suricata, no Kafka/Flink/React/K8s. One core saturates a
~240 Mbps feed. It ships as a self-contained sensor plus a stdlib dashboard.

**The one-line pitch:**
> The statement doesn't ask for a threat detector — it asks for a threat
> detector **inside a room with no door**. Anyone can run an IDS on a mirror
> port; the difficulty is that we are forbidden from asking the network a single
> question.

---

## 1. The single most important thing (lead with this)

**Five of the features the problem statement itself requests are physically
impossible under the problem statement's own first constraint.**

We didn't just note that — we made it a **contract**, enumerated every requested
feature, marked each one, and wrote a **CI gate that fails the build** if any
detector reads a response-side field. The finding is about *the problem*, not a
limitation of our code. This is the headline; everything else supports it.

The contract (`core/observability.py`) has **21 feature rows: 15 OBSERVABLE, 5
IMPOSSIBLE, 1 SUBSTITUTED.** The 5 impossible rows cover six named features
(one row bundles "negotiated cipher **and** server certificate"):

| Requested feature | Why it can never be seen on a diode feed |
|---|---|
| **JA3S / JA4S** server fingerprint | ServerHello is sent by the responder — not on the feed |
| **Negotiated cipher / server certificate** | Both are chosen by the responder after the handshake, off the observable path |
| **Round-trip time** | RTT needs a response; one-way latency is unmeasurable |
| **NXDOMAIN ratio** | RCODE lives in the DNS *response* header the diode never delivers |
| **Outbound-to-inbound byte ratio** | The inbound half is never seen, so the ratio has no denominator |

The gate (`tests/test_contract.py`) greps detector sources for forbidden tokens
(`ja3s`, `server_hello`, `rcode`, `nxdomain`, `ttl`, `rtt`, `bytes_in`, …).
**It has teeth:** injecting an `rcode` read makes it fail; removing it passes.

**How to show it:** the contract table is the strongest single image in the
project. `build_contract_image.py` renders `core/observability.py` to a
**contract.png** — use it, ideally with the row-by-row reveal.

---

## 2. Ten things that are genuinely unique or worth pointing out

Each item: **the point**, the **evidence**, and **how to show it**. Order is a
suggested narrative order, strongest first.

### 1. The one-way observability contract (the real contribution)
Every requested feature classified OBSERVABLE / IMPOSSIBLE / SUBSTITUTED, with
the reason, the consumer function, or the substitute signal. Enforced in CI.
- **Evidence:** `core/observability.py`, `tests/test_contract.py`,
  `contract.png`.
- **Show:** the 5 impossible rows lighting up red; the gate failing on purpose.

### 2. The clock closes the windows, not the traffic
The statement demands *streaming with bounded latency*. On a one-way feed you
cannot wait for the far end to finish a conversation. So detection windows and
flows are closed by **a monotonic clock** (`WindowAggregator`), not by packet
arrival. Otherwise "flood, then silence" sits unscored forever — unbounded
latency on a sensor whose only claim is bounded latency.
- **Evidence:** `core/pipeline.py` (stream clock / window flush), the
  `windows flushed : 60` line in a real run.
- **Show:** an animation of a silent link still emitting a scored window.

### 3. Substitution, done honestly
Where a feature is impossible, we built the closest **observable** proxy and put
its arithmetic on the alert.
- Exfiltration → **cumulative bytes to a novel destination**, measured against
  the source's own median baseline. Default novelty is fleet-relative;
  `--source-context` instead checks the source's retained destination history
  and records its lookback and coverage. Never claim first-ever contact.
- JA3S → **JA4 from the ClientHello**.
- UDP amplification response size → **per-source UDP fan-out and shared-target
  burst counts**.
- NXDOMAIN → **per-source high-entropy query streak + char-CNN quorum**.
- **Evidence:** `core/detectors.py`, `docs/udp-signals.md`.
- **Show:** "asked for X → here is the one-way Y we substituted, and here is the
  arithmetic on the alert."

### 4. QUIC Initial packets are decryptable with no secret — so one direction is enough
QUIC Initials use a **public** version salt + the connection ID (RFC 9001), so
the sensor derives the keys and recovers ClientHello metadata on a strictly
one-way feed. The independent key and packet vectors in [RFC 9001 Appendix
A.1/A.2](https://www.rfc-editor.org/rfc/rfc9001.html#appendix-A.2) validate
the parser. QUIC JA4 has a `q` transport prefix; TLS uses `t`, so their full
fingerprints are not identical. Tampered packets and unsupported versions are
rejected.
- **Evidence:** `core/quic_meta.py`, `tests/test_quic.py`, and
  `tests/fixtures/quic/rfc9001_a2_client_initial.hex`.
- **Show:** "encrypted traffic, still fingerprinted — and we never held a key."

### 5. A numpy-only character CNN with hand-written gradients that are provably correct
The DGA detector is a genuine 1-D convolutional net in **~4,930 parameters**,
no torch, no tensorflow, no GPU. Its forward *and backward* passes are
hand-written numpy — and a wrong convolution gradient would still *train*, so
the test suite checks the **analytic gradients against finite differences**.
- **Evidence:** `core/dga_cnn.py`; `tests/test_dga_cnn.py` asserts worst-case
  error `< 1e-4`; measured match is **7e-09**.
- **Family-held-out:** CNN **1.000** recall vs rules **0.473** on an unseen DGA
  family, benign FP 0.001 vs 0.003.
- **External corpus** (`andrewaeva/DGA`, 694,173 real DGA / 1,000,000 benign
  Alexa): the entropy gate is blind to short-name families; the CNN recovers
  **conficker 0.019 → 0.886** and **pushdo 0.000 → 0.446**.
- **The quorum is a measured constant, not a vibe:** the CNN alone is *not*
  deployable (16.5 % per-string FP on 1 M benign domains). Swept: **17.3
  benign alerts/hour at k=2 → 0.46 at k=4**, with 7/8 families still detected.
  Shipped default is **k=4**.
- **Show:** the gradient check; a per-family bar chart of gate vs CNN.

### 6. It runs against real malware, not just our own generator
Trained on synthetic data, but validated on the **IoT-23** public dataset
(CTU Stratosphere, real malware, Zeek ground truth) with **no retuning**:
- Capture-8-1 **Hakai** — recall/precision 1.000
- Capture-1-1 **HideNSeek** — 1.000 (flagged the infected host, 0 clean FPs)
- Capture-42-1 **Trojan** — **0.000, an honest total miss**
- Honeypot-4-1 benign **Philips HUE** — **structural false positive**
- **⚠ Mandatory caveat:** these numbers are real but **NOT currently
  reproducible from this repo** (the scorer lived in `/tmp`, the 20 GB dataset is
  on an unmounted drive). Never claim reproducibility. Say "measured on CTU
  IoT-23; re-runnable once the dataset is re-mounted."
- **Show:** the scorecard, including the miss and the FP — the honesty is the
  point.

### 7. Reproducibility you can point at
The archived 14,049-packet capture currently emits **45 rules-only / 67 with
`--ml`**. Preserved historical fixtures remain at 46/68; the one removed
`tls_known_malware` alert came from invalid historical synthetic QUIC, and
fixture migration is pending. Current dpkt and Scapy alert records match.
- **Show:** current backend parity and the known fixture mismatch. Do not show
  a zero-byte diff against the preserved historical references or call this
  chain of custody.

### 8. Everything that exists *because* of the constraint
Not asked for, but forced by one-way:
- **Cross-signal fusion** — two weak one-way signals become one strong verdict
  (`confirmed_c2_implant` = beacon + known-bad JA4; `botnet_c2_with_dga` =
  beacon + DGA). Noisy-OR over decayed confidences, **fire-on-escalation** so an
  ongoing incident doesn't re-fire a critical every window.
- **Restart-safe fingerprint inventory** (`--state`) — without it, a sensor
  restart blinds novelty detection for a whole baseline period — *exactly the
  window an attacker would pick.*
- **Baseline poisoning prevention** — known-bad handshakes are **never** fed
  into the inventory, so an attack can't teach the sensor that it's normal.
- **Operator-curated allowlist, deliberately NOT auto-learned** — auto-learning
  would whitelist the existing botnet.
- **Evidence-scaled statistical gates** — CV measured at n=6 is noisy, so the
  gate is tighter for small n (found when a benign DNS poll landed at CV 0.2249
  against a 0.25 gate).
- **Every alert carries a human-readable `why`** next to the machine-readable
  features — a score alone isn't triageable at 03:00.
- **Evidence:** `core/detectors.py`, `docs/destination-policy.md`.
- **Show:** "we went further than the brief" — each derives from one-way.

### 9. A real operator view, offline, one command
`./demo.sh` generates a fresh synthetic one-way capture, starts the dashboard
**before** the pipeline, then streams the pcap at 10× through the normal live
path; alerts populate during replay and the finished view stays open. The
dashboard is **stdlib only** (no Flask, no npm) with **vendored** CSS/Chart.js so
it renders inside an air-gapped enclave. Live mode is an **AF_PACKET** raw socket
with kernel **drop accounting** and a **1-in-N sampling guard** (above the
~50 k pkt/s pure-Python ceiling it degrades coverage *deterministically and
reports the loss*).
- **Evidence:** `demo.sh`, `dashboard.py`, `core/live_source.py`, `docs/demo.md`.
- **Show:** screen-record the replay — alert queue filling, severity/KPI counts
  ticking, sensor strip, then open one alert's evidence.

### 10. A measured negative result, shipped as one
`--models-567` is **four working models + two honest failures** we published:
`encrypted_xgb`, `sequence_cnn`, `scan_rf`, `exfil_xgb` all hit **recall 1.000 at
0 benign FP**; both **IsolationForests report 0.000** because no threshold is
simultaneously sensitive and inside the 0.5 % benign budget (even the most selective thresholds that detect attacks exceed the 0.5 %
benign budget). They are now used as **triage
corroboration**, not classifiers.
- **Evidence:** `models567/eval.json`, `docs/models-567.md`.
- **Show:** "four that work, and two we refuse to dress up."

---

## 3. Suggested video structure

A ~90-second cut:

1. **Hook (0–8s)** — the data diode: an animated one-way pipe with packets
   flowing and a brick wall where the return path would be. Text: *"No replies.
   No handshakes. No decryption. One direction only."*
2. **Positioning (8–20s)** — "PS-26145, NTRO. A threat detector inside a room
   with no door." Land the one-line pitch.
3. **Headline (20–40s)** — the contract. Five requested features slide in and
   turn red: JA3S, negotiated cipher + server cert, RTT, NXDOMAIN, in/out ratio.
   Punchline: *"Five of the problem statement's own requested features are
   impossible under the problem statement's own first constraint."* Then show
   the CI gate failing on purpose.
4. **The move (40–60s)** — substitution: asked-for X → observable Y, with the
   arithmetic drawn on the alert. Include QUIC ("we fingerprinted encrypted
   traffic and never held a key").
5. **Substance (60–80s)** — quick beats: the numpy CNN + gradient check;
   current dpkt/Scapy parity plus the disclosed archive/reference mismatch; the four-plus-two model tier; the artifact that exists
   only because of the constraint (poisoning-proof inventory).
6. **Honesty (80–90s)** — the IoT-23 scorecard *including the miss and the FP*,
   and the MESSY false positive. Close on: *"Where we couldn't do what the
   statement asked, we can tell you exactly why — and what we did instead."*

A 50-second version can use the verbatim opening script in §4.

---

## 4. Fifty-second opening script (verbatim, safe to read aloud)

> "This is PS-26145 — threat detection in unidirectional IP traffic, from NTRO.
> The statement is not really about threat detection; it is about detection
> **inside a room with no door**. Critical-infrastructure operators copy their
> gateway links into a monitoring enclave through a hardware data diode, and
> that enclave has no path back. So we may never send a probe, never complete a
> handshake, and never decrypt a payload.
>
> Every detector in this system runs on **one direction of traffic**. That turns
> out to break most of the standard playbook — and those are the parts we want
> to show you.
>
> **First, our actual contribution:** we enumerated every feature the statement
> asks for and asked which can exist on a one-way feed at all. **Five cannot** —
> JA3S, the negotiated cipher and server certificate, round-trip time, the
> NXDOMAIN ratio, and the outbound-to-inbound byte ratio. Five of the problem
> statement's own requested features are made impossible by its own first
> constraint. We enforce it: a CI test fails the build if any detector reaches
> for a response-side field.
>
> **Second:** where a feature is impossible, we built the closest observable
> substitute and put its arithmetic on the alert. Exfiltration becomes bytes to
> a novel destination, against that host's own baseline; source-relative novelty
> is available as an explicit option within retained history.
> JA3S becomes JA4 — and we still extract it from QUIC, because QUIC Initial
> keys are public by design.
>
> **Third:** it asks for streaming with bounded latency, not an end-of-run
> report. So the **clock** closes our windows, not the traffic — otherwise a
> flood followed by silence sits unscored forever.
>
> We covered all six threat classes. We measured about 50,000 packets per second
> on a single core in pure Python — roughly 240 megabits sustained — and we
> validated against real malware on the IoT-23 public dataset: two families
> detected with no retuning, one honest miss, one false positive we can explain.
> And where we could not do what the statement asked, we can tell you exactly
> why, and what we did instead."

---

## 5. Numbers you MAY quote (qualifiers are part of the number)

| Fact | Value | Mandatory qualifier |
|---|---|---|
| Observability contract | 21 rows: 15 observable / 5 impossible / 1 substituted | 5 impossible rows cover 6 named features |
| Rules-tier throughput | **≈48.6k–50.4k pkt/s ≈ 240 Mbps** | single CPU core, pure Python, no C extension; quoted as a **range** |
| ML-tier throughput | **≈24k–31k pkt/s** | quoted as a **range** — not reproducible as one number |
| Mean packet size | 613.7 B | from the default synthetic capture |
| Archived capture | **45 rules-only / 67 with `--ml`** | 14,049 packets; preserved historical refs remain 46/68 pending migration; one invalid-QUIC-derived record removed |
| Backend parity | dpkt vs scapy **identical** | identical *alert distributions* |
| DGA CNN size / gradient check | ~4,930 params; analytic vs finite-diff **7e-09** | test threshold is `< 1e-4` |
| DGA held-out | CNN **1.000** vs rules **0.473** recall; FP 0.001 vs 0.003 | family-held-out |
| DGA external corpus | conficker 0.019→0.886; pushdo 0.000→0.446 | `andrewaeva/DGA`, 694,173 DGA / 1,000,000 benign |
| CNN quorum sweep | 17.3 → **0.46 benign alerts/h** at k=2 → k=4 | shipped default **k=4**, 7/8 families still detected |
| models-567 | **4 models recall 1.000 @ 0 benign FP**, 2 IsolationForests 0.000 | two are a documented **negative result** |
| IoT-23 | Hakai 1.000, HideNSeek 1.000, Trojan **0.000 miss**, HUE structural FP | **NOT repo-reproducible** — say so |
| PS threat classes | **all six** (a)–(f) | the statement names six; do not say "7/7" |
| Alert latency | ≤ 2 s flow-idle + ≤ 10 s window | bounded **by design**, not a measured tail |
| Dependency footprint | Python stdlib + numpy + dpkt/scapy; LightGBM/XGBoost/sklearn optional | no GPU, no torch, no C toolchain |

---

## 6. Claims the video MUST NOT make

Each of these is false. If the script reaches for one, replace it with the true
version on the right.

| ❌ Do not say | ✅ Say instead |
|---|---|
| "Zero false positives" | "The historical recorded capture showed 46 rules-tier alerts on designated attacker hosts; the current archive has 45 after removing one invalid-QUIC-derived alert. Under our FP-pressure variant there is one critical FP on a benign backup host; an operator-curated authorised-destination registry demotes it to medium, but does not suppress it." |
| "We use Zeek / Suricata" | Neither is installed or invoked. "We hand-wrote the ClientHello/DNS dissectors so the whole system ships with no C toolchain." |
| "Kafka / Flink / ClickHouse / React / ONNX / K8s / Terraform" | None exist. Describe the real pipeline: dpkt → FlowAssembler → WindowAggregator → detectors → fusion → LightGBM, plus a stdlib dashboard. |
| "7 / 7 threat classes" | The statement names **six**. The "seventh" conflates the fusion layer with a detector. |
| "models-567 is six working models" | "Four working models plus two honest negative results used as triage." |
| "MITRE ATT&CK technique IDs" | The alert schema has no such field. Say "scenario tags". |
| "IoT-23 results are reproducible" | "Measured on CTU IoT-23; re-runnable once the dataset is re-mounted." Real, **not** currently reproducible. |
| "The CNN caught a live DGA the rules missed" | At the shipped quorum (k=4) that alert does **not** fire. Quote it as a **benchmark** on 694k external domains. |
| "~2,000× real-time" as a headline | The capture is sparse (~23 pkt/s). Quote the pkt/s and Mbps capability; mention real-time only as a repeatability statement. |
| "The ML tier is our primary detector" | It is **quorum-gated** and collapses under FP pressure (**79 alerts, 59 on designated benign hosts** on the MESSY capture). Present it as a corroborating tier. |
| "Zeek cannot work one-way; we fixed it" | Our own offline testing **disproved** this: vanilla Zeek parses a one-way ClientHello correctly. That was a generator realism bug, recorded in `ZEEK-ONEWAY-FINDINGS.md`. |

---

## 7. Assets on screen

- **`contract.png`** — render of the observability contract
  (`build_contract_image.py`). Best single visual.
- **The dashboard** (`dashboard.py`, port 8600) — dark SOC theme: severity
  badges, alert queue, KPI row, "Sources with alerts", detection categories,
  charts. `./demo.sh` drives a live-updating replay in one command; this is the
  footage for the "operator view" scene.
- **`Diode-Sentinel.pptx`** — the honest deck, generated by `build_deck.py` from
  `PRESENTATION.md`. Reuse its framing; do not hand-edit it.
- **Terminal beats** — the contract gate failing on an injected `rcode` read;
  `run.py --parity` printing an identical-result stamp; the DGA gradient check
  printing `7e-09`.
- **The diode diagram** — animate a one-way pipe with a wall on the return path;
  the whole project's premise in one image.

---

## 8. Tone

- **Direct, measured, unexcited.** The project's credibility *is* its honesty —
  every weakness is stated with a remedy next to it. A flashy video would
  undercut it.
- **Lead with the finding, not the tooling.** The contract is the story.
- **Show the misses.** The honest Trojan miss and the structural FP are
  strengths, not embarrassments — they're the difference between a demo and a
  sensor.
- Palette: Vanta black + amber/orange accent, mono type for IPs and hashes,
  severity ramp red → orange → amber → grey.

## 9. Approved product-demonstration revision (30 September 2026)

The user approved a ~52-second narrated product walkthrough in place of the
contract-first cut. Show the real dashboard, visible mouse movement, live
synthetic replay counters, opening an alert, source filtering and correlation.
Keep the synthetic-replay qualifier with the recorded UI. Do not narrate the
impossible-feature argument or negative-result scorecards in this revision.
This changes editorial emphasis; it does not authorize invented results.

Team name: **samarags**. Music: **First Light - naneki.mp4**, supplied by the
user in diode-sentinel-launch; synchronize the edit to its measured accents.

Approved model explanations (verified in the current adapters and model docs):
- Character CNN: queried domain-name patterns (core/dga_cnn.py).
- Packet-sequence CNN and XGBoost: packet-size/timing sequences and TLS/QUIC
  metadata for encrypted-session analysis (docs/models-567.md).
- Random Forest: per-source destination/port fan-out for scanning.
- XGBoost: current-window pair/source byte volumes, their ratio, window index
  and fleet destination novelty for exfiltration. The separate deterministic
  exfil rule compares against the source's baseline; its optional source-history
  context does not change the trained XGBoost vector.
- LightGBM: flow-level scoring (core/ml_tier.py), a corroborating tier.
- Isolation Forest: anomaly corroboration attached to eligible supervised scan
  or exfiltration alerts with deterministic-rule corroboration. It is not a
  standalone threat verdict (core/models_567.py).

The fresh demonstration is recorded with rules, DGA CNN, --ml and the
--models-567 manifest enabled. The film may describe a loaded model's purpose;
it must not imply that a selected rules alert was generated by that model.
All UI scores remain detector scores, not calibrated probabilities. Do not
invent or hardcode a 0.94 score: show the selected record's actual value.

The visual sequence: name → receiving traffic → alert evidence → source and
correlation → DGA / encrypted-session / scan / exfil model roles → passive
data-diode monitoring → Diode Sentinel, built by samarags. Actual numeric UI
values are sourced from public/captures/capture-manifest.json and the recorded
clips, generated from a fresh seeded synthetic replay. No accuracy benchmark
or throughput claim is made in this revision.

## 10. Updated B/C explainer concepts after the detector-quality pass

The user selected the packet-laboratory and engine-walkthrough directions for
further development, allows a film longer than 90 seconds, and requires an
actual Indian English voiceover. The revised concept outlines are in
`diode-sentinel-launch/concepts/VIDEO-CONCEPTS.md`: B is approximately 3:20,
C approximately 2:45, with a recommended combined direction around 3:30.
This is a storyboard update, not an already rendered or finally selected cut.
The product-first editorial emphasis in §9 continues: demonstrate the software,
explain named models through their inputs, and show the receive-side mechanism.
Do not insert the older impossible-feature lecture or negative-result
scorecard into these concepts. Preserve factual claim boundaries throughout.

Verified additions that may be explained, with their qualifiers:

| Behavior | Permitted explanation and required qualifier | Evidence |
|---|---|---|
| Rolling scan context | `--rolling-scan` is opt-in. Exact distinct destination/port pairs are accumulated across observed windows in a 60-second horizon. The illustrative ten-pairs-plus-ten-different-pairs experiment reaches the existing twenty-pair scan threshold across two adjacent ten-second windows. It is an additional deterministic rule, not a newly trained model or a calibrated slow-scan benchmark. | `core/detectors.py`, `tests/test_rolling_scan.py`, `tests/test_hour_fixes.py`, `docs/rolling-scan.md` |
| Source-relative novelty | `--source-context` is opt-in. A destination previously seen from source A can still be new within source B's retained history. Show source/fleet novelty, retained lookback and coverage. Capacity loss can suppress uncertain novelty claims. This is rule context and does not change the exfil XGBoost vector. | `core/source_history.py`, `core/detectors.py`, `tests/test_source_history.py`, `docs/source-context.md` |
| Metadata-model eligibility | Encrypted metadata XGBoost skips flows without complete observed ClientHello metadata. The packet-sequence branch remains eligible for its own evaluation. An observed empty field is different from a missing observation. Eligibility does not promise a threat verdict. | `core/models_567.py`, `tests/test_hour_fixes.py` |
| Named model measurements | The dashboard labels known complete model vectors with feature names and units. These are recorded inputs, not feature-importance or causal-attribution results. Unknown or partial vectors remain raw. Use the actual selected record's score, with no calibrated-probability claim. | `dashboard_signals.py`, `tests/test_dashboard_signals.py` |
| Selected-alert evidence export | The actual dashboard can download one selected alert as JSON with its original record, triage, active filters, truncation context and a SHA-256 of the original record. Capture identity, packet references and model-artifact identity are explicitly unavailable. No legal chain-of-custody or packet-level provenance claim. | `core/evidence_export.py`, `dashboard.py`, `static/app.js`, `tests/test_evidence_export.py` |
| Independently verified QUIC Initial parsing | RFC 9001 Appendix A.1/A.2 vectors and the published Client Initial fixture validate key derivation and extraction. Explain public version salt/connection-ID inputs and ClientHello metadata. No application-payload inspection; QUIC JA4 uses `q`, TLS uses `t`. | `core/quic_meta.py`, `tests/test_quic.py`, `docs/quic-verification.md` |
| Current checks | All 23 test scripts pass, with an additional explicitly enabled synthetic-demo smoke run and desktop/mobile browser export checks. Current rules/ML archive outputs are 45/67 and complete-record parser parity passes. Preserved 46/68 historical fixtures differ by one removed invalid-QUIC-derived alert; migration is pending. The separate combined-options/model-bundle replay emitted 79 alerts; this is repeatability evidence, not accuracy or throughput. | `docs/one-hour-validation.json`, `docs/ONE-HOUR-DELIVERY.md` |

The ten-plus-ten animation is an illustrative fixture explanation. Record new
software footage from the corresponding actual pipeline scenario before
showing an emitted alert. Likewise, create and record the two-source history
scenario; do not invent a scored response to a slider. Keep “Synthetic replay”
with all demonstration traffic and numbers. The old captures remain historical.

Use natural Indian English narration with verified pronunciation, the supplied
First Light soundtrack, samarags, and the closing tagline **“See everything.
Touch nothing.”** The tagline is positioning, not a promise of perfect coverage.
Maintain the near-black/amber palette, deliberate motion, readable enlarged
software, and visible cursor actions. Update capture provenance and the claims
trace when the next film is produced.


## 11. Produced B/C explainer — current editorial direction (1 October 2026)

The user has now authorized production of the combined B/C film, with Indian
English narration, slower pacing, more explanatory graphics, and fresh working
software demonstrations. This replaces §10's proposal-only editorial status
for this new composition. It does not change any measured product result.
The original 52-second film remains a historical artifact.

The production uses the C pipeline backbone and B packet experiments. Follow
this exact scene order and the registered spoken/visible copy below. All copy
is editorial wording for the verified facts in §§9–10. Use a speech-led timeline
with two seconds before and after each utterance, actual software footage at
normal recorded speed, and music-aligned cuts. Natural Indian English voice:
Microsoft Edge TTS `en-IN-PrabhatNeural`, catalog locale `en-IN`, rate −10%.
The measured final timeline is 7 minutes 33.6 seconds, including complete unaccelerated dashboard workflows. Never
compress speech to fit a short launch template.

The new demonstration is a seeded synthetic replay: 14,049 generator packets
plus 122 focused scenario packets = **14,171 packets seen and analyzed**, with
**108 emitted alert records** under the combined demonstration options. These
are demo counts, not an accuracy result or the archived regression numbers.
The live PCAP feed replays at 25× simulated packet time; cursor recordings and
film playback remain 1× wall-clock speed. Keep the “Synthetic replay” caption.
The recording may show its real completed state after the replay reaches EOF.

All actual UI text, addresses, times, scores, counts, threshold values and
original evidence in the captured dashboard are authorized demonstration
values from `public/explainer-captures/capture-manifest.json`, `alerts.jsonl`,
`run_stats.json`, and the selected-record/export bundle. Preserve qualifiers.
Selected examples: rolling rule **20** retained destination/port pairs,
**10** in the current window, **60 s** horizon; source-context rule **600,000
observed bytes**, **600-byte** source median baseline, **1,000×** ratio,
source-new within covered retained history, fleet-known, **8,640-window**
retention setting. The synthetic scan-model record is `scan_rf`; the encrypted
metadata model is `xgboost` with its recorded ten-element metadata vector.
Use actual selected record scores, never probability-of-compromise wording.
The DNS rules record is not a character-CNN verdict.

Diagrams are explanatory illustrations, not interactive model experiments or
measured production traces. Author original labels for the packet/flow/window,
model-input, correlation and export diagrams using the verified behavior in
§10; mark these as added editorial wording in the claims trace. The generic
DNS label is `domainlabel`. Packet glyphs, illustrative timing marks, source
A/B and destination X, and the ten-plus-ten window arithmetic are permitted
teaching aids. Supporting Isolation Forest evidence joins an eligible model
branch; it is not a standalone winning detector. Named model inputs do not
claim causal attribution. Source novelty remains qualified by retained
lookback/coverage. QUIC Initial metadata is not application decryption.

First Light is the supplied soundtrack. Extend it with smooth crossfades at
its original tempo, duck it below narration, and measure musical accents in
the edited bed for cuts/reveals. Team name: **samarags**. Use the original code
diagram diode mark; no external logo, event credential, team-member names or
repository URL has been supplied. Closing tagline: **See everything. Touch
nothing.** This is positioning, not perfect-coverage assurance.

### Registered production copy and sequence

1. **intro** — label: DIODE SENTINEL. Headline: Small observations. A larger picture.

   Spoken: A packet is a small observation. Where did it come from? Where is it going? How big is it, and when did it arrive? Put those observations together, and a pattern begins to appear. This is Diode Sentinel.

2. **receive** — label: RECEIVE-SIDE MONITORING. Headline: Watch the observations arrive.

   Spoken: The sensor watches the receive side of a hardware data diode. Traffic arrives in one direction. Here, a synthetic replay is running through the actual software. Watch the packet counters, the sensor state, and the alert queue. These are observations being processed, as they arrive.

3. **organize** — label: PACKETS → CONTEXT. Headline: Put the observations together.

   Spoken: First, we give each packet a useful shape: addresses, ports, protocol, size, and time. Related packets form a flow. Alongside that, timed windows collect what happens across the traffic. The clock closes idle flows and completed windows, even when the next packet never arrives.

4. **rhythm** — label: EXPERIMENT 01 · TIMING. Headline: Listen to the rhythm.

   Spoken: Look at these flow starts. The gaps are almost even. Change the spacing, and the rhythm changes. Our beacon rule measures that regularity. Now open the real alert: the interval and its variation are recorded here. The analyst can inspect the pattern behind the score.

5. **rolling** — label: EXPERIMENT 02 · ROLLING CONTEXT. Headline: Keep both windows in view.

   Spoken: A pattern can be spread across time. In this illustration, one source touches ten distinct destination and port pairs, then ten different pairs in the next window. With rolling scan enabled, the rule keeps a sixty second horizon. The union reaches twenty. Here is that pattern, recorded by the actual pipeline.

6. **history** — label: EXPERIMENT 03 · SOURCE CONTEXT. Headline: Remember whose history it is.

   Spoken: Now suppose two hosts contact the same destination. It is familiar to the first host. That does not make it familiar to the second. With source context enabled, we check this host's retained history, then compare transfer volume with its own baseline. The alert records the lookback and coverage that qualify that observation.

7. **dns** — label: DOMAIN-NAME ANALYSIS. Headline: Read the shape of a name.

   Spoken: A domain name is another kind of sequence. Our character C N N examines patterns in its letters. Separate rules inspect the DNS query's length and type. In the software, the detector identifier tells us which check produced this record. We can see the observed query measurements beside it.

8. **encrypted** — label: ENCRYPTED-SESSION ANALYSIS. Headline: Two branches. Different observations.

   Spoken: An encrypted session still has an observable shape. The sequence C N N uses packet sizes and timing. A separate X G Boost model uses observed Client Hello metadata and flow measurements. Each branch receives the inputs it needs. QUIC Initial packets expose Client Hello metadata through public protocol inputs. Open the model alert: cipher counts, extension counts, bytes, and duration now have names.

9. **models** — label: PARALLEL DETECTOR BRANCHES. Headline: The right inputs. The right branch.

   Spoken: The same engine routes different observations to different checks. Random Forest uses scan window fan out. Exfiltration X G Boost uses transfer window features. Light G B M adds flow scoring. Eligible Isolation Forest scores provide supporting evidence. These branches serve different purposes; the recorded alert identifies its detector and its inputs.

10. **fusion** — label: SOURCE ATTRIBUTION & CORRELATION. Headline: Follow the source. Connect the signals.

   Spoken: Detectors first write their own alerts. Then the correlation layer considers recent qualifying signals from the same source. Filter that source, open a correlated record, and inspect its contributors. The observations stay attached, so the analyst can follow how the signals were connected.

11. **handoff** — label: THE ANALYST VIEW. Headline: Carry the evidence forward.

   Spoken: This is where the explanation becomes a workflow. Open an alert. Read its named measurements. Inspect the original evidence. Then download the selected alert as J S O N. The bundle preserves the record, the active filters, and a hash of that record. The software carries the observations all the way to the analyst.

12. **closing** — label: BUILT BY SAMARAGS. Headline: See everything. Touch nothing.

   Spoken: From packets, to patterns, to inspectable evidence. Diode Sentinel. Passive, receive side monitoring. See everything. Touch nothing. Built by Samarags.

Shared visible captions: **Diode Sentinel**; **samarags**; **Built by samarags**;
**Recorded software · Synthetic replay**; **Illustrative diagram · Receive-side
observations**. Single source configuration: `explainer-script.json`.
`explainer-beats.json` records exact speech-led scene times and music accents.
`EXPLAINER-CLAIMS-TRACE.md` enumerates authored text and recorded UI values.
