# Diode Sentinel: nuances worth demonstrating

Research completed 30 September 2026. Scope: PS-26145 requirement/code audit,
public project descriptions, and a proposed B+C explainer. No detector changes
or new video render were made in this research pass.

## Sources and interpretation

The requirements were read from the repository's verbatim transcription,
[PS-26145.md](../PS-26145.md). The official
[SIH listing](https://sih.gov.in/sih2026PS) returned HTTP 403 to automated access
in this session; its live description was not independently re-verified.
Do not present the local submission counts or dates as current official facts.

Public descriptions of [SENTRY](https://github.com/Yasinali123/Cyber-Threat-Detection)
and [this NTRO prototype](https://github.com/angadmaan/ntro-unidirectional-threat-detection)
already advertise passive ingest, timing/entropy features, ML, evidence and a
SOC dashboard. This supports the inference that those headline features alone
are unlikely to distinguish a pitch. Their implementations and benchmark
numbers were not independently run or validated. This research establishes
useful differentiators to demonstrate, not exclusive features or superiority.

## Existing behavior we can show now

| Detail | Why it matters to the statement | Current evidence | Concrete laboratory demonstration |
|---|---|---|---|
| The clock scores completed traffic windows even after packets stop | Streaming constraint (c) concerns when alerts appear, including quiet links | core/pipeline.py WindowAggregator.tick and StreamProcessor.tick; run.py run_stream; tests/test_live.py | Emit a burst, stop traffic, keep the clock visible, and show the detector output at window close. The design bound must be distinguished from measured end-to-end latency. |
| Short beacon series need stronger regularity | Threat (b) concerns periodic behavior; a few coincidentally regular arrivals are weak evidence | core/detectors.py BeaconDetector.on_flow tightens the CV gate below ten flows; output carries count/mean/CV/gate | Add observations one at a time, then vary jitter. Show actual rule measurements and decisions; establish benign behavior separately before quoting accuracy. |
| Domain morphology requires repeated source evidence | Threat (c) combines query-name features with behavioral context | DGADetector._cnn_only requires the configured consecutive positive streak; source re-alert dedup and severity cap remain active | Display one model-positive query, then a genuine sequence through the loaded CNN. Do not invent model scores, guaranteed benign rejection, or a detector result for the original DNS footage. |
| Known-bad fingerprints cannot enter the learned inventory; warm restart preserves fingerprint context | Threat (d) relies on passively learned metadata; the system should preserve useful context across restarts | TlsDetector.on_hello, load_state/save_state; tests/test_tls_meta.py, tests/test_live.py | Introduce a configured known-bad fingerprint during baseline learning, inspect inventory, restart from saved state and repeat traffic. Protection is for known-bad entries, not every unknown malicious fingerprint. |
| Approved transfers remain visible, with narrowly enforced authorization | Threat (f) needs transfer context and structured evidence; routine approved uploads deserve specific operator context | core/destination_policy.py; ExfilDetector.on_window; tests/test_destination_policy.py | Approve one source/destination/port/protocol and transfer-byte cap. Change one field or exceed the cap and show escalation. Registry matches are context, not an accuracy improvement or blanket trust in cloud IPs. |
| Recent signals are correlated by source and repeated combinations suppressed | Standardized supporting evidence should help triage instead of adding unbounded repeat records | FusionEngine.on_alert and tests/test_fusion.py | Age a signal, add another recent class, replay the same combination, then add a new class. Show decay, reuse suppression and escalation. Distinct classes do not prove independent evidence. |
| Quiet traffic, stopped capture and stale sensor updates have distinct operator states | A live/replay dashboard needs meaningful feed status | core/sensor_health.py; run.py heartbeat; dashboard.py health_view; tests/test_sensor_health.py, tests/test_dashboard_health.py | Pause arrivals while the heartbeat continues, then stop the runner and observe status change. A fresh heartbeat proves runner responsiveness, not visibility of the intended network. |
| Replay has concrete fixtures and parser-distribution checks | A demonstrable prototype should produce inspectable repeatable outputs | .regression/ fixtures; run.py --parity; tests/test_live.py | Show frozen full-alert comparisons separately from dpkt/scapy class-distribution parity. Do not describe the CLI parity check as byte-for-byte record equality. |

## Additions most likely to strengthen the product

### 1. Make every alert inspectable back to its input

The PS background expressly values forensic chain of custody. Add a provenance
sidecar connecting input/capture identity, packet indexes or relevant ranges,
full observed flow keys, window times, named feature values and units,
rule/model artifact identity, and parent alert IDs. Display that chain in the
UI and export a compact offline evidence bundle with hashes.

Current alerts contain useful numeric evidence but do not retain complete
packet lineage or stable parent IDs. AlertSink emits a wildcard source port
in flow_id. Several model views show unnamed numeric arrays. A feature schema
and evidence lineage would make the explanation much more useful to an analyst.
Use an opt-in sidecar/new schema version so the committed regression records
remain unchanged. Hashes identify content; a hash alone does not establish
legal custody, trusted timestamps, or authenticity. Retain capture-sensitive
data according to explicit operator policy.

**Demonstration:** open an alert, select a named measurement, highlight the
contributing observation range, and export the same evidence bundle. This is
a powerful endpoint for the animated mechanism.

### 2. Put a deadline on scoring active flows and bound retained state

Completed windows already score on a clock. Flow-model inference is currently
called when a flow becomes idle or at final drain. A continuously active flow
can keep postponing those model calls. In a read-only diagnostic, sixty packets
one second apart left one flow active and produced zero idle closures:
[nuance-stream-checks.json](nuance-stream-checks.json).

Add clock-driven partial-flow snapshots or a defined maximum flow segment age,
while retaining enough context for packet-sequence models. Limit active flow
and detector state, report eviction/coverage, and account for alert deduplication.
A partial-window feature distribution is a new inference input; evaluate it
rather than assuming the existing training threshold transfers unchanged.

**Demonstration:** leave an encrypted flow continuously active and show a model
inspection before it stops. Also show bounded retained state under many flow
keys, with measured latency/memory curves at stated traffic rates.

### 3. Learn destination context per source and watch several time scales

The current destination first-seen set in WindowAggregator is stream-global.
A destination seen from source A is no longer novel for source B, even if B
has never contacted it. This was reproduced in
[nuance-stream-checks.json](nuance-stream-checks.json). Keep fleet novelty and
per-source novelty as separate named features instead of conflating them.
Add bounded rolling fan-out/transfer summaries over longer horizons to examine
slow scans and transfers spread across short windows.

**Demonstration:** an approved backup host and an unrelated host contact the
same destination; source-relative history distinguishes the situations. Then
spread fan-out across time while the long-horizon view accumulates its evidence.
New detectors require held-out evaluation and explicit thresholds; this is
proposed behavior, not a shipped capability.

### 4. Distinguish missing measurements from actual zeros

encrypted_metadata_features currently fills unavailable metadata counts with
zeros. Add availability masks and reason codes: not observed, parse gap,
unsupported version, or genuine present-but-empty field. Carry sampling/drop
and sensor conditions into the evidence view. Route observations to the models
whose required features are present, or use a model trained with explicit
missingness. Do not relabel a score as a calibrated probability.

**Demonstration:** the same packet rhythm with and without a captured handshake
retains its size/timing analysis, while metadata availability is shown clearly.
This illustrates how the engine reasons from the input it actually received.

### 5. Do not count the same evidence twice in correlation

Fusion currently deduplicates by source and threat class, not by originating
packet/flow lineage. Different models and rules can analyze overlapping data.
Attach parent/evidence IDs and make shared ancestry visible; evaluate grouping
or fusion calibration so extra model votes do not imply independent witnesses.

**Demonstration:** run two models on the same flow and show a shared observation
bundle. Add a genuinely different later behavior and show the evidence expand.
The existing noisy-OR score is heuristic, not an independence guarantee.

### 6. Validate supported protocols with independent standards examples

A concrete defect was found while checking the QUIC claim: core/quic_meta.py
uses a 32-byte Initial salt that differs from the 20-byte value required by
[RFC 9001 §5.2](https://www.rfc-editor.org/rfc/rfc9001.html#section-5.2).
Unmodified key derivation fails the published Appendix A.1 key/IV/header-
protection values. Diagnostic:
[nuance-quic-reference-check.json](nuance-quic-reference-check.json).
The current round-trip tests share the same local builder/derivation, so they
cannot detect this interoperability error. Correct it and add independent
published packet/key fixtures and version validation before demonstrating
real QUIC support. Metadata extraction from publicly protected Initial
handshake bytes must be described separately from application-data decryption.

**Demonstration:** a published supported-protocol fixture produces the expected
metadata; tampered/unsupported inputs are identified explicitly. Prefer one
independent lab capture as well. This is an actionable engineering fix, not
a claim we can safely add to the next film today.

## Recommended order

1. Repair and independently verify QUIC interoperability before any renewed
   QUIC claim. Keep this separate from marketing additions.
2. Add named feature evidence and provenance/export; this gives the analyst
   a concrete capability with a strong visual payoff.
3. Add partial-flow deadlines and state accounting, then evaluate the result.
4. Add per-source/long-horizon context and missingness-aware model inputs.
5. Strengthen shared-evidence correlation after lineage is available.

Existing behaviors above can be shown immediately. Proposed capabilities
should enter the video brief only after implementation and validation.

## Proposed C+B film: approximately 3.5–4 minutes

Use C's unfolding mechanism as a persistent map, then move into B's small
experiments and real software interactions. Natural Indian English narration.
The model's name appears after its input and the question it answers.

| Approximate time | Explanation / visual |
|---|---|
| 0:00–0:20 | Receive-side diode; one packet unfolds into observable fields. |
| 0:20–0:50 | Parallel flow, clock-driven window and protocol branches; real live counters. |
| 0:50–1:25 | Rate/source spread and scanning fan-out experiments; DDoS/UDP rules and Random Forest. |
| 1:25–1:55 | Regularity and sample-size experiment; beacon measurements, then DNS morphology and query-shape checks. |
| 1:55–2:25 | Character CNN, sequence CNN and encrypted-metadata XGBoost; real supported metadata with independent validation. |
| 2:25–2:55 | Transfer volume, baseline and narrow operator authorization; transfer XGBoost and eligible anomaly support. |
| 2:55–3:25 | Source evidence timeline; supporting LightGBM, correlation, repeat suppression and actual UI. |
| 3:25–3:50 | Evidence inspection/export if implemented, restart continuity and sensor health. |
| 3:50–4:00 | Brand and samarags close; Indian English narrator; supplied soundtrack arranged for the longer duration. |

Timing is a proposal, not an approved render instruction. If new features are
not implemented, their scenes remain architectural proposals and must not be
cut into the product demonstration as though they exist. The interactive
companion can use the same graphics and expose controls; video alone is not
interactive. Lab values must be real measured outputs or clearly illustrative.
