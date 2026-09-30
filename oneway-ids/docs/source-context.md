# Source-relative destination context

`ExfilDetector(source_context=True)` enables an opt-in, source-relative novelty
check. It uses only observed source and destination IPs and window indices. A
destination first observed from host A can still be new within the retained
history for host B. The default remains `False`, preserving the existing
fleet-global novelty behavior and regression output.

The helper retains at most 50,000 source/destination pairs and defaults to a
lookback of 8,640 windows (24 hours at the default 10-second window). Age
expiration means “not observed within the retained lookback,” never
“first-ever.” If capacity eviction makes a source's history incomplete, unknown
pairs for that source are not promoted as novel. Alert evidence names the
lookback, distinguishes source novelty from fleet novelty, and includes a
coverage snapshot. It does not imply coverage of traffic outside retained
history or traffic lost before ingestion.

This is a rules-only context option. It does not change trained model inputs or
thresholds. Evaluate it against hosts that share destinations, aged contacts,
and high-cardinality source histories before enabling it on a live feed.
