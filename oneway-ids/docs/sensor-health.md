# Sensor health

`run.py` atomically writes `run_stats.json` alongside its alert file. The
dashboard polls this sidecar and presents its `health` object. Live interface
and pcap-stream runs publish a heartbeat once per second, including while
waiting for traffic.

An active runner becomes **Idle** after five seconds without a received
packet. A running state with a heartbeat older than five seconds becomes
**Stale** in the dashboard: the process may have exited or stopped updating.
EOF is **Completed**; interruption or a duration limit is **Stopped**; source
setup/read failures are **Failed**. A missing health report is **Unknown**.
Terminal states remain visible after their heartbeat ages.

Last-packet time is the wall-clock receipt time, independent of the original
capture timestamps shown on alerts. Counts distinguish received, analyzed,
sampled-out and malformed frames. Kernel drops come from socket statistics;
pcap streams cannot report them and display **Unknown**. Offline replay reports
its analyzed count and completion; unavailable capture counters remain unknown.

The tests cover source failures, EOF, idle/stale states and injected socket-drop
counter deltas. A physical AF_PACKET interface run remains unverified.
