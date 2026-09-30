# Opt-in rolling scan context

`ScanDetector(sink, rolling_window=60)` adds an exact fan-out count over the
previous 60 seconds of observed windows. The existing per-window scan rule
continues unchanged. A separate `recon_rolling_vertical_scan` or
`recon_rolling_horizontal_scan` alert is emitted only when the rolling union
reaches the configured scan threshold and the current window is below it. This
avoids a second alert when the existing rule already reports a full scan in
that window.

The feature uses only the visible source IP, destination IP, destination port,
and packet-window times. It does not infer whether a remote port was open or a
connection succeeded. It keeps exact pairs, not a cardinality estimate. State
is capped at 4,096 sources and 2,048 pairs per source. Source or pair eviction
can undercount fan-out; alert evidence reports cumulative eviction counts and
the bounded endpoint sample reports whether it was truncated. Per-source pair
eviction counts cover the current retained source entry; aggregate pair and
source eviction counts persist for the detector lifetime. Eviction must not be
read as proof that no other scan pairs existed.

The default `rolling_window=0` disables the additional rule and preserves the
single-window alert path. The optional behavior is rules-only and does not
change the distribution used to train the scan model. Its 60-second horizon is
an initial policy to evaluate on held-out scan and benign discovery scenarios,
not a calibrated production threshold.
