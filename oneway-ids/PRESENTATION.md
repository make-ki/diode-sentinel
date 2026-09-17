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

## 2. The eight traps in the statement (ranked by how many teams will hit them)

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
> **dnscat2/iodine** (DNS tunnelling), and DGA samples…"*  (unchanged)
> and class (c): *"Entropy/n-gram analysis of DNS query names, plus
> query-length and **record-type anomalies**."*

**dnscat2 and iodine tunnel over TXT / NULL / CNAME records.** A purely lexical
DGA check will not catch them, because the labels can be short or even
human-looking — the anomaly is the **record type and query rate**, not the
entropy.

Our DNS detector covers the lexical half (entropy, label length, vowel/digit
profile, streak) **and now has a learned Tier-2 model on top of it** — a numpy
1D character CNN, trained with a family-held-out split, that reaches **1.000
recall at 0.001 FP on an unseen DGA family** where the entropy rules get 0.473
at 0.003 FP. It also catches a real query on the *shipped demo capture* that
the rules called benign (`8yuxczaumapqpp`: entropy 3.182 against a 3.3 gate).

What is still missing is `qtype`: we **do not parse record-type anomalies**,
which is the other half of the statement's clause and the half that matters
for dnscat2/iodine (they tunnel over TXT/NULL). See §5 for the honest answer.

---

## 3. Two traps specific to class (a) — be ready before a judge notices

> *"(a) Volumetric / protocol DDoS: **SYN floods, UDP reflection/amplification,
> and spoofed-source floods** identified from flow-level rate and **source-IP
> entropy** statistics."*

**(i) There is no `ddos_syn_flood` in the shipped alert file — and that is
correct.** The spoofed-source branch (distinct source IPs ≥ 500) is checked
first and is strictly *more specific*, so a spoofed SYN flood is reported
**once** as `ddos_volumetric_spoofed`, with `syn_ratio: 0.937` right there in
the evidence (both class-(a) alerts carry `distinct_src_ips` 1535 / 1495 and
`syn_ratio` 0.935 / 0.937). Say that out loud *before* someone greps for
`syn_flood` and finds nothing.

**(ii) "Is entropy actually used in the decision?"** Our decision variable is
**distinct-source cardinality**; Shannon entropy of the source distribution is
computed and carried on the alert. They are the same information — entropy is
bounded by `log2(distinct)` — and cardinality gives a threshold that does not
drift with window occupancy. State it plainly; it is a defence, not a dodge.

**(iii) UDP reflection/amplification is not separately modelled.** It is a
volumetric flood and our rate + entropy path catches the *symptom*, but we do
not characterise the reflection signature (many small queries to one service,
large replies coming back). Own this in §5.

---

## 4. Numbers to quote — and the two you must not oversell

### The rate the statement demands
> *"(d) Defined throughput target: Solutions must **state and demonstrate** the
> traffic rate they were tested against (e.g., flows/sec or **Mbps
> sustained**)."*

This capture: 12,571 packets, 6,691,969 bytes, **599.6 s**, mean packet
**532.3 bytes**, **4,213 distinct flows**, of which 4,449 are SYN-only, 662 DNS,
9,455 TLS.

| Mode | Packets/s | Equivalent sustained rate | Flows/s |
|---|---|---|---|
| Rules only (dpkt) | **44,269** | **≈ 188 Mbps** | 18,077 |
| With ML tier (LightGBM) | **24,687** | **≈ 105 Mbps** | 10,081 |

**Say it exactly like this:** *"44,269 packets per second ≈ 188 Mbps sustained,
single CPU core, pure Python, no C extension and no GPU. With the ML tier
scoring every closed flow, 24,687 packets/s ≈ 105 Mbps."*

The Mbps figure is the mean packet size of *this* capture (532 B) times the
measured packet rate. For a SYN flood the binding number is **packets/s**, not
Mbps — small packets are cheaper per byte, so `pkt/s` is the honest headline
and Mbps is the translation the statement asks for.

### ⚠ Do not lead with "2,113× real-time"
It is arithmetically true (600 s of capture in 0.284 s) but it is **the same
single measurement restated** — and it is large largely because the synthetic
capture is **sparse**: it carries only **21 packets/s ≈ 0.09 Mbps**. Lead with
`pkt/s` and `Mbps` as *capability*; mention the real-time factor only as a
repeatability statement, and volunteer the reason it looks big. A judge who
works that out after you have waved it around will trust the rest of your
numbers less.

### Other numbers, with their mandatory qualifiers
- **6/6** PS threat classes covered, **9 distinct threat classes** emitted,
  33 alerts on the default capture.
- **0 true false positives** — *always* add the qualifier: *after
  operator-curated allowlisting, which suppressed 20 benign periodic events.*
  The `run_stats.json` sidecar exposes that 20 on the dashboard; if you say
  "zero FPs" without the qualifier, someone will find the 20 and call it
  cherry-picking.
- **ML evaluation:** temporal split (t < 420 s train / t ≥ 420 s test — no
  temporal leakage). Benign recall 100%, 0 FP; malicious recall 85.7%, with the
  10 misses documented as **generator label noise** (the model is right, the
  generator-derived labels are wrong on benign DNS from an attack host).
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
- **Tests:** 295 checks across seven suites, all green — `test_tls_meta.py` 42,
  `test_fusion.py` 15, `test_quic.py` 10, `test_live.py` 64,
  `test_dashboard.py` 82, `test_dga_cnn.py` 51 (including a finite-difference
  gradient check on the hand-written backprop), `test_bench_dga.py` 31.
  (PLAN.md still contains the
  intermediate counts from mid-development, e.g. "48 unit tests"; those are
  dated log entries, not current totals. Don't read a total off PLAN.md on
  stage.)

---

## 5. Gaps — rehearse these five answers tonight

Own them before a judge finds them. Volunteering a limitation reads as rigour;
getting caught reads as an overclaim.

| # | Question they will ask | Your answer |
|---|---|---|
| 1 | *"Where is your record-type anomaly for DNS tunnelling? The statement names dnscat2/iodine."* | Lexical half is implemented and tested (entropy, label length, vowel/digit profile, streak) **plus a learned Tier-2 character CNN** (1.000 vs 0.473 recall on an unseen DGA family). Record-type is **not** yet parsed. dnscat2/iodine tunnel over TXT/NULL, so that anomaly is `qtype` + query rate, not entropy — and note the CNN does not cover it either, because it reads the label, not the record type. `qtype` is visible in the query, one-way, with no response needed: it is a ~20-line change in the same code path. Say the size of the change; that proves you scoped it. |
| 2 | *"UDP reflection/amplification? Slowloris?"* | Neither is separately modelled. Reflection/amplification is caught as a volumetric flood symptom by rate + entropy, not by its signature. Slowloris appears in the statement's *dataset suggestions*, not in the scored threat list (a)–(f); one-way it would be a long-lived half-open-flow pattern, which our flow-assembler could carry but we have not built. |
| 3 | *"Your own generator, your own labels — isn't that circular?"* | Partly, and we say so. Three mitigations: temporal splits mean the model never sees the future; the 10 "misses" are generator label noise we publish rather than tune away; and the DGA detector has now been scored **as shipped** on an external, citable corpus — andrewaeva/DGA, 694k real DGA domains / 1M benign, nothing refit (`BENCH-DGA.md`) — where the quorum constant was measured rather than guessed. The flow-feature pipeline takes real datasets through the same path — CTU-13, CIC-IDS, CESNET-TLS22 remain the named next step. |
| 4 | *"Is the live capture actually tested against a real interface?"* | **No — and we say that first.** The development container has `CapBnd: 0`, so no capability can be acquired there at all, not even by root or via a file-capped helper. What *is* verified end-to-end: a real FIFO written in chunks by a separate process reproduces the offline alert stream **byte-for-byte**, plus drop accounting, sampling, interface validation and both privilege-failure paths. The only unexercised piece is the `AF_PACKET` socket setup itself. |
| 5 | *"188 Mbps is a microbenchmark extrapolated from a 0.09 Mbps capture."* | Fair. Dissection is O(1) per packet so pkt/s generalises, and the **1-in-N sampling guard exists precisely because the pure-Python ceiling is ~45k pkt/s single core** — above it we degrade coverage deterministically and **report the loss** rather than hide it. Note the PS says the ingest is *simulated*; the ceiling claim is bounded and stated. |

---

## 6. Things in the repo that exist only because of the constraint

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

## 7. Fifty-second opening script

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
> **First:** the statement asks us for outbound-to-inbound byte ratios for
> exfiltration. One-way, that quantity does not exist — you only ever see one
> direction. We replaced it with bytes to destinations the host has never
> spoken to, measured against that host's own baseline, with an age guard.
>
> **Second:** it offers JA3S as a TLS fingerprint. JA3S is computed from the
> server's hello — the wrong direction. So we use JA4, and we still get it out
> of QUIC, because QUIC Initial keys are public by design.
>
> **Third:** it asks for streaming with bounded latency, not an end-of-run
> report. We had to make the **clock** close our detection windows rather than
> the traffic — otherwise a flood followed by silence sits unscored forever,
> which is unbounded latency on a sensor whose only claim is bounded latency.
>
> We covered all six threat classes. We measured 44,000 packets per second on a
> single core in pure Python — about 188 megabits sustained — and we have a
> dashboard that shows the alert stream with the evidence behind every verdict.
> And where we could not do what the statement asked, we can tell you exactly
> why, and what we did instead."

Then go straight to the dashboard and the four claims above.

---

## 8. If you only remember three sentences

1. **"The statement's own feature — outbound-to-inbound byte ratio — is
   unmeasurable one-way; here is what we used instead, and the arithmetic is on
   every alert."**
2. **"The clock closes our windows, not the traffic — that is the difference
   between bounded latency and an end-of-run report."**
3. **"A one-way feed cannot audit itself, so we audit ours — including a bug we
   found where our own drop-accounting was lying."**
