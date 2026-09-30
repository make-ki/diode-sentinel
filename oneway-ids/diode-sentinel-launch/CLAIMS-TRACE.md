> Historical 52-second film. Current B/C explainer trace: [EXPLAINER-CLAIMS-TRACE.md](EXPLAINER-CLAIMS-TRACE.md).

# Product-demo claims trace

Authority: ../VIDEO-BRIEF.md **§9 approved product-demonstration revision**.
That user-approved revision replaces the §3/§8 contract-first narrative.
The film describes actual workflows and model purposes; it makes no accuracy,
false-positive, throughput, production-live-traffic or six-working-model claim.
React/Remotion are video tooling and are never presented as the sensor stack.

## Authored on-screen copy

Every rendered literal from src/product-config.ts is listed below. Unused
callout fields and technical composition parameters are excluded. **ADDED**
means editorial wording beyond the brief's literal wording, with the cited
factual basis.

| Config path | On-screen text | Brief / implementation source |
|---|---|---|
| `brand` | Diode Sentinel | §0 / §9 product identity |
| `team` | samarags | §9 supplied team identity |
| `qualifier` | Recorded software · Synthetic replay | §9 fresh recorded synthetic replay |
| `intro.line` | Traffic. Turned into evidence. | §9 name / real software narrative; ADDED editorial wording |
| `live.title` | Watch the signal take shape. | §2.9 / §9 live operator workflow; ADDED headline wording |
| `live.label` | Live packet analysis | §2.9 / §9 live operator workflow; ADDED headline wording |
| `evidence.title` | Open the alert. See the evidence. | §2.8 / §9 opening severity, detector score and observations; ADDED headline wording |
| `evidence.label` | Evidence-backed alerts | §2.8 / §9 opening severity, detector score and observations; ADDED headline wording |
| `sources.title` | Follow the source. Connect the signals. | §2.8 / §9 source filtering and correlation; core/ml_tier.py / core/models_567.py for corroborating roles; ADDED headline wording |
| `sources.label` | Source attribution & correlation | §2.8 / §9 source filtering and correlation; core/ml_tier.py / core/models_567.py for corroborating roles; ADDED headline wording |
| `sources.support.0.name` | LightGBM | §2.8 / §9 source filtering and correlation; core/ml_tier.py / core/models_567.py for corroborating roles; ADDED headline wording |
| `sources.support.0.role` | Flow-level scoring | §2.8 / §9 source filtering and correlation; core/ml_tier.py / core/models_567.py for corroborating roles; ADDED headline wording |
| `sources.support.1.name` | Isolation Forest | §2.8 / §9 source filtering and correlation; core/ml_tier.py / core/models_567.py for corroborating roles; ADDED headline wording |
| `sources.support.1.role` | Anomaly corroboration | §2.8 / §9 source filtering and correlation; core/ml_tier.py / core/models_567.py for corroborating roles; ADDED headline wording |
| `modelCards.0.title` | Patterns in domain names. | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.0.name` | Character CNN | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.0.role` | DGA analysis | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.0.features.0` | Query strings | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.0.features.1` | Character patterns | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.0.note` | Model role · rules remain enabled | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.1.title` | Signals inside encrypted sessions. | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.1.name` | Sequence CNN + XGBoost | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.1.role` | Encrypted-session analysis | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.1.features.0` | Packet sizes & timing | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.1.features.1` | TLS / QUIC metadata | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.1.note` | Model role · rules remain enabled | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.2.title` | Reveal scanning patterns. | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.2.name` | Random Forest | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.2.role` | Reconnaissance analysis | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.2.features.0` | Destination fan-out | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.2.features.1` | Port fan-out | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.2.note` | Model role · rules remain enabled | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.3.title` | Spot unusual transfers. | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.3.name` | XGBoost | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.3.role` | Exfiltration analysis | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.3.features.0` | Transfer volume | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.3.features.1` | Host baseline & novelty | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `modelCards.3.note` | Model role · rules remain enabled | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels |
| `passive.title` | Observe. Without a probe. | §0 / §4 / §9 receive-side passive hardware-diode monitoring; ADDED headline wording |
| `passive.label` | Passive one-way monitoring | §0 / §4 / §9 receive-side passive hardware-diode monitoring; ADDED headline wording |
| `passive.source` | Received packets | §0 / §4 / §9 receive-side passive hardware-diode monitoring; ADDED headline wording |
| `passive.diode` | Hardware data diode | §0 / §4 / §9 receive-side passive hardware-diode monitoring; ADDED headline wording |
| `passive.sensor` | Diode Sentinel | §0 / §4 / §9 receive-side passive hardware-diode monitoring; ADDED headline wording |
| `closing.line` | Traffic. Turned into evidence. | §0 / §9 SIH identity and samarags; ADDED editorial wording |
| `closing.by` | Built by | §0 / §9 SIH identity and samarags; ADDED editorial wording |
| `closing.event` | SIH 2026 · PS-26145 | §0 / §9 SIH identity and samarags; ADDED editorial wording |

## Spoken copy

| Scene | Exact narration | Source |
|---|---|---|
| intro | Diode Sentinel. Traffic, turned into evidence. | §9 name / real software narrative; ADDED editorial wording; §9. ADDED spoken wording. |
| live | Watch packets arrive, counters update, and security alerts take shape. All in one operator view. | §2.9 / §9 live operator workflow; ADDED headline wording; §9. ADDED spoken wording. |
| evidence | Open an alert to see its severity, score, and the exact signal behind it. | §2.8 / §9 opening severity, detector score and observations; ADDED headline wording; §9. ADDED spoken wording. |
| sources | Follow each source. Correlate signals across detectors. Light G B M and Isolation Forest add supporting evidence. | §2.8 / §9 source filtering and correlation; core/ml_tier.py / core/models_567.py for corroborating roles; ADDED headline wording; §9. ADDED spoken wording. |
| dns | A character C N N examines domain names. | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels; §9. ADDED spoken wording. |
| encrypted | Sequence C N N and X G Boost examine encrypted sessions. | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels; §9. ADDED spoken wording. |
| scan | Random Forest identifies scanning patterns. | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels; §9. ADDED spoken wording. |
| exfil | X G Boost examines transfers and destination novelty. | §9 approved model explanations; core/dga_cnn.py, core/packet_sequence_cnn.py, core/models_567.py; ADDED concise role/input labels; §9. ADDED spoken wording. |
| passive | Passive monitoring. Built for the receive side of a hardware data diode. | §0 / §4 / §9 receive-side passive hardware-diode monitoring; ADDED headline wording; §9. ADDED spoken wording. |
| closing | Diode Sentinel. Built by Sama rags. | §0 / §9 SIH identity and samarags; ADDED editorial wording; §9. ADDED spoken wording. |

“Sama rags” is the voice-engine pronunciation spelling of the supplied
**samarags**; on-screen spelling is samarags. The DNS scene describes the
enabled character CNN's purpose while a **rules DNS-tunnelling alert** is
opened. It does not claim the CNN produced that alert. LightGBM/Isolation
Forest are supporting tiers, not primary proof; their overlays explain roles
and do not attribute the currently selected C2 correlation to Isolation Forest.

## Text and numbers inside recorded software

§2.9 and §9 authorize real dashboard footage. Its labels, dates, addresses,
packet/alert counts, numeric model vectors, scores and observations are
**ADDED to the literal brief** as direct software observations. They retain
the persistent “Recorded software · Synthetic replay” caption. No count
represents independent incidents or detection accuracy. Historical timestamps
are seeded pcap event times; they are not the recording date. Recording was
made fresh on 30 September 2026. All data addresses are synthetic fixtures.

The footage itself is the source of intermediate live counts and UI filter
counts: public/captures/{overview,evidence,sources,correlation,dns,encrypted,scan,exfil,sensor}.mp4.
No number in those recordings is animated, replaced or hardcoded by Remotion.
Final API values and every alert record are preserved in
[the capture manifest](public/captures/capture-manifest.json). Manifest SHA-256:

`9c5093a0a8812694c47f48951ea5032c2119ac4527701374b86a03ec08f2ff8a`

Visible UI-label inventory (labels visible at different camera positions):

- Diode Sentinel
- Security operations
- Workspace
- Overview
- Traffic overview
- Inspect observed signals, supporting evidence and source context.
- Synthetic replay
- Sensor
- Active
- Completed
- Mode
- Packet stream
- Source
- Last packet received · UTC
- Heartbeat
- Seen
- Analyzed
- Sampled out
- Malformed
- Kernel drops
- Unknown
- Rule signals
- Critical rule signals
- Model signals
- Correlations
- Sources with alerts
- Authorised transfers
- Deterministic detector records
- Subset of rule signals
- Model-led alerts; not certainty
- Derived from other signals
- Excludes unattributed records
- Registry-matched alert records
- Alert queue
- Search IP address, detection or evidence…
- Critical
- High
- Medium
- Low
- All detections
- Show up to 400
- All signal origins
- Newest first
- From · UTC
- To · UTC
- Clear time
- Clear source
- Time · UTC
- Severity
- Detection
- Source → Destination
- Score
- Observed signal
- Matched records
- Detection categories
- DDoS / traffic bursts
- C2 beaconing
- DGA / DNS tunnelling
- Encrypted-session malware
- Recon / port scan
- Data exfiltration
- Timestamp
- Recorded Flow Key (Not A Session ID)
- Detector Identifier
- Signal Origin
- Destination
- Rule Score
- Model Score
- Correlation Score
- Observed measurements
- Flows in series
- Mean interval (s)
- Interval CV
- CV gate
- Correlation window (s)
- Combination method
- Signals used by this correlation
- Model
- Raw numeric feature vector
- Query bytes
- Query type
- Maximum label length
- Tunnel queries from source
- Model score (uncalibrated)
- Corroborating anomaly score
- Corroboration score kind
- Interpretation limits
- Suggested verification
- Original detector evidence
- rule
- model
- correlation

UI observation summaries and interpretation text in each selected alert are
listed verbatim in that alert's `triage` fields below, together with every
raw numeric value it can display. Formatting may round a table score to two
decimal places; the modal uses the actual record score. UI boilerplate about
synthetic traffic, score calibration, record counts and visibility limits
comes from static/index.html and static/app.js (§9 actual software); no
production narration is added around those caveats. Filtered “matched” counts
change during replay and use the same records, not separate test results.

Final values / numeric-label provenance (§9 fresh replay, not benchmarks):

```json
{
  "final_sensor_counts": {
    "seen": 14049,
    "analyzed": 14049,
    "sampled_out": 0,
    "malformed": 0,
    "kernel_drops": null
  },
  "final_sensor_status": "completed",
  "final_signal_counts": {
    "raw_records": 114,
    "rule_records": 42,
    "model_records": 61,
    "correlation_records": 11,
    "unknown_records": 0,
    "critical_rule_records": 12,
    "authorised_records": 0,
    "source_count": 5
  },
  "final_alerts": {
    "total": 114,
    "by_severity": {
      "critical": 80,
      "high": 22,
      "medium": 12,
      "low": 0
    },
    "coverage": [
      {
        "key": "a",
        "label": "DDoS / traffic bursts",
        "count": 2
      },
      {
        "key": "b",
        "label": "C2 beaconing",
        "count": 14
      },
      {
        "key": "c",
        "label": "DGA / DNS tunnelling",
        "count": 18
      },
      {
        "key": "d",
        "label": "Encrypted-session malware",
        "count": 41
      },
      {
        "key": "e",
        "label": "Recon / port scan",
        "count": 6
      },
      {
        "key": "f",
        "label": "Data exfiltration",
        "count": 2
      }
    ]
  },
  "sources": [
    {
      "source": "10.0.0.7",
      "records": 51
    },
    {
      "source": "10.0.0.9",
      "records": 38
    },
    {
      "source": "10.0.0.11",
      "records": 15
    },
    {
      "source": "10.0.0.13",
      "records": 7
    },
    {
      "source": "*",
      "records": 2
    },
    {
      "source": "10.0.0.15",
      "records": 1
    }
  ]
}
```

### evidence

Source: §9 recorded UI authorization; exact record in capture-manifest.json.
All following values and the triage text are observations from this synthetic
run, **ADDED to the literal brief**, not benchmark claims.

```json
{
  "timestamp": "2025-09-09T21:24:48.134Z",
  "src": "10.0.0.7",
  "dst": "198.51.100.23",
  "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
  "threat_class": "c2_beaconing",
  "confidence": 0.783,
  "severity": "high",
  "evidence": {
    "flows_in_series": 56,
    "mean_interval_s": 5.09,
    "iat_cv": 0.1279,
    "cv_gate": 0.25,
    "last_iats_s": [
      5.05,
      5.14,
      4.94,
      4.99,
      5.15
    ],
    "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
  },
  "triage": {
    "kind": "rule",
    "label": "Periodic flow pattern",
    "summary": "flows 56; mean interval (s) 5.09; CV 0.1279; gate 0.25",
    "facts": [
      {
        "label": "Flows in series",
        "value": 56
      },
      {
        "label": "Mean interval (s)",
        "value": 5.09
      },
      {
        "label": "Interval CV",
        "value": 0.1279
      },
      {
        "label": "CV gate",
        "value": 0.25
      }
    ],
    "caveat": "Periodicity is one-way observable but cloud telemetry and scheduled jobs can produce the same pattern.",
    "next_step": "Compare the recorded flow times with the source's expected scheduled connections.",
    "score_label": "Rule score",
    "related": []
  }
}
```

### correlation

Source: §9 recorded UI authorization; exact record in capture-manifest.json.
All following values and the triage text are observations from this synthetic
run, **ADDED to the literal brief**, not benchmark claims.

```json
{
  "timestamp": "2025-09-09T21:23:20.243Z",
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
        "threat_class": "encrypted_session_malware",
        "at_s": 200.2,
        "age_s": 0,
        "confidence": 0.944,
        "effective_confidence": 0.944,
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
  },
  "triage": {
    "kind": "correlation",
    "label": "Correlated TLS and periodicity signals",
    "summary": "signals c2_beaconing, encrypted_session_malware, ml_flow_suspicious, tls_known_malware; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not ...",
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
        "label": "encrypted_session_malware",
        "age_seconds": 0,
        "effective_score": 0.944,
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
    ]
  }
}
```

### dns

Source: §9 recorded UI authorization; exact record in capture-manifest.json.
All following values and the triage text are observations from this synthetic
run, **ADDED to the literal brief**, not benchmark claims.

```json
{
  "timestamp": "2025-09-09T21:25:53.000Z",
  "src": "10.0.0.11",
  "dst": "*",
  "flow_id": "10.0.0.11:*->*:53/udp",
  "threat_class": "dns_tunneling",
  "confidence": 0.8,
  "severity": "high",
  "evidence": {
    "qtype": 16,
    "qname": "cskmotbsyintjraf4bkbtxvr7twqje4kxquujoroz5wolf4mmg.exfil.xxxxxxxx.com.",
    "query_bytes": 70,
    "max_label_length": 50,
    "cumulative_tunnel_bytes": 1400,
    "tunnel_queries_from_src": 20,
    "signals": "qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60",
    "note": "response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable",
    "why": "repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups"
  },
  "triage": {
    "kind": "rule",
    "label": "Repeated bulky or overlong DNS queries",
    "summary": "query bytes 70; qtype 16; queries 20; cumulative query bytes 1400; limitation not verified exfil volume",
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
        "value": 20
      },
      {
        "label": "Cumulative query bytes",
        "value": 1400
      }
    ],
    "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
    "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
    "score_label": "Rule score",
    "related": []
  }
}
```

### encrypted

Source: §9 recorded UI authorization; exact record in capture-manifest.json.
All following values and the triage text are observations from this synthetic
run, **ADDED to the literal brief**, not benchmark claims.

```json
{
  "timestamp": "2025-09-09T21:28:35.204Z",
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
  },
  "triage": {
    "kind": "model",
    "label": "Encrypted-session model match",
    "summary": "Raw numeric model vector recorded (10 values)",
    "facts": [
      {
        "label": "Model",
        "value": "xgboost"
      },
      {
        "label": "Raw numeric feature vector",
        "value": [
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
    ],
    "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
    "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
    "score_label": "Model score",
    "related": []
  }
}
```

### scan

Source: §9 recorded UI authorization; exact record in capture-manifest.json.
All following values and the triage text are observations from this synthetic
run, **ADDED to the literal brief**, not benchmark claims.

```json
{
  "timestamp": "2025-09-09T21:26:59.000Z",
  "src": "10.0.0.13",
  "dst": "*",
  "flow_id": "10.0.0.13:*->*:0/*",
  "threat_class": "recon_model_scan",
  "confidence": 0.842,
  "severity": "high",
  "evidence": {
    "model": "scan_rf",
    "features": [
      167,
      2,
      166,
      0.9940119760479041,
      15247
    ],
    "iforest_corroboration": {
      "model": "scan_iforest",
      "anomaly_score": -0.27459781405233485,
      "score_kind": "uncalibrated_decision_function",
      "more_anomalous_when": "lower"
    }
  },
  "triage": {
    "kind": "model",
    "label": "Model-flagged scan pattern",
    "summary": "Raw numeric model vector recorded (5 values)",
    "facts": [
      {
        "label": "Model",
        "value": "scan_rf"
      },
      {
        "label": "Raw numeric feature vector",
        "value": [
          167,
          2,
          166,
          0.9940119760479041,
          15247
        ]
      },
      {
        "label": "IsolationForest anomaly score",
        "value": -0.27459781405233485
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
    "related": []
  }
}
```

### exfil

Source: §9 recorded UI authorization; exact record in capture-manifest.json.
All following values and the triage text are observations from this synthetic
run, **ADDED to the literal brief**, not benchmark claims.

```json
{
  "timestamp": "2025-09-09T21:25:19.000Z",
  "src": "10.0.0.11",
  "dst": "45.33.32.156",
  "flow_id": "10.0.0.11:*->45.33.32.156:0/*",
  "threat_class": "data_exfiltration_model",
  "confidence": 0.756,
  "severity": "high",
  "evidence": {
    "model": "exfil_xgb",
    "features": [
      466200,
      466458,
      0.9994468955404345,
      31,
      0
    ],
    "iforest_corroboration": {
      "model": "exfil_iforest",
      "anomaly_score": -0.2164184822313534,
      "score_kind": "uncalibrated_decision_function",
      "more_anomalous_when": "lower"
    }
  },
  "triage": {
    "kind": "model",
    "label": "Model-flagged transfer pattern",
    "summary": "Raw numeric model vector recorded (5 values)",
    "facts": [
      {
        "label": "Model",
        "value": "exfil_xgb"
      },
      {
        "label": "Raw numeric feature vector",
        "value": [
          466200,
          466458,
          0.9994468955404345,
          31,
          0
        ]
      },
      {
        "label": "IsolationForest anomaly score",
        "value": -0.2164184822313534
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
    "caveat": "One-way bytes show transfer volume, not authorization or successful exfiltration; benign backups can look similar.",
    "next_step": "Compare the observed destination and transfer volume with this source's prior byte baseline and backup schedule.",
    "score_label": "Model score",
    "related": []
  }
}
```

## Artwork and production annotations

The diode mark, light sweep, camera motion and moving diagram packets are
ADDED artwork. They illustrate the §0/§9 one-way architecture; packet speed
and number are not throughput measurements. No custom logo was supplied.
No project URL, hardware performance, probability, accuracy score or result
from an unshown dataset is invented. The music is the user-supplied First
Light track. beats.json contains measured accents and edit timestamps, which
are production metadata rather than product claims.
