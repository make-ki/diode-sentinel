# Reproducing the IoT-23 host-level validation

`training/score_iot23.py` replays an existing local capture through the shipped
rules pipeline and compares alerted source hosts with labels in a Zeek
`conn.log`. It does not download IoT-23, mount a drive, change detector
thresholds, or claim to reproduce the historical scoring run.

```sh
source .env-ml
.venv/bin/python training/score_iot23.py /path/to/capture.pcap /path/to/conn.log
```

The conn log must use Zeek's tab-separated `#fields` format and include
`id.orig_h`, `id.orig_p`, `id.resp_h`, `id.resp_p`, `proto`, and at least one
recognized primary `label` row. `Malicious`, `Attack`, and `Infected` are
recognized positive labels; `Benign`, `Normal`, and `Clean` are recognized
negative labels. IoT-23's combined final suffix form (`label   detailed-label`)
is parsed too, but the detailed label alone never determines class. Unknown or
missing primary labels are excluded from ground truth; if the file has no
recognized labels, scoring stops. Hosts with any malicious row are treated as
malicious if their rows conflict. Normalize other label conventions before
scoring.

Every conn.log row contributes an originator-to-responder 5-tuple. The scorer
feeds a pcap packet only if source address/port, destination address/port, and
protocol match that tuple exactly. Reverse-direction packets are discarded,
even if present in the pcap. If conn.log contains both orientations of the
same 5-tuple, packets in that ambiguous pair are discarded. A zero accepted
packet count stops with an error; verify that the capture and conn.log belong
together before interpreting metrics.

The JSON reports per-host alert presence, TP/FP/FN/TN host counts, host-level
precision and recall, alert classes, and replay counts. Multiple alerts on one
host count once for host metrics. Unlabeled hosts are excluded from the metric;
their alerts still appear in `alerted_hosts`, so precision/recall must be
interpreted against the labeled-host population. This is host-level scoring,
not flow-level precision/recall, and a host with conflicting labels is
positive by policy. The JSON includes SHA-256 hashes of the pcap and conn.log so
the exact local inputs can be identified later.

The previous Capture-8-1, Capture-1-1, Capture-42-1, and Honeypot-4-1 figures
remain historical measurements. Their exact input files, original scorer,
and scoring-time artifacts are not available here, so this script does not
assert that its results will equal those figures. Reproduction requires the
matching local pcap and conn.log from the same scenario and a documented label
schema.
