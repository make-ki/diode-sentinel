# One-hour delivery status — 30 September 2026

This note records the implementation state after the one-hour detector-quality
pass. It is a status record, not a benchmark claim. No model was retrained and
no external or real-world dataset was rerun.

## Shipped behavior and activation

- `run.py --source-context` enables bounded per-source destination history for
  exfil indicators. It is off by default. Evidence distinguishes source
  novelty from fleet novelty and reports lookback and coverage. Capacity loss
  suppresses uncertain new-source novelty claims.
- `run.py --rolling-scan` enables exact distinct `(destination IP, port)` fan-out
  accumulation over a 60-second horizon. The existing per-window scan rule
  remains active; a separate rolling alert is emitted only when the accumulated
  threshold is reached below the current-window threshold. This option is off
  by default. Source and pair state are capped; evidence reports evictions and
  endpoint-sample truncation.
- Category 5 metadata XGBoost skips a flow when a complete ClientHello was not
  observed. The packet-sequence model remains eligible. An observed empty SNI
  or signature-algorithm list remains valid metadata; absent and partial fields
  are not filled with invented values.
- Dashboard triage names common model inputs and supports an offline selected-
  alert evidence bundle. The bundle hashes the alert record. It explicitly does
  not supply capture identity, packet references, or model-artifact identity;
  the hash is not a legal chain-of-custody claim.
- QUIC v1 Initial key derivation and packet parsing pass independent RFC 9001
  Appendix A.1/A.2 values and the published Client Initial fixture, including a
  QUIC JA4 `q` prefix. Application data and later handshake levels remain out
  of scope. Details: `quic-verification.md`.

## Validation and remaining caveats

The latest archived 14,049-packet capture produces 45 rules alerts and 67 with
the ML tier. The complete dpkt and Scapy outputs are byte-identical to each
other. The committed historical reference files still contain 46 and 68 alerts;
the only difference is one removed `tls_known_malware` record caused by the old
invalid synthetic QUIC packet. The references were preserved. The historical
fixture gate is **not passing** until the difference receives review and any
fixture migration is explicit.

All 23 test scripts pass after supplying an isolated synthetic alert input to
the dashboard test. The opt-in demo smoke test was additionally run with
`DIODESENTINEL_DEMO_SMOKE=1`: alerts arrive during the FIFO replay and Ctrl-C
cleans up its processes and temporary files. A separate replay combining
`--models-567 models567/manifest.json --source-context --rolling-scan --parity
--no-state` passes complete-record dpkt/Scapy parity (79 alerts on the archived
capture); this is a synthetic repeatability check, not a quality benchmark.

The deck was regenerated from `build_deck.py` with the corrected claims and
saved to `../Diode-Sentinel.pptx` (20 slides).

Browser verification used actual model records from the combined synthetic
replay. Named metadata inputs are visible, the download preserves the selected
alert and active model filter, and missing capture provenance is explicit.
Desktop and 390-pixel mobile layouts pass overflow checks with no browser
exceptions. The evidence modal width and export row wrapping were corrected
during this review. Detailed results: `one-hour-validation.json`.

The two scan/exfil context flags do not alter trained model inputs or model
thresholds. Active flows still do not receive partial-flow model inference;
all existing flow model evaluations continue to use closed flows. The new
60-second and source-history rules need representative held-out benign traffic
before claiming production calibration or detection quality. No IoT-23 or
external DGA data was rerun in this delivery.
