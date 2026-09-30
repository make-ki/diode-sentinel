# Diode Sentinel explainer — claims trace

Source of truth: `../VIDEO-BRIEF.md` §§9–11. UI values come from the fresh recorded synthetic replay authorized in §11. This is not a performance or accuracy benchmark.

## Narration and scene copy

| Scene | On-screen label and headline | Spoken copy | Brief sections |
|---|---|---|---|
| intro | DIODE SENTINEL<br>Small observations. A larger picture. | A packet is a small observation. Where did it come from? Where is it going? How big is it, and when did it arrive? Put those observations together, and a pattern begins to appear. This is Diode Sentinel. | 0, 9, 10; §11 approved production copy |
| receive | RECEIVE-SIDE MONITORING<br>Watch the observations arrive. | The sensor watches the receive side of a hardware data diode. Traffic arrives in one direction. Here, a synthetic replay is running through the actual software. Watch the packet counters, the sensor state, and the alert queue. These are observations being processed, as they arrive. | 2.9, 9, 10; §11 approved production copy |
| organize | PACKETS → CONTEXT<br>Put the observations together. | First, we give each packet a useful shape: addresses, ports, protocol, size, and time. Related packets form a flow. Alongside that, timed windows collect what happens across the traffic. The clock closes idle flows and completed windows, even when the next packet never arrives. | 2.2, 9, 10; §11 approved production copy |
| rhythm | EXPERIMENT 01 · TIMING<br>Listen to the rhythm. | Look at these flow starts. The gaps are almost even. Change the spacing, and the rhythm changes. Our beacon rule measures that regularity. Now open the real alert: the interval and its variation are recorded here. The analyst can inspect the pattern behind the score. | 9, 10; §11 approved production copy |
| rolling | EXPERIMENT 02 · ROLLING CONTEXT<br>Keep both windows in view. | A pattern can be spread across time. In this illustration, one source touches ten distinct destination and port pairs, then ten different pairs in the next window. With rolling scan enabled, the rule keeps a sixty second horizon. The union reaches twenty. Here is that pattern, recorded by the actual pipeline. | 10; §11 approved production copy |
| history | EXPERIMENT 03 · SOURCE CONTEXT<br>Remember whose history it is. | Now suppose two hosts contact the same destination. It is familiar to the first host. That does not make it familiar to the second. With source context enabled, we check this host's retained history, then compare transfer volume with its own baseline. The alert records the lookback and coverage that qualify that observation. | 2.3, 10; §11 approved production copy |
| dns | DOMAIN-NAME ANALYSIS<br>Read the shape of a name. | A domain name is another kind of sequence. Our character C N N examines patterns in its letters. Separate rules inspect the DNS query's length and type. In the software, the detector identifier tells us which check produced this record. We can see the observed query measurements beside it. | 2.5, 9, 10; §11 approved production copy |
| encrypted | ENCRYPTED-SESSION ANALYSIS<br>Two branches. Different observations. | An encrypted session still has an observable shape. The sequence C N N uses packet sizes and timing. A separate X G Boost model uses observed Client Hello metadata and flow measurements. Each branch receives the inputs it needs. QUIC Initial packets expose Client Hello metadata through public protocol inputs. Open the model alert: cipher counts, extension counts, bytes, and duration now have names. | 2.4, 9, 10; §11 approved production copy |
| models | PARALLEL DETECTOR BRANCHES<br>The right inputs. The right branch. | The same engine routes different observations to different checks. Random Forest uses scan window fan out. Exfiltration X G Boost uses transfer window features. Light G B M adds flow scoring. Eligible Isolation Forest scores provide supporting evidence. These branches serve different purposes; the recorded alert identifies its detector and its inputs. | 9, 10; §11 approved production copy |
| fusion | SOURCE ATTRIBUTION & CORRELATION<br>Follow the source. Connect the signals. | Detectors first write their own alerts. Then the correlation layer considers recent qualifying signals from the same source. Filter that source, open a correlated record, and inspect its contributors. The observations stay attached, so the analyst can follow how the signals were connected. | 2.8, 9, 10; §11 approved production copy |
| handoff | THE ANALYST VIEW<br>Carry the evidence forward. | This is where the explanation becomes a workflow. Open an alert. Read its named measurements. Inspect the original evidence. Then download the selected alert as J S O N. The bundle preserves the record, the active filters, and a hash of that record. The software carries the observations all the way to the analyst. | 9, 10; §11 approved production copy |
| closing | BUILT BY SAMARAGS<br>See everything. Touch nothing. | From packets, to patterns, to inspectable evidence. Diode Sentinel. Passive, receive side monitoring. See everything. Touch nothing. Built by Samarags. | 9, 10; §11 approved production copy |

## Shared production text

| Exact text | Origin |
|---|---|
| Diode Sentinel; samarags; Built by samarags | §§9–11 |
| See everything. Touch nothing. | §§10–11; positioning, not perfect-coverage assurance |
| Recorded software · Synthetic replay | §§9–11; required demonstration qualifier |
| Illustrative diagram · Receive-side observations | §§10–11; illustrative context qualifier |

## Diagram copy and numbers

Authored diagram wording below is flagged as **added wording**: it explains behavior in §10 but is not a verbatim quote from the brief. Labels are original editorial copy, not additional product claims. Illustrative 10 + 10 = 20 pairs, ten-second windows and a sixty-second horizon are explicitly authorized in §10.

| Exact authored literal | Brief basis | Status |
|---|---|---|
| 10 different pairs · union = | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| 10 distinct destination/port pairs | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| 60-second retained horizon | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| A beacon rule can compare observed start-time spacing and its variation. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| A character window moves over a generic DNS domain label for the Character CNN | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| A destination known to source A may be new within source B's retained history | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| A domain label is a sequence of characters. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Analyst handoff | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Analyst inspects a recorded alert and its evidence in the dashboard | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Available metadata | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Character CNN | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Character windows give the model an observed sequence to examine. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| ClientHello | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| ClientHello metadata + flow | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Contributing signals | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Correlate | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| D/P | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| DNS QUERY INPUT · GENERIC LABEL | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| DNS label | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| DNS query-label characters | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Different named models receive only their relevant observations through parallel branches | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Download evidence JSON | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| ENCRYPTED-SESSION ANALYSIS | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Each signal has its own destination. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Evidence | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Evidence first. Correlation follows. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Flow summaries | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Flows and windows form alongside packet-level observations. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| ILLUSTRATIVE FLOW-START PATTERNS | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| ILLUSTRATIVE ROLLING CONTEXT · OPTIONAL RULE | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| ILLUSTRATIVE SOURCE-CONTEXT RULE · OPT-IN | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Illustrative comparison of regularly and irregularly spaced packet arrivals | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Illustrative rolling scan: ten unique destination and port pairs in each of two adjacent ten-second windows within a sixty-second horizon | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Irregular starts | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Isolation Forest | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Isolation Forest supports eligible models; each branch requires its own observed inputs. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Known to A | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| LightGBM | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Named measurements · original record | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| New within B's covered history | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| No complete ClientHello? XGBoost stays ineligible. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Novelty depends on whose history. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| ONE WAY | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Observe · organize · record | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Observed data | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Observed flow | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| One direction. A stream of observations. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| One packet becomes useful in company. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| One-way packet observation crosses the diode to the receive-side sensor | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Organize | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Packet sequence | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Packets | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Packets become flows and time-window summaries, while DNS and ClientHello metadata branch to their consumers | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Parallel encrypted-session analysis: packet sequence remains eligible independently of complete ClientHello metadata | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Parallel model inputs | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Public QUIC Initial inputs | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| RECENT SIGNALS | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Random Forest | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Receive side | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Receive-side sensor | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Recent qualifying signals · decay · escalation suppression | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Recorded evidence | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Recorded fields and values come from the selected dashboard event. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Recorded signals from a source can qualify for a separate recent-signal correlation | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Regular starts | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Retained lookback and coverage qualify the novelty signal. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| SELECTED ALERT | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| SIZE · TIME | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| SLIDING CHARACTER WINDOW | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| SOURCE FILTER | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| SRC  →  DST | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Separate from DNS shape rules | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Sequence CNN | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Sequence CNN remains independently eligible. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Signal · same source | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Signals | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Source | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Source A | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Source B | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Source · destination · size · time | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| The horizon keeps both windows in view. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| The illustrated union reaches the existing 20-pair threshold across adjacent windows. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| The record stays inspectable. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Timed windows | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Timing is part of the observation. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Two branches. Different observations. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Window 1 · 10 s | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| Window 2 · next 10 s | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| XGBoost | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| XGBoost · encrypted | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| XGBoost · exfil | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| another qualifying signal | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| can reveal ClientHello metadata. | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| clock closes the window | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| complete metadata required | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| correlation | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| destination X | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| eligible corroboration only | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| event  →  evidence  →  analyst | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| flow · window · label | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| flow-level corroboration | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| grouped observations | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| headers + time | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| its own retained history | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| metadata model | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| new | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| not in retained set | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| packet-size and timing sequence | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| qualified records | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| recorded by a detector | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| retained destination history | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| same destination | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| scan-window fan-out | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| selected source | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| sequence CNN branch | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| sizes · timing · metadata | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| transfer-window features | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| when fully observed | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| when query is present | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| with contributors | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |
| within recent history | §10 model inputs, packet organization, source history, rolling context, QUIC or export; §11 illustration | Added wording; no invented measurement |

Dynamic characters in the domain-label diagram spell the generic illustrative label `domainlabel`. Dynamic rolling count is the illustrative integers 0–20; 10 and 20 are fixture arithmetic, not observed production throughput. Decorative packet glyphs, card layouts, timing markers and scene progress are illustrative design.

## Recorded dashboard text and numbers

Every text block below was extracted from the actual visible component at the end of its recording. Other visible dashboard chrome and values are captured in the snapshots and the full synthetic `alerts.jsonl`; per-clip actions and the selected original records are stored in `capture-manifest.json`. No dashboard value is replaced by generated text.

Fresh capture: 14171 packets, including 122 focused fixture packets; 108 recorded alerts with the enabled demonstration tiers. Basis: §11, capture manifest and synthetic replay. These are demonstration counts, not archived regression counts.

### overview

Brief: §§9–11. File: overview.mp4. Exact recorded UI text:

```text
Sensor
Completed
Mode
Packet stream
Source
/tmp/nix-shell.laQUSI/diode-explainer-8qgyfsqc/feed.pcap
Last packet received · UTC
19:24:38
Heartbeat
3.7s ago
Seen
14,171
Analyzed
14,171
Sampled out
0
Malformed
0
Kernel drops
Unknown
```

### beacon

Brief: §§9–11. File: beacon.mp4. Exact recorded UI text:

```text
High
Periodic flow pattern
✕

flows 6; mean interval (s) 4.98; CV 0.0179; gate 0.15

Timestamp
2025-09-09T21:20:33.026Z
Recorded Flow Key (Not A Session ID)
10.0.0.7:*->198.51.100.23:443/tcp
Detector Identifier
c2_beaconing
Signal Origin
rule
Source
10.0.0.7
Destination
198.51.100.23
Rule Score
0.798
Severity
high
Observed measurements
Flows in series
6
Mean interval (s)
4.98
Interval CV
0.0179
CV gate
0.15
Interpretation limits

Periodicity is one-way observable but cloud telemetry and scheduled jobs can produce the same pattern. Detector scores are not calibrated probabilities of compromise.

Suggested verification

Compare the recorded flow times with the source's expected scheduled connections.

Download evidence JSON
One selected alert · active filters recorded
Original detector evidence
```

### rolling-scan

Brief: §§9–11. File: rolling-scan.mp4. Exact recorded UI text:

```text
Medium
Rolling-window port scan against one destination
✕

destination/port pairs 20; destinations 1; top-destination pairs 20; rolling horizon (s) 60.0; current-window pairs 10; observed window-end times (stream ...

Timestamp
2025-09-09T21:30:19.000Z
Recorded Flow Key (Not A Session ID)
192.0.2.70:*->198.51.100.70:*/tcp
Detector Identifier
recon_rolling_vertical_scan
Signal Origin
rule
Source
192.0.2.70
Destination
198.51.100.70
Rule Score
0.520
Severity
medium
Observed measurements
Distinct destination/port pairs in rolling history
20
Pairs in current window
10
Distinct destination IPs
1
Pairs on top destination
20
Rolling horizon (s)
60
Oldest observed window end (stream seconds)
610
Newest observed window end (stream seconds)
620
Observed endpoint sample
{"dst":"198.51.100.70","dport":1000,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1001,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1002,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1003,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1004,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1005,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1006,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1007,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1008,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1009,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1010,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1011,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1012,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1013,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1014,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1015,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1016,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1017,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1018,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1019,"protocols":["tcp"]}
Endpoint sample truncated
No
History evictions
{"source_entries":0,"pair_entries_total":0,"pairs_for_source":0}
Interpretation limits

This rolling fan-out pattern uses one-way packet metadata. Bounded history evictions can make the retained pair count lower than the full observed history; authorized scanners can produce similar patterns. Detector scores are not calibrated probabilities of compromise.

Suggested verification

If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.

Download evidence JSON
One selected alert · active filters recorded
Original detector evidence
```

### source-context

Brief: §§9–11. File: source-context.mp4. Exact recorded UI text:

```text
Critical
Large transfer to a new destination
✕

bytes to new destination 600000; baseline bytes 600; ratio 1000.0x; age windows 0

Timestamp
2025-09-09T21:30:39.000Z
Recorded Flow Key (Not A Session ID)
192.0.2.81:*->198.51.100.80:443/tcp
Detector Identifier
data_exfiltration
Signal Origin
rule
Source
192.0.2.81
Destination
198.51.100.80
Rule Score
0.950
Severity
critical
Observed measurements
Observed bytes to new destination
600000
Source median baseline bytes
600
Ratio vs baseline
1000
Pair age (windows)
0
Interpretation limits

One-way bytes show transfer volume, not authorization or successful exfiltration; benign backups can look similar. Detector scores are not calibrated probabilities of compromise.

Suggested verification

Compare the observed destination and transfer volume with this source's prior byte baseline and backup schedule.

Download evidence JSON
One selected alert · active filters recorded
Original detector evidence
{
  "bytes_to_new_dst": 600000,
  "pair_age_windows": 0,
  "src_baseline_bytes_median": 600,
  "ratio_vs_baseline": 1000,
  "novel_destination": true,
  "why": "large sustained upload to a destination not observed within this source's retained history lookback, far above its normal observed window volume",
  "source_novel_within_lookback": true,
  "source_history_lookback_windows": 8640,
  "source_history_coverage_at_admission": "complete_within_lookback",
  "source_history_coverage_now": "complete_within_lookback",
  "fleet_destination_novel": false,
  "source_history": {
    "retained_pairs": 3645,
    "capacity": 50000,
    "max_age_windows": 8640,
    "incomplete_sources": 0,
    "global_coverage_incomplete": false,
    "expired_entries": 0,
    "evicted_entries": 0
  }
}
```

### dns

Brief: §§9–11. File: dns.mp4. Exact recorded UI text:

```text
Medium
Repeated bulky or overlong DNS queries
✕

query bytes 70; qtype 16; queries 5; cumulative query bytes 350; limitation not verified exfil volume

Timestamp
2025-09-09T21:24:08.000Z
Recorded Flow Key (Not A Session ID)
10.0.0.11:*->*:53/udp
Detector Identifier
dns_tunneling
Signal Origin
rule
Source
10.0.0.11
Destination
*
Rule Score
0.537
Severity
medium
Observed measurements
Query bytes
70
Query type
16
Maximum label length
50
Tunnel-like queries
5
Cumulative query bytes
350
Interpretation limits

DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use. Detector scores are not calibrated probabilities of compromise.

Suggested verification

Review the captured DNS query names and qtypes for this source and time window.

Download evidence JSON
One selected alert · active filters recorded
Original detector evidence
{
  "qtype": 16,
  "qname": "bxxlyy2nw2fmfbf2ncfcnnwfww4q4s6sko2tvgof2okt5z2gjy.exfil.xxxxxxxx.com.",
  "query_bytes": 70,
  "max_label_length": 50,
  "cumulative_tunnel_bytes": 350,
  "tunnel_queries_from_src": 5,
  "signals": "qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60",
  "note": "response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable",
  "why": "repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups"
}
```

### encrypted-metadata

Brief: §§9–11. File: encrypted-metadata.mp4. Exact recorded UI text:

```text
Critical
Encrypted-session model match
✕

named model inputs ClientHello cipher-suite count=6.0, ClientHello extension count=3.0, ClientHello offered TLS version=11.0

Timestamp
2025-09-09T21:23:20.243Z
Recorded Flow Key (Not A Session ID)
10.0.0.7:*->198.51.100.23:8443/tcp
Detector Identifier
encrypted_session_malware
Signal Origin
model
Source
10.0.0.7
Destination
198.51.100.23
Model Score
0.944
Severity
critical
Observed measurements
Model
xgboost
ClientHello cipher-suite count (count)
6
ClientHello extension count (count)
3
ClientHello offered TLS version (code: 10=TLS 1.0; 11=TLS 1.1; 12=TLS 1.2; 13=TLS 1.3; 0=unknown)
11
Transport code (0 = TLS, 1 = QUIC)
0
SNI-present flag (0/1)
0
Signature-algorithm count (count)
2
Flow packet count (packets)
3
Flow bytes (bytes)
394
Flow duration (seconds)
0.019999980926513672
Packet-size coefficient of variation (unitless)
0.45623195266236183
Interpretation limits

The named vector contains client-side metadata and flow measurements. This alert has no metadata-availability flags, so a recorded zero does not establish whether a field was absent, empty, or defaulted. Detector scores are not calibrated probabilities of compromise.

Suggested verification

Review the raw recorded model features alongside the source's deterministic alerts.

Download evidence JSON
One selected alert · active filters recorded
Original detector evidence
{
  "model": "xgboost",
  "metadata_features": [
    6,
    3,
    11,
    0,
    0,
    2,
    3,
    394,
    0.019999980926513672,
    0.45623195266236183
  ]
}
```

### scan-model

Brief: §§9–11. File: scan-model.mp4. Exact recorded UI text:

```text
Critical
Model-flagged scan pattern
✕

named model inputs Distinct destination/port pairs=202.0, Distinct destination IPs=3.0, Maximum ports on one destination=200.0

Timestamp
2025-09-09T21:24:19.000Z
Recorded Flow Key (Not A Session ID)
10.0.0.13:*->*:0/*
Detector Identifier
recon_model_scan
Signal Origin
model
Source
10.0.0.13
Destination
*
Model Score
1.000
Severity
critical
Observed measurements
Model
scan_rf
Distinct destination/port pairs (pairs)
202
Distinct destination IPs (IPs)
3
Maximum ports on one destination (ports)
200
Maximum per-destination share of pairs (unitless ratio)
0.9900990099009901
Source bytes in window (bytes)
14416
IsolationForest anomaly score
-0.2838237650122478
IsolationForest score kind
uncalibrated_decision_function
IsolationForest more anomalous when
lower
Interpretation limits

This is a one-way traffic pattern; legitimate scanners or bursts can produce similar measurements. Detector scores are not calibrated probabilities of compromise.

Suggested verification

If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.

Download evidence JSON
One selected alert · active filters recorded
Original detector evidence
{
  "model": "scan_rf",
  "features": [
    202,
    3,
    200,
    0.9900990099009901,
    14416
  ],
  "iforest_corroboration": {
    "model": "scan_iforest",
    "anomaly_score": -0.2838237650122478,
    "score_kind": "uncalibrated_decision_function",
    "more_anomalous_when": "lower"
  }
}
```

### source-correlation

Brief: §§9–11. File: source-correlation.mp4. Exact recorded UI text:

```text
Critical
Correlated TLS and periodicity signals
✕

signals c2_beaconing, ml_flow_suspicious, tls_known_malware; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation

Timestamp
2025-09-09T21:23:20.233Z
Recorded Flow Key (Not A Session ID)
10.0.0.7:*->*:0/*
Detector Identifier
confirmed_c2_implant
Signal Origin
correlation
Source
10.0.0.7
Destination
*
Correlation Score
0.999
Severity
critical
Observed measurements
Correlation window (s)
120
Combination method
noisy-OR with exponential decay (half-life=120s)
Signals used by this correlation
C2 beaconing
12.2 s before correlation · 198.51.100.23 · weighted score 0.689
Suspicious flow
7.1 s before correlation · 198.51.100.23 · weighted score 0.96
TLS local indicator match
0 s before correlation · 198.51.100.23 · weighted score 0.99
Interpretation limits

Correlation combines detector outputs from one-way observations; signals may share causes and do not confirm compromise. Detector scores are not calibrated probabilities of compromise.

Suggested verification

Review each listed source alert and its packet-time window before escalating.

Download evidence JSON
One selected alert · active filters recorded
Original detector evidence
{
  "contributing_signals": [
    {
      "threat_class": "c2_beaconing",
      "at_s": 188,
      "age_s": 12.2,
      "confidence": 0.739,
      "effective_confidence": 0.689,
      "dst": "198.51.100.23",
      "dport": 0
    },
    {
      "threat_class": "ml_flow_suspicious",
      "at_s": 193.1,
      "age_s": 7.1,
      "confidence": 1,
      "effective_confidence": 0.96,
      "dst": "198.51.100.23",
      "dport": 0
    },
    {
      "threat_class": "tls_known_malware",
      "at_s": 200.2,
      "age_s": 0,
      "confidence": 0.99,
      "effective_confidence": 0.99,
      "dst": "198.51.100.23",
      "dport": 0
    }
  ],
  "combination": "noisy-OR with exponential decay (half-life=120s)",
  "window_s": 120,
  "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"
}
```

### evidence-export

Brief: §§9–11. File: evidence-export.mp4. Exact recorded UI text:

```text
Medium
Rolling-window port scan against one destination
✕

destination/port pairs 20; destinations 1; top-destination pairs 20; rolling horizon (s) 60.0; current-window pairs 10; observed window-end times (stream ...

Timestamp
2025-09-09T21:30:19.000Z
Recorded Flow Key (Not A Session ID)
192.0.2.70:*->198.51.100.70:*/tcp
Detector Identifier
recon_rolling_vertical_scan
Signal Origin
rule
Source
192.0.2.70
Destination
198.51.100.70
Rule Score
0.520
Severity
medium
Observed measurements
Distinct destination/port pairs in rolling history
20
Pairs in current window
10
Distinct destination IPs
1
Pairs on top destination
20
Rolling horizon (s)
60
Oldest observed window end (stream seconds)
610
Newest observed window end (stream seconds)
620
Observed endpoint sample
{"dst":"198.51.100.70","dport":1000,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1001,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1002,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1003,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1004,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1005,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1006,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1007,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1008,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1009,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1010,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1011,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1012,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1013,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1014,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1015,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1016,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1017,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1018,"protocols":["tcp"]}, {"dst":"198.51.100.70","dport":1019,"protocols":["tcp"]}
Endpoint sample truncated
No
History evictions
{"source_entries":0,"pair_entries_total":0,"pairs_for_source":0}
Interpretation limits

This rolling fan-out pattern uses one-way packet metadata. Bounded history evictions can make the retained pair count lower than the full observed history; authorized scanners can produce similar patterns. Detector scores are not calibrated probabilities of compromise.

Suggested verification

If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.

Download evidence JSON
Evidence bundle downloaded
Original detector evidence
```

## Exact selected records and captured interactions

These original synthetic records supply all displayed detector values, addresses, timestamps, scores and model inputs. Qualifiers are retained in the software and the surrounding Synthetic replay caption.

```json
{
  "beacon": {
    "record": {
      "timestamp": "2025-09-09T21:20:33.026Z",
      "src": "10.0.0.7",
      "dst": "198.51.100.23",
      "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
      "threat_class": "c2_beaconing",
      "confidence": 0.798,
      "severity": "high",
      "evidence": {
        "flows_in_series": 6,
        "mean_interval_s": 4.98,
        "iat_cv": 0.0179,
        "cv_gate": 0.15,
        "last_iats_s": [
          4.84,
          5.06,
          4.94,
          4.97,
          5.09
        ],
        "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
      }
    },
    "triage": {
      "kind": "rule",
      "label": "Periodic flow pattern",
      "summary": "flows 6; mean interval (s) 4.98; CV 0.0179; gate 0.15",
      "facts": [
        {
          "label": "Flows in series",
          "value": 6
        },
        {
          "label": "Mean interval (s)",
          "value": 4.98
        },
        {
          "label": "Interval CV",
          "value": 0.0179
        },
        {
          "label": "CV gate",
          "value": 0.15
        }
      ],
      "caveat": "Periodicity is one-way observable but cloud telemetry and scheduled jobs can produce the same pattern.",
      "next_step": "Compare the recorded flow times with the source's expected scheduled connections.",
      "score_label": "Rule score",
      "related": [],
      "export_key": "59156ea0de1376d189ce83efe6d0ae2e30bbebfa35b1171ea6f3a848840324d8"
    },
    "record_key": "59156ea0de1376d189ce83efe6d0ae2e30bbebfa35b1171ea6f3a848840324d8",
    "ui_row_key": "2025-09-09T21:20:33.026Z|10.0.0.7|c2_beaconing|0.798"
  },
  "rolling-scan": {
    "record": {
      "timestamp": "2025-09-09T21:30:19.000Z",
      "src": "192.0.2.70",
      "dst": "198.51.100.70",
      "flow_id": "192.0.2.70:*->198.51.100.70:*/tcp",
      "threat_class": "recon_rolling_vertical_scan",
      "confidence": 0.52,
      "severity": "medium",
      "evidence": {
        "rolling_window_s": 60,
        "rolling_distinct_dst_port_pairs": 20,
        "current_window_distinct_pairs": 10,
        "distinct_dst_ips": 1,
        "pairs_on_top_dst": 20,
        "oldest_observed_window_end_s": 610,
        "newest_observed_window_end_s": 620,
        "observed_endpoints_sample": [
          {
            "dst": "198.51.100.70",
            "dport": 1000,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1001,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1002,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1003,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1004,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1005,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1006,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1007,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1008,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1009,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1010,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1011,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1012,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1013,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1014,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1015,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1016,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1017,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1018,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1019,
            "protocols": [
              "tcp"
            ]
          }
        ],
        "observed_endpoints_truncated": false,
        "history_evictions": {
          "source_entries": 0,
          "pair_entries_total": 0,
          "pairs_for_source": 0
        },
        "why": "distinct destination/port pairs accumulated from one source within the observed rolling time horizon; all inputs are one-way packet metadata"
      }
    },
    "triage": {
      "kind": "rule",
      "label": "Rolling-window port scan against one destination",
      "summary": "destination/port pairs 20; destinations 1; top-destination pairs 20; rolling horizon (s) 60.0; current-window pairs 10; observed window-end times (stream ...",
      "facts": [
        {
          "label": "Distinct destination/port pairs in rolling history",
          "value": 20
        },
        {
          "label": "Pairs in current window",
          "value": 10
        },
        {
          "label": "Distinct destination IPs",
          "value": 1
        },
        {
          "label": "Pairs on top destination",
          "value": 20
        },
        {
          "label": "Rolling horizon (s)",
          "value": 60
        },
        {
          "label": "Oldest observed window end (stream seconds)",
          "value": 610
        },
        {
          "label": "Newest observed window end (stream seconds)",
          "value": 620
        },
        {
          "label": "Observed endpoint sample",
          "value": [
            {
              "dst": "198.51.100.70",
              "dport": 1000,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1001,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1002,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1003,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1004,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1005,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1006,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1007,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1008,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1009,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1010,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1011,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1012,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1013,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1014,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1015,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1016,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1017,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1018,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1019,
              "protocols": [
                "tcp"
              ]
            }
          ]
        },
        {
          "label": "Endpoint sample truncated",
          "value": false
        },
        {
          "label": "History evictions",
          "value": {
            "source_entries": 0,
            "pair_entries_total": 0,
            "pairs_for_source": 0
          }
        }
      ],
      "caveat": "This rolling fan-out pattern uses one-way packet metadata. Bounded history evictions can make the retained pair count lower than the full observed history; authorized scanners can produce similar patterns.",
      "next_step": "If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.",
      "score_label": "Rule score",
      "related": [],
      "export_key": "4084786e2a47d581b2f7278d9426ffe17914ca99899c139a7d471afbde89c4b0"
    },
    "record_key": "4084786e2a47d581b2f7278d9426ffe17914ca99899c139a7d471afbde89c4b0",
    "ui_row_key": "2025-09-09T21:30:19.000Z|192.0.2.70|recon_rolling_vertical_scan|0.52"
  },
  "source-context": {
    "record": {
      "timestamp": "2025-09-09T21:30:39.000Z",
      "src": "192.0.2.81",
      "dst": "198.51.100.80",
      "flow_id": "192.0.2.81:*->198.51.100.80:443/tcp",
      "threat_class": "data_exfiltration",
      "confidence": 0.95,
      "severity": "critical",
      "evidence": {
        "bytes_to_new_dst": 600000,
        "pair_age_windows": 0,
        "src_baseline_bytes_median": 600,
        "ratio_vs_baseline": 1000,
        "novel_destination": true,
        "why": "large sustained upload to a destination not observed within this source's retained history lookback, far above its normal observed window volume",
        "source_novel_within_lookback": true,
        "source_history_lookback_windows": 8640,
        "source_history_coverage_at_admission": "complete_within_lookback",
        "source_history_coverage_now": "complete_within_lookback",
        "fleet_destination_novel": false,
        "source_history": {
          "retained_pairs": 3645,
          "capacity": 50000,
          "max_age_windows": 8640,
          "incomplete_sources": 0,
          "global_coverage_incomplete": false,
          "expired_entries": 0,
          "evicted_entries": 0
        }
      }
    },
    "triage": {
      "kind": "rule",
      "label": "Large transfer to a new destination",
      "summary": "bytes to new destination 600000; baseline bytes 600; ratio 1000.0x; age windows 0",
      "facts": [
        {
          "label": "Observed bytes to new destination",
          "value": 600000
        },
        {
          "label": "Source median baseline bytes",
          "value": 600
        },
        {
          "label": "Ratio vs baseline",
          "value": 1000
        },
        {
          "label": "Pair age (windows)",
          "value": 0
        }
      ],
      "caveat": "One-way bytes show transfer volume, not authorization or successful exfiltration; benign backups can look similar.",
      "next_step": "Compare the observed destination and transfer volume with this source's prior byte baseline and backup schedule.",
      "score_label": "Rule score",
      "related": [],
      "export_key": "78e40440ebc15b12208757c53975bb59339ae8524d704fb441cfeb9193ae3580"
    },
    "record_key": "78e40440ebc15b12208757c53975bb59339ae8524d704fb441cfeb9193ae3580",
    "ui_row_key": "2025-09-09T21:30:39.000Z|192.0.2.81|data_exfiltration|0.95"
  },
  "dns": {
    "record": {
      "timestamp": "2025-09-09T21:24:08.000Z",
      "src": "10.0.0.11",
      "dst": "*",
      "flow_id": "10.0.0.11:*->*:53/udp",
      "threat_class": "dns_tunneling",
      "confidence": 0.537,
      "severity": "medium",
      "evidence": {
        "qtype": 16,
        "qname": "bxxlyy2nw2fmfbf2ncfcnnwfww4q4s6sko2tvgof2okt5z2gjy.exfil.xxxxxxxx.com.",
        "query_bytes": 70,
        "max_label_length": 50,
        "cumulative_tunnel_bytes": 350,
        "tunnel_queries_from_src": 5,
        "signals": "qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60",
        "note": "response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable",
        "why": "repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups"
      }
    },
    "triage": {
      "kind": "rule",
      "label": "Repeated bulky or overlong DNS queries",
      "summary": "query bytes 70; qtype 16; queries 5; cumulative query bytes 350; limitation not verified exfil volume",
      "facts": [
        {
          "label": "Query bytes",
          "value": 70
        },
        {
          "label": "Query type",
          "value": 16
        },
        {
          "label": "Maximum label length",
          "value": 50
        },
        {
          "label": "Tunnel-like queries",
          "value": 5
        },
        {
          "label": "Cumulative query bytes",
          "value": 350
        }
      ],
      "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
      "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
      "score_label": "Rule score",
      "related": [],
      "export_key": "991d04486e4164715eae235e527354c595f97e5ac84b386f1392697d5ba5c37f"
    },
    "record_key": "991d04486e4164715eae235e527354c595f97e5ac84b386f1392697d5ba5c37f",
    "ui_row_key": "2025-09-09T21:24:08.000Z|10.0.0.11|dns_tunneling|0.537"
  },
  "encrypted-metadata": {
    "record": {
      "timestamp": "2025-09-09T21:23:20.243Z",
      "src": "10.0.0.7",
      "dst": "198.51.100.23",
      "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
      "threat_class": "encrypted_session_malware",
      "confidence": 0.944,
      "severity": "critical",
      "evidence": {
        "model": "xgboost",
        "metadata_features": [
          6,
          3,
          11,
          0,
          0,
          2,
          3,
          394,
          0.019999980926513672,
          0.45623195266236183
        ]
      }
    },
    "triage": {
      "kind": "model",
      "label": "Encrypted-session model match",
      "summary": "named model inputs ClientHello cipher-suite count=6.0, ClientHello extension count=3.0, ClientHello offered TLS version=11.0",
      "facts": [
        {
          "label": "Model",
          "value": "xgboost"
        },
        {
          "label": "ClientHello cipher-suite count (count)",
          "value": 6
        },
        {
          "label": "ClientHello extension count (count)",
          "value": 3
        },
        {
          "label": "ClientHello offered TLS version (code: 10=TLS 1.0; 11=TLS 1.1; 12=TLS 1.2; 13=TLS 1.3; 0=unknown)",
          "value": 11
        },
        {
          "label": "Transport code (0 = TLS, 1 = QUIC)",
          "value": 0
        },
        {
          "label": "SNI-present flag (0/1)",
          "value": 0
        },
        {
          "label": "Signature-algorithm count (count)",
          "value": 2
        },
        {
          "label": "Flow packet count (packets)",
          "value": 3
        },
        {
          "label": "Flow bytes (bytes)",
          "value": 394
        },
        {
          "label": "Flow duration (seconds)",
          "value": 0.019999980926513672
        },
        {
          "label": "Packet-size coefficient of variation (unitless)",
          "value": 0.45623195266236183
        }
      ],
      "caveat": "The named vector contains client-side metadata and flow measurements. This alert has no metadata-availability flags, so a recorded zero does not establish whether a field was absent, empty, or defaulted.",
      "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
      "score_label": "Model score",
      "related": [],
      "export_key": "ac23cbcf86ec643146d58d0555d08a313fbab313b6ba6bc8c0140907ddad7075"
    },
    "record_key": "ac23cbcf86ec643146d58d0555d08a313fbab313b6ba6bc8c0140907ddad7075",
    "ui_row_key": "2025-09-09T21:23:20.243Z|10.0.0.7|encrypted_session_malware|0.944"
  },
  "scan-model": {
    "record": {
      "timestamp": "2025-09-09T21:24:19.000Z",
      "src": "10.0.0.13",
      "dst": "*",
      "flow_id": "10.0.0.13:*->*:0/*",
      "threat_class": "recon_model_scan",
      "confidence": 1,
      "severity": "critical",
      "evidence": {
        "model": "scan_rf",
        "features": [
          202,
          3,
          200,
          0.9900990099009901,
          14416
        ],
        "iforest_corroboration": {
          "model": "scan_iforest",
          "anomaly_score": -0.2838237650122478,
          "score_kind": "uncalibrated_decision_function",
          "more_anomalous_when": "lower"
        }
      }
    },
    "triage": {
      "kind": "model",
      "label": "Model-flagged scan pattern",
      "summary": "named model inputs Distinct destination/port pairs=202.0, Distinct destination IPs=3.0, Maximum ports on one destination=200.0",
      "facts": [
        {
          "label": "Model",
          "value": "scan_rf"
        },
        {
          "label": "Distinct destination/port pairs (pairs)",
          "value": 202
        },
        {
          "label": "Distinct destination IPs (IPs)",
          "value": 3
        },
        {
          "label": "Maximum ports on one destination (ports)",
          "value": 200
        },
        {
          "label": "Maximum per-destination share of pairs (unitless ratio)",
          "value": 0.9900990099009901
        },
        {
          "label": "Source bytes in window (bytes)",
          "value": 14416
        },
        {
          "label": "IsolationForest anomaly score",
          "value": -0.2838237650122478
        },
        {
          "label": "IsolationForest score kind",
          "value": "uncalibrated_decision_function"
        },
        {
          "label": "IsolationForest more anomalous when",
          "value": "lower"
        }
      ],
      "caveat": "This is a one-way traffic pattern; legitimate scanners or bursts can produce similar measurements.",
      "next_step": "If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.",
      "score_label": "Model score",
      "related": [],
      "export_key": "ffb5fb07512eb85077fc5554a6bf7035529e192463ab49ad3af66ea5c60cc2ba"
    },
    "record_key": "ffb5fb07512eb85077fc5554a6bf7035529e192463ab49ad3af66ea5c60cc2ba",
    "ui_row_key": "2025-09-09T21:24:19.000Z|10.0.0.13|recon_model_scan|1"
  },
  "source-correlation": {
    "record": {
      "timestamp": "2025-09-09T21:23:20.233Z",
      "src": "10.0.0.7",
      "dst": "*",
      "flow_id": "10.0.0.7:*->*:0/*",
      "threat_class": "confirmed_c2_implant",
      "confidence": 0.999,
      "severity": "critical",
      "evidence": {
        "contributing_signals": [
          {
            "threat_class": "c2_beaconing",
            "at_s": 188,
            "age_s": 12.2,
            "confidence": 0.739,
            "effective_confidence": 0.689,
            "dst": "198.51.100.23",
            "dport": 0
          },
          {
            "threat_class": "ml_flow_suspicious",
            "at_s": 193.1,
            "age_s": 7.1,
            "confidence": 1,
            "effective_confidence": 0.96,
            "dst": "198.51.100.23",
            "dport": 0
          },
          {
            "threat_class": "tls_known_malware",
            "at_s": 200.2,
            "age_s": 0,
            "confidence": 0.99,
            "effective_confidence": 0.99,
            "dst": "198.51.100.23",
            "dport": 0
          }
        ],
        "combination": "noisy-OR with exponential decay (half-life=120s)",
        "window_s": 120,
        "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"
      }
    },
    "triage": {
      "kind": "correlation",
      "label": "Correlated TLS and periodicity signals",
      "summary": "signals c2_beaconing, ml_flow_suspicious, tls_known_malware; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
      "facts": [
        {
          "label": "Correlation window (s)",
          "value": 120
        },
        {
          "label": "Combination method",
          "value": "noisy-OR with exponential decay (half-life=120s)"
        }
      ],
      "caveat": "Correlation combines detector outputs from one-way observations; signals may share causes and do not confirm compromise.",
      "next_step": "Review each listed source alert and its packet-time window before escalating.",
      "score_label": "Correlation score",
      "related": [
        {
          "label": "c2_beaconing",
          "age_seconds": 12.2,
          "effective_score": 0.689,
          "destination": "198.51.100.23"
        },
        {
          "label": "ml_flow_suspicious",
          "age_seconds": 7.1,
          "effective_score": 0.96,
          "destination": "198.51.100.23"
        },
        {
          "label": "tls_known_malware",
          "age_seconds": 0,
          "effective_score": 0.99,
          "destination": "198.51.100.23"
        }
      ],
      "export_key": "c0fbac1eb8c2b817b2a90106a36cb713b51b8263813c69a4b6b2ab31ef41c558"
    },
    "record_key": "c0fbac1eb8c2b817b2a90106a36cb713b51b8263813c69a4b6b2ab31ef41c558",
    "ui_row_key": "2025-09-09T21:23:20.233Z|10.0.0.7|confirmed_c2_implant|0.999"
  },
  "evidence-export": {
    "record": {
      "timestamp": "2025-09-09T21:30:19.000Z",
      "src": "192.0.2.70",
      "dst": "198.51.100.70",
      "flow_id": "192.0.2.70:*->198.51.100.70:*/tcp",
      "threat_class": "recon_rolling_vertical_scan",
      "confidence": 0.52,
      "severity": "medium",
      "evidence": {
        "rolling_window_s": 60,
        "rolling_distinct_dst_port_pairs": 20,
        "current_window_distinct_pairs": 10,
        "distinct_dst_ips": 1,
        "pairs_on_top_dst": 20,
        "oldest_observed_window_end_s": 610,
        "newest_observed_window_end_s": 620,
        "observed_endpoints_sample": [
          {
            "dst": "198.51.100.70",
            "dport": 1000,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1001,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1002,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1003,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1004,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1005,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1006,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1007,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1008,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1009,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1010,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1011,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1012,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1013,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1014,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1015,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1016,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1017,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1018,
            "protocols": [
              "tcp"
            ]
          },
          {
            "dst": "198.51.100.70",
            "dport": 1019,
            "protocols": [
              "tcp"
            ]
          }
        ],
        "observed_endpoints_truncated": false,
        "history_evictions": {
          "source_entries": 0,
          "pair_entries_total": 0,
          "pairs_for_source": 0
        },
        "why": "distinct destination/port pairs accumulated from one source within the observed rolling time horizon; all inputs are one-way packet metadata"
      }
    },
    "triage": {
      "kind": "rule",
      "label": "Rolling-window port scan against one destination",
      "summary": "destination/port pairs 20; destinations 1; top-destination pairs 20; rolling horizon (s) 60.0; current-window pairs 10; observed window-end times (stream ...",
      "facts": [
        {
          "label": "Distinct destination/port pairs in rolling history",
          "value": 20
        },
        {
          "label": "Pairs in current window",
          "value": 10
        },
        {
          "label": "Distinct destination IPs",
          "value": 1
        },
        {
          "label": "Pairs on top destination",
          "value": 20
        },
        {
          "label": "Rolling horizon (s)",
          "value": 60
        },
        {
          "label": "Oldest observed window end (stream seconds)",
          "value": 610
        },
        {
          "label": "Newest observed window end (stream seconds)",
          "value": 620
        },
        {
          "label": "Observed endpoint sample",
          "value": [
            {
              "dst": "198.51.100.70",
              "dport": 1000,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1001,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1002,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1003,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1004,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1005,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1006,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1007,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1008,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1009,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1010,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1011,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1012,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1013,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1014,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1015,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1016,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1017,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1018,
              "protocols": [
                "tcp"
              ]
            },
            {
              "dst": "198.51.100.70",
              "dport": 1019,
              "protocols": [
                "tcp"
              ]
            }
          ]
        },
        {
          "label": "Endpoint sample truncated",
          "value": false
        },
        {
          "label": "History evictions",
          "value": {
            "source_entries": 0,
            "pair_entries_total": 0,
            "pairs_for_source": 0
          }
        }
      ],
      "caveat": "This rolling fan-out pattern uses one-way packet metadata. Bounded history evictions can make the retained pair count lower than the full observed history; authorized scanners can produce similar patterns.",
      "next_step": "If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.",
      "score_label": "Rule score",
      "related": [],
      "export_key": "4084786e2a47d581b2f7278d9426ffe17914ca99899c139a7d471afbde89c4b0"
    },
    "record_key": "4084786e2a47d581b2f7278d9426ffe17914ca99899c139a7d471afbde89c4b0",
    "ui_row_key": "2025-09-09T21:30:19.000Z|192.0.2.70|recon_rolling_vertical_scan|0.52"
  },
  "rolling_scan": {
    "timestamp": "2025-09-09T21:30:19.000Z",
    "src": "192.0.2.70",
    "dst": "198.51.100.70",
    "flow_id": "192.0.2.70:*->198.51.100.70:*/tcp",
    "threat_class": "recon_rolling_vertical_scan",
    "confidence": 0.52,
    "severity": "medium",
    "evidence": {
      "rolling_window_s": 60,
      "rolling_distinct_dst_port_pairs": 20,
      "current_window_distinct_pairs": 10,
      "distinct_dst_ips": 1,
      "pairs_on_top_dst": 20,
      "oldest_observed_window_end_s": 610,
      "newest_observed_window_end_s": 620,
      "observed_endpoints_sample": [
        {
          "dst": "198.51.100.70",
          "dport": 1000,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1001,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1002,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1003,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1004,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1005,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1006,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1007,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1008,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1009,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1010,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1011,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1012,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1013,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1014,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1015,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1016,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1017,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1018,
          "protocols": [
            "tcp"
          ]
        },
        {
          "dst": "198.51.100.70",
          "dport": 1019,
          "protocols": [
            "tcp"
          ]
        }
      ],
      "observed_endpoints_truncated": false,
      "history_evictions": {
        "source_entries": 0,
        "pair_entries_total": 0,
        "pairs_for_source": 0
      },
      "why": "distinct destination/port pairs accumulated from one source within the observed rolling time horizon; all inputs are one-way packet metadata"
    }
  },
  "source_context": {
    "timestamp": "2025-09-09T21:30:39.000Z",
    "src": "192.0.2.81",
    "dst": "198.51.100.80",
    "flow_id": "192.0.2.81:*->198.51.100.80:443/tcp",
    "threat_class": "data_exfiltration",
    "confidence": 0.95,
    "severity": "critical",
    "evidence": {
      "bytes_to_new_dst": 600000,
      "pair_age_windows": 0,
      "src_baseline_bytes_median": 600,
      "ratio_vs_baseline": 1000,
      "novel_destination": true,
      "why": "large sustained upload to a destination not observed within this source's retained history lookback, far above its normal observed window volume",
      "source_novel_within_lookback": true,
      "source_history_lookback_windows": 8640,
      "source_history_coverage_at_admission": "complete_within_lookback",
      "source_history_coverage_now": "complete_within_lookback",
      "fleet_destination_novel": false,
      "source_history": {
        "retained_pairs": 3645,
        "capacity": 50000,
        "max_age_windows": 8640,
        "incomplete_sources": 0,
        "global_coverage_incomplete": false,
        "expired_entries": 0,
        "evicted_entries": 0
      }
    }
  },
  "encrypted_metadata_xgb": {
    "timestamp": "2025-09-09T21:23:20.243Z",
    "src": "10.0.0.7",
    "dst": "198.51.100.23",
    "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
    "threat_class": "encrypted_session_malware",
    "confidence": 0.944,
    "severity": "critical",
    "evidence": {
      "model": "xgboost",
      "metadata_features": [
        6,
        3,
        11,
        0,
        0,
        2,
        3,
        394,
        0.019999980926513672,
        0.45623195266236183
      ]
    }
  }
}
```

Recorded cursor/filter actions and their timing (these are action logs, not additional detector measurements):

```json
[
  {
    "clip": "overview",
    "selector": "#sensor-strip",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22046.826,
    "dwell_ms": 3500
  },
  {
    "clip": "overview",
    "selector": "#kpis",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22052.618,
    "dwell_ms": 3500
  },
  {
    "clip": "overview",
    "selector": "#queue-count",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22056.342,
    "dwell_ms": 1500
  },
  {
    "clip": "beacon",
    "selector": "#search",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22068.329,
    "dwell_ms": 0
  },
  {
    "clip": "beacon",
    "selector": "#alert-rows tr[data-key]",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22072.067,
    "dwell_ms": 0
  },
  {
    "clip": "beacon",
    "selector": "#detail-facts",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22078.405,
    "dwell_ms": 4200
  },
  {
    "clip": "rolling-scan",
    "selector": "#search",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22091.329,
    "dwell_ms": 0
  },
  {
    "clip": "rolling-scan",
    "selector": "#alert-rows tr[data-key]",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22095.026,
    "dwell_ms": 0
  },
  {
    "clip": "rolling-scan",
    "selector": "#detail-facts",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22101.673,
    "dwell_ms": 4500
  },
  {
    "clip": "source-context",
    "selector": "#search",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22118.394,
    "dwell_ms": 0
  },
  {
    "clip": "source-context",
    "selector": "#alert-rows tr[data-key]",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22122.088,
    "dwell_ms": 0
  },
  {
    "clip": "source-context",
    "selector": "#detail-facts",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22128.736,
    "dwell_ms": 4500
  },
  {
    "clip": "source-context",
    "selector": ".raw-evidence summary",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22133.344,
    "dwell_ms": 1800
  },
  {
    "clip": "source-context",
    "selector": "#detail-evidence",
    "action": "gradual evidence scroll",
    "scroll_steps": 4,
    "timestamp_monotonic": 22138.218
  },
  {
    "clip": "dns",
    "selector": "#search",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22145.396,
    "dwell_ms": 0
  },
  {
    "clip": "dns",
    "selector": "#alert-rows tr[data-key]",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22149.091,
    "dwell_ms": 0
  },
  {
    "clip": "dns",
    "selector": "#detail-facts",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22155.435,
    "dwell_ms": 4200
  },
  {
    "clip": "encrypted-metadata",
    "selector": "#search",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22169.408,
    "dwell_ms": 0
  },
  {
    "clip": "encrypted-metadata",
    "selector": "#alert-rows tr[data-key]",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22173.135,
    "dwell_ms": 0
  },
  {
    "clip": "encrypted-metadata",
    "selector": "#detail-facts",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22179.804,
    "dwell_ms": 4500
  },
  {
    "clip": "scan-model",
    "selector": "#search",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22202.641,
    "dwell_ms": 0
  },
  {
    "clip": "scan-model",
    "selector": "#alert-rows tr[data-key]",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22206.361,
    "dwell_ms": 0
  },
  {
    "clip": "scan-model",
    "selector": "#detail-facts",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22212.708,
    "dwell_ms": 4200
  },
  {
    "clip": "source-correlation",
    "selector": "#top-sources [data-source=\"10.0.0.7\"]",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22227.949,
    "dwell_ms": 1500
  },
  {
    "clip": "source-correlation",
    "selector": "#source-filter",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22231.6,
    "dwell_ms": 1500
  },
  {
    "clip": "source-correlation",
    "selector": "#search",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22235.272,
    "dwell_ms": 0
  },
  {
    "clip": "source-correlation",
    "selector": "#alert-rows tr[data-key]",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22238.973,
    "dwell_ms": 0
  },
  {
    "clip": "source-correlation",
    "selector": "#detail-related",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22245.615,
    "dwell_ms": 4500
  },
  {
    "clip": "evidence-export",
    "selector": "#search",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22249.605,
    "dwell_ms": 0
  },
  {
    "clip": "evidence-export",
    "selector": "#alert-rows tr[data-key]",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22253.302,
    "dwell_ms": 0
  },
  {
    "clip": "evidence-export",
    "selector": "#detail-facts",
    "click": false,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22258.465,
    "dwell_ms": 3000
  },
  {
    "clip": "evidence-export",
    "selector": ".raw-evidence summary",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22264.272,
    "dwell_ms": 3000
  },
  {
    "clip": "evidence-export",
    "selector": "#export-alert",
    "click": true,
    "steps": 60,
    "move_seconds": 1.1,
    "timestamp_monotonic": 22266.413,
    "dwell_ms": 0
  }
]
```

## All replay record values and dynamic counters

The live Seen and Analyzed counters progress through actual replay counts up to 14,171, with 0 sampled out. Queue, severity, source, category and origin counts change as these records arrive or filters change. Their brief basis is §11: recorded synthetic replay values, with the Synthetic replay qualifier. This section preserves the entire 108-record stream, including every original score/address/time/measurement that may appear in the dashboard table. No counter state is a performance benchmark.

```jsonl
{"timestamp": "2025-09-09T21:20:08.143Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "encrypted_session_malware", "confidence": 1.0, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9999}}
{"timestamp": "2025-09-09T21:20:08.143Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 2, "nbytes": 174, "duration": 0.01, "nsyn": 1, "bytes_per_pkt": 87.0, "pkts_per_sec": 200.0, "is_udp": 0, "dport": 443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:20:08.143Z", "src": "10.0.0.7", "dst": "*", "flow_id": "10.0.0.7:*->*:0/*", "threat_class": "multi_signal_fusion", "confidence": 0.999, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "encrypted_session_malware", "at_s": 8.1, "age_s": 0.0, "confidence": 1.0, "effective_confidence": 0.999, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "ml_flow_suspicious", "at_s": 8.1, "age_s": 0.0, "confidence": 1.0, "effective_confidence": 0.999, "dst": "198.51.100.23", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:20:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:20:33.026Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.798, "severity": "high", "evidence": {"flows_in_series": 6, "mean_interval_s": 4.98, "iat_cv": 0.0179, "cv_gate": 0.15, "last_iats_s": [4.84, 5.06, 4.94, 4.97, 5.09], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:20:33.026Z", "src": "10.0.0.7", "dst": "*", "flow_id": "10.0.0.7:*->*:0/*", "threat_class": "multi_signal_fusion", "confidence": 0.996, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "c2_beaconing", "at_s": 33.0, "age_s": 0.0, "confidence": 0.798, "effective_confidence": 0.798, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "encrypted_session_malware", "at_s": 8.1, "age_s": 24.9, "confidence": 1.0, "effective_confidence": 0.866, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "ml_flow_suspicious", "at_s": 8.1, "age_s": 24.9, "confidence": 1.0, "effective_confidence": 0.866, "dst": "198.51.100.23", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:21:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:21:12.889Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 2, "nbytes": 174, "duration": 0.01, "nsyn": 1, "bytes_per_pkt": 87.0, "pkts_per_sec": 200.0, "is_udp": 0, "dport": 443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:21:20.000Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.645, "severity": "medium", "evidence": {"qname_label": "ujt4ftlh33hw8d", "label_length": 14, "char_entropy_bits": 3.38, "vowel_ratio": 0.07, "digit_ratio": 0.29, "high_entropy_query_streak": 3, "dga_queries_seen_from_src": 5, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:21:20.000Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:0/*", "threat_class": "multi_signal_fusion", "confidence": 0.98, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "dga_domain", "at_s": 80.0, "age_s": 0.0, "confidence": 0.645, "effective_confidence": 0.645, "dst": "*", "dport": 0}, {"threat_class": "ml_flow_suspicious", "at_s": 70.0, "age_s": 10.0, "confidence": 1.0, "effective_confidence": 0.944, "dst": "8.8.8.8", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:21:22.955Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.933, "severity": "critical", "evidence": {"flows_in_series": 16, "mean_interval_s": 4.99, "iat_cv": 0.0278, "cv_gate": 0.25, "last_iats_s": [5.18, 4.97, 4.8, 5.15, 4.93], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:22:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:22:12.932Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 2, "nbytes": 174, "duration": 0.01, "nsyn": 1, "bytes_per_pkt": 87.0, "pkts_per_sec": 200.0, "is_udp": 0, "dport": 443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:22:17.990Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.701, "severity": "high", "evidence": {"flows_in_series": 26, "mean_interval_s": 5.19, "iat_cv": 0.1825, "cv_gate": 0.25, "last_iats_s": [5.22, 5.03, 4.84, 4.96, 5.07], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:23:10.000Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.691, "severity": "medium", "evidence": {"qname_label": "5qxs2u4oj7g4eb", "label_length": 14, "char_entropy_bits": 3.66, "vowel_ratio": 0.21, "digit_ratio": 0.36, "high_entropy_query_streak": 3, "dga_queries_seen_from_src": 13, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:23:08.019Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.739, "severity": "high", "evidence": {"flows_in_series": 36, "mean_interval_s": 5.14, "iat_cv": 0.1574, "cv_gate": 0.25, "last_iats_s": [5.16, 5.08, 4.74, 5.12, 5.03], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:23:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:23:13.137Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 2, "nbytes": 174, "duration": 0.01, "nsyn": 1, "bytes_per_pkt": 87.0, "pkts_per_sec": 200.0, "is_udp": 0, "dport": 443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:23:20.233Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tls", "threat_class": "tls_known_malware", "confidence": 0.99, "severity": "critical", "evidence": {"ja4": "t11i060300_0fe2066a0070_637ee6fc4330", "ja3": "50b71d2a05458c98bc2005134ca0bfa8", "sni": null, "cipher_count": 6, "tls_version": "11", "transport": "tls", "match_source": "threat-intel (known-bad JA4)", "why": "ClientHello fingerprint matches a known-malware TLS stack"}}
{"timestamp": "2025-09-09T21:23:20.233Z", "src": "10.0.0.7", "dst": "*", "flow_id": "10.0.0.7:*->*:0/*", "threat_class": "confirmed_c2_implant", "confidence": 0.999, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "c2_beaconing", "at_s": 188.0, "age_s": 12.2, "confidence": 0.739, "effective_confidence": 0.689, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "ml_flow_suspicious", "at_s": 193.1, "age_s": 7.1, "confidence": 1.0, "effective_confidence": 0.96, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "tls_known_malware", "at_s": 200.2, "age_s": 0.0, "confidence": 0.99, "effective_confidence": 0.99, "dst": "198.51.100.23", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:23:20.243Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.944, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 0, 0.0, 2.0, 3.0, 394.0, 0.019999980926513672, 0.45623195266236183]}}
{"timestamp": "2025-09-09T21:23:20.243Z", "src": "10.0.0.7", "dst": "*", "flow_id": "10.0.0.7:*->*:0/*", "threat_class": "confirmed_c2_implant", "confidence": 0.999, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "c2_beaconing", "at_s": 188.0, "age_s": 12.2, "confidence": 0.739, "effective_confidence": 0.689, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "encrypted_session_malware", "at_s": 200.2, "age_s": 0.0, "confidence": 0.944, "effective_confidence": 0.944, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "ml_flow_suspicious", "at_s": 193.1, "age_s": 7.1, "confidence": 1.0, "effective_confidence": 0.96, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "tls_known_malware", "at_s": 200.2, "age_s": 0.0, "confidence": 0.99, "effective_confidence": 0.99, "dst": "198.51.100.23", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:23:20.243Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.999, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9989}}
{"timestamp": "2025-09-09T21:23:54.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.833, "severity": "high", "evidence": {"qname_label": "zqfpqeayynkpfxxnwigm2tsdpghbkphkh6acsenborxd7rwhgl", "label_length": 50, "char_entropy_bits": 4.54, "vowel_ratio": 0.12, "digit_ratio": 0.06, "high_entropy_query_streak": 3, "dga_queries_seen_from_src": 3, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:24:00.000Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.691, "severity": "medium", "evidence": {"qname_label": "kbsepr1b20uc87", "label_length": 14, "char_entropy_bits": 3.66, "vowel_ratio": 0.14, "digit_ratio": 0.36, "high_entropy_query_streak": 3, "dga_queries_seen_from_src": 18, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:23:57.873Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.764, "severity": "high", "evidence": {"flows_in_series": 46, "mean_interval_s": 5.11, "iat_cv": 0.1405, "cv_gate": 0.25, "last_iats_s": [4.99, 4.83, 5.04, 4.92, 4.98], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:24:05.079Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.944, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 0, 0.0, 2.0, 3.0, 394.0, 0.019999980926513672, 0.45623195266236183]}}
{"timestamp": "2025-09-09T21:24:05.079Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.999, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9989}}
{"timestamp": "2025-09-09T21:24:08.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dns_tunneling", "confidence": 0.537, "severity": "medium", "evidence": {"qtype": 16, "qname": "bxxlyy2nw2fmfbf2ncfcnnwfww4q4s6sko2tvgof2okt5z2gjy.exfil.xxxxxxxx.com.", "query_bytes": 70, "max_label_length": 50, "cumulative_tunnel_bytes": 350, "tunnel_queries_from_src": 5, "signals": "qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60", "note": "response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable", "why": "repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups"}}
{"timestamp": "2025-09-09T21:24:08.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:0/*", "threat_class": "multi_signal_fusion", "confidence": 0.893, "severity": "high", "evidence": {"contributing_signals": [{"threat_class": "dga_domain", "at_s": 234.0, "age_s": 14.0, "confidence": 0.833, "effective_confidence": 0.768, "dst": "*", "dport": 0}, {"threat_class": "dns_tunneling", "at_s": 248.0, "age_s": 0.0, "confidence": 0.537, "effective_confidence": 0.537, "dst": "*", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:24:10.134Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/quic", "threat_class": "tls_novel_fingerprint", "confidence": 0.8, "severity": "high", "evidence": {"ja4": "q11i060300_0fe2066a0070_637ee6fc4330", "ja3": "50b71d2a05458c98bc2005134ca0bfa8", "sni": null, "cipher_count": 6, "ext_count": 3, "tls_version": "11", "transport": "quic", "novelty_scope": "global", "src_inventory_size": 1, "note": "server-side JA3S/cert unavailable (one-way feed)", "why": "fingerprint never seen fleet-wide -- new software or C2 implant"}}
{"timestamp": "2025-09-09T21:24:10.134Z", "src": "10.0.0.7", "dst": "*", "flow_id": "10.0.0.7:*->*:0/*", "threat_class": "confirmed_c2_implant", "confidence": 0.999, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "c2_beaconing", "at_s": 237.9, "age_s": 12.3, "confidence": 0.764, "effective_confidence": 0.712, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "encrypted_session_malware", "at_s": 245.1, "age_s": 5.1, "confidence": 0.944, "effective_confidence": 0.917, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "ml_flow_suspicious", "at_s": 193.1, "age_s": 57.0, "confidence": 1.0, "effective_confidence": 0.719, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "tls_known_malware", "at_s": 200.2, "age_s": 49.9, "confidence": 0.99, "effective_confidence": 0.742, "dst": "198.51.100.23", "dport": 0}, {"threat_class": "tls_novel_fingerprint", "at_s": 250.1, "age_s": 0.0, "confidence": 0.8, "effective_confidence": 0.8, "dst": "198.51.100.23", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:24:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:24:10.134Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/udp", "threat_class": "encrypted_session_malware", "confidence": 0.986, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 1, 0.0, 2.0, 1.0, 166.0, 0.0, 0.0]}}
{"timestamp": "2025-09-09T21:24:19.000Z", "src": "10.0.0.13", "dst": "203.0.113.20", "flow_id": "10.0.0.13:*->203.0.113.20:*/tcp", "threat_class": "recon_vertical_scan", "confidence": 0.702, "severity": "high", "evidence": {"distinct_dst_port_pairs": 202, "distinct_dst_ips": 3, "pairs_on_top_dst": 200, "window": "250-260s", "why": "single source fanned out across many destination ports/hosts in one window"}}
{"timestamp": "2025-09-09T21:24:19.000Z", "src": "10.0.0.13", "dst": "*", "flow_id": "10.0.0.13:*->*:0/*", "threat_class": "recon_model_scan", "confidence": 1.0, "severity": "critical", "evidence": {"model": "scan_rf", "features": [202.0, 3.0, 200.0, 0.9900990099009901, 14416.0], "iforest_corroboration": {"model": "scan_iforest", "anomaly_score": -0.2838237650122478, "score_kind": "uncalibrated_decision_function", "more_anomalous_when": "lower"}}}
{"timestamp": "2025-09-09T21:24:19.000Z", "src": "10.0.0.13", "dst": "*", "flow_id": "10.0.0.13:*->*:0/*", "threat_class": "multi_signal_fusion", "confidence": 0.999, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "recon_model_scan", "at_s": 259.0, "age_s": 0.0, "confidence": 1.0, "effective_confidence": 0.999, "dst": "*", "dport": 0}, {"threat_class": "recon_vertical_scan", "at_s": 259.0, "age_s": 0.0, "confidence": 0.702, "effective_confidence": 0.702, "dst": "203.0.113.20", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:24:17.912Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 2, "nbytes": 174, "duration": 0.01, "nsyn": 1, "bytes_per_pkt": 87.0, "pkts_per_sec": 200.0, "is_udp": 0, "dport": 443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:24:19.930Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/udp", "threat_class": "encrypted_session_malware", "confidence": 0.986, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 1, 0.0, 2.0, 1.0, 166.0, 0.0, 0.0]}}
{"timestamp": "2025-09-09T21:24:30.000Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.691, "severity": "medium", "evidence": {"qname_label": "ey3m0nq8ut60wl", "label_length": 14, "char_entropy_bits": 3.66, "vowel_ratio": 0.14, "digit_ratio": 0.36, "high_entropy_query_streak": 3, "dga_queries_seen_from_src": 21, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:24:30.142Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/udp", "threat_class": "encrypted_session_malware", "confidence": 0.986, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 1, 0.0, 2.0, 1.0, 166.0, 0.0, 0.0]}}
{"timestamp": "2025-09-09T21:24:43.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dns_tunneling", "confidence": 0.625, "severity": "medium", "evidence": {"qtype": 16, "qname": "xlrqf7k7o2bwbvb3h5gyl2ikwmheddtqxzrtgsuggmkh43x65t.exfil.xxxxxxxx.com.", "query_bytes": 70, "max_label_length": 50, "cumulative_tunnel_bytes": 700, "tunnel_queries_from_src": 10, "signals": "qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60", "note": "response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable", "why": "repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups"}}
{"timestamp": "2025-09-09T21:24:48.134Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.783, "severity": "high", "evidence": {"flows_in_series": 56, "mean_interval_s": 5.09, "iat_cv": 0.1279, "cv_gate": 0.25, "last_iats_s": [5.05, 5.14, 4.94, 4.99, 5.15], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:24:50.183Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.944, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 0, 0.0, 2.0, 3.0, 394.0, 0.019999980926513672, 0.45623195266236183]}}
{"timestamp": "2025-09-09T21:24:50.183Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.999, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9989}}
{"timestamp": "2025-09-09T21:25:04.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.854, "severity": "high", "evidence": {"qname_label": "2qfsp3nr4t72j6djrz7ykh35xqngutddlwa2q7scjs5woizmts", "label_length": 50, "char_entropy_bits": 4.67, "vowel_ratio": 0.08, "digit_ratio": 0.24, "high_entropy_query_streak": 13, "dga_queries_seen_from_src": 13, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:25:08.226Z", "src": "10.0.0.15", "dst": "151.101.1.3", "flow_id": "10.0.0.15:*->151.101.1.3:443/tls", "threat_class": "tls_novel_fingerprint", "confidence": 0.6, "severity": "medium", "evidence": {"ja4": "t12d080400_f876287a346c_e09390cf9280", "ja3": "949056d163340de1df376c954f73b160", "sni": "update.microsoft.com", "cipher_count": 8, "ext_count": 4, "tls_version": "12", "transport": "tls", "novelty_scope": "host", "src_inventory_size": 1, "note": "server-side JA3S/cert unavailable (one-way feed)", "why": "fingerprint new to this host but known elsewhere -- possible lateral movement or host software change"}}
{"timestamp": "2025-09-09T21:25:10.000Z", "src": "*", "dst": "*", "flow_id": "*:*->*:443/tcp", "threat_class": "ddos_volumetric_spoofed", "confidence": 0.905, "severity": "critical", "evidence": {"window_pkts": 1978, "pkt_rate_per_s": 197.8, "distinct_src_ips": 1523, "src_ip_entropy_bits": 9.29, "syn_ratio": 0.771, "why": "packet-rate spike with high source-IP entropy => spoofed-source volumetric flood"}}
{"timestamp": "2025-09-09T21:25:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:25:20.000Z", "src": "*", "dst": "*", "flow_id": "*:*->*:443/tcp", "threat_class": "ddos_volumetric_spoofed", "confidence": 0.901, "severity": "critical", "evidence": {"window_pkts": 1924, "pkt_rate_per_s": 192.4, "distinct_src_ips": 1506, "src_ip_entropy_bits": 9.28, "syn_ratio": 0.783, "why": "packet-rate spike with high source-IP entropy => spoofed-source volumetric flood"}}
{"timestamp": "2025-09-09T21:25:19.000Z", "src": "10.0.0.11", "dst": "45.33.32.156", "flow_id": "10.0.0.11:*->45.33.32.156:8443/tcp", "threat_class": "data_exfiltration", "confidence": 0.95, "severity": "critical", "evidence": {"bytes_to_new_dst": 933800, "pair_age_windows": 1, "src_baseline_bytes_median": 3349, "ratio_vs_baseline": 278.8, "novel_destination": true, "why": "large sustained upload to a destination not observed within this source's retained history lookback, far above its normal observed window volume", "source_novel_within_lookback": true, "source_history_lookback_windows": 8640, "source_history_coverage_at_admission": "complete_within_lookback", "source_history_coverage_now": "complete_within_lookback", "fleet_destination_novel": false, "source_history": {"retained_pairs": 1881, "capacity": 50000, "max_age_windows": 8640, "incomplete_sources": 0, "global_coverage_incomplete": false, "expired_entries": 0, "evicted_entries": 0}}}
{"timestamp": "2025-09-09T21:25:19.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:0/*", "threat_class": "confirmed_exfiltration", "confidence": 0.995, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "data_exfiltration", "at_s": 319.0, "age_s": 0.0, "confidence": 0.95, "effective_confidence": 0.95, "dst": "45.33.32.156", "dport": 0}, {"threat_class": "dga_domain", "at_s": 304.0, "age_s": 15.0, "confidence": 0.854, "effective_confidence": 0.783, "dst": "*", "dport": 0}, {"threat_class": "dns_tunneling", "at_s": 283.0, "age_s": 36.0, "confidence": 0.625, "effective_confidence": 0.508, "dst": "*", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:25:19.000Z", "src": "10.0.0.11", "dst": "45.33.32.156", "flow_id": "10.0.0.11:*->45.33.32.156:0/*", "threat_class": "data_exfiltration_model", "confidence": 0.756, "severity": "high", "evidence": {"model": "exfil_xgb", "features": [466200.0, 466458.0, 0.9994468955404345, 31.0, 0.0], "iforest_corroboration": {"model": "exfil_iforest", "anomaly_score": -0.2164184822313534, "score_kind": "uncalibrated_decision_function", "more_anomalous_when": "lower"}}}
{"timestamp": "2025-09-09T21:25:19.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:0/*", "threat_class": "confirmed_exfiltration", "confidence": 0.999, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "data_exfiltration", "at_s": 319.0, "age_s": 0.0, "confidence": 0.95, "effective_confidence": 0.95, "dst": "45.33.32.156", "dport": 0}, {"threat_class": "data_exfiltration_model", "at_s": 319.0, "age_s": 0.0, "confidence": 0.756, "effective_confidence": 0.756, "dst": "45.33.32.156", "dport": 0}, {"threat_class": "dga_domain", "at_s": 304.0, "age_s": 15.0, "confidence": 0.854, "effective_confidence": 0.783, "dst": "*", "dport": 0}, {"threat_class": "dns_tunneling", "at_s": 283.0, "age_s": 36.0, "confidence": 0.625, "effective_confidence": 0.508, "dst": "*", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:25:17.988Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 2, "nbytes": 174, "duration": 0.01, "nsyn": 1, "bytes_per_pkt": 87.0, "pkts_per_sec": 200.0, "is_udp": 0, "dport": 443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:25:30.000Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.668, "severity": "medium", "evidence": {"qname_label": "y7zxdfld9cba72", "label_length": 14, "char_entropy_bits": 3.52, "vowel_ratio": 0.07, "digit_ratio": 0.29, "high_entropy_query_streak": 3, "dga_queries_seen_from_src": 26, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:25:34.738Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.939, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 0, 0.0, 2.0, 3.0, 394.0, 0.020000934600830078, 0.45623195266236183]}}
{"timestamp": "2025-09-09T21:25:34.738Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.994, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9937}}
{"timestamp": "2025-09-09T21:25:37.860Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.789, "severity": "high", "evidence": {"flows_in_series": 66, "mean_interval_s": 5.08, "iat_cv": 0.1243, "cv_gate": 0.25, "last_iats_s": [5.02, 5.03, 4.95, 4.92, 4.98], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:25:50.500Z", "src": "10.0.0.9", "dst": "198.51.100.99", "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp", "threat_class": "encrypted_session_malware", "confidence": 1.0, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9999}}
{"timestamp": "2025-09-09T21:25:50.500Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:0/*", "threat_class": "multi_signal_fusion", "confidence": 0.999, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "dga_domain", "at_s": 330.0, "age_s": 20.5, "confidence": 0.668, "effective_confidence": 0.593, "dst": "*", "dport": 0}, {"threat_class": "encrypted_session_malware", "at_s": 350.5, "age_s": 0.0, "confidence": 1.0, "effective_confidence": 0.999, "dst": "198.51.100.99", "dport": 0}, {"threat_class": "ml_flow_suspicious", "at_s": 310.0, "age_s": 40.5, "confidence": 1.0, "effective_confidence": 0.791, "dst": "8.8.8.8", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:25:53.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dns_tunneling", "confidence": 0.8, "severity": "high", "evidence": {"qtype": 16, "qname": "cskmotbsyintjraf4bkbtxvr7twqje4kxquujoroz5wolf4mmg.exfil.xxxxxxxx.com.", "query_bytes": 70, "max_label_length": 50, "cumulative_tunnel_bytes": 1400, "tunnel_queries_from_src": 20, "signals": "qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60", "note": "response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable", "why": "repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups"}}
{"timestamp": "2025-09-09T21:26:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:26:14.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.797, "severity": "high", "evidence": {"qname_label": "yjiajt442c25tfg2khzclmcjd2ggftgnx6dzokat6e3zjycyfm", "label_length": 50, "char_entropy_bits": 4.32, "vowel_ratio": 0.1, "digit_ratio": 0.2, "high_entropy_query_streak": 23, "dga_queries_seen_from_src": 23, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:26:19.770Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.948, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 0, 0.0, 2.0, 3.0, 394.0, 0.019999027252197266, 0.45623195266236183]}}
{"timestamp": "2025-09-09T21:26:19.770Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.999, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9989}}
{"timestamp": "2025-09-09T21:26:19.770Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 3, "nbytes": 394, "duration": 0.02, "nsyn": 1, "bytes_per_pkt": 131.33, "pkts_per_sec": 150.01, "is_udp": 0, "dport": 8443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:26:20.125Z", "src": "10.0.0.9", "dst": "198.51.100.99", "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp", "threat_class": "encrypted_session_malware", "confidence": 1.0, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9999}}
{"timestamp": "2025-09-09T21:26:27.908Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.789, "severity": "high", "evidence": {"flows_in_series": 76, "mean_interval_s": 5.08, "iat_cv": 0.1242, "cv_gate": 0.25, "last_iats_s": [4.95, 5.19, 4.74, 5.16, 4.89], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:26:49.000Z", "src": "10.0.0.13", "dst": "203.0.113.20", "flow_id": "10.0.0.13:*->203.0.113.20:*/tcp", "threat_class": "recon_vertical_scan", "confidence": 0.835, "severity": "high", "evidence": {"distinct_dst_port_pairs": 335, "distinct_dst_ips": 2, "pairs_on_top_dst": 334, "window": "400-410s", "why": "single source fanned out across many destination ports/hosts in one window"}}
{"timestamp": "2025-09-09T21:26:49.000Z", "src": "10.0.0.13", "dst": "*", "flow_id": "10.0.0.13:*->*:0/*", "threat_class": "recon_model_scan", "confidence": 0.808, "severity": "high", "evidence": {"model": "scan_rf", "features": [335.0, 2.0, 334.0, 0.9970149253731343, 18106.0], "iforest_corroboration": {"model": "scan_iforest", "anomaly_score": -0.2759091284631018, "score_kind": "uncalibrated_decision_function", "more_anomalous_when": "lower"}}}
{"timestamp": "2025-09-09T21:26:50.000Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.691, "severity": "medium", "evidence": {"qname_label": "jotv7h10b8vk9q", "label_length": 14, "char_entropy_bits": 3.66, "vowel_ratio": 0.07, "digit_ratio": 0.36, "high_entropy_query_streak": 3, "dga_queries_seen_from_src": 33, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:26:50.055Z", "src": "10.0.0.9", "dst": "198.51.100.99", "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp", "threat_class": "encrypted_session_malware", "confidence": 1.0, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9999}}
{"timestamp": "2025-09-09T21:26:59.000Z", "src": "10.0.0.13", "dst": "203.0.113.20", "flow_id": "10.0.0.13:*->203.0.113.20:*/tcp", "threat_class": "recon_vertical_scan", "confidence": 0.667, "severity": "medium", "evidence": {"distinct_dst_port_pairs": 167, "distinct_dst_ips": 2, "pairs_on_top_dst": 166, "window": "410-420s", "why": "single source fanned out across many destination ports/hosts in one window"}}
{"timestamp": "2025-09-09T21:26:59.000Z", "src": "10.0.0.13", "dst": "*", "flow_id": "10.0.0.13:*->*:0/*", "threat_class": "recon_model_scan", "confidence": 0.842, "severity": "high", "evidence": {"model": "scan_rf", "features": [167.0, 2.0, 166.0, 0.9940119760479041, 15247.0], "iforest_corroboration": {"model": "scan_iforest", "anomaly_score": -0.27459781405233485, "score_kind": "uncalibrated_decision_function", "more_anomalous_when": "lower"}}}
{"timestamp": "2025-09-09T21:27:05.084Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "c2_beaconing", "confidence": 0.816, "severity": "high", "evidence": {"flows_in_series": 6, "mean_interval_s": 44.97, "iat_cv": 0.0058, "cv_gate": 0.15, "last_iats_s": [44.84, 45.1, 44.55, 45.03, 45.33], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:27:05.104Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.944, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 0, 0.0, 2.0, 3.0, 394.0, 0.019999980926513672, 0.45623195266236183]}}
{"timestamp": "2025-09-09T21:27:05.104Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.999, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9989}}
{"timestamp": "2025-09-09T21:27:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:27:18.003Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.935, "severity": "critical", "evidence": {"flows_in_series": 86, "mean_interval_s": 5.0, "iat_cv": 0.0263, "cv_gate": 0.25, "last_iats_s": [4.89, 5.03, 5.18, 4.78, 5.15], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:27:20.260Z", "src": "10.0.0.9", "dst": "198.51.100.99", "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp", "threat_class": "encrypted_session_malware", "confidence": 1.0, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9999}}
{"timestamp": "2025-09-09T21:27:24.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.853, "severity": "high", "evidence": {"qname_label": "dxlds3dkbcqndbwk72j76pgmdganl3vowtpgrk7zytfz6524ne", "label_length": 50, "char_entropy_bits": 4.67, "vowel_ratio": 0.06, "digit_ratio": 0.22, "high_entropy_query_streak": 33, "dga_queries_seen_from_src": 33, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:27:22.893Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 2, "nbytes": 174, "duration": 0.01, "nsyn": 1, "bytes_per_pkt": 87.0, "pkts_per_sec": 200.0, "is_udp": 0, "dport": 443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:27:30.000Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.668, "severity": "medium", "evidence": {"qname_label": "ulthycx8ae0jxy", "label_length": 14, "char_entropy_bits": 3.52, "vowel_ratio": 0.21, "digit_ratio": 0.14, "high_entropy_query_streak": 3, "dga_queries_seen_from_src": 37, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:27:49.955Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.939, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 0, 0.0, 2.0, 3.0, 394.0, 0.020000934600830078, 0.45623195266236183]}}
{"timestamp": "2025-09-09T21:27:49.955Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.992, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.992}}
{"timestamp": "2025-09-09T21:27:50.077Z", "src": "10.0.0.9", "dst": "198.51.100.99", "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp", "threat_class": "encrypted_session_malware", "confidence": 1.0, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9999}}
{"timestamp": "2025-09-09T21:28:08.015Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.936, "severity": "critical", "evidence": {"flows_in_series": 96, "mean_interval_s": 5.0, "iat_cv": 0.0261, "cv_gate": 0.25, "last_iats_s": [4.87, 4.91, 5.09, 4.89, 5.14], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:28:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:28:13.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dns_tunneling", "confidence": 0.97, "severity": "critical", "evidence": {"qtype": 16, "qname": "t5wswrjqsw3ks7zbdetf3y7h54bdpnxhtyrmnh7udsktmaausz.exfil.xxxxxxxx.com.", "query_bytes": 70, "max_label_length": 50, "cumulative_tunnel_bytes": 2800, "tunnel_queries_from_src": 40, "signals": "qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60", "note": "response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable", "why": "repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups"}}
{"timestamp": "2025-09-09T21:28:20.000Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.691, "severity": "medium", "evidence": {"qname_label": "90472uqln6bgua", "label_length": 14, "char_entropy_bits": 3.66, "vowel_ratio": 0.21, "digit_ratio": 0.43, "high_entropy_query_streak": 3, "dga_queries_seen_from_src": 41, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:28:19.861Z", "src": "10.0.0.9", "dst": "198.51.100.99", "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.815, "severity": "high", "evidence": {"flows_in_series": 6, "mean_interval_s": 29.87, "iat_cv": 0.0064, "cv_gate": 0.15, "last_iats_s": [29.62, 29.93, 30.2, 29.82, 29.79], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:28:19.861Z", "src": "10.0.0.9", "dst": "*", "flow_id": "10.0.0.9:*->*:0/*", "threat_class": "botnet_c2_with_dga", "confidence": 0.999, "severity": "critical", "evidence": {"contributing_signals": [{"threat_class": "c2_beaconing", "at_s": 499.9, "age_s": 0.0, "confidence": 0.815, "effective_confidence": 0.815, "dst": "198.51.100.99", "dport": 0}, {"threat_class": "dga_domain", "at_s": 500.0, "age_s": 0.0, "confidence": 0.691, "effective_confidence": 0.691, "dst": "*", "dport": 0}, {"threat_class": "encrypted_session_malware", "at_s": 470.1, "age_s": 29.8, "confidence": 1.0, "effective_confidence": 0.842, "dst": "198.51.100.99", "dport": 0}, {"threat_class": "ml_flow_suspicious", "at_s": 490.0, "age_s": 9.9, "confidence": 1.0, "effective_confidence": 0.945, "dst": "8.8.8.8", "dport": 0}], "combination": "noisy-OR with exponential decay (half-life=120s)", "window_s": 120.0, "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"}}
{"timestamp": "2025-09-09T21:28:19.871Z", "src": "10.0.0.9", "dst": "198.51.100.99", "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp", "threat_class": "encrypted_session_malware", "confidence": 1.0, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9999}}
{"timestamp": "2025-09-09T21:28:22.898Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 2, "nbytes": 174, "duration": 0.01, "nsyn": 1, "bytes_per_pkt": 87.0, "pkts_per_sec": 200.0, "is_udp": 0, "dport": 443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:28:34.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.839, "severity": "high", "evidence": {"qname_label": "bqhyphlsmybr7uliqjdryq4ly6bvnjlukeg4d6ewoytx7vt2co", "label_length": 50, "char_entropy_bits": 4.58, "vowel_ratio": 0.14, "digit_ratio": 0.14, "high_entropy_query_streak": 43, "dga_queries_seen_from_src": 43, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:28:35.194Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tls", "threat_class": "tls_known_malware", "confidence": 0.99, "severity": "critical", "evidence": {"ja4": "t11i060300_0fe2066a0070_637ee6fc4330", "ja3": "50b71d2a05458c98bc2005134ca0bfa8", "sni": null, "cipher_count": 6, "tls_version": "11", "transport": "tls", "match_source": "threat-intel (known-bad JA4)", "why": "ClientHello fingerprint matches a known-malware TLS stack"}}
{"timestamp": "2025-09-09T21:28:35.204Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.944, "severity": "critical", "evidence": {"model": "xgboost", "metadata_features": [6.0, 3.0, 11.0, 0, 0.0, 2.0, 3.0, 394.0, 0.019999980926513672, 0.45623195266236183]}}
{"timestamp": "2025-09-09T21:28:35.204Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp", "threat_class": "encrypted_session_malware", "confidence": 0.999, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9989}}
{"timestamp": "2025-09-09T21:28:49.569Z", "src": "10.0.0.9", "dst": "198.51.100.99", "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp", "threat_class": "encrypted_session_malware", "confidence": 1.0, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9999}}
{"timestamp": "2025-09-09T21:28:58.131Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.935, "severity": "critical", "evidence": {"flows_in_series": 106, "mean_interval_s": 5.0, "iat_cv": 0.0267, "cv_gate": 0.25, "last_iats_s": [5.28, 4.87, 5.02, 5.06, 5.03], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:29:10.000Z", "src": "10.0.0.9", "dst": "8.8.8.8", "flow_id": "10.0.0.9:*->8.8.8.8:53/udp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9998, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 1, "nbytes": 78, "duration": 0.0, "nsyn": 0, "bytes_per_pkt": 78.0, "pkts_per_sec": 1000.0, "is_udp": 1, "dport": 53, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:29:20.450Z", "src": "10.0.0.9", "dst": "198.51.100.99", "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp", "threat_class": "encrypted_session_malware", "confidence": 1.0, "severity": "critical", "evidence": {"model": "1d-cnn", "sequence_score": 0.9999}}
{"timestamp": "2025-09-09T21:29:23.061Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "ml_flow_suspicious", "confidence": 1.0, "severity": "critical", "evidence": {"malicious_probability": 0.9999, "model": "lightgbm (temporal split)", "flow_features": {"npkt": 2, "nbytes": 174, "duration": 0.01, "nsyn": 1, "bytes_per_pkt": 87.0, "pkts_per_sec": 200.0, "is_udp": 0, "dport": 443, "sport_priv": 0, "dst_internal": 0}, "why": "supervised model flags this flow's feature vector as highly likely malicious"}}
{"timestamp": "2025-09-09T21:29:44.000Z", "src": "10.0.0.11", "dst": "*", "flow_id": "10.0.0.11:*->*:53/udp", "threat_class": "dga_domain", "confidence": 0.817, "severity": "high", "evidence": {"qname_label": "6fsxab54kbuja7dh67oqmtvezwomvfumt5k5i6v74vf4z4l6a3", "label_length": 50, "char_entropy_bits": 4.45, "vowel_ratio": 0.18, "digit_ratio": 0.3, "high_entropy_query_streak": 53, "dga_queries_seen_from_src": 53, "note": "response side not observable (one-way); NXDOMAIN correlation unavailable", "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains", "dga_cnn_prob": 1.0, "detector_tier": "tier1_lexical+cnn_confirmed"}}
{"timestamp": "2025-09-09T21:29:48.134Z", "src": "10.0.0.7", "dst": "198.51.100.23", "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp", "threat_class": "c2_beaconing", "confidence": 0.935, "severity": "critical", "evidence": {"flows_in_series": 116, "mean_interval_s": 5.0, "iat_cv": 0.0268, "cv_gate": 0.25, "last_iats_s": [4.91, 5.07, 4.89, 4.97, 5.25], "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"}}
{"timestamp": "2025-09-09T21:30:19.000Z", "src": "192.0.2.70", "dst": "198.51.100.70", "flow_id": "192.0.2.70:*->198.51.100.70:*/tcp", "threat_class": "recon_rolling_vertical_scan", "confidence": 0.52, "severity": "medium", "evidence": {"rolling_window_s": 60.0, "rolling_distinct_dst_port_pairs": 20, "current_window_distinct_pairs": 10, "distinct_dst_ips": 1, "pairs_on_top_dst": 20, "oldest_observed_window_end_s": 610.0, "newest_observed_window_end_s": 620.0, "observed_endpoints_sample": [{"dst": "198.51.100.70", "dport": 1000, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1001, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1002, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1003, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1004, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1005, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1006, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1007, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1008, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1009, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1010, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1011, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1012, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1013, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1014, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1015, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1016, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1017, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1018, "protocols": ["tcp"]}, {"dst": "198.51.100.70", "dport": 1019, "protocols": ["tcp"]}], "observed_endpoints_truncated": false, "history_evictions": {"source_entries": 0, "pair_entries_total": 0, "pairs_for_source": 0}, "why": "distinct destination/port pairs accumulated from one source within the observed rolling time horizon; all inputs are one-way packet metadata"}}
{"timestamp": "2025-09-09T21:30:39.000Z", "src": "192.0.2.81", "dst": "198.51.100.80", "flow_id": "192.0.2.81:*->198.51.100.80:443/tcp", "threat_class": "data_exfiltration", "confidence": 0.95, "severity": "critical", "evidence": {"bytes_to_new_dst": 600000, "pair_age_windows": 0, "src_baseline_bytes_median": 600, "ratio_vs_baseline": 1000.0, "novel_destination": true, "why": "large sustained upload to a destination not observed within this source's retained history lookback, far above its normal observed window volume", "source_novel_within_lookback": true, "source_history_lookback_windows": 8640, "source_history_coverage_at_admission": "complete_within_lookback", "source_history_coverage_now": "complete_within_lookback", "fleet_destination_novel": false, "source_history": {"retained_pairs": 3645, "capacity": 50000, "max_age_windows": 8640, "incomplete_sources": 0, "global_coverage_incomplete": false, "expired_entries": 0, "evicted_entries": 0}}}
```

## Export and evidence provenance

Selected alert identities, recorded model inputs and scores are the original pipeline records in the capture manifest. Downloaded bundles are listed under `downloads`, with original-record hashes, filters and explicit provenance availability. The alert-record SHA-256 is not packet provenance or legal chain of custody.

## Additions not in the brief

The diagram wording enumerated above and original visual artwork are added editorial content. Scene labels/headlines and narration are registered in §11 by their source file. There are no invented capabilities, accuracy figures, threat verdicts, calibrated probabilities, team members, event wins or product URLs.
