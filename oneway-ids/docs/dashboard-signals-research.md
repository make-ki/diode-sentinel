# Dashboard signal content: research and repo-specific recommendation

Research checked 29–30 September 2026. This note concerns what an analyst needs to see and do in the dashboard, not visual styling. Product references below are primary documentation. Those products' workflows are research references, not features shipped here. The proposed fields and ordering are an inference from those workflows and the actual alert records in this repository.

## What established SOC workflows expose

- Elastic's alert detail view puts related entities, correlated alerts, threat-intelligence matches, and prevalence in the investigation context. Its detection response overview emphasizes recent/high-priority alerts and drill-through from counts to alerts. This supports showing the reason for a signal beside direct pivots into nearby alerts and time context, rather than a chart that cannot be investigated. [Elastic: detection alert details](https://www.elastic.co/guide/en/security/current/view-alert-details.html) · [Elastic: Detection & Response dashboard](https://www.elastic.co/guide/en/security/current/detection-response-dashboard.html)
- Microsoft Sentinel describes an incident as a chronology of evidence and entities, and puts the alert timeline at the center so the analyst can answer why the item was raised. For this sensor, use an alert/source chronology with contributing detector records; do not invent identities or endpoint entities. [Microsoft Sentinel: incident investigation](https://learn.microsoft.com/en-us/azure/sentinel/incident-investigation)
- Security Onion's Alerts interface supports time selection, sorting, grouped and detailed views, acknowledgement, escalation to cases, row details, and pivots into Hunt or PCAP. The useful pattern is a compact queue with a detail surface and explicit analyst workflow state. This repo currently has no persisted acknowledgement/case workflow or full packet retrieval, so these controls should only be added when backed by real state/actions. [Security Onion: Alerts](https://docs.securityonion.net/en/2.4/alerts.html)
- Suricata EVE uses timestamp, flow identifier, source/destination tuple, protocol, and alert metadata; its `flow_id` correlates related event types. The repository's `flow_id` is a display tuple key, not a Suricata session ID: it must not be presented as evidence that both directions or a complete session were observed. [Suricata: EVE JSON format](https://docs.suricata.io/en/latest/output/eve/eve-json-format.html)
- Elastic's risk/criticality filters depend on separately available entity risk and asset criticality fields. Those are enrichment inputs, not properties inferable from an IP address or alert confidence. [Elastic: risk score data](https://www.elastic.co/guide/en/security/current/analyze-risk-score-data.html)

## Signals actually present in this repo

The emitted record has `timestamp`, `src`, `dst`, `flow_id`, `threat_class`, `confidence`, `severity`, and `evidence`. I inspected `.regression/alerts_rules.reference.jsonl` (46 alerts) and `.regression/alerts_ml.reference.jsonl` (68 alerts), rather than relying on detector labels alone. Rules fixture classes are 14 `c2_beaconing`, 14 `dga_domain`, 4 `dns_tunneling`, 3 `tls_known_malware`, 3 `recon_vertical_scan`, 2 `ddos_volumetric_spoofed`, and six singletons across fusion, novel TLS, and exfiltration. The ML fixture adds 20 `ml_flow_suspicious` alerts and more fusion records. These are regression replay outputs, not live prevalence estimates.

| Signal | Evidence fields to put in the alert detail | Analyst interpretation |
|---|---|---|
| C2 beaconing | `flows_in_series`, `mean_interval_s`, `iat_cv`, `cv_gate`, `last_iats_s` | Show the measured interval variation against the detector gate; it is periodicity evidence, not proof of C2. |
| DGA domain | `qname_label`, `label_length`, `char_entropy_bits`, `vowel_ratio`, `digit_ratio`, `high_entropy_query_streak`, `dga_queries_seen_from_src` | Show the exact scored label and lexical measurements. DNS response codes and NXDOMAIN rate are unavailable. |
| DNS tunneling | `qname`, `qtype`, `query_bytes`, `max_label_length`, `tunnel_queries_from_src`, `cumulative_tunnel_bytes`, `signals` | Show the actual query-side observations and which gates contributed. `cumulative_tunnel_bytes` sums lengths of anomalous query names; it is not verified exfiltrated data. Do not imply successful resolution or returned data. |
| TLS known/novel | `transport`, `tls_version`, `ja3`, `ja4`, `cipher_count`, `ext_count`, `sni`, `match_source` (known-match only) | Mark JA3/JA4 as client-hello fingerprints. The current `KNOWN_BAD_JA4` entry is a simulated hello-profile indicator in `core/hello_profiles.py` / `core/config.py`, despite the emitted `match_source` text saying “threat-intel”; present its provenance as a local simulated indicator, not an external threat-intelligence match. A client hello does not reveal negotiated cipher, server certificate, or server fingerprint. |
| Recon scan | `distinct_dst_ips`, `distinct_dst_port_pairs`, `pairs_on_top_dst`, `window` | Show fan-out counts and observation window, not a generic “attack” label. |
| DDoS / spoofed flood | `window_pkts`, `pkt_rate_per_s`, `distinct_src_ips`, `src_ip_entropy_bits`, `syn_ratio` | Show packet rate, source diversity/entropy, and SYN proportion. These fixture alerts do not include a `window_s` field; do not invent or imply a duration unless separately surfaced from the detector's real window configuration. Do not infer replies or victim impact. |
| Exfiltration | `bytes_to_new_dst`, `src_baseline_bytes_median`, `ratio_vs_baseline`, `novel_destination`, `pair_age_windows` | Make the baseline and observed destination novelty explicit. There is no emitted `novelty_scope` field on these alerts. “New destination” is relative to observed inventory, not reputation or confirmed exfiltration. |
| Fusion | `combination`, `window_s`, `contributing_signals[]` including class, confidence, age and effective confidence | Show each source signal and decay/age. Prefer “correlated signals” or the emitted fusion class; avoid an unqualified confirmed-incident banner. |
| ML flow | `model`, `malicious_probability`, `flow_features` | Label as model score/probability with model name, not calibrated threat certainty. Its MESSY-capture false-positive behavior is documented; do not make it the primary queue ranking signal. |

The evidence object also contains detector-written `why` strings and sometimes `note`/`signals`. These should be secondary explanatory text. The measured values and threshold/gate fields should be the primary explanation because they are inspectable and make alert quality auditable. Fields in this table were checked against the fixture JSONL and detector implementation; optional model modes can emit different schemas, as noted below.

### Optional model evidence and limits

The 68-alert ML fixture includes 20 `ml_flow_suspicious` records with `model`, `malicious_probability`, and `flow_features`; this is the existing LightGBM flow tier. The probability is a model output and the documented MESSY replay emits many false positives on designated benign hosts, so it should be visibly marked as model evidence and must not dominate queue priority.

`--models-567` is a separate optional mode and is not represented by these two default regression fixtures. It can emit `encrypted_session_malware`, `recon_model_scan`, and `data_exfiltration_model` with model-specific fields such as `model`, feature vectors, or sequence score. Its measured validation supports four supervised models at recall 1.000 and zero benign false positives on the documented temporal split; the two IsolationForest models failed to meet the 0.5% benign-FP budget at sensitive thresholds and therefore are not shipped as standalone alert sources. If these alerts are displayed, preserve model name and raw feature/score semantics; IsolationForest evidence is explicitly an uncalibrated corroborating score.

The optional DGA CNN is another distinct mode. Its per-label score alone has a measured high benign false-positive rate and the shipped detector requires a multi-query quorum. Do not expose a CNN-only score as a standalone malicious verdict. If a CNN-assisted alert is ever added to the UI, show the quorum/streak context and label the score as model output.

## One-way boundary and absent context

The dashboard can safely show the observed directional source/destination addresses, destination port/protocol where represented in `flow_id`, capture timestamp, source-side timing and volume, source-written DNS query fields, and client hello metadata. Preserve the direction label (“observed source → destination”) in detail views.

Do not show as if measured: server-side JA3S, negotiated cipher, server certificate, RTT, DNS response code/NXDOMAIN ratio, reverse-direction bytes, completed handshake/session state, or server replies. A `dst: "*"` means the alert has no specific destination attribution; it should remain explicitly unattributed. The repository does not supply asset names, user identity, business criticality, host ownership, external threat-intelligence reputation feed, analyst acknowledgement/assignment, case status, or packet-retention link. Such enrichment may be useful later, but the UI must not fabricate defaults or infer it from private/public IP ranges. In particular, the current TLS `match_source` string overstates provenance: the configured indicator comes from the repository's simulated hello profile, not an external feed.

Severity is currently assigned from confidence thresholds in `core/detectors.py`; confidence is detector output, not an empirically calibrated probability that the host is malicious. Display both the severity label and numeric confidence, with concise help text that explains this distinction. A fusion alert aggregates detector outputs; it is not independent confirmation.

## Recommended minimum signals surface

1. **Queue columns:** first/last observed time (for grouped rows), severity, detector/threat class, observed source → destination, count, confidence, and a small “signals” count for multi-detector correlation. Default ordering should favor severity and recency while retaining filters for time, class, source, destination, severity, and model-vs-rule source. Do not rank only by the maximum source alert confidence: repeated medium alerts can be operationally important.
2. **Detail header:** detector name/class, severity, raw confidence with its uncalibrated meaning, time, directional tuple, and whether this is a single detector or fusion record.
3. **Evidence block:** render evidence as typed key/value facts; promote detector-specific measured values and their threshold/gate side by side. Keep `why` as a short explanation below facts. For fusion, list contributing signals with their ages and effective confidence. For DNS, show the full query only in the expanded view because it can be long/sensitive.
4. **Triage pivots:** clicking source/destination should filter the observed alert set; offer “same source in time window” and “same flow key” pivots. A timeline should contain only observed alerts and capture events available to this app, with gaps left as gaps. Any grouping must retain access to each original alert.
5. **Sensor context:** show feed state, capture/parser mode, last data timestamp, and packet/alert counters only when sourced from `run_stats.json`; mark paused/disconnected/stale distinctly. A quiet queue alone cannot distinguish a quiet network from a stopped sensor.
6. **Analyst disposition:** acknowledgement, notes, assignment, or cases become useful SOC functions once persisted server-side. Current alert JSONL is append-only output and does not provide this lifecycle, so these are roadmap items rather than pretend-working buttons.

For a first implementation pass, prioritize (1) queue fields and filters, (2) evidence values with gates/thresholds, (3) grouped-alert expansion that preserves raw records, (4) source/time pivots, and (5) honest sensor freshness. Add no broad dashboard chart unless it answers a clear triage question and links into the underlying records. This ordering is an inference from the product workflows above and the project's one-way data contract.

## Implemented surface (30 September 2026)

The dashboard now prioritises the alert queue, with charts below it. A separate
presentation adapter (`dashboard_signals.py`) reads recorded evidence without
changing alert files or detector decisions. It supplies concise measurements,
typed facts, limitations and read-only verification suggestions for each known
class. Unknown classes keep their original evidence and receive no invented
measurements. Original detector rationale remains available in the raw evidence
expander, including any wording that the cautious presentation qualifies.

The summary partitions raw records into rule, model and correlation records;
critical rule records are a labelled subset. Correlation records are never
counted as additional independent incidents. The queue identifies each record's
origin and exposes UTC time bounds, exact-source filtering, origin filtering,
and optional severity-first ordering. The leading-detections chart filters by
class when a bar is selected. Source summaries show the composition of matched
records, rather than calling an address compromised because it has many alerts.

Correlations show their recorded contributors, ages and effective scores.
Rule/model/correlation scores are not presented as calibrated probabilities of
compromise. The authorisation registry is shown only where an alert records a
match. DNS query-name byte counts are not presented as verified stolen data.
The shipped TLS known-list indicator's simulated provenance is explicit.

Run-sidecar fields are labelled as last-run metadata. Browser refresh status is
separate from capture health, which remains unreported. No active-sensor,
zero-loss, ownership, successful-session, acknowledgement or case-state claims
are manufactured. Grouped incidents, persisted analyst dispositions and direct
PCAP retrieval remain proposals, not shipped features.
