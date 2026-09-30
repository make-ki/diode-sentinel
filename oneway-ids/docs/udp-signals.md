# One-way UDP burst signals

The sensor emits two UDP window signals from fields already visible in the
captured direction. `udp_burst_fanout` attributes traffic to a source when one
10-second window contains at least 100 UDP datagrams (10 packets/s) and at
least 20 distinct destination IP/port endpoints. `udp_target_burst` records a
shared target when one endpoint receives at least 1,000 visible datagrams from
at least 50 source IPs in the same window. Window length follows the configured
`WINDOW` value.

These are prototype thresholds, not calibrated production flood rates. They
are meant to make the trigger inspectable and avoid treating a small number of
ordinary DNS/QUIC datagrams as a burst. Tune them against representative benign
and attack captures for the deployment link before operational use. The alert
evidence records the measured packet and byte counts, rates, endpoint/source
cardinalities, and the threshold values that fired.

The source fan-out signal is the one-way substitute for UDP reflection source
port analysis. Both signals describe observed datagrams only. Neither claims a
response, reflection, amplification, or the intent of the sender. UDP-only
DDoS and recon alerts also carry `udp` in their alert flow ID rather than
assuming TCP.
