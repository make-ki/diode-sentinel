export const capture = {
  "source": "fresh seeded synthetic replay",
  "viewport": {
    "width": 1600,
    "height": 1000
  },
  "clips": {
    "overview": {
      "focus": {
        "x": 234,
        "y": 239.59375,
        "width": 1338,
        "height": 65
      },
      "recordedSeconds": 13.094,
      "focusSelector": "#sensor-strip"
    },
    "evidence": {
      "focus": {
        "x": 432.5,
        "y": 100.78125,
        "width": 720,
        "height": 798.421875
      },
      "recordedSeconds": 12.157,
      "focusSelector": "#detail-modal .modal-box"
    },
    "sources": {
      "focus": {
        "x": 1313,
        "y": 129.28125,
        "width": 258,
        "height": 63.5
      },
      "recordedSeconds": 10.027,
      "focusSelector": "#top-sources"
    },
    "correlation": {
      "focus": {
        "x": 432.5,
        "y": 0,
        "width": 720,
        "height": 1000
      },
      "recordedSeconds": 9.804,
      "focusSelector": "#detail-modal .modal-box"
    },
    "dns": {
      "focus": {
        "x": 432.5,
        "y": 66.28125,
        "width": 720,
        "height": 867.421875
      },
      "recordedSeconds": 9.533,
      "focusSelector": "#detail-modal .modal-box"
    },
    "encrypted": {
      "focus": {
        "x": 432.5,
        "y": 126.28125,
        "width": 720,
        "height": 747.421875
      },
      "recordedSeconds": 9.801,
      "focusSelector": "#detail-modal .modal-box"
    },
    "scan": {
      "focus": {
        "x": 432.5,
        "y": 56.390625,
        "width": 720,
        "height": 887.21875
      },
      "recordedSeconds": 8.046,
      "focusSelector": "#detail-modal .modal-box"
    },
    "exfil": {
      "focus": {
        "x": 432.5,
        "y": 66.28125,
        "width": 720,
        "height": 867.421875
      },
      "recordedSeconds": 8.078,
      "focusSelector": "#detail-modal .modal-box"
    },
    "sensor": {
      "focus": {
        "x": 234,
        "y": 77.59375,
        "width": 1338,
        "height": 65
      },
      "recordedSeconds": 5.281,
      "focusSelector": "#sensor-strip"
    }
  },
  "interactions": [
    {
      "clip": "overview",
      "selector": "#sensor-strip",
      "click": false
    },
    {
      "clip": "overview",
      "selector": "#kpis",
      "click": false
    },
    {
      "clip": "overview",
      "selector": "#queue-count",
      "click": false
    },
    {
      "clip": "evidence",
      "selector": "#search",
      "click": true
    },
    {
      "clip": "evidence",
      "selector": "#alert-rows tr[data-key]",
      "click": true
    },
    {
      "clip": "evidence",
      "selector": "#detail-facts",
      "click": false
    },
    {
      "clip": "evidence",
      "selector": "#detail-meta",
      "click": false
    },
    {
      "clip": "sources",
      "selector": "#top-sources",
      "click": false
    },
    {
      "clip": "sources",
      "selector": "#top-sources [data-source]",
      "click": true
    },
    {
      "clip": "sources",
      "selector": "#source-filter",
      "click": false
    },
    {
      "clip": "correlation",
      "selector": "#search",
      "click": true
    },
    {
      "clip": "correlation",
      "selector": "#alert-rows tr[data-key]",
      "click": true
    },
    {
      "clip": "correlation",
      "selector": "#detail-related",
      "click": false
    },
    {
      "clip": "dns",
      "selector": "#search",
      "click": true
    },
    {
      "clip": "dns",
      "selector": "#alert-rows tr[data-key]",
      "click": true
    },
    {
      "clip": "dns",
      "selector": "#detail-facts",
      "click": false
    },
    {
      "clip": "encrypted",
      "selector": "#search",
      "click": true
    },
    {
      "clip": "encrypted",
      "selector": "#alert-rows tr[data-key]",
      "click": true
    },
    {
      "clip": "encrypted",
      "selector": "#detail-facts",
      "click": false
    },
    {
      "clip": "scan",
      "selector": "#search",
      "click": true
    },
    {
      "clip": "scan",
      "selector": "#alert-rows tr[data-key]",
      "click": true
    },
    {
      "clip": "scan",
      "selector": "#detail-facts",
      "click": false
    },
    {
      "clip": "exfil",
      "selector": "#search",
      "click": true
    },
    {
      "clip": "exfil",
      "selector": "#alert-rows tr[data-key]",
      "click": true
    },
    {
      "clip": "exfil",
      "selector": "#detail-facts",
      "click": false
    },
    {
      "clip": "sensor",
      "selector": "a.nav-link[href=\"#sensor-strip\"]",
      "click": true
    },
    {
      "clip": "sensor",
      "selector": "#sensor-strip",
      "click": false
    }
  ],
  "stats": {
    "total": 114,
    "critical": 80,
    "high": 22,
    "medium": 12,
    "low": 0,
    "classes": [
      "botnet_c2_with_dga",
      "c2_beaconing",
      "confirmed_c2_implant",
      "confirmed_exfiltration",
      "data_exfiltration",
      "data_exfiltration_model",
      "ddos_volumetric_spoofed",
      "dga_domain",
      "dns_tunneling",
      "encrypted_session_malware",
      "ml_flow_suspicious",
      "multi_signal_fusion",
      "recon_model_scan",
      "recon_vertical_scan",
      "tls_known_malware",
      "tls_novel_fingerprint"
    ],
    "suppressed": 20,
    "by_class": {
      "encrypted_session_malware": 37,
      "ml_flow_suspicious": 20,
      "c2_beaconing": 14,
      "dga_domain": 14,
      "multi_signal_fusion": 6,
      "dns_tunneling": 4,
      "tls_known_malware": 3,
      "recon_vertical_scan": 3,
      "recon_model_scan": 3,
      "confirmed_c2_implant": 2,
      "ddos_volumetric_spoofed": 2,
      "confirmed_exfiltration": 2,
      "tls_novel_fingerprint": 1,
      "data_exfiltration": 1,
      "data_exfiltration_model": 1,
      "botnet_c2_with_dga": 1
    },
    "by_severity": {
      "critical": 80,
      "high": 22,
      "medium": 12,
      "low": 0
    },
    "hosts": 5,
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
    ],
    "first_alert": "2025-09-09T21:20:08.143000+00:00",
    "last_alert": "2025-09-09T21:29:48.134000+00:00",
    "span_seconds": 580,
    "sensor": {
      "suppressed": 20,
      "parser": "live",
      "pkt_per_s": 209,
      "alerts": 114,
      "mode": "live",
      "health": {
        "status": "completed",
        "mode": "pcap_stream",
        "interface": null,
        "path": "/tmp/nix-shell.l9Xrtl/diode-product-f7vi045l/feed.pcap",
        "started_at": "2026-09-30T13:39:23.899604Z",
        "updated_at": "2026-09-30T13:40:32.162171Z",
        "heartbeat_at": "2026-09-30T13:40:32.162171Z",
        "last_packet_at": "2026-09-30T13:40:32.019019Z",
        "counts": {
          "seen": 14049,
          "analyzed": 14049,
          "sampled_out": 0,
          "malformed": 0,
          "kernel_drops": null
        },
        "error": null,
        "heartbeat_age_seconds": 27.4
      }
    },
    "synthetic_demo": true,
    "signals": {
      "raw_records": 114,
      "rule_records": 42,
      "model_records": 61,
      "correlation_records": 11,
      "unknown_records": 0,
      "critical_rule_records": 12,
      "authorised_records": 0,
      "source_count": 5
    }
  },
  "alerts": {
    "alerts": [
      {
        "timestamp": "2025-09-09T21:20:08.143Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.987,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            0,
            0,
            0,
            0,
            0,
            0,
            2,
            174,
            0.009999990463256836,
            0.3793103448275862
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
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                174,
                0.009999990463256836,
                0.3793103448275862
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:20:08.143Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9999
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9999",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:20:08.143Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 2,
            "nbytes": 174,
            "duration": 0.01,
            "nsyn": 1,
            "bytes_per_pkt": 87,
            "pkts_per_sec": 200,
            "is_udp": 0,
            "dport": 443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=2, bytes=174, duration_s=0.01, SYNs=1, mean_bytes_per_packet=87.0, packets_per_second=200.0, destination_port=443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 2
            },
            {
              "label": "Observed bytes",
              "value": 174
            },
            {
              "label": "Flow duration (s)",
              "value": 0.01
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 87
            },
            {
              "label": "Packets per second",
              "value": 200
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:20:08.143Z",
        "src": "10.0.0.7",
        "dst": "*",
        "flow_id": "10.0.0.7:*->*:0/*",
        "threat_class": "multi_signal_fusion",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "contributing_signals": [
            {
              "threat_class": "encrypted_session_malware",
              "at_s": 8.1,
              "age_s": 0,
              "confidence": 0.987,
              "effective_confidence": 0.987,
              "dst": "198.51.100.23",
              "dport": 0
            },
            {
              "threat_class": "ml_flow_suspicious",
              "at_s": 8.1,
              "age_s": 0,
              "confidence": 1,
              "effective_confidence": 0.999,
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
          "label": "Multiple correlated detector signals",
          "summary": "signals encrypted_session_malware, ml_flow_suspicious; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
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
              "label": "encrypted_session_malware",
              "age_seconds": 0,
              "effective_score": 0.987,
              "destination": "198.51.100.23"
            },
            {
              "label": "ml_flow_suspicious",
              "age_seconds": 0,
              "effective_score": 0.999,
              "destination": "198.51.100.23"
            }
          ]
        }
      },
      {
        "timestamp": "2025-09-09T21:20:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
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
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:20:33.026Z",
        "src": "10.0.0.7",
        "dst": "*",
        "flow_id": "10.0.0.7:*->*:0/*",
        "threat_class": "multi_signal_fusion",
        "confidence": 0.996,
        "severity": "critical",
        "evidence": {
          "contributing_signals": [
            {
              "threat_class": "c2_beaconing",
              "at_s": 33,
              "age_s": 0,
              "confidence": 0.798,
              "effective_confidence": 0.798,
              "dst": "198.51.100.23",
              "dport": 0
            },
            {
              "threat_class": "encrypted_session_malware",
              "at_s": 8.1,
              "age_s": 24.9,
              "confidence": 0.987,
              "effective_confidence": 0.855,
              "dst": "198.51.100.23",
              "dport": 0
            },
            {
              "threat_class": "ml_flow_suspicious",
              "at_s": 8.1,
              "age_s": 24.9,
              "confidence": 1,
              "effective_confidence": 0.866,
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
          "label": "Multiple correlated detector signals",
          "summary": "signals c2_beaconing, encrypted_session_malware, ml_flow_suspicious; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
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
              "age_seconds": 0,
              "effective_score": 0.798,
              "destination": "198.51.100.23"
            },
            {
              "label": "encrypted_session_malware",
              "age_seconds": 24.9,
              "effective_score": 0.855,
              "destination": "198.51.100.23"
            },
            {
              "label": "ml_flow_suspicious",
              "age_seconds": 24.9,
              "effective_score": 0.866,
              "destination": "198.51.100.23"
            }
          ]
        }
      },
      {
        "timestamp": "2025-09-09T21:21:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:21:12.889Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 2,
            "nbytes": 174,
            "duration": 0.01,
            "nsyn": 1,
            "bytes_per_pkt": 87,
            "pkts_per_sec": 200,
            "is_udp": 0,
            "dport": 443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=2, bytes=174, duration_s=0.01, SYNs=1, mean_bytes_per_packet=87.0, packets_per_second=200.0, destination_port=443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 2
            },
            {
              "label": "Observed bytes",
              "value": 174
            },
            {
              "label": "Flow duration (s)",
              "value": 0.01
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 87
            },
            {
              "label": "Packets per second",
              "value": 200
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:21:20.000Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.645,
        "severity": "medium",
        "evidence": {
          "qname_label": "ujt4ftlh33hw8d",
          "label_length": 14,
          "char_entropy_bits": 3.38,
          "vowel_ratio": 0.07,
          "digit_ratio": 0.29,
          "high_entropy_query_streak": 3,
          "dga_queries_seen_from_src": 5,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label ujt4ftlh33hw8d; length 14; lexical entropy (bits) 3.38",
          "facts": [
            {
              "label": "DNS label",
              "value": "ujt4ftlh33hw8d"
            },
            {
              "label": "Label length",
              "value": 14
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 3.38
            },
            {
              "label": "High-entropy streak",
              "value": 3
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:21:20.000Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:0/*",
        "threat_class": "multi_signal_fusion",
        "confidence": 0.98,
        "severity": "critical",
        "evidence": {
          "contributing_signals": [
            {
              "threat_class": "dga_domain",
              "at_s": 80,
              "age_s": 0,
              "confidence": 0.645,
              "effective_confidence": 0.645,
              "dst": "*",
              "dport": 0
            },
            {
              "threat_class": "ml_flow_suspicious",
              "at_s": 70,
              "age_s": 10,
              "confidence": 1,
              "effective_confidence": 0.944,
              "dst": "8.8.8.8",
              "dport": 0
            }
          ],
          "combination": "noisy-OR with exponential decay (half-life=120s)",
          "window_s": 120,
          "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"
        },
        "triage": {
          "kind": "correlation",
          "label": "Multiple correlated detector signals",
          "summary": "signals dga_domain, ml_flow_suspicious; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
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
              "label": "dga_domain",
              "age_seconds": 0,
              "effective_score": 0.645,
              "destination": null
            },
            {
              "label": "ml_flow_suspicious",
              "age_seconds": 10,
              "effective_score": 0.944,
              "destination": "8.8.8.8"
            }
          ]
        }
      },
      {
        "timestamp": "2025-09-09T21:21:22.955Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.933,
        "severity": "critical",
        "evidence": {
          "flows_in_series": 16,
          "mean_interval_s": 4.99,
          "iat_cv": 0.0278,
          "cv_gate": 0.25,
          "last_iats_s": [
            5.18,
            4.97,
            4.8,
            5.15,
            4.93
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 16; mean interval (s) 4.99; CV 0.0278; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 16
            },
            {
              "label": "Mean interval (s)",
              "value": 4.99
            },
            {
              "label": "Interval CV",
              "value": 0.0278
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
      },
      {
        "timestamp": "2025-09-09T21:22:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:22:12.932Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 2,
            "nbytes": 174,
            "duration": 0.01,
            "nsyn": 1,
            "bytes_per_pkt": 87,
            "pkts_per_sec": 200,
            "is_udp": 0,
            "dport": 443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=2, bytes=174, duration_s=0.01, SYNs=1, mean_bytes_per_packet=87.0, packets_per_second=200.0, destination_port=443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 2
            },
            {
              "label": "Observed bytes",
              "value": 174
            },
            {
              "label": "Flow duration (s)",
              "value": 0.01
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 87
            },
            {
              "label": "Packets per second",
              "value": 200
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:22:17.990Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.701,
        "severity": "high",
        "evidence": {
          "flows_in_series": 26,
          "mean_interval_s": 5.19,
          "iat_cv": 0.1825,
          "cv_gate": 0.25,
          "last_iats_s": [
            5.22,
            5.03,
            4.84,
            4.96,
            5.07
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 26; mean interval (s) 5.19; CV 0.1825; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 26
            },
            {
              "label": "Mean interval (s)",
              "value": 5.19
            },
            {
              "label": "Interval CV",
              "value": 0.1825
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
      },
      {
        "timestamp": "2025-09-09T21:23:08.019Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.739,
        "severity": "high",
        "evidence": {
          "flows_in_series": 36,
          "mean_interval_s": 5.14,
          "iat_cv": 0.1574,
          "cv_gate": 0.25,
          "last_iats_s": [
            5.16,
            5.08,
            4.74,
            5.12,
            5.03
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 36; mean interval (s) 5.14; CV 0.1574; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 36
            },
            {
              "label": "Mean interval (s)",
              "value": 5.14
            },
            {
              "label": "Interval CV",
              "value": 0.1574
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
      },
      {
        "timestamp": "2025-09-09T21:23:10.000Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.691,
        "severity": "medium",
        "evidence": {
          "qname_label": "5qxs2u4oj7g4eb",
          "label_length": 14,
          "char_entropy_bits": 3.66,
          "vowel_ratio": 0.21,
          "digit_ratio": 0.36,
          "high_entropy_query_streak": 3,
          "dga_queries_seen_from_src": 13,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label 5qxs2u4oj7g4eb; length 14; lexical entropy (bits) 3.66",
          "facts": [
            {
              "label": "DNS label",
              "value": "5qxs2u4oj7g4eb"
            },
            {
              "label": "Label length",
              "value": 14
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 3.66
            },
            {
              "label": "High-entropy streak",
              "value": 3
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:23:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:23:13.137Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 2,
            "nbytes": 174,
            "duration": 0.01,
            "nsyn": 1,
            "bytes_per_pkt": 87,
            "pkts_per_sec": 200,
            "is_udp": 0,
            "dport": 443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=2, bytes=174, duration_s=0.01, SYNs=1, mean_bytes_per_packet=87.0, packets_per_second=200.0, destination_port=443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 2
            },
            {
              "label": "Observed bytes",
              "value": 174
            },
            {
              "label": "Flow duration (s)",
              "value": 0.01
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 87
            },
            {
              "label": "Packets per second",
              "value": 200
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:23:20.233Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tls",
        "threat_class": "tls_known_malware",
        "confidence": 0.99,
        "severity": "critical",
        "evidence": {
          "ja4": "t11i060300_0fe2066a0070_637ee6fc4330",
          "ja3": "50b71d2a05458c98bc2005134ca0bfa8",
          "sni": null,
          "cipher_count": 6,
          "tls_version": "11",
          "transport": "tls",
          "match_source": "threat-intel (known-bad JA4)",
          "why": "ClientHello fingerprint matches a known-malware TLS stack"
        },
        "triage": {
          "kind": "rule",
          "label": "TLS fingerprint on local known list",
          "summary": "JA4 t11i060300_0fe2066a0070_637ee6fc4330; matched local configured list not externally validated",
          "facts": [
            {
              "label": "JA4",
              "value": "t11i060300_0fe2066a0070_637ee6fc4330"
            },
            {
              "label": "Detector-reported match source",
              "value": "threat-intel (known-bad JA4)"
            },
            {
              "label": "Transport",
              "value": "tls"
            }
          ],
          "caveat": "ClientHello is one-way observable; bundled known-JA4 indicator is a simulated profile, not validated external threat intelligence.",
          "next_step": "Compare the observed JA4 and SNI with the host's approved software inventory.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
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
          ]
        }
      },
      {
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
      },
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
      },
      {
        "timestamp": "2025-09-09T21:23:20.243Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9989
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9989",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9989
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:23:54.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.833,
        "severity": "high",
        "evidence": {
          "qname_label": "zqfpqeayynkpfxxnwigm2tsdpghbkphkh6acsenborxd7rwhgl",
          "label_length": 50,
          "char_entropy_bits": 4.54,
          "vowel_ratio": 0.12,
          "digit_ratio": 0.06,
          "high_entropy_query_streak": 3,
          "dga_queries_seen_from_src": 3,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label zqfpqeayynkpfxxnwigm2tsdpghbkphkh6acsenborxd7rwhgl; length 50; lexical entropy (bits) 4.54",
          "facts": [
            {
              "label": "DNS label",
              "value": "zqfpqeayynkpfxxnwigm2tsdpghbkphkh6acsenborxd7rwhgl"
            },
            {
              "label": "Label length",
              "value": 50
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 4.54
            },
            {
              "label": "High-entropy streak",
              "value": 3
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:23:57.873Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.764,
        "severity": "high",
        "evidence": {
          "flows_in_series": 46,
          "mean_interval_s": 5.11,
          "iat_cv": 0.1405,
          "cv_gate": 0.25,
          "last_iats_s": [
            4.99,
            4.83,
            5.04,
            4.92,
            4.98
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 46; mean interval (s) 5.11; CV 0.1405; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 46
            },
            {
              "label": "Mean interval (s)",
              "value": 5.11
            },
            {
              "label": "Interval CV",
              "value": 0.1405
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
      },
      {
        "timestamp": "2025-09-09T21:24:00.000Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.691,
        "severity": "medium",
        "evidence": {
          "qname_label": "kbsepr1b20uc87",
          "label_length": 14,
          "char_entropy_bits": 3.66,
          "vowel_ratio": 0.14,
          "digit_ratio": 0.36,
          "high_entropy_query_streak": 3,
          "dga_queries_seen_from_src": 18,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label kbsepr1b20uc87; length 14; lexical entropy (bits) 3.66",
          "facts": [
            {
              "label": "DNS label",
              "value": "kbsepr1b20uc87"
            },
            {
              "label": "Label length",
              "value": 14
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 3.66
            },
            {
              "label": "High-entropy streak",
              "value": 3
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:05.079Z",
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
      },
      {
        "timestamp": "2025-09-09T21:24:05.079Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9989
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9989",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9989
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
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
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:08.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:0/*",
        "threat_class": "multi_signal_fusion",
        "confidence": 0.893,
        "severity": "high",
        "evidence": {
          "contributing_signals": [
            {
              "threat_class": "dga_domain",
              "at_s": 234,
              "age_s": 14,
              "confidence": 0.833,
              "effective_confidence": 0.768,
              "dst": "*",
              "dport": 0
            },
            {
              "threat_class": "dns_tunneling",
              "at_s": 248,
              "age_s": 0,
              "confidence": 0.537,
              "effective_confidence": 0.537,
              "dst": "*",
              "dport": 0
            }
          ],
          "combination": "noisy-OR with exponential decay (half-life=120s)",
          "window_s": 120,
          "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"
        },
        "triage": {
          "kind": "correlation",
          "label": "Multiple correlated detector signals",
          "summary": "signals dga_domain, dns_tunneling; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
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
              "label": "dga_domain",
              "age_seconds": 14,
              "effective_score": 0.768,
              "destination": null
            },
            {
              "label": "dns_tunneling",
              "age_seconds": 0,
              "effective_score": 0.537,
              "destination": null
            }
          ]
        }
      },
      {
        "timestamp": "2025-09-09T21:24:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:10.134Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/quic",
        "threat_class": "tls_known_malware",
        "confidence": 0.99,
        "severity": "critical",
        "evidence": {
          "ja4": "t11i060300_0fe2066a0070_637ee6fc4330",
          "ja3": "50b71d2a05458c98bc2005134ca0bfa8",
          "sni": null,
          "cipher_count": 6,
          "tls_version": "11",
          "transport": "quic",
          "match_source": "threat-intel (known-bad JA4)",
          "why": "ClientHello fingerprint matches a known-malware TLS stack"
        },
        "triage": {
          "kind": "rule",
          "label": "TLS fingerprint on local known list",
          "summary": "JA4 t11i060300_0fe2066a0070_637ee6fc4330; matched local configured list not externally validated",
          "facts": [
            {
              "label": "JA4",
              "value": "t11i060300_0fe2066a0070_637ee6fc4330"
            },
            {
              "label": "Detector-reported match source",
              "value": "threat-intel (known-bad JA4)"
            },
            {
              "label": "Transport",
              "value": "quic"
            }
          ],
          "caveat": "ClientHello is one-way observable; bundled known-JA4 indicator is a simulated profile, not validated external threat intelligence.",
          "next_step": "Compare the observed JA4 and SNI with the host's approved software inventory.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:10.134Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/udp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.986,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            6,
            3,
            11,
            1,
            0,
            2,
            1,
            166,
            0,
            0
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
                1,
                0,
                2,
                1,
                166,
                0,
                0
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:17.912Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 2,
            "nbytes": 174,
            "duration": 0.01,
            "nsyn": 1,
            "bytes_per_pkt": 87,
            "pkts_per_sec": 200,
            "is_udp": 0,
            "dport": 443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=2, bytes=174, duration_s=0.01, SYNs=1, mean_bytes_per_packet=87.0, packets_per_second=200.0, destination_port=443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 2
            },
            {
              "label": "Observed bytes",
              "value": 174
            },
            {
              "label": "Flow duration (s)",
              "value": 0.01
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 87
            },
            {
              "label": "Packets per second",
              "value": 200
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:19.000Z",
        "src": "10.0.0.13",
        "dst": "203.0.113.20",
        "flow_id": "10.0.0.13:*->203.0.113.20:*/tcp",
        "threat_class": "recon_vertical_scan",
        "confidence": 0.702,
        "severity": "high",
        "evidence": {
          "distinct_dst_port_pairs": 202,
          "distinct_dst_ips": 3,
          "pairs_on_top_dst": 200,
          "window": "250-260s",
          "why": "single source fanned out across many destination ports/hosts in one window"
        },
        "triage": {
          "kind": "rule",
          "label": "Port scan against one destination",
          "summary": "destination/port pairs 202; destinations 3; top-destination pairs 200; window 250-260s",
          "facts": [
            {
              "label": "Destination/port pairs",
              "value": 202
            },
            {
              "label": "Destination IPs",
              "value": 3
            },
            {
              "label": "Pairs on top destination",
              "value": 200
            },
            {
              "label": "Window",
              "value": "250-260s"
            }
          ],
          "caveat": "This is a one-way traffic pattern; legitimate scanners or bursts can produce similar measurements.",
          "next_step": "If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
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
                202,
                3,
                200,
                0.9900990099009901,
                14416
              ]
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
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:19.000Z",
        "src": "10.0.0.13",
        "dst": "*",
        "flow_id": "10.0.0.13:*->*:0/*",
        "threat_class": "multi_signal_fusion",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "contributing_signals": [
            {
              "threat_class": "recon_model_scan",
              "at_s": 259,
              "age_s": 0,
              "confidence": 1,
              "effective_confidence": 0.999,
              "dst": "*",
              "dport": 0
            },
            {
              "threat_class": "recon_vertical_scan",
              "at_s": 259,
              "age_s": 0,
              "confidence": 0.702,
              "effective_confidence": 0.702,
              "dst": "203.0.113.20",
              "dport": 0
            }
          ],
          "combination": "noisy-OR with exponential decay (half-life=120s)",
          "window_s": 120,
          "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"
        },
        "triage": {
          "kind": "correlation",
          "label": "Multiple correlated detector signals",
          "summary": "signals recon_model_scan, recon_vertical_scan; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
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
              "label": "recon_model_scan",
              "age_seconds": 0,
              "effective_score": 0.999,
              "destination": null
            },
            {
              "label": "recon_vertical_scan",
              "age_seconds": 0,
              "effective_score": 0.702,
              "destination": "203.0.113.20"
            }
          ]
        }
      },
      {
        "timestamp": "2025-09-09T21:24:19.930Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/udp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.986,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            6,
            3,
            11,
            1,
            0,
            2,
            1,
            166,
            0,
            0
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
                1,
                0,
                2,
                1,
                166,
                0,
                0
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:30.000Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.691,
        "severity": "medium",
        "evidence": {
          "qname_label": "ey3m0nq8ut60wl",
          "label_length": 14,
          "char_entropy_bits": 3.66,
          "vowel_ratio": 0.14,
          "digit_ratio": 0.36,
          "high_entropy_query_streak": 3,
          "dga_queries_seen_from_src": 21,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label ey3m0nq8ut60wl; length 14; lexical entropy (bits) 3.66",
          "facts": [
            {
              "label": "DNS label",
              "value": "ey3m0nq8ut60wl"
            },
            {
              "label": "Label length",
              "value": 14
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 3.66
            },
            {
              "label": "High-entropy streak",
              "value": 3
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:30.142Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/udp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.986,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            6,
            3,
            11,
            1,
            0,
            2,
            1,
            166,
            0,
            0
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
                1,
                0,
                2,
                1,
                166,
                0,
                0
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:24:43.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:53/udp",
        "threat_class": "dns_tunneling",
        "confidence": 0.625,
        "severity": "medium",
        "evidence": {
          "qtype": 16,
          "qname": "xlrqf7k7o2bwbvb3h5gyl2ikwmheddtqxzrtgsuggmkh43x65t.exfil.xxxxxxxx.com.",
          "query_bytes": 70,
          "max_label_length": 50,
          "cumulative_tunnel_bytes": 700,
          "tunnel_queries_from_src": 10,
          "signals": "qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60",
          "note": "response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable",
          "why": "repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups"
        },
        "triage": {
          "kind": "rule",
          "label": "Repeated bulky or overlong DNS queries",
          "summary": "query bytes 70; qtype 16; queries 10; cumulative query bytes 700; limitation not verified exfil volume",
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
              "value": 10
            },
            {
              "label": "Cumulative query bytes",
              "value": 700
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
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
      },
      {
        "timestamp": "2025-09-09T21:24:50.183Z",
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
      },
      {
        "timestamp": "2025-09-09T21:24:50.183Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9989
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9989",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9989
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:04.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.854,
        "severity": "high",
        "evidence": {
          "qname_label": "2qfsp3nr4t72j6djrz7ykh35xqngutddlwa2q7scjs5woizmts",
          "label_length": 50,
          "char_entropy_bits": 4.67,
          "vowel_ratio": 0.08,
          "digit_ratio": 0.24,
          "high_entropy_query_streak": 13,
          "dga_queries_seen_from_src": 13,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label 2qfsp3nr4t72j6djrz7ykh35xqngutddlwa2q7scjs5woizmts; length 50; lexical entropy (bits) 4.67",
          "facts": [
            {
              "label": "DNS label",
              "value": "2qfsp3nr4t72j6djrz7ykh35xqngutddlwa2q7scjs5woizmts"
            },
            {
              "label": "Label length",
              "value": 50
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 4.67
            },
            {
              "label": "High-entropy streak",
              "value": 13
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:08.226Z",
        "src": "10.0.0.15",
        "dst": "151.101.1.3",
        "flow_id": "10.0.0.15:*->151.101.1.3:443/tls",
        "threat_class": "tls_novel_fingerprint",
        "confidence": 0.6,
        "severity": "medium",
        "evidence": {
          "ja4": "t12d080400_f876287a346c_e09390cf9280",
          "ja3": "949056d163340de1df376c954f73b160",
          "sni": "update.microsoft.com",
          "cipher_count": 8,
          "ext_count": 4,
          "tls_version": "12",
          "transport": "tls",
          "novelty_scope": "host",
          "src_inventory_size": 1,
          "note": "server-side JA3S/cert unavailable (one-way feed)",
          "why": "fingerprint new to this host but known elsewhere -- possible lateral movement or host software change"
        },
        "triage": {
          "kind": "rule",
          "label": "New TLS fingerprint",
          "summary": "JA4 t12d080400_f876287a346c_e09390cf9280; SNI update.microsoft.com; scope host",
          "facts": [
            {
              "label": "JA4",
              "value": "t12d080400_f876287a346c_e09390cf9280"
            },
            {
              "label": "SNI",
              "value": "update.microsoft.com"
            },
            {
              "label": "Novelty scope",
              "value": "host"
            },
            {
              "label": "Transport",
              "value": "tls"
            }
          ],
          "caveat": "Only client-side TLS metadata is visible; novelty or a local known-list match can also reflect legitimate software changes.",
          "next_step": "Compare the observed JA4 and SNI with the host's approved software inventory.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:10.000Z",
        "src": "*",
        "dst": "*",
        "flow_id": "*:*->*:443/tcp",
        "threat_class": "ddos_volumetric_spoofed",
        "confidence": 0.905,
        "severity": "critical",
        "evidence": {
          "window_pkts": 1978,
          "pkt_rate_per_s": 197.8,
          "distinct_src_ips": 1523,
          "src_ip_entropy_bits": 9.29,
          "syn_ratio": 0.771,
          "why": "packet-rate spike with high source-IP entropy => spoofed-source volumetric flood"
        },
        "triage": {
          "kind": "rule",
          "label": "High-volume traffic with many sources",
          "summary": "packets 1978; pkt/s 197.8; source IPs 1523; SYN ratio 0.771",
          "facts": [
            {
              "label": "Window packets",
              "value": 1978
            },
            {
              "label": "Packet rate (per second)",
              "value": 197.8
            },
            {
              "label": "Source IPs",
              "value": 1523
            },
            {
              "label": "Source IP entropy (bits)",
              "value": 9.29
            },
            {
              "label": "SYN ratio",
              "value": 0.771
            }
          ],
          "caveat": "This is a one-way traffic pattern; legitimate scanners or bursts can produce similar measurements.",
          "next_step": "Inspect the packet sample and source distribution for the recorded window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:17.988Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 2,
            "nbytes": 174,
            "duration": 0.01,
            "nsyn": 1,
            "bytes_per_pkt": 87,
            "pkts_per_sec": 200,
            "is_udp": 0,
            "dport": 443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=2, bytes=174, duration_s=0.01, SYNs=1, mean_bytes_per_packet=87.0, packets_per_second=200.0, destination_port=443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 2
            },
            {
              "label": "Observed bytes",
              "value": 174
            },
            {
              "label": "Flow duration (s)",
              "value": 0.01
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 87
            },
            {
              "label": "Packets per second",
              "value": 200
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:19.000Z",
        "src": "10.0.0.11",
        "dst": "45.33.32.156",
        "flow_id": "10.0.0.11:*->45.33.32.156:8443/tcp",
        "threat_class": "data_exfiltration",
        "confidence": 0.95,
        "severity": "critical",
        "evidence": {
          "bytes_to_new_dst": 933800,
          "pair_age_windows": 1,
          "src_baseline_bytes_median": 3349,
          "ratio_vs_baseline": 278.8,
          "novel_destination": true,
          "why": "large sustained upload to a never-before-seen destination, far above the source host's normal window volume"
        },
        "triage": {
          "kind": "rule",
          "label": "Large transfer to a new destination",
          "summary": "bytes to new destination 933800; baseline bytes 3349; ratio 278.8x; age windows 1",
          "facts": [
            {
              "label": "Observed bytes to new destination",
              "value": 933800
            },
            {
              "label": "Source median baseline bytes",
              "value": 3349
            },
            {
              "label": "Ratio vs baseline",
              "value": 278.8
            },
            {
              "label": "Pair age (windows)",
              "value": 1
            }
          ],
          "caveat": "One-way bytes show transfer volume, not authorization or successful exfiltration; benign backups can look similar.",
          "next_step": "Compare the observed destination and transfer volume with this source's prior byte baseline and backup schedule.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:19.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:0/*",
        "threat_class": "confirmed_exfiltration",
        "confidence": 0.995,
        "severity": "critical",
        "evidence": {
          "contributing_signals": [
            {
              "threat_class": "data_exfiltration",
              "at_s": 319,
              "age_s": 0,
              "confidence": 0.95,
              "effective_confidence": 0.95,
              "dst": "45.33.32.156",
              "dport": 0
            },
            {
              "threat_class": "dga_domain",
              "at_s": 304,
              "age_s": 15,
              "confidence": 0.854,
              "effective_confidence": 0.783,
              "dst": "*",
              "dport": 0
            },
            {
              "threat_class": "dns_tunneling",
              "at_s": 283,
              "age_s": 36,
              "confidence": 0.625,
              "effective_confidence": 0.508,
              "dst": "*",
              "dport": 0
            }
          ],
          "combination": "noisy-OR with exponential decay (half-life=120s)",
          "window_s": 120,
          "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"
        },
        "triage": {
          "kind": "correlation",
          "label": "Correlated transfer signals",
          "summary": "signals data_exfiltration, dga_domain, dns_tunneling; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
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
              "label": "data_exfiltration",
              "age_seconds": 0,
              "effective_score": 0.95,
              "destination": "45.33.32.156"
            },
            {
              "label": "dga_domain",
              "age_seconds": 15,
              "effective_score": 0.783,
              "destination": null
            },
            {
              "label": "dns_tunneling",
              "age_seconds": 36,
              "effective_score": 0.508,
              "destination": null
            }
          ]
        }
      },
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
      },
      {
        "timestamp": "2025-09-09T21:25:19.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:0/*",
        "threat_class": "confirmed_exfiltration",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "contributing_signals": [
            {
              "threat_class": "data_exfiltration",
              "at_s": 319,
              "age_s": 0,
              "confidence": 0.95,
              "effective_confidence": 0.95,
              "dst": "45.33.32.156",
              "dport": 0
            },
            {
              "threat_class": "data_exfiltration_model",
              "at_s": 319,
              "age_s": 0,
              "confidence": 0.756,
              "effective_confidence": 0.756,
              "dst": "45.33.32.156",
              "dport": 0
            },
            {
              "threat_class": "dga_domain",
              "at_s": 304,
              "age_s": 15,
              "confidence": 0.854,
              "effective_confidence": 0.783,
              "dst": "*",
              "dport": 0
            },
            {
              "threat_class": "dns_tunneling",
              "at_s": 283,
              "age_s": 36,
              "confidence": 0.625,
              "effective_confidence": 0.508,
              "dst": "*",
              "dport": 0
            }
          ],
          "combination": "noisy-OR with exponential decay (half-life=120s)",
          "window_s": 120,
          "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"
        },
        "triage": {
          "kind": "correlation",
          "label": "Correlated transfer signals",
          "summary": "signals data_exfiltration, data_exfiltration_model, dga_domain, dns_tunneling; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
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
              "label": "data_exfiltration",
              "age_seconds": 0,
              "effective_score": 0.95,
              "destination": "45.33.32.156"
            },
            {
              "label": "data_exfiltration_model",
              "age_seconds": 0,
              "effective_score": 0.756,
              "destination": "45.33.32.156"
            },
            {
              "label": "dga_domain",
              "age_seconds": 15,
              "effective_score": 0.783,
              "destination": null
            },
            {
              "label": "dns_tunneling",
              "age_seconds": 36,
              "effective_score": 0.508,
              "destination": null
            }
          ]
        }
      },
      {
        "timestamp": "2025-09-09T21:25:20.000Z",
        "src": "*",
        "dst": "*",
        "flow_id": "*:*->*:443/tcp",
        "threat_class": "ddos_volumetric_spoofed",
        "confidence": 0.901,
        "severity": "critical",
        "evidence": {
          "window_pkts": 1924,
          "pkt_rate_per_s": 192.4,
          "distinct_src_ips": 1506,
          "src_ip_entropy_bits": 9.28,
          "syn_ratio": 0.783,
          "why": "packet-rate spike with high source-IP entropy => spoofed-source volumetric flood"
        },
        "triage": {
          "kind": "rule",
          "label": "High-volume traffic with many sources",
          "summary": "packets 1924; pkt/s 192.4; source IPs 1506; SYN ratio 0.783",
          "facts": [
            {
              "label": "Window packets",
              "value": 1924
            },
            {
              "label": "Packet rate (per second)",
              "value": 192.4
            },
            {
              "label": "Source IPs",
              "value": 1506
            },
            {
              "label": "Source IP entropy (bits)",
              "value": 9.28
            },
            {
              "label": "SYN ratio",
              "value": 0.783
            }
          ],
          "caveat": "This is a one-way traffic pattern; legitimate scanners or bursts can produce similar measurements.",
          "next_step": "Inspect the packet sample and source distribution for the recorded window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:30.000Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.668,
        "severity": "medium",
        "evidence": {
          "qname_label": "y7zxdfld9cba72",
          "label_length": 14,
          "char_entropy_bits": 3.52,
          "vowel_ratio": 0.07,
          "digit_ratio": 0.29,
          "high_entropy_query_streak": 3,
          "dga_queries_seen_from_src": 26,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label y7zxdfld9cba72; length 14; lexical entropy (bits) 3.52",
          "facts": [
            {
              "label": "DNS label",
              "value": "y7zxdfld9cba72"
            },
            {
              "label": "Label length",
              "value": 14
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 3.52
            },
            {
              "label": "High-entropy streak",
              "value": 3
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:34.738Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.939,
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
            0.020000934600830078,
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
                0.020000934600830078,
                0.45623195266236183
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:34.738Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.994,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9937
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9937",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9937
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:37.860Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.789,
        "severity": "high",
        "evidence": {
          "flows_in_series": 66,
          "mean_interval_s": 5.08,
          "iat_cv": 0.1243,
          "cv_gate": 0.25,
          "last_iats_s": [
            5.02,
            5.03,
            4.95,
            4.92,
            4.98
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 66; mean interval (s) 5.08; CV 0.1243; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 66
            },
            {
              "label": "Mean interval (s)",
              "value": 5.08
            },
            {
              "label": "Interval CV",
              "value": 0.1243
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
      },
      {
        "timestamp": "2025-09-09T21:25:50.500Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.987,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            0,
            0,
            0,
            0,
            0,
            0,
            2,
            174,
            0.009999990463256836,
            0.3793103448275862
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
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                174,
                0.009999990463256836,
                0.3793103448275862
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:25:50.500Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:0/*",
        "threat_class": "multi_signal_fusion",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "contributing_signals": [
            {
              "threat_class": "dga_domain",
              "at_s": 330,
              "age_s": 20.5,
              "confidence": 0.668,
              "effective_confidence": 0.593,
              "dst": "*",
              "dport": 0
            },
            {
              "threat_class": "encrypted_session_malware",
              "at_s": 350.5,
              "age_s": 0,
              "confidence": 0.987,
              "effective_confidence": 0.987,
              "dst": "198.51.100.99",
              "dport": 0
            },
            {
              "threat_class": "ml_flow_suspicious",
              "at_s": 310,
              "age_s": 40.5,
              "confidence": 1,
              "effective_confidence": 0.791,
              "dst": "8.8.8.8",
              "dport": 0
            }
          ],
          "combination": "noisy-OR with exponential decay (half-life=120s)",
          "window_s": 120,
          "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"
        },
        "triage": {
          "kind": "correlation",
          "label": "Multiple correlated detector signals",
          "summary": "signals dga_domain, encrypted_session_malware, ml_flow_suspicious; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
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
              "label": "dga_domain",
              "age_seconds": 20.5,
              "effective_score": 0.593,
              "destination": null
            },
            {
              "label": "encrypted_session_malware",
              "age_seconds": 0,
              "effective_score": 0.987,
              "destination": "198.51.100.99"
            },
            {
              "label": "ml_flow_suspicious",
              "age_seconds": 40.5,
              "effective_score": 0.791,
              "destination": "8.8.8.8"
            }
          ]
        }
      },
      {
        "timestamp": "2025-09-09T21:25:50.500Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9999
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9999",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
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
      },
      {
        "timestamp": "2025-09-09T21:26:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:14.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.797,
        "severity": "high",
        "evidence": {
          "qname_label": "yjiajt442c25tfg2khzclmcjd2ggftgnx6dzokat6e3zjycyfm",
          "label_length": 50,
          "char_entropy_bits": 4.32,
          "vowel_ratio": 0.1,
          "digit_ratio": 0.2,
          "high_entropy_query_streak": 23,
          "dga_queries_seen_from_src": 23,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label yjiajt442c25tfg2khzclmcjd2ggftgnx6dzokat6e3zjycyfm; length 50; lexical entropy (bits) 4.32",
          "facts": [
            {
              "label": "DNS label",
              "value": "yjiajt442c25tfg2khzclmcjd2ggftgnx6dzokat6e3zjycyfm"
            },
            {
              "label": "Label length",
              "value": 50
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 4.32
            },
            {
              "label": "High-entropy streak",
              "value": 23
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:19.770Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.948,
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
            0.019999027252197266,
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
                0.019999027252197266,
                0.45623195266236183
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:19.770Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9989
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9989",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9989
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:19.770Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 3,
            "nbytes": 394,
            "duration": 0.02,
            "nsyn": 1,
            "bytes_per_pkt": 131.33,
            "pkts_per_sec": 150.01,
            "is_udp": 0,
            "dport": 8443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=3, bytes=394, duration_s=0.02, SYNs=1, mean_bytes_per_packet=131.33, packets_per_second=150.01, destination_port=8443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 3
            },
            {
              "label": "Observed bytes",
              "value": 394
            },
            {
              "label": "Flow duration (s)",
              "value": 0.02
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 131.33
            },
            {
              "label": "Packets per second",
              "value": 150.01
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 8443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:20.125Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.987,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            0,
            0,
            0,
            0,
            0,
            0,
            2,
            174,
            0.009999990463256836,
            0.3793103448275862
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
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                174,
                0.009999990463256836,
                0.3793103448275862
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:20.125Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9999
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9999",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:27.908Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.789,
        "severity": "high",
        "evidence": {
          "flows_in_series": 76,
          "mean_interval_s": 5.08,
          "iat_cv": 0.1242,
          "cv_gate": 0.25,
          "last_iats_s": [
            4.95,
            5.19,
            4.74,
            5.16,
            4.89
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 76; mean interval (s) 5.08; CV 0.1242; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 76
            },
            {
              "label": "Mean interval (s)",
              "value": 5.08
            },
            {
              "label": "Interval CV",
              "value": 0.1242
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
      },
      {
        "timestamp": "2025-09-09T21:26:49.000Z",
        "src": "10.0.0.13",
        "dst": "203.0.113.20",
        "flow_id": "10.0.0.13:*->203.0.113.20:*/tcp",
        "threat_class": "recon_vertical_scan",
        "confidence": 0.835,
        "severity": "high",
        "evidence": {
          "distinct_dst_port_pairs": 335,
          "distinct_dst_ips": 2,
          "pairs_on_top_dst": 334,
          "window": "400-410s",
          "why": "single source fanned out across many destination ports/hosts in one window"
        },
        "triage": {
          "kind": "rule",
          "label": "Port scan against one destination",
          "summary": "destination/port pairs 335; destinations 2; top-destination pairs 334; window 400-410s",
          "facts": [
            {
              "label": "Destination/port pairs",
              "value": 335
            },
            {
              "label": "Destination IPs",
              "value": 2
            },
            {
              "label": "Pairs on top destination",
              "value": 334
            },
            {
              "label": "Window",
              "value": "400-410s"
            }
          ],
          "caveat": "This is a one-way traffic pattern; legitimate scanners or bursts can produce similar measurements.",
          "next_step": "If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:49.000Z",
        "src": "10.0.0.13",
        "dst": "*",
        "flow_id": "10.0.0.13:*->*:0/*",
        "threat_class": "recon_model_scan",
        "confidence": 0.808,
        "severity": "high",
        "evidence": {
          "model": "scan_rf",
          "features": [
            335,
            2,
            334,
            0.9970149253731343,
            18106
          ],
          "iforest_corroboration": {
            "model": "scan_iforest",
            "anomaly_score": -0.2759091284631018,
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
                335,
                2,
                334,
                0.9970149253731343,
                18106
              ]
            },
            {
              "label": "IsolationForest anomaly score",
              "value": -0.2759091284631018
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
      },
      {
        "timestamp": "2025-09-09T21:26:50.000Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.691,
        "severity": "medium",
        "evidence": {
          "qname_label": "jotv7h10b8vk9q",
          "label_length": 14,
          "char_entropy_bits": 3.66,
          "vowel_ratio": 0.07,
          "digit_ratio": 0.36,
          "high_entropy_query_streak": 3,
          "dga_queries_seen_from_src": 33,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label jotv7h10b8vk9q; length 14; lexical entropy (bits) 3.66",
          "facts": [
            {
              "label": "DNS label",
              "value": "jotv7h10b8vk9q"
            },
            {
              "label": "Label length",
              "value": 14
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 3.66
            },
            {
              "label": "High-entropy streak",
              "value": 3
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:50.055Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.987,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            0,
            0,
            0,
            0,
            0,
            0,
            2,
            174,
            0.009999990463256836,
            0.3793103448275862
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
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                174,
                0.009999990463256836,
                0.3793103448275862
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:50.055Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9999
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9999",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:26:59.000Z",
        "src": "10.0.0.13",
        "dst": "203.0.113.20",
        "flow_id": "10.0.0.13:*->203.0.113.20:*/tcp",
        "threat_class": "recon_vertical_scan",
        "confidence": 0.667,
        "severity": "medium",
        "evidence": {
          "distinct_dst_port_pairs": 167,
          "distinct_dst_ips": 2,
          "pairs_on_top_dst": 166,
          "window": "410-420s",
          "why": "single source fanned out across many destination ports/hosts in one window"
        },
        "triage": {
          "kind": "rule",
          "label": "Port scan against one destination",
          "summary": "destination/port pairs 167; destinations 2; top-destination pairs 166; window 410-420s",
          "facts": [
            {
              "label": "Destination/port pairs",
              "value": 167
            },
            {
              "label": "Destination IPs",
              "value": 2
            },
            {
              "label": "Pairs on top destination",
              "value": 166
            },
            {
              "label": "Window",
              "value": "410-420s"
            }
          ],
          "caveat": "This is a one-way traffic pattern; legitimate scanners or bursts can produce similar measurements.",
          "next_step": "If a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.",
          "score_label": "Rule score",
          "related": []
        }
      },
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
      },
      {
        "timestamp": "2025-09-09T21:27:05.084Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.816,
        "severity": "high",
        "evidence": {
          "flows_in_series": 6,
          "mean_interval_s": 44.97,
          "iat_cv": 0.0058,
          "cv_gate": 0.15,
          "last_iats_s": [
            44.84,
            45.1,
            44.55,
            45.03,
            45.33
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 6; mean interval (s) 44.97; CV 0.0058; gate 0.15",
          "facts": [
            {
              "label": "Flows in series",
              "value": 6
            },
            {
              "label": "Mean interval (s)",
              "value": 44.97
            },
            {
              "label": "Interval CV",
              "value": 0.0058
            },
            {
              "label": "CV gate",
              "value": 0.15
            }
          ],
          "caveat": "Periodicity is one-way observable but cloud telemetry and scheduled jobs can produce the same pattern.",
          "next_step": "Compare the recorded flow times with the source's expected scheduled connections.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:05.104Z",
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
      },
      {
        "timestamp": "2025-09-09T21:27:05.104Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9989
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9989",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9989
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:18.003Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.935,
        "severity": "critical",
        "evidence": {
          "flows_in_series": 86,
          "mean_interval_s": 5,
          "iat_cv": 0.0263,
          "cv_gate": 0.25,
          "last_iats_s": [
            4.89,
            5.03,
            5.18,
            4.78,
            5.15
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 86; mean interval (s) 5.0; CV 0.0263; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 86
            },
            {
              "label": "Mean interval (s)",
              "value": 5
            },
            {
              "label": "Interval CV",
              "value": 0.0263
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
      },
      {
        "timestamp": "2025-09-09T21:27:20.260Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.987,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            0,
            0,
            0,
            0,
            0,
            0,
            2,
            174,
            0.009999990463256836,
            0.3793103448275862
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
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                174,
                0.009999990463256836,
                0.3793103448275862
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:20.260Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9999
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9999",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:22.893Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 2,
            "nbytes": 174,
            "duration": 0.01,
            "nsyn": 1,
            "bytes_per_pkt": 87,
            "pkts_per_sec": 200,
            "is_udp": 0,
            "dport": 443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=2, bytes=174, duration_s=0.01, SYNs=1, mean_bytes_per_packet=87.0, packets_per_second=200.0, destination_port=443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 2
            },
            {
              "label": "Observed bytes",
              "value": 174
            },
            {
              "label": "Flow duration (s)",
              "value": 0.01
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 87
            },
            {
              "label": "Packets per second",
              "value": 200
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:24.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.853,
        "severity": "high",
        "evidence": {
          "qname_label": "dxlds3dkbcqndbwk72j76pgmdganl3vowtpgrk7zytfz6524ne",
          "label_length": 50,
          "char_entropy_bits": 4.67,
          "vowel_ratio": 0.06,
          "digit_ratio": 0.22,
          "high_entropy_query_streak": 33,
          "dga_queries_seen_from_src": 33,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label dxlds3dkbcqndbwk72j76pgmdganl3vowtpgrk7zytfz6524ne; length 50; lexical entropy (bits) 4.67",
          "facts": [
            {
              "label": "DNS label",
              "value": "dxlds3dkbcqndbwk72j76pgmdganl3vowtpgrk7zytfz6524ne"
            },
            {
              "label": "Label length",
              "value": 50
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 4.67
            },
            {
              "label": "High-entropy streak",
              "value": 33
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:30.000Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.668,
        "severity": "medium",
        "evidence": {
          "qname_label": "ulthycx8ae0jxy",
          "label_length": 14,
          "char_entropy_bits": 3.52,
          "vowel_ratio": 0.21,
          "digit_ratio": 0.14,
          "high_entropy_query_streak": 3,
          "dga_queries_seen_from_src": 37,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label ulthycx8ae0jxy; length 14; lexical entropy (bits) 3.52",
          "facts": [
            {
              "label": "DNS label",
              "value": "ulthycx8ae0jxy"
            },
            {
              "label": "Label length",
              "value": 14
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 3.52
            },
            {
              "label": "High-entropy streak",
              "value": 3
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:49.955Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.939,
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
            0.020000934600830078,
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
                0.020000934600830078,
                0.45623195266236183
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:49.955Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.992,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.992
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.992",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.992
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:50.077Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.987,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            0,
            0,
            0,
            0,
            0,
            0,
            2,
            174,
            0.009999990463256836,
            0.3793103448275862
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
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                174,
                0.009999990463256836,
                0.3793103448275862
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:27:50.077Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9999
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9999",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:08.015Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.936,
        "severity": "critical",
        "evidence": {
          "flows_in_series": 96,
          "mean_interval_s": 5,
          "iat_cv": 0.0261,
          "cv_gate": 0.25,
          "last_iats_s": [
            4.87,
            4.91,
            5.09,
            4.89,
            5.14
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 96; mean interval (s) 5.0; CV 0.0261; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 96
            },
            {
              "label": "Mean interval (s)",
              "value": 5
            },
            {
              "label": "Interval CV",
              "value": 0.0261
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
      },
      {
        "timestamp": "2025-09-09T21:28:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:13.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:53/udp",
        "threat_class": "dns_tunneling",
        "confidence": 0.97,
        "severity": "critical",
        "evidence": {
          "qtype": 16,
          "qname": "t5wswrjqsw3ks7zbdetf3y7h54bdpnxhtyrmnh7udsktmaausz.exfil.xxxxxxxx.com.",
          "query_bytes": 70,
          "max_label_length": 50,
          "cumulative_tunnel_bytes": 2800,
          "tunnel_queries_from_src": 40,
          "signals": "qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60",
          "note": "response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable",
          "why": "repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups"
        },
        "triage": {
          "kind": "rule",
          "label": "Repeated bulky or overlong DNS queries",
          "summary": "query bytes 70; qtype 16; queries 40; cumulative query bytes 2800; limitation not verified exfil volume",
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
              "value": 40
            },
            {
              "label": "Cumulative query bytes",
              "value": 2800
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:19.861Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.815,
        "severity": "high",
        "evidence": {
          "flows_in_series": 6,
          "mean_interval_s": 29.87,
          "iat_cv": 0.0064,
          "cv_gate": 0.15,
          "last_iats_s": [
            29.62,
            29.93,
            30.2,
            29.82,
            29.79
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 6; mean interval (s) 29.87; CV 0.0064; gate 0.15",
          "facts": [
            {
              "label": "Flows in series",
              "value": 6
            },
            {
              "label": "Mean interval (s)",
              "value": 29.87
            },
            {
              "label": "Interval CV",
              "value": 0.0064
            },
            {
              "label": "CV gate",
              "value": 0.15
            }
          ],
          "caveat": "Periodicity is one-way observable but cloud telemetry and scheduled jobs can produce the same pattern.",
          "next_step": "Compare the recorded flow times with the source's expected scheduled connections.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:19.861Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:0/*",
        "threat_class": "botnet_c2_with_dga",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "contributing_signals": [
            {
              "threat_class": "c2_beaconing",
              "at_s": 499.9,
              "age_s": 0,
              "confidence": 0.815,
              "effective_confidence": 0.815,
              "dst": "198.51.100.99",
              "dport": 0
            },
            {
              "threat_class": "dga_domain",
              "at_s": 500,
              "age_s": 0,
              "confidence": 0.691,
              "effective_confidence": 0.691,
              "dst": "*",
              "dport": 0
            },
            {
              "threat_class": "encrypted_session_malware",
              "at_s": 470.1,
              "age_s": 29.8,
              "confidence": 0.987,
              "effective_confidence": 0.831,
              "dst": "198.51.100.99",
              "dport": 0
            },
            {
              "threat_class": "ml_flow_suspicious",
              "at_s": 490,
              "age_s": 9.9,
              "confidence": 1,
              "effective_confidence": 0.945,
              "dst": "8.8.8.8",
              "dport": 0
            }
          ],
          "combination": "noisy-OR with exponential decay (half-life=120s)",
          "window_s": 120,
          "why": "multiple independent detectors firing on one source -- jointly far more indicative than any single signal"
        },
        "triage": {
          "kind": "correlation",
          "label": "Correlated periodicity and DNS signals",
          "summary": "signals c2_beaconing, dga_domain, encrypted_session_malware, ml_flow_suspicious; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation",
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
              "age_seconds": 0,
              "effective_score": 0.815,
              "destination": "198.51.100.99"
            },
            {
              "label": "dga_domain",
              "age_seconds": 0,
              "effective_score": 0.691,
              "destination": null
            },
            {
              "label": "encrypted_session_malware",
              "age_seconds": 29.8,
              "effective_score": 0.831,
              "destination": "198.51.100.99"
            },
            {
              "label": "ml_flow_suspicious",
              "age_seconds": 9.9,
              "effective_score": 0.945,
              "destination": "8.8.8.8"
            }
          ]
        }
      },
      {
        "timestamp": "2025-09-09T21:28:19.871Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.987,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            0,
            0,
            0,
            0,
            0,
            0,
            2,
            174,
            0.009999990463256836,
            0.3793103448275862
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
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                174,
                0.009999990463256836,
                0.3793103448275862
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:19.871Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9999
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9999",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:20.000Z",
        "src": "10.0.0.9",
        "dst": "*",
        "flow_id": "10.0.0.9:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.691,
        "severity": "medium",
        "evidence": {
          "qname_label": "90472uqln6bgua",
          "label_length": 14,
          "char_entropy_bits": 3.66,
          "vowel_ratio": 0.21,
          "digit_ratio": 0.43,
          "high_entropy_query_streak": 3,
          "dga_queries_seen_from_src": 41,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label 90472uqln6bgua; length 14; lexical entropy (bits) 3.66",
          "facts": [
            {
              "label": "DNS label",
              "value": "90472uqln6bgua"
            },
            {
              "label": "Label length",
              "value": 14
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 3.66
            },
            {
              "label": "High-entropy streak",
              "value": 3
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:22.898Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 2,
            "nbytes": 174,
            "duration": 0.01,
            "nsyn": 1,
            "bytes_per_pkt": 87,
            "pkts_per_sec": 200,
            "is_udp": 0,
            "dport": 443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=2, bytes=174, duration_s=0.01, SYNs=1, mean_bytes_per_packet=87.0, packets_per_second=200.0, destination_port=443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 2
            },
            {
              "label": "Observed bytes",
              "value": 174
            },
            {
              "label": "Flow duration (s)",
              "value": 0.01
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 87
            },
            {
              "label": "Packets per second",
              "value": 200
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:34.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.839,
        "severity": "high",
        "evidence": {
          "qname_label": "bqhyphlsmybr7uliqjdryq4ly6bvnjlukeg4d6ewoytx7vt2co",
          "label_length": 50,
          "char_entropy_bits": 4.58,
          "vowel_ratio": 0.14,
          "digit_ratio": 0.14,
          "high_entropy_query_streak": 43,
          "dga_queries_seen_from_src": 43,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label bqhyphlsmybr7uliqjdryq4ly6bvnjlukeg4d6ewoytx7vt2co; length 50; lexical entropy (bits) 4.58",
          "facts": [
            {
              "label": "DNS label",
              "value": "bqhyphlsmybr7uliqjdryq4ly6bvnjlukeg4d6ewoytx7vt2co"
            },
            {
              "label": "Label length",
              "value": 50
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 4.58
            },
            {
              "label": "High-entropy streak",
              "value": 43
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:35.194Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tls",
        "threat_class": "tls_known_malware",
        "confidence": 0.99,
        "severity": "critical",
        "evidence": {
          "ja4": "t11i060300_0fe2066a0070_637ee6fc4330",
          "ja3": "50b71d2a05458c98bc2005134ca0bfa8",
          "sni": null,
          "cipher_count": 6,
          "tls_version": "11",
          "transport": "tls",
          "match_source": "threat-intel (known-bad JA4)",
          "why": "ClientHello fingerprint matches a known-malware TLS stack"
        },
        "triage": {
          "kind": "rule",
          "label": "TLS fingerprint on local known list",
          "summary": "JA4 t11i060300_0fe2066a0070_637ee6fc4330; matched local configured list not externally validated",
          "facts": [
            {
              "label": "JA4",
              "value": "t11i060300_0fe2066a0070_637ee6fc4330"
            },
            {
              "label": "Detector-reported match source",
              "value": "threat-intel (known-bad JA4)"
            },
            {
              "label": "Transport",
              "value": "tls"
            }
          ],
          "caveat": "ClientHello is one-way observable; bundled known-JA4 indicator is a simulated profile, not validated external threat intelligence.",
          "next_step": "Compare the observed JA4 and SNI with the host's approved software inventory.",
          "score_label": "Rule score",
          "related": []
        }
      },
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
      },
      {
        "timestamp": "2025-09-09T21:28:35.204Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:8443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.999,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9989
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9989",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9989
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:49.569Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.987,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            0,
            0,
            0,
            0,
            0,
            0,
            2,
            174,
            0.009999990463256836,
            0.3793103448275862
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
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                174,
                0.009999990463256836,
                0.3793103448275862
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:49.569Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9999
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9999",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:28:58.131Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.935,
        "severity": "critical",
        "evidence": {
          "flows_in_series": 106,
          "mean_interval_s": 5,
          "iat_cv": 0.0267,
          "cv_gate": 0.25,
          "last_iats_s": [
            5.28,
            4.87,
            5.02,
            5.06,
            5.03
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 106; mean interval (s) 5.0; CV 0.0267; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 106
            },
            {
              "label": "Mean interval (s)",
              "value": 5
            },
            {
              "label": "Interval CV",
              "value": 0.0267
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
      },
      {
        "timestamp": "2025-09-09T21:29:10.000Z",
        "src": "10.0.0.9",
        "dst": "8.8.8.8",
        "flow_id": "10.0.0.9:*->8.8.8.8:53/udp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9998,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 1,
            "nbytes": 78,
            "duration": 0,
            "nsyn": 0,
            "bytes_per_pkt": 78,
            "pkts_per_sec": 1000,
            "is_udp": 1,
            "dport": 53,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=1, bytes=78, duration_s=0.0, SYNs=0, mean_bytes_per_packet=78.0, packets_per_second=1000.0, destination_port=53",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 1
            },
            {
              "label": "Observed bytes",
              "value": 78
            },
            {
              "label": "Flow duration (s)",
              "value": 0
            },
            {
              "label": "Observed SYNs",
              "value": 0
            },
            {
              "label": "Mean bytes per packet",
              "value": 78
            },
            {
              "label": "Packets per second",
              "value": 1000
            },
            {
              "label": "Raw feature is_udp",
              "value": 1
            },
            {
              "label": "Destination port",
              "value": 53
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9998
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:29:20.450Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 0.987,
        "severity": "critical",
        "evidence": {
          "model": "xgboost",
          "metadata_features": [
            0,
            0,
            0,
            0,
            0,
            0,
            2,
            174,
            0.009999990463256836,
            0.3793103448275862
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
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                174,
                0.009999990463256836,
                0.3793103448275862
              ]
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:29:20.450Z",
        "src": "10.0.0.9",
        "dst": "198.51.100.99",
        "flow_id": "10.0.0.9:*->198.51.100.99:443/tcp",
        "threat_class": "encrypted_session_malware",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "model": "1d-cnn",
          "sequence_score": 0.9999
        },
        "triage": {
          "kind": "model",
          "label": "Encrypted-session model match",
          "summary": "model 1d-cnn; uncalibrated model score 0.9999",
          "facts": [
            {
              "label": "Model",
              "value": "1d-cnn"
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:29:23.061Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "ml_flow_suspicious",
        "confidence": 1,
        "severity": "critical",
        "evidence": {
          "malicious_probability": 0.9999,
          "model": "lightgbm (temporal split)",
          "flow_features": {
            "npkt": 2,
            "nbytes": 174,
            "duration": 0.01,
            "nsyn": 1,
            "bytes_per_pkt": 87,
            "pkts_per_sec": 200,
            "is_udp": 0,
            "dport": 443,
            "sport_priv": 0,
            "dst_internal": 0
          },
          "why": "supervised model flags this flow's feature vector as highly likely malicious"
        },
        "triage": {
          "kind": "model",
          "label": "Model-flagged flow pattern",
          "summary": "observed flow packets=2, bytes=174, duration_s=0.01, SYNs=1, mean_bytes_per_packet=87.0, packets_per_second=200.0, destination_port=443",
          "facts": [
            {
              "label": "Model",
              "value": "lightgbm (temporal split)"
            },
            {
              "label": "Observed packets",
              "value": 2
            },
            {
              "label": "Observed bytes",
              "value": 174
            },
            {
              "label": "Flow duration (s)",
              "value": 0.01
            },
            {
              "label": "Observed SYNs",
              "value": 1
            },
            {
              "label": "Mean bytes per packet",
              "value": 87
            },
            {
              "label": "Packets per second",
              "value": 200
            },
            {
              "label": "Raw feature is_udp",
              "value": 0
            },
            {
              "label": "Destination port",
              "value": 443
            },
            {
              "label": "Raw feature sport_priv",
              "value": 0
            },
            {
              "label": "Raw feature dst_internal",
              "value": 0
            },
            {
              "label": "Model score (uncalibrated)",
              "value": 0.9999
            }
          ],
          "caveat": "A model score is not proof of malicious activity; the flow model can flag benign traffic shapes absent from training.",
          "next_step": "Review the raw recorded model features alongside the source's deterministic alerts.",
          "score_label": "Model score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:29:44.000Z",
        "src": "10.0.0.11",
        "dst": "*",
        "flow_id": "10.0.0.11:*->*:53/udp",
        "threat_class": "dga_domain",
        "confidence": 0.817,
        "severity": "high",
        "evidence": {
          "qname_label": "6fsxab54kbuja7dh67oqmtvezwomvfumt5k5i6v74vf4z4l6a3",
          "label_length": 50,
          "char_entropy_bits": 4.45,
          "vowel_ratio": 0.18,
          "digit_ratio": 0.3,
          "high_entropy_query_streak": 53,
          "dga_queries_seen_from_src": 53,
          "note": "response side not observable (one-way); NXDOMAIN correlation unavailable",
          "why": "streak of labels with high entropy + non-lexical vowel/digit profile => algorithmically generated domains",
          "dga_cnn_prob": 1,
          "detector_tier": "tier1_lexical+cnn_confirmed"
        },
        "triage": {
          "kind": "rule",
          "label": "Suspicious DNS label pattern",
          "summary": "label 6fsxab54kbuja7dh67oqmtvezwomvfumt5k5i6v74vf4z4l6a3; length 50; lexical entropy (bits) 4.45",
          "facts": [
            {
              "label": "DNS label",
              "value": "6fsxab54kbuja7dh67oqmtvezwomvfumt5k5i6v74vf4z4l6a3"
            },
            {
              "label": "Label length",
              "value": 50
            },
            {
              "label": "Lexical entropy (bits)",
              "value": 4.45
            },
            {
              "label": "High-entropy streak",
              "value": 53
            }
          ],
          "caveat": "DNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use.",
          "next_step": "Review the captured DNS query names and qtypes for this source and time window.",
          "score_label": "Rule score",
          "related": []
        }
      },
      {
        "timestamp": "2025-09-09T21:29:48.134Z",
        "src": "10.0.0.7",
        "dst": "198.51.100.23",
        "flow_id": "10.0.0.7:*->198.51.100.23:443/tcp",
        "threat_class": "c2_beaconing",
        "confidence": 0.935,
        "severity": "critical",
        "evidence": {
          "flows_in_series": 116,
          "mean_interval_s": 5,
          "iat_cv": 0.0268,
          "cv_gate": 0.25,
          "last_iats_s": [
            4.91,
            5.07,
            4.89,
            4.97,
            5.25
          ],
          "why": "flow series with near-constant inter-arrival time => periodic C2 beacon"
        },
        "triage": {
          "kind": "rule",
          "label": "Periodic flow pattern",
          "summary": "flows 116; mean interval (s) 5.0; CV 0.0268; gate 0.25",
          "facts": [
            {
              "label": "Flows in series",
              "value": 116
            },
            {
              "label": "Mean interval (s)",
              "value": 5
            },
            {
              "label": "Interval CV",
              "value": 0.0268
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
    ],
    "matched": 114,
    "stats": {
      "total": 114,
      "critical": 80,
      "high": 22,
      "medium": 12,
      "low": 0,
      "classes": [
        "botnet_c2_with_dga",
        "c2_beaconing",
        "confirmed_c2_implant",
        "confirmed_exfiltration",
        "data_exfiltration",
        "data_exfiltration_model",
        "ddos_volumetric_spoofed",
        "dga_domain",
        "dns_tunneling",
        "encrypted_session_malware",
        "ml_flow_suspicious",
        "multi_signal_fusion",
        "recon_model_scan",
        "recon_vertical_scan",
        "tls_known_malware",
        "tls_novel_fingerprint"
      ],
      "suppressed": 20,
      "by_class": {
        "encrypted_session_malware": 37,
        "ml_flow_suspicious": 20,
        "c2_beaconing": 14,
        "dga_domain": 14,
        "multi_signal_fusion": 6,
        "dns_tunneling": 4,
        "tls_known_malware": 3,
        "recon_vertical_scan": 3,
        "recon_model_scan": 3,
        "confirmed_c2_implant": 2,
        "ddos_volumetric_spoofed": 2,
        "confirmed_exfiltration": 2,
        "tls_novel_fingerprint": 1,
        "data_exfiltration": 1,
        "data_exfiltration_model": 1,
        "botnet_c2_with_dga": 1
      },
      "by_severity": {
        "critical": 80,
        "high": 22,
        "medium": 12,
        "low": 0
      },
      "hosts": 5,
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
      ],
      "first_alert": "2025-09-09T21:20:08.143000+00:00",
      "last_alert": "2025-09-09T21:29:48.134000+00:00",
      "span_seconds": 580,
      "sensor": {
        "suppressed": 20,
        "parser": "live",
        "pkt_per_s": 209,
        "alerts": 114,
        "mode": "live",
        "health": {
          "status": "completed",
          "mode": "pcap_stream",
          "interface": null,
          "path": "/tmp/nix-shell.l9Xrtl/diode-product-f7vi045l/feed.pcap",
          "started_at": "2026-09-30T13:39:23.899604Z",
          "updated_at": "2026-09-30T13:40:32.162171Z",
          "heartbeat_at": "2026-09-30T13:40:32.162171Z",
          "last_packet_at": "2026-09-30T13:40:32.019019Z",
          "counts": {
            "seen": 14049,
            "analyzed": 14049,
            "sampled_out": 0,
            "malformed": 0,
            "kernel_drops": null
          },
          "error": null,
          "heartbeat_age_seconds": 27.4
        }
      },
      "synthetic_demo": true,
      "signals": {
        "raw_records": 114,
        "rule_records": 42,
        "model_records": 61,
        "correlation_records": 11,
        "unknown_records": 0,
        "critical_rule_records": 12,
        "authorised_records": 0,
        "source_count": 5
      }
    },
    "timeline": {
      "labels": [
        "21:20:08",
        "21:20:38",
        "21:21:08",
        "21:21:38",
        "21:22:08",
        "21:22:38",
        "21:23:08",
        "21:23:38",
        "21:24:08",
        "21:24:38",
        "21:25:08",
        "21:25:38",
        "21:26:08",
        "21:26:38",
        "21:27:08",
        "21:27:38",
        "21:28:08",
        "21:28:38",
        "21:29:08",
        "21:29:38"
      ],
      "series": {
        "critical": [
          6,
          0,
          4,
          0,
          2,
          0,
          7,
          2,
          8,
          2,
          9,
          3,
          6,
          4,
          5,
          5,
          9,
          3,
          4,
          1
        ],
        "high": [
          1,
          0,
          0,
          0,
          1,
          1,
          0,
          3,
          1,
          2,
          2,
          1,
          2,
          4,
          1,
          0,
          2,
          0,
          0,
          1
        ],
        "medium": [
          0,
          0,
          1,
          0,
          0,
          0,
          1,
          2,
          1,
          1,
          2,
          0,
          0,
          2,
          1,
          0,
          1,
          0,
          0,
          0
        ],
        "low": [
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0,
          0
        ]
      },
      "bucket_seconds": 30,
      "count": 114
    },
    "sources": [
      {
        "src": "10.0.0.7",
        "n": 51,
        "classes": {
          "encrypted_session_malware": 21,
          "ml_flow_suspicious": 10,
          "multi_signal_fusion": 2,
          "c2_beaconing": 13,
          "tls_known_malware": 3,
          "confirmed_c2_implant": 2
        },
        "worst": "critical",
        "confidence": 1,
        "dominant": "encrypted_session_malware",
        "dominant_count": 21,
        "signals": {
          "raw_records": 51,
          "rule_records": 16,
          "model_records": 31,
          "correlation_records": 4,
          "unknown_records": 0,
          "critical_rule_records": 8,
          "authorised_records": 0,
          "source_count": 1
        }
      },
      {
        "src": "10.0.0.9",
        "n": 38,
        "classes": {
          "ml_flow_suspicious": 10,
          "dga_domain": 8,
          "multi_signal_fusion": 2,
          "encrypted_session_malware": 16,
          "c2_beaconing": 1,
          "botnet_c2_with_dga": 1
        },
        "worst": "critical",
        "confidence": 1,
        "dominant": "encrypted_session_malware",
        "dominant_count": 16,
        "signals": {
          "raw_records": 38,
          "rule_records": 9,
          "model_records": 26,
          "correlation_records": 3,
          "unknown_records": 0,
          "critical_rule_records": 0,
          "authorised_records": 0,
          "source_count": 1
        }
      },
      {
        "src": "10.0.0.11",
        "n": 15,
        "classes": {
          "dga_domain": 6,
          "dns_tunneling": 4,
          "multi_signal_fusion": 1,
          "data_exfiltration": 1,
          "confirmed_exfiltration": 2,
          "data_exfiltration_model": 1
        },
        "worst": "critical",
        "confidence": 0.999,
        "dominant": "dga_domain",
        "dominant_count": 6,
        "signals": {
          "raw_records": 15,
          "rule_records": 11,
          "model_records": 1,
          "correlation_records": 3,
          "unknown_records": 0,
          "critical_rule_records": 2,
          "authorised_records": 0,
          "source_count": 1
        }
      },
      {
        "src": "10.0.0.13",
        "n": 7,
        "classes": {
          "recon_vertical_scan": 3,
          "recon_model_scan": 3,
          "multi_signal_fusion": 1
        },
        "worst": "critical",
        "confidence": 1,
        "dominant": "recon_vertical_scan",
        "dominant_count": 3,
        "signals": {
          "raw_records": 7,
          "rule_records": 3,
          "model_records": 3,
          "correlation_records": 1,
          "unknown_records": 0,
          "critical_rule_records": 0,
          "authorised_records": 0,
          "source_count": 1
        }
      },
      {
        "src": "*",
        "n": 2,
        "classes": {
          "ddos_volumetric_spoofed": 2
        },
        "worst": "critical",
        "confidence": 0.905,
        "dominant": "ddos_volumetric_spoofed",
        "dominant_count": 2,
        "signals": {
          "raw_records": 2,
          "rule_records": 2,
          "model_records": 0,
          "correlation_records": 0,
          "unknown_records": 0,
          "critical_rule_records": 2,
          "authorised_records": 0,
          "source_count": 0
        }
      },
      {
        "src": "10.0.0.15",
        "n": 1,
        "classes": {
          "tls_novel_fingerprint": 1
        },
        "worst": "medium",
        "confidence": 0.6,
        "dominant": "tls_novel_fingerprint",
        "dominant_count": 1,
        "signals": {
          "raw_records": 1,
          "rule_records": 1,
          "model_records": 0,
          "correlation_records": 0,
          "unknown_records": 0,
          "critical_rule_records": 0,
          "authorised_records": 0,
          "source_count": 1
        }
      }
    ],
    "generated_at": "2026-09-30T13:40:59+00:00"
  }
} as const;
