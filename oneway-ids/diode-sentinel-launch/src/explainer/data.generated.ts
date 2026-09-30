export const explainer = {
  "fps": 30,
  "width": 1920,
  "height": 1080,
  "duration": 13608,
  "scenes": [
    {
      "id": "intro",
      "label": "DIODE SENTINEL",
      "title": "Small observations. A larger picture.",
      "minSeconds": 18,
      "graphic": "receive",
      "clip": null,
      "text": "A packet is a small observation. Where did it come from? Where is it going? How big is it, and when did it arrive? Put those observations together, and a pattern begins to appear. This is Diode Sentinel.",
      "briefSections": [
        "0",
        "9",
        "10"
      ],
      "start": 0,
      "end": 740,
      "graphicReveal": 38,
      "uiReveal": 326,
      "clipAvailable": false
    },
    {
      "id": "receive",
      "label": "RECEIVE-SIDE MONITORING",
      "title": "Watch the observations arrive.",
      "minSeconds": 22,
      "graphic": "receive",
      "clip": "overview",
      "text": "The sensor watches the receive side of a hardware data diode. Traffic arrives in one direction. Here, a synthetic replay is running through the actual software. Watch the packet counters, the sensor state, and the alert queue. These are observations being processed, as they arrive.",
      "briefSections": [
        "2.9",
        "9",
        "10"
      ],
      "start": 740,
      "end": 1874,
      "graphicReveal": 36,
      "uiReveal": 378,
      "clipAvailable": true
    },
    {
      "id": "organize",
      "label": "PACKETS \u2192 CONTEXT",
      "title": "Put the observations together.",
      "minSeconds": 24,
      "graphic": "organize",
      "clip": "overview",
      "text": "First, we give each packet a useful shape: addresses, ports, protocol, size, and time. Related packets form a flow. Alongside that, timed windows collect what happens across the traffic. The clock closes idle flows and completed windows, even when the next packet never arrives.",
      "briefSections": [
        "2.2",
        "9",
        "10"
      ],
      "start": 1874,
      "end": 3026,
      "graphicReveal": 36,
      "uiReveal": 396,
      "clipAvailable": true
    },
    {
      "id": "rhythm",
      "label": "EXPERIMENT 01 \u00b7 TIMING",
      "title": "Listen to the rhythm.",
      "minSeconds": 22,
      "graphic": "rhythm",
      "clip": "beacon",
      "text": "Look at these flow starts. The gaps are almost even. Change the spacing, and the rhythm changes. Our beacon rule measures that regularity. Now open the real alert: the interval and its variation are recorded here. The analyst can inspect the pattern behind the score.",
      "briefSections": [
        "9",
        "10"
      ],
      "start": 3026,
      "end": 4106,
      "graphicReveal": 36,
      "uiReveal": 386,
      "clipAvailable": true
    },
    {
      "id": "rolling",
      "label": "EXPERIMENT 02 \u00b7 ROLLING CONTEXT",
      "title": "Keep both windows in view.",
      "minSeconds": 26,
      "graphic": "rolling",
      "clip": "rolling-scan",
      "text": "A pattern can be spread across time. In this illustration, one source touches ten distinct destination and port pairs, then ten different pairs in the next window. With rolling scan enabled, the rule keeps a sixty second horizon. The union reaches twenty. Here is that pattern, recorded by the actual pipeline.",
      "briefSections": [
        "10"
      ],
      "start": 4106,
      "end": 5356,
      "graphicReveal": 35,
      "uiReveal": 432,
      "clipAvailable": true
    },
    {
      "id": "history",
      "label": "EXPERIMENT 03 \u00b7 SOURCE CONTEXT",
      "title": "Remember whose history it is.",
      "minSeconds": 26,
      "graphic": "history",
      "clip": "source-context",
      "text": "Now suppose two hosts contact the same destination. It is familiar to the first host. That does not make it familiar to the second. With source context enabled, we check this host's retained history, then compare transfer volume with its own baseline. The alert records the lookback and coverage that qualify that observation.",
      "briefSections": [
        "2.3",
        "10"
      ],
      "start": 5356,
      "end": 6625,
      "graphicReveal": 28,
      "uiReveal": 441,
      "clipAvailable": true
    },
    {
      "id": "dns",
      "label": "DOMAIN-NAME ANALYSIS",
      "title": "Read the shape of a name.",
      "minSeconds": 23,
      "graphic": "dns",
      "clip": "dns",
      "text": "A domain name is another kind of sequence. Our character C N N examines patterns in its letters. Separate rules inspect the DNS query's length and type. In the software, the detector identifier tells us which check produced this record. We can see the observed query measurements beside it.",
      "briefSections": [
        "2.5",
        "9",
        "10"
      ],
      "start": 6625,
      "end": 7777,
      "graphicReveal": 36,
      "uiReveal": 414,
      "clipAvailable": true
    },
    {
      "id": "encrypted",
      "label": "ENCRYPTED-SESSION ANALYSIS",
      "title": "Two branches. Different observations.",
      "minSeconds": 32,
      "graphic": "encrypted",
      "clip": "encrypted-metadata",
      "text": "An encrypted session still has an observable shape. The sequence C N N uses packet sizes and timing. A separate X G Boost model uses observed Client Hello metadata and flow measurements. Each branch receives the inputs it needs. QUIC Initial packets expose Client Hello metadata through public protocol inputs. Open the model alert: cipher counts, extension counts, bytes, and duration now have names.",
      "briefSections": [
        "2.4",
        "9",
        "10"
      ],
      "start": 7777,
      "end": 9325,
      "graphicReveal": 36,
      "uiReveal": 540,
      "clipAvailable": true
    },
    {
      "id": "models",
      "label": "PARALLEL DETECTOR BRANCHES",
      "title": "The right inputs. The right branch.",
      "minSeconds": 22,
      "graphic": "models",
      "clip": "scan-model",
      "text": "The same engine routes different observations to different checks. Random Forest uses scan window fan out. Exfiltration X G Boost uses transfer window features. Light G B M adds flow scoring. Eligible Isolation Forest scores provide supporting evidence. These branches serve different purposes; the recorded alert identifies its detector and its inputs.",
      "briefSections": [
        "9",
        "10"
      ],
      "start": 9325,
      "end": 10513,
      "graphicReveal": 36,
      "uiReveal": 486,
      "clipAvailable": true
    },
    {
      "id": "fusion",
      "label": "SOURCE ATTRIBUTION & CORRELATION",
      "title": "Follow the source. Connect the signals.",
      "minSeconds": 22,
      "graphic": "fusion",
      "clip": "source-correlation",
      "text": "Detectors first write their own alerts. Then the correlation layer considers recent qualifying signals from the same source. Filter that source, open a correlated record, and inspect its contributors. The observations stay attached, so the analyst can follow how the signals were connected.",
      "briefSections": [
        "2.8",
        "9",
        "10"
      ],
      "start": 10513,
      "end": 11628,
      "graphicReveal": 35,
      "uiReveal": 396,
      "clipAvailable": true
    },
    {
      "id": "handoff",
      "label": "THE ANALYST VIEW",
      "title": "Carry the evidence forward.",
      "minSeconds": 28,
      "graphic": "handoff",
      "clip": "evidence-export",
      "text": "This is where the explanation becomes a workflow. Open an alert. Read its named measurements. Inspect the original evidence. Then download the selected alert as J S O N. The bundle preserves the record, the active filters, and a hash of that record. The software carries the observations all the way to the analyst.",
      "briefSections": [
        "9",
        "10"
      ],
      "start": 11628,
      "end": 12960,
      "graphicReveal": 36,
      "uiReveal": 450,
      "clipAvailable": true
    },
    {
      "id": "closing",
      "label": "BUILT BY SAMARAGS",
      "title": "See everything. Touch nothing.",
      "minSeconds": 14,
      "graphic": "receive",
      "clip": null,
      "text": "From packets, to patterns, to inspectable evidence. Diode Sentinel. Passive, receive side monitoring. See everything. Touch nothing. Built by Samarags.",
      "briefSections": [
        "9",
        "10"
      ],
      "start": 12960,
      "end": 13608,
      "graphicReveal": 36,
      "uiReveal": 288,
      "clipAvailable": false
    }
  ],
  "narration": [
    {
      "id": "intro",
      "text": "A packet is a small observation. Where did it come from? Where is it going? How big is it, and when did it arrive? Put those observations together, and a pattern begins to appear. This is Diode Sentinel.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 20.256,
      "durationSeconds": 20.256,
      "minSeconds": 18.0,
      "file": "explainer-narration/intro.wav",
      "audioSha256": "40e389284c362fda7967dd4b608e6912d1dfecc718b4a89b62812fb346f00526",
      "startFrame": 60,
      "durationFrames": 609
    },
    {
      "id": "receive",
      "text": "The sensor watches the receive side of a hardware data diode. Traffic arrives in one direction. Here, a synthetic replay is running through the actual software. Watch the packet counters, the sensor state, and the alert queue. These are observations being processed, as they arrive.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 25.128,
      "durationSeconds": 25.128,
      "minSeconds": 22.0,
      "file": "explainer-narration/receive.wav",
      "audioSha256": "eead2ecb6d72fd38bbdfe13823ae35a84f0f2da5bf8a06196c4a38a6102a645d",
      "startFrame": 800,
      "durationFrames": 755
    },
    {
      "id": "organize",
      "text": "First, we give each packet a useful shape: addresses, ports, protocol, size, and time. Related packets form a flow. Alongside that, timed windows collect what happens across the traffic. The clock closes idle flows and completed windows, even when the next packet never arrives.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 26.352,
      "durationSeconds": 26.352,
      "minSeconds": 24.0,
      "file": "explainer-narration/organize.wav",
      "audioSha256": "e23eb8df041d1c4236aa70e71122b8159c81e3075e79558be7aef64aa17c19a9",
      "startFrame": 1934,
      "durationFrames": 792
    },
    {
      "id": "rhythm",
      "text": "Look at these flow starts. The gaps are almost even. Change the spacing, and the rhythm changes. Our beacon rule measures that regularity. Now open the real alert: the interval and its variation are recorded here. The analyst can inspect the pattern behind the score.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 25.656,
      "durationSeconds": 25.656,
      "minSeconds": 22.0,
      "file": "explainer-narration/rhythm.wav",
      "audioSha256": "ea1a62bcee5914c9ef50ee83c511fb24ae042a823096253c21a4fd757c2f2f50",
      "startFrame": 3086,
      "durationFrames": 771
    },
    {
      "id": "rolling",
      "text": "A pattern can be spread across time. In this illustration, one source touches ten distinct destination and port pairs, then ten different pairs in the next window. With rolling scan enabled, the rule keeps a sixty second horizon. The union reaches twenty. Here is that pattern, recorded by the actual pipeline.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 28.272,
      "durationSeconds": 28.272,
      "minSeconds": 26.0,
      "file": "explainer-narration/rolling.wav",
      "audioSha256": "b529946a0c8b0b03adacd8a70ba38fa44afc536d554bd28444b274940bf5defb",
      "startFrame": 4166,
      "durationFrames": 850
    },
    {
      "id": "history",
      "text": "Now suppose two hosts contact the same destination. It is familiar to the first host. That does not make it familiar to the second. With source context enabled, we check this host's retained history, then compare transfer volume with its own baseline. The alert records the lookback and coverage that qualify that observation.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 28.512,
      "durationSeconds": 28.512,
      "minSeconds": 26.0,
      "file": "explainer-narration/history.wav",
      "audioSha256": "4d29e22a9562322f7da37b37e69dbc0f497aa08a9c4916ef17fba7b5e4dc6038",
      "startFrame": 5416,
      "durationFrames": 857
    },
    {
      "id": "dns",
      "text": "A domain name is another kind of sequence. Our character C N N examines patterns in its letters. Separate rules inspect the DNS query's length and type. In the software, the detector identifier tells us which check produced this record. We can see the observed query measurements beside it.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 26.928,
      "durationSeconds": 26.928,
      "minSeconds": 23.0,
      "file": "explainer-narration/dns.wav",
      "audioSha256": "19f552ff0292e72701c3dba405549475fa5524ea0df4834a1407e3eb57330095",
      "startFrame": 6685,
      "durationFrames": 809
    },
    {
      "id": "encrypted",
      "text": "An encrypted session still has an observable shape. The sequence C N N uses packet sizes and timing. A separate X G Boost model uses observed Client Hello metadata and flow measurements. Each branch receives the inputs it needs. QUIC Initial packets expose Client Hello metadata through public protocol inputs. Open the model alert: cipher counts, extension counts, bytes, and duration now have names.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 37.272,
      "durationSeconds": 37.272,
      "minSeconds": 32.0,
      "file": "explainer-narration/encrypted.wav",
      "audioSha256": "3c0a45a8927ba07dc4f172d1d97dd805dc0e46755641f0525faff906f6725c70",
      "startFrame": 7837,
      "durationFrames": 1120
    },
    {
      "id": "models",
      "text": "The same engine routes different observations to different checks. Random Forest uses scan window fan out. Exfiltration X G Boost uses transfer window features. Light G B M adds flow scoring. Eligible Isolation Forest scores provide supporting evidence. These branches serve different purposes; the recorded alert identifies its detector and its inputs.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 32.928,
      "durationSeconds": 32.928,
      "minSeconds": 22.0,
      "file": "explainer-narration/models.wav",
      "audioSha256": "2cda10f5fe73c306cc3e93544b7b79467825edcbcab9b4beca5474c64a820845",
      "startFrame": 9385,
      "durationFrames": 989
    },
    {
      "id": "fusion",
      "text": "Detectors first write their own alerts. Then the correlation layer considers recent qualifying signals from the same source. Filter that source, open a correlated record, and inspect its contributors. The observations stay attached, so the analyst can follow how the signals were connected.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 25.392,
      "durationSeconds": 25.392,
      "minSeconds": 22.0,
      "file": "explainer-narration/fusion.wav",
      "audioSha256": "1b32952148c134f5d901989686f13f84b08c73c341bb76b0f77ef9e46a75db2a",
      "startFrame": 10573,
      "durationFrames": 763
    },
    {
      "id": "handoff",
      "text": "This is where the explanation becomes a workflow. Open an alert. Read its named measurements. Inspect the original evidence. Then download the selected alert as J S O N. The bundle preserves the record, the active filters, and a hash of that record. The software carries the observations all the way to the analyst.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 30.12,
      "durationSeconds": 30.12,
      "minSeconds": 28.0,
      "file": "explainer-narration/handoff.wav",
      "audioSha256": "153b3b563b9525d6db115d90b4fef20814ba32998699528318aba609b2406ef7",
      "startFrame": 11688,
      "durationFrames": 905
    },
    {
      "id": "closing",
      "text": "From packets, to patterns, to inspectable evidence. Diode Sentinel. Passive, receive side monitoring. See everything. Touch nothing. Built by Samarags.",
      "provider": "Microsoft Edge TTS",
      "locale": "en-IN",
      "voice": "en-IN-PrabhatNeural",
      "rate": "-10%",
      "speechSeconds": 16.776,
      "durationSeconds": 16.776,
      "minSeconds": 14.0,
      "file": "explainer-narration/closing.wav",
      "audioSha256": "b8d1e26e9bfa339984dd31c3424e5b002c596c75395f978aa2a69f47222658e6",
      "startFrame": 13020,
      "durationFrames": 505
    }
  ],
  "music": "explainer-music.wav",
  "capture": {
    "source": "fresh seeded gen_traffic.py capture plus focused synthetic PCAP scenarios",
    "qualifier": "Synthetic replay; detector outputs are scenario evidence, not accuracy claims.",
    "replay": {
      "seed": "generator default",
      "mode": "--pipe pcap FIFO",
      "speed": 25,
      "pipeline_flags": [
        "--no-state",
        "--dga-cnn",
        "--ml",
        "--models-567 models567/manifest.json",
        "--source-context",
        "--rolling-scan"
      ]
    },
    "viewport": {
      "width": 1600,
      "height": 1000
    },
    "clips": {
      "overview": {
        "focusSelector": "#sensor-strip",
        "focusBounds": {
          "x": 234,
          "y": 239.59375,
          "width": 1338,
          "height": 65
        },
        "recordedSeconds": 24.001,
        "visibleText": "Sensor\nCompleted\nMode\nPacket stream\nSource\n/tmp/nix-shell.laQUSI/diode-explainer-8qgyfsqc/feed.pcap\nLast packet received \u00b7 UTC\n19:24:38\nHeartbeat\n3.7s ago\nSeen\n14,171\nAnalyzed\n14,171\nSampled out\n0\nMalformed\n0\nKernel drops\nUnknown",
        "video": "overview.webm",
        "poster": "overview.png",
        "timestamps": {
          "start_utc": "2026-09-30T19:24:18.888+00:00",
          "end_utc": "2026-09-30T19:24:42.888+00:00",
          "start_monotonic": 22041.098,
          "end_monotonic": 22065.099
        }
      },
      "beacon": {
        "focusSelector": "#detail-modal .modal-box",
        "focusBounds": {
          "x": 432.5,
          "y": 76.78125,
          "width": 720,
          "height": 846.421875
        },
        "recordedSeconds": 22.0,
        "visibleText": "High\nPeriodic flow pattern\n\u2715\n\nflows 6; mean interval (s) 4.98; CV 0.0179; gate 0.15\n\nTimestamp\n2025-09-09T21:20:33.026Z\nRecorded Flow Key (Not A Session ID)\n10.0.0.7:*->198.51.100.23:443/tcp\nDetector Identifier\nc2_beaconing\nSignal Origin\nrule\nSource\n10.0.0.7\nDestination\n198.51.100.23\nRule Score\n0.798\nSeverity\nhigh\nObserved measurements\nFlows in series\n6\nMean interval (s)\n4.98\nInterval CV\n0.0179\nCV gate\n0.15\nInterpretation limits\n\nPeriodicity is one-way observable but cloud telemetry and scheduled jobs can produce the same pattern. Detector scores are not calibrated probabilities of compromise.\n\nSuggested verification\n\nCompare the recorded flow times with the source's expected scheduled connections.\n\nDownload evidence JSON\nOne selected alert \u00b7 active filters recorded\nOriginal detector evidence",
        "video": "beacon.webm",
        "poster": "beacon.png",
        "timestamps": {
          "start_utc": "2026-09-30T19:24:43.256+00:00",
          "end_utc": "2026-09-30T19:25:05.256+00:00",
          "start_monotonic": 22065.467,
          "end_monotonic": 22087.467
        }
      },
      "rolling-scan": {
        "focusSelector": "#detail-modal .modal-box",
        "focusBounds": {
          "x": 432.5,
          "y": 20,
          "width": 720,
          "height": 960
        },
        "recordedSeconds": 26.002,
        "visibleText": "Medium\nRolling-window port scan against one destination\n\u2715\n\ndestination/port pairs 20; destinations 1; top-destination pairs 20; rolling horizon (s) 60.0; current-window pairs 10; observed window-end times (stream ...\n\nTimestamp\n2025-09-09T21:30:19.000Z\nRecorded Flow Key (Not A Session ID)\n192.0.2.70:*->198.51.100.70:*/tcp\nDetector Identifier\nrecon_rolling_vertical_scan\nSignal Origin\nrule\nSource\n192.0.2.70\nDestination\n198.51.100.70\nRule Score\n0.520\nSeverity\nmedium\nObserved measurements\nDistinct destination/port pairs in rolling history\n20\nPairs in current window\n10\nDistinct destination IPs\n1\nPairs on top destination\n20\nRolling horizon (s)\n60\nOldest observed window end (stream seconds)\n610\nNewest observed window end (stream seconds)\n620\nObserved endpoint sample\n{\"dst\":\"198.51.100.70\",\"dport\":1000,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1001,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1002,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1003,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1004,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1005,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1006,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1007,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1008,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1009,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1010,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1011,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1012,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1013,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1014,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1015,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1016,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1017,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1018,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1019,\"protocols\":[\"tcp\"]}\nEndpoint sample truncated\nNo\nHistory evictions\n{\"source_entries\":0,\"pair_entries_total\":0,\"pairs_for_source\":0}\nInterpretation limits\n\nThis rolling fan-out pattern uses one-way packet metadata. Bounded history evictions can make the retained pair count lower than the full observed history; authorized scanners can produce similar patterns. Detector scores are not calibrated probabilities of compromise.\n\nSuggested verification\n\nIf a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.\n\nDownload evidence JSON\nOne selected alert \u00b7 active filters recorded\nOriginal detector evidence",
        "video": "rolling-scan.webm",
        "poster": "rolling-scan.png",
        "timestamps": {
          "start_utc": "2026-09-30T19:25:06.279+00:00",
          "end_utc": "2026-09-30T19:25:32.281+00:00",
          "start_monotonic": 22088.49,
          "end_monotonic": 22114.491
        }
      },
      "source-context": {
        "focusSelector": "#detail-modal .modal-box",
        "focusBounds": {
          "x": 432.5,
          "y": 20,
          "width": 720,
          "height": 960
        },
        "recordedSeconds": 26.001,
        "visibleText": "Critical\nLarge transfer to a new destination\n\u2715\n\nbytes to new destination 600000; baseline bytes 600; ratio 1000.0x; age windows 0\n\nTimestamp\n2025-09-09T21:30:39.000Z\nRecorded Flow Key (Not A Session ID)\n192.0.2.81:*->198.51.100.80:443/tcp\nDetector Identifier\ndata_exfiltration\nSignal Origin\nrule\nSource\n192.0.2.81\nDestination\n198.51.100.80\nRule Score\n0.950\nSeverity\ncritical\nObserved measurements\nObserved bytes to new destination\n600000\nSource median baseline bytes\n600\nRatio vs baseline\n1000\nPair age (windows)\n0\nInterpretation limits\n\nOne-way bytes show transfer volume, not authorization or successful exfiltration; benign backups can look similar. Detector scores are not calibrated probabilities of compromise.\n\nSuggested verification\n\nCompare the observed destination and transfer volume with this source's prior byte baseline and backup schedule.\n\nDownload evidence JSON\nOne selected alert \u00b7 active filters recorded\nOriginal detector evidence\n{\n  \"bytes_to_new_dst\": 600000,\n  \"pair_age_windows\": 0,\n  \"src_baseline_bytes_median\": 600,\n  \"ratio_vs_baseline\": 1000,\n  \"novel_destination\": true,\n  \"why\": \"large sustained upload to a destination not observed within this source's retained history lookback, far above its normal observed window volume\",\n  \"source_novel_within_lookback\": true,\n  \"source_history_lookback_windows\": 8640,\n  \"source_history_coverage_at_admission\": \"complete_within_lookback\",\n  \"source_history_coverage_now\": \"complete_within_lookback\",\n  \"fleet_destination_novel\": false,\n  \"source_history\": {\n    \"retained_pairs\": 3645,\n    \"capacity\": 50000,\n    \"max_age_windows\": 8640,\n    \"incomplete_sources\": 0,\n    \"global_coverage_incomplete\": false,\n    \"expired_entries\": 0,\n    \"evicted_entries\": 0\n  }\n}",
        "video": "source-context.webm",
        "poster": "source-context.png",
        "timestamps": {
          "start_utc": "2026-09-30T19:25:33.315+00:00",
          "end_utc": "2026-09-30T19:25:59.316+00:00",
          "start_monotonic": 22115.526,
          "end_monotonic": 22141.527
        }
      },
      "dns": {
        "focusSelector": "#detail-modal .modal-box",
        "focusBounds": {
          "x": 432.5,
          "y": 20,
          "width": 720,
          "height": 960
        },
        "recordedSeconds": 23.001,
        "visibleText": "Medium\nRepeated bulky or overlong DNS queries\n\u2715\n\nquery bytes 70; qtype 16; queries 5; cumulative query bytes 350; limitation not verified exfil volume\n\nTimestamp\n2025-09-09T21:24:08.000Z\nRecorded Flow Key (Not A Session ID)\n10.0.0.11:*->*:53/udp\nDetector Identifier\ndns_tunneling\nSignal Origin\nrule\nSource\n10.0.0.11\nDestination\n*\nRule Score\n0.537\nSeverity\nmedium\nObserved measurements\nQuery bytes\n70\nQuery type\n16\nMaximum label length\n50\nTunnel-like queries\n5\nCumulative query bytes\n350\nInterpretation limits\n\nDNS response outcomes are unavailable on this feed; query shape alone can flag legitimate unusual use. Detector scores are not calibrated probabilities of compromise.\n\nSuggested verification\n\nReview the captured DNS query names and qtypes for this source and time window.\n\nDownload evidence JSON\nOne selected alert \u00b7 active filters recorded\nOriginal detector evidence\n{\n  \"qtype\": 16,\n  \"qname\": \"bxxlyy2nw2fmfbf2ncfcnnwfww4q4s6sko2tvgof2okt5z2gjy.exfil.xxxxxxxx.com.\",\n  \"query_bytes\": 70,\n  \"max_label_length\": 50,\n  \"cumulative_tunnel_bytes\": 350,\n  \"tunnel_queries_from_src\": 5,\n  \"signals\": \"qtype=16 (TXT); max label len 50 >= 40; query len 70 >= 60\",\n  \"note\": \"response side not observable (one-way); RCODE and NXDOMAIN correlation unavailable\",\n  \"why\": \"repeated bulky/overlong DNS queries => data encoded into the query channel rather than lookups\"\n}",
        "video": "dns.webm",
        "poster": "dns.png",
        "timestamps": {
          "start_utc": "2026-09-30T19:26:00.359+00:00",
          "end_utc": "2026-09-30T19:26:23.361+00:00",
          "start_monotonic": 22142.57,
          "end_monotonic": 22165.572
        }
      },
      "encrypted-metadata": {
        "focusSelector": "#detail-modal .modal-box",
        "focusBounds": {
          "x": 432.5,
          "y": 20,
          "width": 720,
          "height": 960
        },
        "recordedSeconds": 32.001,
        "visibleText": "Critical\nEncrypted-session model match\n\u2715\n\nnamed model inputs ClientHello cipher-suite count=6.0, ClientHello extension count=3.0, ClientHello offered TLS version=11.0\n\nTimestamp\n2025-09-09T21:23:20.243Z\nRecorded Flow Key (Not A Session ID)\n10.0.0.7:*->198.51.100.23:8443/tcp\nDetector Identifier\nencrypted_session_malware\nSignal Origin\nmodel\nSource\n10.0.0.7\nDestination\n198.51.100.23\nModel Score\n0.944\nSeverity\ncritical\nObserved measurements\nModel\nxgboost\nClientHello cipher-suite count (count)\n6\nClientHello extension count (count)\n3\nClientHello offered TLS version (code: 10=TLS 1.0; 11=TLS 1.1; 12=TLS 1.2; 13=TLS 1.3; 0=unknown)\n11\nTransport code (0 = TLS, 1 = QUIC)\n0\nSNI-present flag (0/1)\n0\nSignature-algorithm count (count)\n2\nFlow packet count (packets)\n3\nFlow bytes (bytes)\n394\nFlow duration (seconds)\n0.019999980926513672\nPacket-size coefficient of variation (unitless)\n0.45623195266236183\nInterpretation limits\n\nThe named vector contains client-side metadata and flow measurements. This alert has no metadata-availability flags, so a recorded zero does not establish whether a field was absent, empty, or defaulted. Detector scores are not calibrated probabilities of compromise.\n\nSuggested verification\n\nReview the raw recorded model features alongside the source's deterministic alerts.\n\nDownload evidence JSON\nOne selected alert \u00b7 active filters recorded\nOriginal detector evidence\n{\n  \"model\": \"xgboost\",\n  \"metadata_features\": [\n    6,\n    3,\n    11,\n    0,\n    0,\n    2,\n    3,\n    394,\n    0.019999980926513672,\n    0.45623195266236183\n  ]\n}",
        "video": "encrypted-metadata.webm",
        "poster": "encrypted-metadata.png",
        "timestamps": {
          "start_utc": "2026-09-30T19:26:24.381+00:00",
          "end_utc": "2026-09-30T19:26:56.382+00:00",
          "start_monotonic": 22166.592,
          "end_monotonic": 22198.593
        }
      },
      "scan-model": {
        "focusSelector": "#detail-modal .modal-box",
        "focusBounds": {
          "x": 432.5,
          "y": 20,
          "width": 720,
          "height": 960
        },
        "recordedSeconds": 22.001,
        "visibleText": "Critical\nModel-flagged scan pattern\n\u2715\n\nnamed model inputs Distinct destination/port pairs=202.0, Distinct destination IPs=3.0, Maximum ports on one destination=200.0\n\nTimestamp\n2025-09-09T21:24:19.000Z\nRecorded Flow Key (Not A Session ID)\n10.0.0.13:*->*:0/*\nDetector Identifier\nrecon_model_scan\nSignal Origin\nmodel\nSource\n10.0.0.13\nDestination\n*\nModel Score\n1.000\nSeverity\ncritical\nObserved measurements\nModel\nscan_rf\nDistinct destination/port pairs (pairs)\n202\nDistinct destination IPs (IPs)\n3\nMaximum ports on one destination (ports)\n200\nMaximum per-destination share of pairs (unitless ratio)\n0.9900990099009901\nSource bytes in window (bytes)\n14416\nIsolationForest anomaly score\n-0.2838237650122478\nIsolationForest score kind\nuncalibrated_decision_function\nIsolationForest more anomalous when\nlower\nInterpretation limits\n\nThis is a one-way traffic pattern; legitimate scanners or bursts can produce similar measurements. Detector scores are not calibrated probabilities of compromise.\n\nSuggested verification\n\nIf a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.\n\nDownload evidence JSON\nOne selected alert \u00b7 active filters recorded\nOriginal detector evidence\n{\n  \"model\": \"scan_rf\",\n  \"features\": [\n    202,\n    3,\n    200,\n    0.9900990099009901,\n    14416\n  ],\n  \"iforest_corroboration\": {\n    \"model\": \"scan_iforest\",\n    \"anomaly_score\": -0.2838237650122478,\n    \"score_kind\": \"uncalibrated_decision_function\",\n    \"more_anomalous_when\": \"lower\"\n  }\n}",
        "video": "scan-model.webm",
        "poster": "scan-model.png",
        "timestamps": {
          "start_utc": "2026-09-30T19:26:57.519+00:00",
          "end_utc": "2026-09-30T19:27:19.520+00:00",
          "start_monotonic": 22199.73,
          "end_monotonic": 22221.731
        }
      },
      "source-correlation": {
        "focusSelector": "#detail-modal .modal-box",
        "focusBounds": {
          "x": 432.5,
          "y": 20,
          "width": 720,
          "height": 960
        },
        "recordedSeconds": 22.814,
        "visibleText": "Critical\nCorrelated TLS and periodicity signals\n\u2715\n\nsignals c2_beaconing, ml_flow_suspicious, tls_known_malware; window (s) 120.0; method noisy-OR; 120ss half-life; limitation not confirmation\n\nTimestamp\n2025-09-09T21:23:20.233Z\nRecorded Flow Key (Not A Session ID)\n10.0.0.7:*->*:0/*\nDetector Identifier\nconfirmed_c2_implant\nSignal Origin\ncorrelation\nSource\n10.0.0.7\nDestination\n*\nCorrelation Score\n0.999\nSeverity\ncritical\nObserved measurements\nCorrelation window (s)\n120\nCombination method\nnoisy-OR with exponential decay (half-life=120s)\nSignals used by this correlation\nC2 beaconing\n12.2 s before correlation \u00b7 198.51.100.23 \u00b7 weighted score 0.689\nSuspicious flow\n7.1 s before correlation \u00b7 198.51.100.23 \u00b7 weighted score 0.96\nTLS local indicator match\n0 s before correlation \u00b7 198.51.100.23 \u00b7 weighted score 0.99\nInterpretation limits\n\nCorrelation combines detector outputs from one-way observations; signals may share causes and do not confirm compromise. Detector scores are not calibrated probabilities of compromise.\n\nSuggested verification\n\nReview each listed source alert and its packet-time window before escalating.\n\nDownload evidence JSON\nOne selected alert \u00b7 active filters recorded\nOriginal detector evidence\n{\n  \"contributing_signals\": [\n    {\n      \"threat_class\": \"c2_beaconing\",\n      \"at_s\": 188,\n      \"age_s\": 12.2,\n      \"confidence\": 0.739,\n      \"effective_confidence\": 0.689,\n      \"dst\": \"198.51.100.23\",\n      \"dport\": 0\n    },\n    {\n      \"threat_class\": \"ml_flow_suspicious\",\n      \"at_s\": 193.1,\n      \"age_s\": 7.1,\n      \"confidence\": 1,\n      \"effective_confidence\": 0.96,\n      \"dst\": \"198.51.100.23\",\n      \"dport\": 0\n    },\n    {\n      \"threat_class\": \"tls_known_malware\",\n      \"at_s\": 200.2,\n      \"age_s\": 0,\n      \"confidence\": 0.99,\n      \"effective_confidence\": 0.99,\n      \"dst\": \"198.51.100.23\",\n      \"dport\": 0\n    }\n  ],\n  \"combination\": \"noisy-OR with exponential decay (half-life=120s)\",\n  \"window_s\": 120,\n  \"why\": \"multiple independent detectors firing on one source -- jointly far more indicative than any single signal\"\n}",
        "video": "source-correlation.webm",
        "poster": "source-correlation.png",
        "timestamps": {
          "start_utc": "2026-09-30T19:27:20.592+00:00",
          "end_utc": "2026-09-30T19:27:43.407+00:00",
          "start_monotonic": 22222.803,
          "end_monotonic": 22245.617
        }
      },
      "evidence-export": {
        "focusSelector": "#export-alert",
        "recordedSeconds": 28.002,
        "visibleText": "Medium\nRolling-window port scan against one destination\n\u2715\n\ndestination/port pairs 20; destinations 1; top-destination pairs 20; rolling horizon (s) 60.0; current-window pairs 10; observed window-end times (stream ...\n\nTimestamp\n2025-09-09T21:30:19.000Z\nRecorded Flow Key (Not A Session ID)\n192.0.2.70:*->198.51.100.70:*/tcp\nDetector Identifier\nrecon_rolling_vertical_scan\nSignal Origin\nrule\nSource\n192.0.2.70\nDestination\n198.51.100.70\nRule Score\n0.520\nSeverity\nmedium\nObserved measurements\nDistinct destination/port pairs in rolling history\n20\nPairs in current window\n10\nDistinct destination IPs\n1\nPairs on top destination\n20\nRolling horizon (s)\n60\nOldest observed window end (stream seconds)\n610\nNewest observed window end (stream seconds)\n620\nObserved endpoint sample\n{\"dst\":\"198.51.100.70\",\"dport\":1000,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1001,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1002,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1003,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1004,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1005,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1006,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1007,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1008,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1009,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1010,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1011,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1012,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1013,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1014,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1015,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1016,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1017,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1018,\"protocols\":[\"tcp\"]}, {\"dst\":\"198.51.100.70\",\"dport\":1019,\"protocols\":[\"tcp\"]}\nEndpoint sample truncated\nNo\nHistory evictions\n{\"source_entries\":0,\"pair_entries_total\":0,\"pairs_for_source\":0}\nInterpretation limits\n\nThis rolling fan-out pattern uses one-way packet metadata. Bounded history evictions can make the retained pair count lower than the full observed history; authorized scanners can produce similar patterns. Detector scores are not calibrated probabilities of compromise.\n\nSuggested verification\n\nIf a retained capture is available, inspect this source's destination/port pairs and compare with the approved scanner schedule.\n\nDownload evidence JSON\nEvidence bundle downloaded\nOriginal detector evidence",
        "selectedRecordKey": "4084786e2a47d581b2f7278d9426ffe17914ca99899c139a7d471afbde89c4b0",
        "video": "evidence-export.webm",
        "poster": "evidence-export.png",
        "timestamps": {
          "start_utc": "2026-09-30T19:27:44.536+00:00",
          "end_utc": "2026-09-30T19:28:12.538+00:00",
          "start_monotonic": 22246.747,
          "end_monotonic": 22274.749
        }
      }
    },
    "interactions": [
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
    ],
    "selected_records": {
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
            "rolling_window_s": 60.0,
            "rolling_distinct_dst_port_pairs": 20,
            "current_window_distinct_pairs": 10,
            "distinct_dst_ips": 1,
            "pairs_on_top_dst": 20,
            "oldest_observed_window_end_s": 610.0,
            "newest_observed_window_end_s": 620.0,
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
              "value": 60.0
            },
            {
              "label": "Oldest observed window end (stream seconds)",
              "value": 610.0
            },
            {
              "label": "Newest observed window end (stream seconds)",
              "value": 620.0
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
            "ratio_vs_baseline": 1000.0,
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
              "value": 1000.0
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
              6.0,
              3.0,
              11.0,
              0,
              0.0,
              2.0,
              3.0,
              394.0,
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
              "value": 6.0
            },
            {
              "label": "ClientHello extension count (count)",
              "value": 3.0
            },
            {
              "label": "ClientHello offered TLS version (code: 10=TLS 1.0; 11=TLS 1.1; 12=TLS 1.2; 13=TLS 1.3; 0=unknown)",
              "value": 11.0
            },
            {
              "label": "Transport code (0 = TLS, 1 = QUIC)",
              "value": 0
            },
            {
              "label": "SNI-present flag (0/1)",
              "value": 0.0
            },
            {
              "label": "Signature-algorithm count (count)",
              "value": 2.0
            },
            {
              "label": "Flow packet count (packets)",
              "value": 3.0
            },
            {
              "label": "Flow bytes (bytes)",
              "value": 394.0
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
          "confidence": 1.0,
          "severity": "critical",
          "evidence": {
            "model": "scan_rf",
            "features": [
              202.0,
              3.0,
              200.0,
              0.9900990099009901,
              14416.0
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
              "value": 202.0
            },
            {
              "label": "Distinct destination IPs (IPs)",
              "value": 3.0
            },
            {
              "label": "Maximum ports on one destination (ports)",
              "value": 200.0
            },
            {
              "label": "Maximum per-destination share of pairs (unitless ratio)",
              "value": 0.9900990099009901
            },
            {
              "label": "Source bytes in window (bytes)",
              "value": 14416.0
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
                "at_s": 188.0,
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
                "confidence": 1.0,
                "effective_confidence": 0.96,
                "dst": "198.51.100.23",
                "dport": 0
              },
              {
                "threat_class": "tls_known_malware",
                "at_s": 200.2,
                "age_s": 0.0,
                "confidence": 0.99,
                "effective_confidence": 0.99,
                "dst": "198.51.100.23",
                "dport": 0
              }
            ],
            "combination": "noisy-OR with exponential decay (half-life=120s)",
            "window_s": 120.0,
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
              "value": 120.0
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
              "age_seconds": 0.0,
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
            "rolling_window_s": 60.0,
            "rolling_distinct_dst_port_pairs": 20,
            "current_window_distinct_pairs": 10,
            "distinct_dst_ips": 1,
            "pairs_on_top_dst": 20,
            "oldest_observed_window_end_s": 610.0,
            "newest_observed_window_end_s": 620.0,
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
              "value": 60.0
            },
            {
              "label": "Oldest observed window end (stream seconds)",
              "value": 610.0
            },
            {
              "label": "Newest observed window end (stream seconds)",
              "value": 620.0
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
          "rolling_window_s": 60.0,
          "rolling_distinct_dst_port_pairs": 20,
          "current_window_distinct_pairs": 10,
          "distinct_dst_ips": 1,
          "pairs_on_top_dst": 20,
          "oldest_observed_window_end_s": 610.0,
          "newest_observed_window_end_s": 620.0,
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
          "ratio_vs_baseline": 1000.0,
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
            6.0,
            3.0,
            11.0,
            0,
            0.0,
            2.0,
            3.0,
            394.0,
            0.019999980926513672,
            0.45623195266236183
          ]
        }
      }
    },
    "downloads": {
      "diode-alert-4084786e2a47.json": {
        "path": "downloads/diode-alert-4084786e2a47.json",
        "sha256": "f70b49606b0bcaa96f6f88d4f9d53242d4b91211094173760e55751376fe1c2d",
        "bytes": 10065
      }
    },
    "scenario": {
      "linktype": 1,
      "generator_packets": 14049,
      "fixture_packets": 122,
      "packets_total": 14171,
      "fixture_timestamps": {
        "time_base": 1757452800.0,
        "rolling_scan_windows": [
          1757453405.1,
          1757453415.1
        ],
        "source_history_seed": [
          1757453425.0,
          1757453425.1
        ],
        "source_history_transfer": [
          1757453435.1,
          1757453435.199
        ]
      }
    },
    "stats": {
      "total": 108,
      "critical": 72,
      "high": 23,
      "medium": 13,
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
        "recon_rolling_vertical_scan",
        "recon_vertical_scan",
        "tls_known_malware",
        "tls_novel_fingerprint"
      ],
      "suppressed": 20,
      "by_class": {
        "encrypted_session_malware": 28,
        "ml_flow_suspicious": 20,
        "c2_beaconing": 14,
        "dga_domain": 14,
        "multi_signal_fusion": 6,
        "dns_tunneling": 4,
        "confirmed_c2_implant": 3,
        "recon_vertical_scan": 3,
        "recon_model_scan": 3,
        "tls_known_malware": 2,
        "tls_novel_fingerprint": 2,
        "ddos_volumetric_spoofed": 2,
        "data_exfiltration": 2,
        "confirmed_exfiltration": 2,
        "data_exfiltration_model": 1,
        "botnet_c2_with_dga": 1,
        "recon_rolling_vertical_scan": 1
      },
      "by_severity": {
        "critical": 72,
        "high": 23,
        "medium": 13,
        "low": 0
      },
      "hosts": 7,
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
          "count": 32
        },
        {
          "key": "e",
          "label": "Recon / port scan",
          "count": 7
        },
        {
          "key": "f",
          "label": "Data exfiltration",
          "count": 3
        }
      ],
      "first_alert": "2025-09-09T21:20:08.143000+00:00",
      "last_alert": "2025-09-09T21:30:39+00:00",
      "span_seconds": 630.9,
      "sensor": {
        "suppressed": 20,
        "parser": "live",
        "pkt_per_s": 558,
        "alerts": 108,
        "mode": "live",
        "health": {
          "status": "completed",
          "mode": "pcap_stream",
          "interface": null,
          "path": "/tmp/nix-shell.laQUSI/diode-explainer-8qgyfsqc/feed.pcap",
          "started_at": "2026-09-30T19:24:12.708904Z",
          "updated_at": "2026-09-30T19:24:38.116082Z",
          "heartbeat_at": "2026-09-30T19:24:38.116082Z",
          "last_packet_at": "2026-09-30T19:24:38.114277Z",
          "counts": {
            "seen": 14171,
            "analyzed": 14171,
            "sampled_out": 0,
            "malformed": 0,
            "kernel_drops": null
          },
          "error": null,
          "heartbeat_age_seconds": 214.8
        }
      },
      "synthetic_demo": true,
      "signals": {
        "raw_records": 108,
        "rule_records": 44,
        "model_records": 52,
        "correlation_records": 12,
        "unknown_records": 0,
        "critical_rule_records": 12,
        "authorised_records": 0,
        "source_count": 7
      }
    },
    "api_alert_summary": {
      "matched": 108,
      "stats": {
        "total": 108,
        "critical": 72,
        "high": 23,
        "medium": 13,
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
          "recon_rolling_vertical_scan",
          "recon_vertical_scan",
          "tls_known_malware",
          "tls_novel_fingerprint"
        ],
        "suppressed": 20,
        "by_class": {
          "encrypted_session_malware": 28,
          "ml_flow_suspicious": 20,
          "c2_beaconing": 14,
          "dga_domain": 14,
          "multi_signal_fusion": 6,
          "dns_tunneling": 4,
          "confirmed_c2_implant": 3,
          "recon_vertical_scan": 3,
          "recon_model_scan": 3,
          "tls_known_malware": 2,
          "tls_novel_fingerprint": 2,
          "ddos_volumetric_spoofed": 2,
          "data_exfiltration": 2,
          "confirmed_exfiltration": 2,
          "data_exfiltration_model": 1,
          "botnet_c2_with_dga": 1,
          "recon_rolling_vertical_scan": 1
        },
        "by_severity": {
          "critical": 72,
          "high": 23,
          "medium": 13,
          "low": 0
        },
        "hosts": 7,
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
            "count": 32
          },
          {
            "key": "e",
            "label": "Recon / port scan",
            "count": 7
          },
          {
            "key": "f",
            "label": "Data exfiltration",
            "count": 3
          }
        ],
        "first_alert": "2025-09-09T21:20:08.143000+00:00",
        "last_alert": "2025-09-09T21:30:39+00:00",
        "span_seconds": 630.9,
        "sensor": {
          "suppressed": 20,
          "parser": "live",
          "pkt_per_s": 558,
          "alerts": 108,
          "mode": "live",
          "health": {
            "status": "completed",
            "mode": "pcap_stream",
            "interface": null,
            "path": "/tmp/nix-shell.laQUSI/diode-explainer-8qgyfsqc/feed.pcap",
            "started_at": "2026-09-30T19:24:12.708904Z",
            "updated_at": "2026-09-30T19:24:38.116082Z",
            "heartbeat_at": "2026-09-30T19:24:38.116082Z",
            "last_packet_at": "2026-09-30T19:24:38.114277Z",
            "counts": {
              "seen": 14171,
              "analyzed": 14171,
              "sampled_out": 0,
              "malformed": 0,
              "kernel_drops": null
            },
            "error": null,
            "heartbeat_age_seconds": 214.8
          }
        },
        "synthetic_demo": true,
        "signals": {
          "raw_records": 108,
          "rule_records": 44,
          "model_records": 52,
          "correlation_records": 12,
          "unknown_records": 0,
          "critical_rule_records": 12,
          "authorised_records": 0,
          "source_count": 7
        }
      }
    },
    "pipeline_alerts": {
      "count": 108,
      "sha256": "fe68e48f415d96e4635bcbc49ccb02e9e2edded15c81dcd34e331bef6b61ee8c",
      "path": "alerts.jsonl"
    },
    "artifact_hashes": {
      "alerts.jsonl": {
        "sha256": "fe68e48f415d96e4635bcbc49ccb02e9e2edded15c81dcd34e331bef6b61ee8c",
        "bytes": 58902
      },
      "beacon.mp4": {
        "sha256": "f9b3c8a188d974b9a22938439d01c4e82639af75187dbaf8b3f24753bb451f02",
        "bytes": 1631586
      },
      "beacon.png": {
        "sha256": "81b61bce1938700cf84569c396d8111e3cca4c62b59462bfadc3502c3d54180a",
        "bytes": 152467
      },
      "beacon.webm": {
        "sha256": "68c72f6790d5709f9458f14eb84dc5b4680d5b726cec54d6a938cd19c687eabb",
        "bytes": 1679395
      },
      "capture.log": {
        "sha256": "4e9c0b90c8a6d45e869c9ee7d442a9c165b34e16fa46188b80c08e3e0fd85907",
        "bytes": 3441
      },
      "dns.mp4": {
        "sha256": "638fadf4c81eccfa11060c32c475850d32952437b861f98a8740370c80b52cda",
        "bytes": 1848642
      },
      "dns.png": {
        "sha256": "9d33cced1b8e3bf7d9f4519953f7b97b8dbe9c7bd3a3bdc2abe21af92364b973",
        "bytes": 171318
      },
      "dns.webm": {
        "sha256": "a991fdda511cccaa096c94be95c8078edb2beec47f74137dcccd65e40cb7c4c3",
        "bytes": 1744966
      },
      "downloads/diode-alert-4084786e2a47.json": {
        "sha256": "f70b49606b0bcaa96f6f88d4f9d53242d4b91211094173760e55751376fe1c2d",
        "bytes": 10065
      },
      "encrypted-metadata.mp4": {
        "sha256": "50e57d1ce227b0da50977c1ce5d2a5d196f2f9f99e6538e26620a1755835432a",
        "bytes": 2679308
      },
      "encrypted-metadata.png": {
        "sha256": "9ddf1de11f04a5fb102cbfcf9ebfc6d81ed4d5976f72110f61a29b2f2a6ab014",
        "bytes": 175700
      },
      "encrypted-metadata.webm": {
        "sha256": "b4dacf1eb3f6823511c452db96b83bf9f3086241dbe4c35dc5afe92490a85282",
        "bytes": 2439602
      },
      "evidence-export.mp4": {
        "sha256": "1d002a7f3239b981a75cb3be5e86155408822df134fff53fe71dc6c9dddae3d4",
        "bytes": 2589657
      },
      "evidence-export.png": {
        "sha256": "830f43df25dd2a6e3f32c149c36fce2f936e8550b06d7068b8c303079ab554d4",
        "bytes": 196328
      },
      "evidence-export.webm": {
        "sha256": "4ac4503b406ef8d72970afefe8ddb1a10d93d13c5f5ff67cf551db958692531a",
        "bytes": 2283778
      },
      "explainer-replay.pcap": {
        "sha256": "6e4be0118226746f668e9163113e74e312483691876b8e6c54e2aacff89d015c",
        "bytes": 9462177
      },
      "overview.mp4": {
        "sha256": "ef3d14bf835823e2d6c0cad5218b490d54d8478c8326624d0462849f02767e62",
        "bytes": 2670222
      },
      "overview.png": {
        "sha256": "cee318ca7aa5dd9d89d66f0cf1eb14408eec37e10d79bde48168505c1fc68865",
        "bytes": 153720
      },
      "overview.webm": {
        "sha256": "e9edc0d3485dec1a9191df83cb4fe9c12d089d62e967f880937ed86adc305ebc",
        "bytes": 2542584
      },
      "rolling-scan.mp4": {
        "sha256": "e728f140c5ce64500756ec5950a744d3f8ee78ce4d9cf6faba22c15f12d741ae",
        "bytes": 2128261
      },
      "rolling-scan.png": {
        "sha256": "43b9a69492ee4efc4119ad95b0ad52b11a42b17f93a898374ed4b21ce405d9cb",
        "bytes": 187966
      },
      "rolling-scan.webm": {
        "sha256": "dec590787281d2d16c4dae205552255e9ba4e673c3815da4e714b4be9bb14f09",
        "bytes": 1962652
      },
      "run_stats.json": {
        "sha256": "379b981b819c28dce1e572e44be36bf157002e35417ea49d6302bcde518d7248",
        "bytes": 533
      },
      "scan-model.mp4": {
        "sha256": "2c4d6d1c89bd8bc1a17a84af8f7745b01271d85cd91c80b26a3a4038bfda5407",
        "bytes": 1567648
      },
      "scan-model.png": {
        "sha256": "c36fd9c33ed9f7f08c765f1dba25ca3a99a2bf02ff800bc1d172c2a0a32e3e7f",
        "bytes": 156017
      },
      "scan-model.webm": {
        "sha256": "f8fc4252786de00c363481c1c624ffbe3ba05887ca7649c647f41e7f5b8365ac",
        "bytes": 1926177
      },
      "source-context.mp4": {
        "sha256": "b4733ab86acc8afc1e8d999e78c37b19816f9e1e4bca7143161085f47a7d1adb",
        "bytes": 1802897
      },
      "source-context.png": {
        "sha256": "8bd87491ae8d381975e9f943596a9115e90b8a75c992f54e5800fd539d82ff96",
        "bytes": 154220
      },
      "source-context.webm": {
        "sha256": "2d7f72aeb2b83f376a361a9b923c63e3ac519c73878533ffdd68643af99ba50f",
        "bytes": 2260270
      },
      "source-correlation.mp4": {
        "sha256": "0299317bae59fcf4ee3a13f2cc9147381ec80951f7406da000699139f9374a77",
        "bytes": 1744348
      },
      "source-correlation.png": {
        "sha256": "a49c94da34be0c987c15618942b1db61f2c4e7cca5d12c9cbcfdf2007cced972",
        "bytes": 159868
      },
      "source-correlation.webm": {
        "sha256": "d32bf7a01f2d7a897e8d8afd20bc99c5c65dc816a23b06878166741af660c401",
        "bytes": 2162969
      }
    }
  },
  "team": "samarags",
  "brand": "Diode Sentinel",
  "scriptSha256": "95cbcf830e102885b045fd4bb36edbe44e5098b0cca15ef8ce8847108d6b1b2d"
} as const;
