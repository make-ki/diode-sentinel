# PS-26145 — the parts of the statement most teams will read past

Source: sih.gov.in, Problem Statement **26145**, *AI-Based Detection of Cyber
Threats in Unidirectional IP Traffic*, by **NTRO**, category **Software**,
theme **Blockchain & Cybersecurity**.

Every "what we built" claim below is anchored to a file you can open on stage.
Nothing here is aspirational — where something is a gap, it says so.

---

## 1. The one-line positioning

> The statement does not ask for a threat detector. It asks for a threat
> detector **inside a room with no door**. Anyone can run Suricata on a mirror
> port; the entire difficulty is that we are forbidden from asking the network
> a single question.

Use that framing for the opening. It reframes every judge question from "does
it detect X?" to "did you respect the constraint?" — which is the fight you
win.

---

## 2. The observability contract — this is the actual contribution

Every team will build detectors. The finding that no other submission will
have is a **contract**: we enumerated every feature PS-26145 asks for, and for
each one stated whether it can exist on a one-way feed at all.

The artifact is `observability.py` — 21 rows, each carrying the feature, the PS
class, a status, and the reason it cannot be seen. The statuses:

| Status | Count | Meaning |
|---|---|---|
| `OBSERVABLE` | **15** | computed from the feed; row cites the consuming function |
| `IMPOSSIBLE` | **5** | information-theoretically absent; row states the physical reason |
| `SUBSTITUTED` | **1** | the requested signal is impossible, so a one-way proxy replaces it |

**The headline, and it is a finding about the problem statement itself:**
five of the features the PS *requests* are unsatisfiable under the PS's *own*
constraint (a):

| PS class | Requested feature | Why it cannot exist one-way |
|---|---|---|
| (d) | **JA3S / JA4S server fingerprint** | computed from the ServerHello, sent by the responder — the wrong direction |
| (d) | **negotiated cipher / server certificate** | both chosen by the responder after the handshake, off the observable path |
| (b) | **round-trip time** | needs the response; one-way latency is unmeasurable without a return path |
| (c) | **NXDOMAIN ratio** | RCODE lives in the DNS response header, which the diode never delivers |
| (f) | **outbound-to-inbound byte ratio** | the inbound half is never seen, so the ratio has no denominator |

**Say this line:** *"Five of the features the problem statement asks us to
implement are made impossible by the problem statement's own first constraint.
That is not our limitation — it is the geometry of a diode. A detector that
reads one anyway does not fail loudly, it silently produces garbage, so we
made the contract enforceable rather than descriptive."*

**The gate is real code, not a doc table.** `test_contract.py` scans the
detector sources for forbidden bidirectional tokens — `ja3s`, `server_hello`,
`rcode`, `nxdomain`, `ttl`, `rtt`, `bytes_in`, `in_out_ratio` — and **fails the
build** on a hit. It was verified to fail on an injected `rcode` read and to
pass once removed. So the contract cannot drift out of sync with the
implementation: if someone reaches for a response-side field, CI catches it.

The one `SUBSTITUTED` row is worth its own sentence: UDP reflection is defined
by *response* size, so we substitute per-source UDP fan-out cardinality — the
observable symptom of a host spraying queries at many services.

This is also the honest answer to "what is novel here?" It is not a Zeek config
trick and not a model. It is a proof that a named subset of the requirement
space is empty, plus the machinery that keeps the codebase on the right side of
that line.

---

## 3. The eight traps in the statement (ranked by how many teams will hit them)

### Trap 1 — class (f) asks for a ratio that cannot exist in one direction
> *"(f) Data exfiltration: Asymmetric flow-volume anomalies and **unusual
> outbound-to-inbound byte ratios**."*

On a one-way feed you see **one direction**. There is no inbound half, so an
outbound:inbound byte ratio is **not computable**. Any team that lists it as a
feature is either not actually working one-way, or is quietly using both
directions of a bidirectional capture.

**What we did instead** — two one-way-observable substitutes:

- cumulative bytes to a `(src, dst)` pair that source has **never talked to
  before**, and
- that total against the source's **own median bytes per window**, plus a
  **pair-age guard** so a long transfer cannot slip under the bar in window
  two, three, four…

Every exfil alert carries the arithmetic:
`bytes_to_new_dst`, `src_baseline_bytes_median`, `ratio_vs_baseline`,
`pair_age_windows`. (`detectors.py` → `ExfilDetector`.)

**Say this line:** *"The statement's own feature is unmeasurable one-way. We
replaced it with the closest thing that is measurable, and we put the
replacement's arithmetic on the alert so you can audit it."*

---

### Trap 2 — DGA detection normally leans on NXDOMAIN. There is no DNS response
The standard DGA pipeline reads DNS logs and counts **NXDOMAINs** per host —
that is a *response*. The response travels the opposite direction and never
crosses a diode.

Our alerts state the limitation in their own evidence, verbatim:

> `"note": "response side not observable (one-way); NXDOMAIN correlation unavailable"`

So we detect from the **query alone**: character entropy + vowel/digit lexical
profile of the first label, plus a **streak** requirement across queries from
the same source. (`detectors.py` → `DgaDetector`.)

**Say this line:** *"Everyone's DGA detector secretly depends on the DNS
response. Ours can't, so the alert tells you what it couldn't see."*

---

### Trap 3 — the statement offers JA3S. JA3S is structurally impossible one-way
> *"(d) Malware inside encrypted sessions: Detection from TLS/QUIC metadata
> alone (**JA3/JA3S or JA4** fingerprints, packet-size and timing sequences)"*

JA3S is a **server** fingerprint — computed from the ServerHello, which travels
the other way. Also invisible in a one-way capture: the negotiated cipher
suite, the server certificate, and the ALPN *agreement*.

So three techniques that sound obvious are actually off the table:
JA3S, "self-signed certificate" detection, and server-side cipher inspection.

We compute **JA4** (client) and carry **JA3** alongside, and every alert states
that server-side fields are invisible.

**And the bonus nobody expects:** the one thing that *is* recoverable is QUIC.
QUIC **Initial** packets are decryptable with **no secret at all** — RFC 9001
derives the keys from a public version salt plus the connection ID. So we can
pull a real JA4 out of QUIC traffic on a one-way feed. We proved it rather than
asserted it: the JA4 extracted from a decrypted QUIC Initial is
**byte-identical** to the direct TLS parse (`test_quic.py`), and a
GCM-tampered packet is rejected rather than mis-fingerprinted.

Prep the follow-up: *"isn't that decryption?"* → No payload is decrypted. The
Initial packet is decryptable **by protocol design** with public inputs; no
secret, no key material, no certificate. It is the one place the cryptography
hands you the metadata for free.

---

### Trap 4 — "no return path" also bans techniques *inside your own monitor*
> *"no ability to send probes, complete handshakes with the traffic source, or
> push a mitigation command back"*

Teams bolt on Suricata or Zeek out of the box. Both assume **both halves** of a
conversation: stream reassembly, protocol confirmation, and connection state
all degrade on a one-way feed — you get "partial connection" output and noise.

**And there is a second-order trap almost nobody mentions:** TCP reassembly
normally leans on the **ACK clock** to know what it has already seen. On a
one-way feed there are no ACKs, so retransmits and gaps must be detected
yourself. We wrote a sequence tracker for exactly this, on the reasoning that
**a wrong fingerprint is worse than no fingerprint** (`tls_meta.py` →
`SeqTracker`).

---

### Trap 5 — "streaming, not batch" is the constraint that eliminates most submissions
> *"(c) Streaming, not batch: The pipeline must process traffic incrementally
> and raise alerts with **bounded latency**, not just produce an end-of-run
> report."*

Most submissions load the pcap into pandas, compute features over the whole
capture, and print a report. That is explicitly out of scope.

The **subtle** half nobody gets: a tumbling-window aggregator that only closes
a window *when the next packet arrives* **cannot score a flood followed by
silence**. The flood ends, the link goes quiet, and the verdict sits unscored —
**unbounded latency on a sensor whose entire claim is bounded latency**. The
clock has to close windows, not the traffic.

We have that idle-aware tick, and we prove it **by contrast** in the tests:
freeze the clock and the flood verdict only appears at end-of-run; advance the
clock and it appears *during* the capture (`test_live.py`).

**Quote the budget:** ≤ 2 s flow-idle timeout + ≤ 10 s window, bounded **by
construction**, not measured as a tail.

---

### Trap 6 — "read-only ingest" includes your capture plumbing
> *"(a) Read-only ingest: Treat the input as strictly read-only."*

Everyone reads this as "don't touch the traffic". The reverse is where teams
lose points — **your own capture path can silently destroy the guarantees you
just claimed:**

- a FIFO writer that is **not packet-buffered** (`dumpcap` without `-U`)
  buffers whole seconds → your bounded-latency claim is quietly gone;
- `PACKET_STATISTICS` is **read-and-clear**, so drops must be tracked as
  deltas;
- **the remote feed can never report its own loss — but your capture path's
  loss is visible and must be reported, not hidden.** We found a real
  silent-discard bug where ICMP/GRE/ESP frames were dropped without
  incrementing any counter, which made thrown-away frames look *processed*.
  Fixed with an explicit counter plus a tested invariant: the accounting
  buckets must **partition** everything seen (`live_source.py`).

**Say this line:** *"A one-way feed cannot audit itself. So we audit ours, and
we found a bug where our own accounting was lying."*

---

### Trap 7 — "clean chain of custody for forensic use" is a real requirement
Forensic means **reproducible** and **accurate**. Two concrete things:

- **Reproducible:** offline replay and `--ml` reproduce the original alert
  files **byte-for-byte** against committed regression fixtures, and backend
  parity is asserted (`--parity`: dpkt vs scapy produce **identical** alert
  distributions). A replay today matches a replay from last week.
- **Accurate:** we found our own evidence-integrity bug — live alert
  timestamps rendered the millisecond field **one second off**, because the
  anchor's fractional part and `t % 1` disagreed. Completely invisible offline
  (whole-number anchor), fatal live. Fixing it mattered because **the timestamp
  is evidence**.

---

### Trap 8 — the statement names the dataset that should scare you
> Dataset link: *"attack traffic from hping3 (SYN/UDP floods), **Slowloris**,
> **dnscat2/iodine** (DNS tunnelling), and DGA samples…"*
> and class (c): *"Entropy/n-gram analysis of DNS query names, plus
> query-length and **record-type anomalies**."*

**dnscat2 and iodine tunnel over TXT / NULL / CNAME records.** A purely lexical
DGA check will not catch them, because the labels can be short or even
human-looking — the anomaly is the **record type and query rate**, not the
entropy.

Our DNS detector now covers **both halves of that clause**. The lexical half
(entropy, label length, vowel/digit profile, streak); and the record-type half,
which we added precisely because the statement asked for it and it is one-way
observable by construction — the client writes the qtype into the query, so no
response is needed. `_tunnel_check` fires on **record-type anomaly** (a TXT/NULL
query from a host that has only ever sent A/AAAA), **query length**, and **max
label length**. On the shipped capture it emits 4 `dns_tunneling` alerts at up
to 0.97 confidence on the host running a base32-chunked TXT tunnel, and fusion
correlates those with the exfil signal into a single `confirmed_exfiltration`
verdict. The query itself is the exfiltrated data; we never see the response and
never need to.

The lexical half also has a learned Tier-2 model on top of it — a numpy
1D character CNN, trained with a family-held-out split, that reaches **1.000
recall at 0.001 FP on an unseen DGA family** where the entropy rules get 0.473
at 0.003 FP. It also catches a real query on the *shipped demo capture* that
the rules called benign (`8yuxczaumapqpp`: entropy 3.182 against a 3.3 gate).

**The honest boundary:** the CNN reads the *label*, not the record type, so it
does not cover the tunnelling half — that is what the qtype check is for. And
NXDOMAIN correlation remains impossible (see the contract, §2), which is the
usual crutch a DGA detector leans on.

---

## 4. Two traps specific to class (a) — be ready before a judge notices

> *"(a) Volumetric / protocol DDoS: **SYN floods, UDP reflection/amplification,
> and spoofed-source floods** identified from flow-level rate and **source-IP
> entropy** statistics."*

**(i) There is no `ddos_syn_flood` in the shipped alert file — and that is
correct.** The spoofed-source branch (distinct source IPs ≥ 500) is checked
first and is strictly *more specific*, so a spoofed SYN flood is reported
**once** as `ddos_volumetric_spoofed`, with the `syn_ratio` right there in the
evidence (on the shipped capture, ~0.93 for both class-(a) alerts, each also
carrying `distinct_src_ips` in the ~1,500 range — the exact counts shift with
the generator's spoofed-source draw, so read them off the alert, don't memorise
them). Say that out loud *before* someone greps for `syn_flood` and finds
nothing.

**(ii) "Is entropy actually used in the decision?"** Our decision variable is
**distinct-source cardinality**; Shannon entropy of the source distribution is
computed and carried on the alert. They are the same information — entropy is
bounded by `log2(distinct)` — and cardinality gives a threshold that does not
drift with window occupancy. State it plainly; it is a defence, not a dodge.

**(iii) UDP reflection/amplification is not separately modelled.** It is a
volumetric flood and our rate + entropy path catches the *symptom*, but we do
not characterise the reflection signature (many small queries to one service,
large replies coming back). Own this in §6.

---

## 5. Numbers to quote — and the two you must not oversell

### The rate the statement demands
> *"(d) Defined throughput target: Solutions must **state and demonstrate** the
> traffic rate they were tested against (e.g., flows/sec or **Mbps
> sustained**)."*

This capture: **14,049 packets, 8,622,217 bytes, 598.8 s**, mean packet
**613.7 bytes**, **5,225 distinct flows**, of which 4,617 are SYN-only, 720 DNS,
7,107 TLS.

| Mode | Packets/s | Equivalent sustained rate | Flows/s |
|---|---|---|---|
| Rules only (dpkt) | **≈48,600–50,400** | **≈ 240 Mbps** | ≈19,200–20,300 |
| With ML tier (LightGBM) | **≈24,000–31,000** | **≈ 120–155 Mbps** | ≈9,700–11,800 |

Measured over repeated runs on one CPU core, pure Python, no C extension and no
GPU. The rules tier is tight across runs; the ML tier varies more with model
warm-up and cache state, so it is quoted as a range — a single false-precision
number would not be reproducible. The Mbps figures use this capture's mean
packet size (613.7 B).

**Say it exactly like this:** *"About 50,000 packets per second — roughly 240
Mbps sustained — on a single CPU core, in pure Python with no C extension and
no GPU. With the ML tier scoring every closed flow it drops to roughly 24 to 31
thousand packets per second."*

The Mbps figure is the mean packet size of *this* capture (613.7 B) times the
measured packet rate. For a SYN flood the binding number is **packets/s**, not
Mbps — small packets are cheaper per byte, so `pkt/s` is the honest headline
and Mbps is the translation the statement asks for.

### ⚠ Do not lead with the real-time factor
It is arithmetically true (600 s of capture processed in well under a second,
so roughly 2,000× real-time — the exact digit varies with run-to-run cache
state, so quote "~2,000×", not a precise figure) but it is **the same single
measurement restated** — and it is large largely because the synthetic
capture is **sparse**: it carries only **23 packets/s ≈ 0.11 Mbps**. Lead with
`pkt/s` and `Mbps` as *capability*; mention the real-time factor only as a
repeatability statement, and volunteer the reason it looks big. A judge who
works that out after you have waved it around will trust the rest of your
numbers less.

### Other numbers, with their mandatory qualifiers
- **6/6** PS threat classes covered, **12 distinct threat classes** emitted by
  the rules tier (13 including the ML tier's `ml_flow_suspicious`),
  45 alerts on the default capture (67 with the ML tier), plus 20 benign
  periodic events suppressed by the allowlist.
- **False positives — the measured answer, not the headline you want.** On the
  default capture the rules tier emits **45 alerts, every one on a host the
  generator designates as an attacker**; that is zero FPs. But we built a
  deliberate FP-pressure variant (`MESSY=1`) that injects *benign* patterns a
  real network has: first-time cloud-backup uploads, low-jitter IoT telemetry,
  CDN-style long subdomain labels. On it the rules tier emits **one true
  critical FP — `data_exfiltration` at 0.95 on the benign backup host** —
  because "large sustained upload to a never-before-seen destination" is
  *exactly what a backup is*. Own that on stage; it is the honest cost of a
  one-way exfil detector that cannot ask "was that authorised?"
  Do **not** say "zero false positives" without the FP-pressure qualifier.
  Also do not lean on the allowlist count as a result: `ALLOWLIST` in
  `config.py` is operator-curated against the same three telemetry IPs the
  generator emits, so "zero FPs after allowlisting" is partly circular.
- **ML evaluation:** temporal split (t < 500 s train / t ≥ 500 s test — no
  temporal leakage). Benign recall 100%, 0 FP; malicious recall 85.7%, with the
  10 misses documented as **generator label noise** (the model is right, the
  generator-derived labels are wrong on benign DNS from an attack host).
- **⚠ Do not headline `--models-567` as six working models.** Its own
  `models567/eval.json` is the honest record. **Four** of the six —
  `encrypted_xgb`, `sequence_cnn`, `scan_rf`, `exfil_xgb` — reach recall
  **1.000** at **0** benign FP on the temporal holdout (t ≥ 390 s). The other
  two are the IsolationForest pair, and they are a *measured negative result*,
  not a tuning issue: they do detect every malicious row, but only at
  thresholds where they also fire on 2–6% of benign windows; tighten past that
  and they go blind. **No operating point is both sensitive and quiet**, so the
  threshold selector ships the quiet point and reports recall 0.000 rather than
  hiding a noisy one. Say "four of six, and the two that fail are the
  unsupervised ones — here is the sweep that shows no good operating point
  exists." The supervised models are the deployable ones.
  Also worth saying, because it is the more interesting half of the story: the
  `scan_rf` and `exfil_xgb` models used to read 0.000 too, and that was **not**
  a model failure — the temporal split placed every malicious scan and exfil
  row in training, so the holdout had nothing to score. Once the generator
  emitted attack bursts on both sides of the split, the same architectures
  scored perfectly. "Unmeasurable" and "broken" are different claims, and the
  old table conflated them.
- **⚠ The ML tier breaks under FP pressure.** On the `MESSY` capture the
  supervised flow model emits **74 `ml_flow_suspicious` alerts at confidence
  1.0, almost all on benign hosts** (IoT telemetry, backup, ordinary web
  browsing) — benign traffic shapes absent from its training capture. This is
  the measured reason the rules tier stays primary and the ML tier is
  quorum-gated. If a judge asks "does the ML model generalise?", this is the
  answer, and it is not a comforting one.
- **The tier-boundary lesson:** per-flow ML on bare SYN packets produced
  **3,021 alerts**; excluding bare SYNs at the tier boundary and letting the
  aggregate detectors own them brought it to **20**, all on true attack hosts.
  This is a *maturity* signal — quote it when someone asks about false
  positives.
- **The DGA CNN (the strongest model result you have).** A 1D character CNN,
  4,930 parameters, numpy only. Family-held-out, one held-out family of each
  kind:

  | Held-out family | CNN recall | rule recall |
  |---|---|---|
  | `hex_like` (same kind, unseen family) | **1.000** | 0.473 |
  | `dictionary_pair` (different kind) | 0.007 | 0.004 |
  | benign FP rate | **0.001** | 0.003 |

  And the line to actually say: *"On our demo capture the CNN caught a real
  DGA query the rules called benign — entropy 3.182 against a 3.3 gate.
  That miss is caused by the exact short-string entropy bias we documented in
  our README's lessons section before we built the model."* Present the
  dictionary row too: morphology alone cannot settle dictionary DGA, which is
  why the CNN is a quorum-gated confirmer, never labelled critical.

- **The external corpus (the answer to "isn't this all self-play?").**
  `bench_dga.py` scores the shipped, un-retouched detector on
  `andrewaeva/DGA` — 694,173 real DGA domains across 8 named malware
  families against 1,000,000 Alexa domains, model loaded exactly as
  committed (`BENCH-DGA.md`). Three measured stories:

  - *The rules have a blind spot we predicted.* The entropy gate's
    10-character length floor scores **0.019 / 0.000** TPR on conficker and
    pushdo (median labels: **8** chars); the CNN, which has no length floor,
    scores **0.886 / 0.446** on exactly those families.
  - *The CNN alone is not deployable.* Its per-string false-positive rate on
    1M real benign domains is **16.5%** — real hostnames include `ccmhw`,
    `7ri-rj`, `059455`, which no morphology model separates from DGA. That
    is not hidden: it is the measured reason the quorum exists.
  - *The shipped quorum is a measured constant, not a guess.* Swept against
    1M benign queries: **17.3 alerts/hour** on a purely benign host at k=2,
    **0.46 at k=4** with 7/8 families still detected. The honest cost, said
    out loud: at k=4 the demo capture no longer shows a CNN-only alert —
    the sensor that cried wolf 17×/hour was worse than missing one label.

  Also own it before someone finds it: rovnix and matsnu are **not**
  separated per-string (0.226 / 0.257) and no CNN threshold fixes it, and
  mixed-host precision at 5% DGA prevalence is 0.171 — the layered policy is
  what keeps the benign case quiet, not the CNN alone.
- **Tests:** 323 checks across ten suites, all green — `test_tls_meta.py` 35,
  `test_fusion.py` 19, `test_quic.py` 10, `test_live.py` 70,
  `test_dashboard.py` 75, `test_dga_cnn.py` 51 (including a finite-difference
  gradient check on the hand-written backprop), `test_bench_dga.py` 31,
  `test_metrics.py` 19, `test_contract.py` 6, `test_models_567.py` 7.
  (PLAN.md still contains the
  intermediate counts from mid-development, e.g. "48 unit tests"; those are
  dated log entries, not current totals. Don't read a total off PLAN.md on
  stage.)

### Real-dataset validation — IoT-23 (the answer to "isn't this all self-play?")

The synthetic capture is our own generator with our own labels, and Gap 3 says
so plainly. So we validated against a real public dataset: **IoT-23** (CTU
Stratosphere Laboratory, 2020, CC-BY-4.0) — real infected IoT devices, real
malware, with Zeek `conn.log` labels as ground truth. Nothing was retuned; the
shipped detector ran on each scenario as committed.

Scoring is **per host, not per flow**, and the reason matters: Mirai worm-spread
makes one infected host emit tens of thousands of Zeek-"Benign" scan flows, so
per-flow precision looks like 0.017 when the detector is actually right. A host
is the unit an analyst responds to.

| Scenario | Malware | LAN infected | Alerts | Host recall | Host precision |
|---|---|---|---|---|---|
| Capture-8-1 | Hakai | 1 | 206 | **1.000** | **1.000** |
| Capture-1-1 | HideNSeek | 1 | 38,401 | **1.000** (flagged the infected host, 0 clean-host FPs) | — |
| Capture-42-1 | Trojan | 1 | 0 | **0.000 — a total miss** | — |
| Honeypot-4-1 | *benign* Philips HUE | 0 | 8 | — | **0.000 — real FP** |

**What generalizes, and what does not:**

- **The C2-beaconing detector generalises to real malware with no retuning** —
  perfect host recall on Hakai and HideNSeek, two different families on two
  different captures. Periodicity is periodicity regardless of the botnet.
- **A real, honest miss.** Capture-42-1 has six malicious C&C-FileDownload
  flows and we raised **zero** alerts. The Trojan's traffic did not trip any
  one-way signal we currently compute. Say this before anyone finds it.
- **A real, structural false positive.** The benign Philips HUE smart bulb
  phoning home to Google (216.239.35.x) and AWS (52.209/52.215) fires as **C2
  beaconing** — low-jitter periodic traffic to a small set of cloud
  destinations is *exactly* what beaconing looks like one-way. This is not a
  tuning bug; it is a fundamental confound for a one-way egress monitor, and it
  is the same reason the `ALLOWLIST` exists. Every one-way IDS has to answer
  for this, and most do not notice.
- The 38,401 alerts on Capture-1-1 include ~37.7k `recon_*` flows from the
  single infected host — a **scoring artifact** of worm-spread, not detector
  error. Per-host scoring is what keeps that readable.

**This is the strongest unclaimed result in the repo and it belongs in the
deck.** Two real malware families detected with no retuning, one honest miss,
one structural FP — all on public, citable data. Cite it as: Parmisano, Garcia,
Erquiaga, "IoT-23 dataset", Stratosphere Lab, 2020, CC-BY-4.0.

---

## 6. Gaps — rehearse these five answers tonight

Own them before a judge finds them. Volunteering a limitation reads as rigour;
getting caught reads as an overclaim.

| # | Question they will ask | Your answer |
|---|---|---|
| 1 | *"Where is your record-type anomaly for DNS tunnelling? The statement names dnscat2/iodine."* | **Implemented.** Both halves of class (c) are covered: the lexical half (entropy, label length, vowel/digit profile, streak, plus a learned character CNN — 1.000 vs 0.473 recall on an unseen DGA family) and the record-type half (`qtype` anomaly for TXT/NULL, query length, max label length). `qtype` is parsed in `pcap_reader.py` and `live_source.py` and threaded through the packet tuple; `_tunnel_check` fires on it, and 4 `dns_tunneling` alerts at up to 0.97 fire on the shipped capture. All three signals are written by the client into the query, so all three are one-way observable with no response — unlike RCODE/NXDOMAIN, which the observability contract marks IMPOSSIBLE and the detector never reads. What is *not* covered: the CNN reads the label, not the record type, so tunnelling detection is rule-based only; and we have no dnscat2/iodine capture to test against, only a synthetic base32 TXT tunnel built to look like one. |
| 2 | *"UDP reflection/amplification? Slowloris?"* | Neither is separately modelled. Reflection/amplification is caught as a volumetric flood symptom by rate + entropy, not by its signature. Slowloris appears in the statement's *dataset suggestions*, not in the scored threat list (a)–(f); one-way it would be a long-lived half-open-flow pattern, which our flow-assembler could carry but we have not built. |
| 3 | *"Your own generator, your own labels — isn't that circular?"* | Partly, and we say so. Four mitigations, in increasing strength: temporal splits mean the model never sees the future; the 10 "misses" are generator label noise we publish rather than tune away; the DGA detector is scored **as shipped** on an external, citable corpus — andrewaeva/DGA, 694k real DGA domains / 1M benign, nothing refit (`BENCH-DGA.md`) — where the quorum constant was measured rather than guessed; and **the whole sensor has now run against real malware on IoT-23** (CTU Stratosphere, CC-BY) with Zeek ground truth — perfect host recall on Hakai and HideNSeek, an honest total miss on a Trojan, and one structural cloud-telemetry FP. See §5. That is the answer that survives scrutiny: not "we will validate on real data", but "here is where we already did, including the misses." |
| 4 | *"Is the live capture actually tested against a real interface?"* | **No — and we say that first.** The development container has `CapBnd: 0`, so no capability can be acquired there at all, not even by root or via a file-capped helper. What *is* verified end-to-end: a real FIFO written in chunks by a separate process reproduces the offline alert stream **byte-for-byte**, plus drop accounting, sampling, interface validation and both privilege-failure paths. The only unexercised piece is the `AF_PACKET` socket setup itself. |
| 5 | *"240 Mbps is a microbenchmark extrapolated from a 0.11 Mbps capture."* | Fair. Dissection is O(1) per packet so pkt/s generalises, and the **1-in-N sampling guard exists precisely because the pure-Python ceiling is ~50k pkt/s single core** — above it we degrade coverage deterministically and **report the loss** rather than hide it. Note the PS says the ingest is *simulated*; the ceiling claim is bounded and stated. |

---

## 7. Things in the repo that exist only because of the constraint

Use these as "we went further than the brief" — each is a direct consequence of
one-way, not a generic feature.

1. **Cross-signal fusion** (not asked for). Two weak one-way signals become one
   strong verdict: beacon + known-bad JA4 → `confirmed_c2_implant`; beacon +
   DGA → `botnet_c2_with_dga`. Fire-on-escalation semantics, so an ongoing
   incident does not re-fire a critical alert every window.
2. **Restart-safe fingerprint inventory** (`--state`). Without warm-start, a
   sensor restart blinds novelty detection for another baseline period —
   *exactly the window an attacker would choose.* The baseline gate is skipped
   on a warm load, not just the inventory.
3. **Baseline poisoning prevention.** Known-bad TLS handshakes are **never**
   fed into the inventory, so an ongoing attack cannot teach the sensor that it
   is normal.
4. **Operator-curated allowlist, deliberately not auto-learned.** Auto-learning
   periodic traffic whitelists existing botnets — the same workflow RITA and
   AC-Hunter force on analysts.
5. **Evidence-scaled statistical gates.** Sampling CV at n=6 is noisy: a benign
   exponential process dips under a fixed gate by luck ~2% of the time. So the
   gate is tight for small n and standard for n ≥ 10. (This was found by a real
   benign DNS poll landing at CV 0.2249 against a 0.25 gate.)
6. **Every alert carries a human-readable `why`** next to the machine-readable
   feature values. The statement asks for "supporting evidence feature"; a
   label plus a score is not triageable at 03:00.
7. **A second, independently trained model on a different input type** — the
   DGA character CNN reads the *string*; the LightGBM tier reads *tabular flow
   statistics*. Different data, different failure modes, and the CNN's win is
   attributable to a specific documented bias in the rules rather than to
   "more ML". It is also numpy-only, so it adds no dependency to a project that
   has been careful about that.

---

## 8. Fifty-second opening script

> "This is PS-26145 — threat detection in unidirectional IP traffic, from
> NTRO. The statement is not really about threat detection; it is about
> detection **inside a room with no door**. Critical-infrastructure operators
> copy their gateway links into a monitoring enclave through a hardware data
> diode, and that enclave has no path back. So we may never send a probe,
> never complete a handshake, and never decrypt a payload.
>
> Every detector in this system runs on **one direction of traffic**. That
> turns out to break most of the standard playbook, and those are the parts we
> want to show you.
>
> **First, and this is our actual contribution:** we enumerated every feature
> the statement asks for and asked which of them can exist on a one-way feed at
> all. **Five of them cannot** — JA3S, the negotiated cipher and server
> certificate, round-trip time, the NXDOMAIN ratio, and the
> outbound-to-inbound byte ratio. Five of the problem statement's own requested
> features are made impossible by the problem statement's own first
> constraint. That is a finding about the problem, not a limitation of our
> code, and we enforce it: a CI test fails the build if any detector reaches
> for a response-side field.
>
> **Second:** where a requested feature is impossible, we built the closest
> observable substitute and put its arithmetic on the alert. Exfiltration
> becomes bytes to a destination the host has never spoken to, against that
> host's own baseline. JA3S becomes JA4 — and we still extract it from QUIC,
> because QUIC Initial keys are public by design.
>
> **Third:** it asks for streaming with bounded latency, not an end-of-run
> report. We had to make the **clock** close our detection windows rather than
> the traffic — otherwise a flood followed by silence sits unscored forever,
> which is unbounded latency on a sensor whose only claim is bounded latency.
>
> We covered all six threat classes. We measured about 50,000 packets per
> second on a single core in pure Python — roughly 240 megabits sustained —
> and we validated
> against real malware on the IoT-23 public dataset: two families detected with
> no retuning, one honest miss, one false positive we can explain. And where we
> could not do what the statement asked, we can tell you exactly
> why, and what we did instead."

Then go straight to the dashboard and the four claims above.

---

## 9. If you only remember three sentences

1. **"Five of the features the problem statement requests are impossible under
   its own first constraint — we enumerated them, substituted one-way signals,
   and made the constraint enforceable in CI so the code cannot silently
   reach for a response that never arrives."**
2. **"The clock closes our windows, not the traffic — that is the difference
   between bounded latency and an end-of-run report."**
3. **"We ran it against real malware on IoT-23, not just our own generator:
   two families detected with no retuning, one honest miss, and one false
   positive that is structural to one-way monitoring rather than a bug."**
