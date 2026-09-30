# Hackathon edge: ten-hour proof-first plan

**Status: planning only.** The user set a ten-hour elapsed window. Plan on
three independent Luna workers alongside the root agent, with integration and
review done sequentially. Parallelism can reduce elapsed time; it does not
guarantee all work will finish. This is a selected first-wave MVP. The complete roadmap is
backlog, roughly **2–4 weeks for one developer** or **1–2 weeks with independent
workstreams**, plus any time waiting on outside data or lab hardware.

The product position is: **“A passive sensor that turns one-way traffic into
explainable, traceable, timely threat evidence.”** This is a proof target, not
a promise of winning or superiority. The first ten hours should earn a
reviewable demonstration by addressing protocol correctness, traceable alert
evidence, source-local context, and repeatable scenarios. Do not present
planned behavior as shipped or expand the scope into a full model rewrite.

The boundary is [PS-26145.md](../PS-26145.md): read-only one-way input, no
probes or source queries, no response path or mitigation, no payload
decryption. Keep the implementation pure Python and suitable for an offline
enclave. No GPU, Torch, large distributed stack, external runtime service, or
new web framework is needed for this proof.

## Existing work to reuse

| Existing artifact | Verified capability | Limit to state accurately |
|---|---|---|
| `core/observability.py`, `tests/test_contract.py` | One-way feature registry and a source-token test for forbidden response-side fields. | Literal scanning is a narrower guarantee than typed dependency coverage; optional model adapters are not all enumerated by the current gate. |
| `core/pipeline.py`, `run.py`, `tests/test_live.py` | Shared replay/live processor, clock-driven traffic-window close, quiet-window test, FIFO replay, and selected live/offline aggregate parity. | `run.py --parity` compares threat-class counts. Existing live/offline test checks counts/classes, not every packet record or complete alert JSON record. |
| `core/sensor_health.py`, dashboard views/tests | Heartbeat, stale, stopped, and failed sensor states. | A fresh heartbeat shows the runner is responsive; it does not prove the intended feed is present or loss-free. |
| `demo.sh`, `demo_replay.py`, `tests/test_demo_smoke.py` | Synthetic pcap can be paced through the live FIFO path; alerts appear before replay ends. | This is not a physical AF_PACKET test or an interactive multi-case judge runner. |
| DGA CNN, `training/bench_dga.py` | Numpy character CNN, gradient checks, family-held-out and external-corpus evaluation, and measured quorum tradeoff. | Those results apply to the stated DGA data and setup, not the entire detector stack. |
| `core/destination_policy.py` and tests | Narrow source/destination/port/protocol/byte authorization with continued visibility of transfers. | A registry or allow rule is context, not evidence that a provider or host is benign. |
| `training/score_iot23.py`, `tests/test_iot23.py`, `docs/iot23-validation.md` | Local input scorer with hashes and host-level outcomes. | Historical PCAP and `conn.log` are unavailable here; the existing scorer cannot recreate old measurements without matching files. |
| `.regression/alerts_rules.reference.jsonl`, `alerts_ml.reference.jsonl` | Byte-stable synthetic replay outputs for the named tiers. | Preserve these files; use separate versioned fixtures for intentional changes. |

## Ten-hour elapsed schedule

Hours are elapsed from the start. Work packets may run in parallel only when
they have separate files/interfaces; the root agent reviews and integrates
results at each boundary. Budgets below are capacity estimates, not completion
promises. Reserve the final two hours for integration rather than adding scope.

| Elapsed | Parallel work and targets | Exit check |
|---|---|---|
| **0–0.5 h** | Root: inspect git/status and current regression hashes; create isolated output locations; start a claims ledger mapping each demo claim to code, fixture, and status. Freeze existing `.regression` baselines. | Baseline known, outputs isolated, no data downloads or live production capture. |
| **0.5–2 h** | Worker A: QUIC RFC check/fix in `core/quic_meta.py`, `tests/test_quic.py`, frozen fixtures under `tests/fixtures/quic/`. Worker B: evidence v2 schema and names/units/missingness/provenance skeleton in a new sidecar module/schema docs. Worker C: dashboard data model for evidence timeline and scenario metadata, without changing legacy alert JSON. Root: typed one-way feature contract additions in `core/observability.py`/`tests/test_contract.py`. | Independent fixtures establish QUIC key/IV/HP and packet behavior; schema/interface reviewed before cross-cutting implementation. |
| **2–4.5 h** | Root: analyst evidence sidecar export and timeline for a representative alert path; implement stable joins and metadata redaction. Worker A: source-relative novelty as a separate `(src,dst)` observed-history map, leaving legacy novelty untouched; add opt-in Exfil eligibility. Worker B: one opt-in 60-second scan horizon built from six 10-second windows, with distinct endpoint-pair evidence, deduplication, per-source caps, and TTL. Repeated endpoints do not inflate distinct counts; after a gap over 60s the rollup ages out. Track history loss so an expired/evicted history is not silently described as “first-ever novel.” Worker C: deterministic scenario manifest/runner scaffold reusing `demo.sh`, `demo_replay.py`, and the dashboard. | At least one alert can be traced to named observations and source-context tests distinguish source novelty from fleet novelty. New rule-v2 behavior is opt-in; every new history structure has a cap/TTL and visible loss/eviction behavior. |
| **4.5–6 h** | Integrate evidence lineage and source-local context. Add a minimal incident timeline/grouping view only if ancestry IDs are stable; group records deterministically and retain originals. Add small offline MITRE candidate tags only if rationale, prerequisites, and pinned ATT&CK version are explicit. Model views must show named inputs or abstention, not invented feature importance. | Shared evidence is shown as shared ancestry, not independent votes or a new probability. If IDs/schema are unstable, leave incident grouping and tags as backlog. |
| **6–8 h** | Finish four deterministic acceptance scenarios and focused behavior tests: (1) QUIC reference and malformed packet; (2) source novelty plus 60-second scan union, repeated endpoint, and >60-second expiry; (3) evidence sidecar join with unavailable metadata; (4) quiet-window close plus stale/stopped health. Add packet-record/full-alert parity on the small fixtures. Run latency/RSS smoke measurements on controlled synthetic input; report duration/rate and limitations. Review output hashes against frozen references. | Four reproducible commands, first-difference failures, behavior tests, and legacy regression gate. Measurements are labeled smoke tests, not sustained-capacity evidence. |
| **8–10 h** | Sequential integration, regression fixes, claims-ledger update, final scenario walkthrough, freeze. Regenerate the honest deck source only if measured claims changed and output write access is available. Capture a current UI/demo walkthrough for later film production; do not spend the core window rendering a film. | A fresh checkout/operator can run the named scenario and inspect resulting evidence; unsupported capabilities remain labeled planned or unsupported. |

### Required ten-hour scope and cut lines

**Required if the corresponding code passes review:** QUIC independent RFC
fixtures and retry correctness; evidence sidecar with stable joins, named
features and honest missingness; source-relative novelty stored separately
from legacy fleet novelty; opt-in Exfil eligibility; one 60-second scan union
of six 10-second windows with distinct-pair evidence, deduplication, per-source
caps/TTL, and explicit history-loss state; deterministic scenarios; full
record parity on representative fixtures; truthful claims ledger. Keep
remaining work in backlog if any integration gate fails. New v2 history must
be bounded; do not claim that every legacy state structure becomes bounded in
this window.

The core deliverables have the following acceptance gates. These are proposed
tests and policies, not results already obtained:

| Ticket | File targets | Behavior required to finish |
|---|---|---|
| E01: standards-correct QUIC | `core/quic_meta.py`, `core/tls_meta.py`, independent fixtures, `tests/test_quic.py` | Published key/IV/header-protection values and packet metadata match; unsupported/tampered inputs are handled; a failed first parse does not suppress a later valid Initial. |
| E02: traceable alert evidence | New sidecar/feature schema, `core/detectors.py`, model adapters, dashboard detail view/export | One rule alert and one model alert export named measurements with units, actual observation scope, artifact identity, missingness, and a stable join back to their unchanged source records. |
| E03: source-relative history | `core/pipeline.py`, `core/detectors.py`, config and behavior tests | When A visits X, then B visits X, B's source-relative first contact is distinguished from fleet novelty; old behavior remains identical with the option off. |
| E04: slow scan context | Scan detector/config and scenario tests | Ten new endpoints in each of two adjacent windows cross a provisional 20-endpoint gate; repeated endpoints do not inflate counts; evidence more than 60 seconds apart does not combine. |
| E05: reviewable demo and proof | Existing demo runner, new scenario manifests, fixture parity tests, claims ledger | Cases reset independently, inputs/outputs have identities, packet and complete-alert differences are actionable, and historical regression files remain unmodified. |

Do not pass rolling scan features to the existing single-window Random Forest
without matching validation. An expired/evicted history entry is not proof
that a destination was never seen; expose coverage loss and describe novelty
against the retained observation horizon.

**Conditional:** minimal incident grouping, MITRE candidate context, named
model-input view, and a brief dashboard timeline, only after evidence ancestry
is stable. MITRE is context, not a detector verdict. [T1046 Network Service
Discovery](https://attack.mitre.org/techniques/T1046/) may fit qualifying scan
evidence; [T1568.002 DGA](https://attack.mitre.org/techniques/T1568/002/) may fit
supported DGA evidence. [T1071.004 DNS](https://attack.mitre.org/techniques/T1071/004/)
needs sufficient DNS C2 context; a qtype or DNS-volume anomaly alone is not
enough. Pin an ATT&CK version and show rationale if tags are added.

**Defer:** new active-flow model inference unless model eligibility is
independently validated; partial packet-sequence scoring without matched
training/recalibration; broad redesign of all six detectors; long-horizon
exfiltration model; comprehensive model calibration; FFT/HLL or another
IsolationForest; dataset downloads and historical IoT-23 re-scoring; hardware
capture validation; and the four-minute film. These exceed the ten-hour MVP or
depend on unavailable inputs.

## Engineering notes and acceptance criteria

### QUIC and the compatibility gate (P0)

`docs/nuance-quic-reference-check.json` records that current
`core/quic_meta.py` has a 32-byte QUIC v1 salt where RFC 9001 specifies 20
bytes. The current round-trip tests share the local builder and derivation,
which is why they miss the interoperability error. Correct and independently
verify [RFC 9001 §5.2](https://www.rfc-editor.org/rfc/rfc9001.html#section-5.2),
[Appendix A.1](https://www.rfc-editor.org/rfc/rfc9001.html#appendix-A.1), and
[Appendix A.2](https://www.rfc-editor.org/rfc/rfc9001.html#appendix-A.2).
Cover supported-version gates, malformed lengths, tampering, and unknown
versions. `StreamProcessor.feed` currently adds a QUIC tuple to `quic_seen`
before parse success. A malformed first Initial must not hide a later valid
Initial; ensure retries and retained keys are bounded. Compare supported
outputs against a reviewed fixture before changing baseline files.

There are two additional correctness checks. `parse_client_hello` currently
builds a JA4 with the TLS `t` prefix before QUIC sets its transport metadata;
[FoxIO's JA4 specification](https://github.com/FoxIO-LLC/ja4/blob/main/technical_details/JA4.md)
requires `q` for QUIC. The generator's QUIC branch also reuses
`malware_hello()`, which offers legacy TLS 1.1, whereas
[RFC 9001 §4.2](https://www.rfc-editor.org/rfc/rfc9001.html#section-4.2)
requires QUIC clients to offer TLS 1.3 or newer. Verify these independently;
do not equate cryptographic round-trip success with a conformant QUIC session.

The historical regression records include this generated QUIC fingerprint.
Do not promise that corrected protocol semantics produce identical QUIC
records from the old invalid capture. Preserve historical references and
input hashes, keep unrelated legacy behavior byte-identical, and introduce
an explicitly versioned, standards-valid QUIC scenario with its own reviewed
expected records. A failed old-capture check must be explained rather than
silently accepted or fixed by weakening the parser. Read
`ZEEK-ONEWAY-FINDINGS.md` before any generator work. Do not promote the
corrected path as the default until fixture migration and all required
regression gates are resolved.

### Evidence sidecar and missingness (P0)

Preserve legacy JSONL bytes. Version the new sidecar and key entries with
`(run-id, JSONL record offset/hash)`. Include schema version, named feature
values and units, missing reason, observation IDs, capture/run ID, event and
emission time, packet/window/flow reference, model manifest/config hashes, and
parent evidence IDs. Record an exact 5-tuple only if it was actually observed.
Unknown/unavailable is not zero. Export metadata redacted by default while
preserving stable joins; raw pcap export is an explicit operator action.
Hashes identify content, but do not prove legal custody, trusted time, or
authenticity. Model schema mismatch must be visible and the incompatible model
must abstain while rules and eligible model branches continue.

`Models567.score_flow` currently evaluates encrypted-metadata XGBoost even
when a parsed ClientHello is absent; missing metadata is fed as zeros. The
missingness/eligibility v2 must explicitly gate this model on the features it
requires. Do not let one ineligible model suppress unrelated rule or eligible
model results. The typed observability gate should include
`core/models_567.py`, `core/ml_tier.py`, and
`core/packet_sequence_cnn.py`; retain the literal forbidden-token scan as a
separate, narrower check.

### Streaming limits and detector v2

Window closure is clock-driven today; flow-model scoring waits for idle
closure or final drain. A continuously active flow may not be scored during a
live run. Active-flow snapshots are diagnostic-only stretch work in this
window; never feed partial vectors to shipped closed-flow models or advertise
active-flow model detection without matched training/evaluation and
recalibration. If a timer is implemented, label it as a diagnostic snapshot,
preserve original flow start, and abstain when required evidence is missing.
Sequence-model partial windows require matched training and recalibration.

Later streaming work must bound flow assembler, TLS state, `quic_seen`, source
histories, model/IF dedup, fusion state, and alert retention. `AlertSink`
retains all alerts and dashboard statistics reread the complete JSONL; a
production path needs a disk journal and bounded in-memory tail/index. Expose
TTL/cap evictions and coverage. Measure p95/p99 event-to-alert and
event-to-dashboard latency, RSS, drops and throughput under short-flow,
high-churn, long-lived, and burst-then-silence workloads. State rate, packet
size, duration and sampling. A short synthetic smoke run is not sustained
capacity evidence.

Keep the first detector experiment narrow: the current destination history in
`WindowAggregator.seen_dsts` is stream-global. Separate source-relative
novelty from fleet novelty and try one configurable rolling horizon for slow
scans. Later test provisional 10s/60s/300s contexts for transfers and scans,
DNS source/suffix histories against ordinary TXT/SPF/DKIM use and tunnel
chunks, beacon jitter/missed intervals on benign telemetry, and DDoS observed
rate changes. Never infer UDP amplification from unseen replies. Keep the
existing narrow destination authorization. Quarantine candidate learned
baseline context for review; known-bad exclusion does not prevent all
unknown-attack baseline poisoning. Defer FFT/spectral work and another
IsolationForest until evaluation supports their cost.

### Model and external-data validity

`training/train_models_567.evaluate` currently uses the temporal holdout to
sweep thresholds. The `exfil_features` vector contains `float(window.idx)`, an
absolute synthetic schedule marker. Correct this in a versioned model feature
schema by removing it; test clock shifts and changed attack schedules, then
retrain. Split training, threshold/calibration validation, and final untouched
test by scenario, host, time, and family where meaningful. Keep preprocessing
inside training. Report false alerts per benign host-hour/day and
precision/recall at explicit FP budgets with uncertainty; report calibration
only when verified. Do not spend the ten-hour MVP retraining every tier.

The IoT-23 scorer already exists and hashes local inputs. The matching
historical PCAP and `conn.log` are not in the repository, so historical figures
cannot be reproduced now. Restore exact files and document scenario, archive
version, labels, license and hashes before reporting new versioned results.
Host-level alert presence is not flow-level precision/recall. Do not download
large data in this window. The local DGA corpus archive/text and current small
model artifacts are already present (`.bench/` and repository model files);
the 10-hour plan does not need a training download. A public IoT-23 copy with
different hashes is a new evaluation, not reproduction of the prior
measurement.

### Scenario runner and offline package

Use deterministic local input manifests, isolated outputs, reset/cleanup, and
expected alerts or documented ranges. Run through the existing dashboard/FIFO
path. Add field-by-field packet and canonical full-alert parity; preserve the
current byte-identical references.

Later package an offline wheelhouse or Nix closure, dependency/model hashes,
and self-check. Dashboard should bind loopback by default with deliberate
enclave-facing configuration. No external API, network probe, mitigation,
GPU, or undeclared service is part of the demonstration. FIFO/replay is
unprivileged. AF_PACKET and kernel-drop proof requires a controlled lab
interface and `CAP_NET_RAW`; never test on a production interface. This
hardware validation is conditional and needs no confirmation merely to finish
the plan.

## Backlog after the first ten hours

| Backlog | Prerequisites and finish criteria | Rough solo effort |
|---|---|---:|
| Evidence/incident workflow | Stable IDs, ancestry-aware dedup, deterministic grouping with raw alerts preserved, reviewed export. | 2–4d |
| Partial-flow/state bounds | Eligibility, snapshot semantics, bounds across structures, long-lived/high-churn matrix, measured p95/p99. | 3–5d |
| Detection v2 | Per-source/fleet history, multiple horizons, held-out DNS/beacon/DDoS/exfil evaluation. | 3–5d |
| Model validity | Remove schedule leakage; separate train/validation/test; schema-aware missingness; host/scenario/family splits and FP workload. | 3–6d plus retraining |
| External validation | Restore exact IoT-23 files or separately identify a new public copy; publish versioned scores. | 1–2d after data access; wait unbounded |
| Capacity/offline install | Controlled lab capture, sustained rate/drop/RSS/latency runs, network-disabled package check. | 2–4d plus hardware/cache |
| Four-minute C+B film | After proof/claims freeze: real UI, mechanism visual, natural Indian English narration, captions, soundtrack for duration, prerecorded fallback; verify voice sample first. | 2–3d |

## Claims and completion discipline

Maintain a claims ledger with status `implemented + tested`, `measured
narrowly`, `planned`, or `unsupported`, plus source, fixture, input identity,
caveat and date. Update `VIDEO-BRIEF.md` only after gates pass. If a measured
number changes, regenerate the deck from `build_deck.py` in the same session;
its target is `../Diode-Sentinel.pptx`, outside this repository’s writable
root, so obtain the usual output-path write approval when generation is
actually requested. Do not put fresh result numbers in a slide or film until
their exact test was run and recorded.

No outside input blocks the ten-hour synthetic/replay work. The only material
external dependencies are the exact IoT-23 inputs for historical reproduction
and a controlled capture host/interface for AF_PACKET hardware claims. The
ten-hour window is the governing budget; finish the selected MVP, record
unfinished gates plainly, and leave the broader roadmap in backlog.
