# Diode Sentinel: packet-to-evidence explainer concepts

Updated 1 October 2026 after the 30 September detector-quality pass. These are revised
storyboards for the next film, not a completed video. The existing 52-second
product demo remains unchanged. The user prefers B and C and has removed the
90-second ceiling. The recommended direction now combines C's architecture
with B's experiments.

Narration requirement added by the user: **Indian English voiceover**, with
natural Indian pronunciation and cadence, clear technical terms and a warm,
curious delivery. Borrow Feynman's explanatory approach: show an observation,
build a simple mental model, let the viewer see the mechanism, then name the
technical tool. Do not impersonate him or present invented quotations.

The interactive storyboard is `pipeline-lab.html`: choose a concept, step
through the verified pipeline, play the staged explanation, or change the
illustrative burst timing. It is a concept preview, not a detector simulator.

## A. Follow the evidence — suggested 80–100 seconds

One highlighted source anchors the whole explanation. Its packets become
observations, then flow summaries and time-window statistics. DNS and
ClientHello metadata branch into their own checks. Rules and enabled models
produce alerts. Recent qualifying signals from the same source are correlated.
The graphic resolves into the real dashboard, where the cursor opens evidence.

Sample opening: “A packet is a small observation. Where did it come from?
Where is it going? How big is it? And when did it arrive? Now watch what happens
when we put those observations together.”

Key visual moments:
- A received packet unfolds into addresses, ports, size and timestamp.
- Related packets gather into a flow; a clock closes completed summaries.
- A recurring rhythm becomes a visible spacing pattern.
- Domain characters, packet sequences and fan-out reach their relevant models.
- Recent signals connect on a source timeline, then become real dashboard evidence.

An alternative if the film follows one source continuously rather than moving
between experiments and architecture layers.

## B. The packet laboratory — 3 minutes 20 seconds

The teaching-led version. Make one observation, change one condition, and let
the viewer understand what changed. Each experiment ends in the actual
software: the cursor opens the resulting recorded signal and its evidence.
Keep the sensor visibly receive-only throughout.

Sample opening: “A packet on its own tells us very little. But give it some
company, and a pattern begins to appear. Let's see how.”

| Time | Experiment and explanation | Graphic and actual software action |
|---|---|---|
| 0:00–0:15 | Start with one received packet: source, destination, size, time. | A packet unfolds into four observations. Pull back to the diode and sensor. |
| 0:15–0:35 | Put observations together into flows and timed windows. | Match the graphic to a fresh synthetic replay in the real dashboard. Move the cursor to sensor state and analyzed packets. |
| 0:35–1:00 | Change regular flow starts into irregular starts. Explain the timing pattern used by the beacon rule. | An illustrative rhythm slider changes spacing. Cut to an actual beacon alert, its interval and variation evidence, then filter its source. |
| 1:00–1:25 | Spread a scan across windows: ten distinct destination/port pairs, then ten different pairs. The rolling union reaches twenty within the 60-second horizon. | Keep both ten-second windows visible inside one moving horizon. Enable `--rolling-scan`; open the emitted rolling-rule alert and its measured pair count. Separately name Random Forest's current-window scan inputs; do not credit the rolling rule to that model. |
| 1:25–1:50 | A destination familiar to host A can still be new within host B's retained history. Add unusual transfer volume and compare it with B's own baseline. | Two source-history cards share a destination. Enable `--source-context`; open a real exfil indicator and its source/fleet novelty, lookback and coverage fields. Volume and novelty are indicators, not a confirmed theft verdict. |
| 1:50–2:15 | Show why domain characters and DNS query shape offer different observations. | Slide character windows across a DNS label to explain the numpy character CNN. Then show actual DNS evidence; distinguish the model's role from the rule that generated the selected alert. |
| 2:15–2:45 | Explain the two encrypted-session branches: packet-size/timing sequences and observed ClientHello metadata. QUIC Initial metadata uses public protocol inputs. | Branch into sequence CNN and metadata XGBoost. Show a complete ClientHello activating the metadata branch; when absent, that branch stays unscored while the sequence branch remains eligible. Open the actual XGBoost alert and named cipher/extension counts, flow bytes and duration. |
| 2:45–3:10 | Follow signals from the same source into correlation, then inspect and retain the evidence. | Cursor filters a source, opens a correlation and its contributing signals, then opens a selected alert and clicks “Download evidence JSON.” Show the downloaded original record, active filters and record hash. |
| 3:10–3:20 | Resolve the observations back into the product. | Diode Sentinel. “See everything. Touch nothing.” Built by samarags. |

The advantage of B is that the new behavior becomes understandable on screen:
remembering observations across time, remembering context per source, and
making the model's inputs inspectable. The companion preview can use sliders
and toggles; the film shows those controls being operated deliberately.
Illustrative controls remain labeled and never manufacture a model score.

## C. Inside the engine — 2 minutes 45 seconds

The architecture-led version. One receive-side packet opens up the complete
engine. A restrained camera moves through its parallel branches, then each
layer resolves into the corresponding real dashboard action. This now has
enough time to teach the mechanism, rather than ending at a polished diagram.

Sample opening: “A network sends a stream of observations. Diode Sentinel
organizes them, measures their patterns, and carries the evidence all the way
to the analyst.”

| Time | Engine layer | Graphic and actual software action |
|---|---|---|
| 0:00–0:15 | Receive-side boundary | Packets cross the hardware diode into the sensor. Keep the direction clear; use the receive-side monitoring view as the first software anchor. |
| 0:15–0:35 | Normalize packets | Addresses, ports, protocol, length and time become structured observations. Available DNS and ClientHello metadata branch to their own checks. |
| 0:35–1:00 | Assemble flows and clock-driven windows | Flows and window summaries develop in parallel. The clock closes idle flows and completed windows even after arrivals stop. Add the optional 60-second rolling scan context around the ten-second windows; show the actual rolling alert. |
| 1:00–1:35 | Route observations to their consumers | DNS labels → character CNN; packet-size/timing sequences → sequence CNN; ClientHello plus flow measurements → encrypted XGBoost; scan-window fan-out → Random Forest; transfer-window features → exfil XGBoost. LightGBM is flow corroboration; eligible Isolation Forest scores remain supporting evidence. Open one actual model alert while its inputs light up in the diagram. |
| 1:35–2:00 | Source context and evidence availability | Add the opt-in source-relative destination history beside the exfil rule. Show the metadata eligibility gate beside encrypted XGBoost. Keep these rule/context additions separate from trained model vectors. |
| 2:00–2:20 | Record and correlate signals | Individual detector alerts reach the sink first. Fusion separately joins recent qualifying signals from the same source with decay and escalation suppression. Cursor filters that source and opens the contributing evidence. |
| 2:20–2:40 | Analyst handoff | The diagram becomes the real UI. Inspect named measurements, open original evidence, download the selected alert bundle, and reveal its active filters and alert-record hash. |
| 2:40–2:45 | Closing | Diode Sentinel. “See everything. Touch nothing.” samarags. |

C's advantage is a clear account of where each observation goes, when it is
evaluated, and what the analyst receives. Motion is deliberate: parallel
branches, subtle depth, continuous camera moves, then matching UI close-ups.
There is no claim that every packet runs through every model or that active
flows already receive partial-flow model inference.

## Recommended production direction

Use **C as the backbone with B's experiments inside it**, targeting roughly
3 minutes 30 seconds. Follow the full packet-to-evidence path, pause for the
rhythm, rolling-scan and source-history experiments, then return to the engine
and finish in the real dashboard. Reserve at least a minute for actual
software footage interleaved with the explanation, not only an ending reveal.

Use a warm, natural **Indian English** narrator with verified Indian English
pronunciation; replace the previous narration asset rather than relabeling it.
Teach through observations and small experiments, with a confident product
tone. Keep the Vanta-black/amber palette, subtle depth, clear mouse movement
and supplied **First Light** soundtrack. Choose cuts around its measured
accents after the narration pacing is established; duck music under speech.

These outlines use the user's product-first emphasis: demonstrate the
receive-side design and its observable inputs through the mechanism. They do
not insert the older impossible-feature lecture or negative-result scorecard.
Measured weaknesses are not converted into false performance claims.

## What changed after the build

- Rolling scan and source history are implemented, **opt-in rules**, with
  focused behavior tests. They are stronger teaching scenes than another
  generic threat-category card.
- Model evidence now has **named inputs**. The encrypted-model scene can land
  in a real modal rather than leaving the viewer with an unexplained score.
- A metadata eligibility gate makes the branch animation faithful to the
  pipeline: no complete observed ClientHello means no metadata-model score.
- QUIC now has independent RFC 9001 Appendix A.1/A.2 verification. Explain
  public Initial inputs and ClientHello recovery, not payload inspection or
  secret-key possession; QUIC and TLS JA4 transport prefixes differ.
- The analyst can **download selected-alert evidence**, including active
  filters and a SHA-256 of the original alert record. This supplies a concrete
  ending to the packet-to-evidence story, without claiming packet provenance
  or legal chain of custody.
- Full-record backend parity, all 23 test scripts, synthetic demo smoke and
  desktop/mobile browser checks pass. Current archive counts are 45/67 for
  rules/ML; the historical 46/68 fixtures have one known removed invalid-QUIC
  alert and await reviewed migration. None of these is a detection benchmark.

## Footage and production requirements

1. Record fresh footage with the relevant optional flags enabled. Existing
   52-second captures predate these changes and cannot stand in for them.
2. Use the real pipeline to produce a scan spread across windows and a
   two-source shared-destination fixture. Record their actual alerts before
   writing numeric copy. The existing main capture does not establish that
   the new rolling rule fires; use the focused scenarios.
3. Illustrative diagrams can show the ten-plus-ten experiment, labeled as
   such. Packet counts, model outputs and exports in the software footage
   must come from the recorded replay. Do not reuse stale screenshot values.
4. Read `VIDEO-BRIEF.md` §10 for the updated claim boundaries. Regenerate the
   capture manifest and claims trace when producing the selected film.
5. The interactive storyboard is a concept preview, not a simulator or proof
   of detector quality. The current step timing is for review, not final edit
   pacing. No new video or voice track has been rendered by this update.

## Verified technical foundation

- Receive and normalize: core/live_source.py, core/pcap_reader.py.
- In parallel: flows, timed traffic summaries, supported DNS/TLS/QUIC metadata:
  core/pipeline.py. A clock closes idle flows and completed windows.
- Rules: DDoS/UDP bursts, scanning, exfiltration, beaconing, DNS and fingerprint
  checks in core/detectors.py.
- Character CNN consumes DNS labels; sequence CNN consumes encoded packet-size/
  timing sequences; XGBoost consumes encrypted metadata or transfer features;
  Random Forest consumes scan-window features. LightGBM scores flows.
- Isolation Forest supplies eligible scan/exfil anomaly corroboration; it is
  not an independent primary verdict: core/models_567.py.
- Individual alerts are written first. Fusion separately correlates recent
  qualifying signals by source, with decay and escalation suppression:
  AlertSink and FusionEngine in core/detectors.py.
- Dashboard reads records and sensor state, then exposes triage and related
  evidence: dashboard.py, dashboard_signals.py, static/app.js.

Do not draw every packet passing serially through every model. Do not present
an illustrative experiment as measured detection performance. Detector scores
are not calibrated probabilities. `VIDEO-BRIEF.md` §10 records the verified
development and proposed B/C framing; it does not claim either film has been
produced.
