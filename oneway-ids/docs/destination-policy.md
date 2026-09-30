# Authorised transfer registry

Use `run.py --authorised-destinations registry.json`. The JSON list contains
operator-approved source and destination CIDRs, protocol, port, a descriptive
volume class, and a byte cap for each young transfer. The default is empty.
Malformed entries fail before capture. No DNS, ASN or cloud lookup is made;
a cloud provider address is not evidence that its tenant is trustworthy.

`examples/messy-authorised-destinations.json` is a **synthetic demo approval**,
not a deployable reputation feed. Its 2,000,000-byte cap covers the generator's
1,680,000-byte backup with some headroom. The label `volume_class` is descriptive;
`max_bytes` is the actual limit, applied to cumulative observed wire bytes for
that source/destination during the exfil detector's six-window young-transfer
period. This is not a daily quota or a persistent baseline.

On the synthetic MESSY replay, without policy, 10.0.0.6's backup emits a critical
exfil alert at 0.95. With this explicit approval it emits a medium alert at 0.6,
with `authorised_destination: true`, original confidence and matched registry
names. This is operator triage of a known false positive, not an improvement in
intrinsic detection accuracy. Other ports, transports, sources or destinations
are not covered. All observed endpoints for a pair must match. Exceeding the
cap or adding an unauthorised port can escalate while the transfer is still
eligible. The pre-transfer baseline is frozen after demotion so the upload
cannot hide a later violation by inflating its own baseline.

Demoted alerts do not enter fusion. Independent malicious signals remain
eligible. The policy applies to rules-tier exfil alerts only; optional ML model
alerts are not blanket-authorised. Default replay retains the byte-identical
46 rules / 68 ML fixtures. Exfil flow IDs now use observed protocol/port, or
wildcards when multiple endpoints contributed, instead of a hardcoded 8443.
