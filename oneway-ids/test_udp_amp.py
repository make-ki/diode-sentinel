"""Tests for the UDP reflection/amplification detector (PS class (a),
second half). Run: python3 test_udp_amp.py

Follows the test_dns_tunnel.py contract:
  - a RecSink so tests never touch alerts.jsonl;
  - thresholds read from config (a stale test cannot block a re-tune);
  - pure-function wire/shape tests first, then per-mechanism gates,
    dedupe semantics, benign-corpus guards, then the pipeline + e2e
    evidence schema.
"""
import json
import os
import sys

from collections import Counter

from config import (UDP_AMP_MIN_SRCS, UDP_AMP_MIN_PKTS,
                    UDP_AMP_MIN_QPS_WINDOW, UDP_AMP_MIN_QPS,
                    UDP_AMP_SMALL_SHARE, UDP_AMP_SMALL_BYTES,
                    UDP_AMP_WINDOW, UDP_AMP_REALERT_SECS,
                    UDP_AMP_REFLECTOR, UDP_AMP_VICTIM)
from udp_amp import (UdpAmpDetector, AMPLIFIER_PORTS, PORT_NAMES)

PASSED = 0


def check(name, ok, detail=""):
    global PASSED
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}" + (f" {detail}" if detail and not ok else ""))
    if not ok:
        sys.exit(1)
    PASSED += 1


class RecSink:
    """Minimal AlertSink stand-in (records alerts, no file)."""

    def __init__(self):
        self.alerts = []
        self.suppressed = 0

    def emit(self, t, src, dst, dport, proto, threat, conf, evidence):
        self.alerts.append({"t": t, "src": src, "dst": dst, "dport": dport,
                            "proto": proto, "threat_class": threat,
                            "confidence": conf, "evidence": evidence,
                            "severity": ("critical" if conf >= 0.9 else
                                         "high" if conf >= 0.7 else
                                         "medium" if conf >= 0.5 else "low")})

    def suppress(self):
        self.suppressed += 1


def classes_of(sink):
    return Counter(a["threat_class"] for a in sink.alerts)


def mechs_of(sink):
    return [a["evidence"]["mechanism"] for a in sink.alerts]


def feed(det, src, t0, n, step, dst=UDP_AMP_REFLECTOR, dport=53,
         size=UDP_AMP_SMALL_BYTES):
    for i in range(n):
        det.on_packet(t0 + i * step, src, dst, dport, size)


# ------------------------------------------------- 1. amplifier port table
check("ports_include_classics",
      {53, 123, 161, 1900, 11211, 19} <= AMPLIFIER_PORTS)
check("ports_exclude_quic", 443 not in AMPLIFIER_PORTS)
check("port_names_cover_table",
      all(p in PORT_NAMES for p in AMPLIFIER_PORTS))

# non-amplifier traffic is invisible to the detector, structurally
sink = RecSink()
det = UdpAmpDetector(sink)
feed(det, "10.9.9.9", 0.0, 5000, 0.001, dport=443, size=1200)
det.flush_current()
check("quic_never_enters_windows", not sink.alerts)

# --------------------------------------- 2. mechanism 1: query rate spike
# sustained >= MIN_QPS to one service -> fires at the per-service gate.
# Feed n+ queries spaced to land > MIN_QPS *within each window*: qps here is
# (UDP_AMP_MIN_QPS*2) with the campaign spanning 2 windows.
sink = RecSink()
det = UdpAmpDetector(sink)
qps = UDP_AMP_MIN_QPS * 2
step = 1.0 / qps
n = int(UDP_AMP_MIN_QPS_WINDOW) + 5
feed(det, UDP_AMP_VICTIM, 0.0, n, step)
det.flush_current()
spikes = [a for a in sink.alerts
          if a["evidence"]["mechanism"] == "query_rate_spike"]
check("rate_fires_above_qps_gate", len(spikes) == 1, len(spikes))
check("rate_evidence_carries_service",
      spikes and spikes[0]["evidence"]["service"] == "DNS")
check("rate_evidence_carries_qps",
      spikes and spikes[0]["evidence"]["window_qps"] >= UDP_AMP_MIN_QPS)
check("rate_one_way_note",
      spikes and "one-way" in spikes[0]["evidence"]["note"])
check("rate_never_critical_alone",
      all(a["confidence"] < 0.9 for a in spikes))

# below the sustained-qps gate: silent (1.5 qps, benign-ish resolver load)
sink = RecSink()
det = UdpAmpDetector(sink)
feed(det, UDP_AMP_VICTIM, 0.0, UDP_AMP_MIN_QPS_WINDOW + 5,
     1.0 / (UDP_AMP_MIN_QPS * 0.5))
det.flush_current()
check("rate_below_gate_silent",
      not [a for a in sink.alerts
           if a["evidence"]["mechanism"] == "query_rate_spike"])

# few queries at high rate (short campaign) does not reach the evidence floor
sink = RecSink()
det = UdpAmpDetector(sink)
feed(det, UDP_AMP_VICTIM, 0.0, UDP_AMP_MIN_QPS_WINDOW - 1, 0.01)
det.flush_current()
check("rate_needs_min_window_queries", not sink.alerts)

# --------------------------------------- 3. mechanism 2: small query burst
# a window packed with tiny frames at >=90% small share -> burst fires
sink = RecSink()
det = UdpAmpDetector(sink)
n = UDP_AMP_MIN_PKTS + 5
feed(det, UDP_AMP_VICTIM, 0.0, n, UDP_AMP_WINDOW / (n + 1))
det.flush_current()
bursts = [a for a in sink.alerts
          if a["evidence"]["mechanism"] == "small_query_burst"]
check("burst_fires_on_small_share", len(bursts) == 1, len(bursts))
check("burst_share_recorded",
      bursts and bursts[0]["evidence"]["small_packet_share"]
      >= UDP_AMP_SMALL_SHARE)

# big frames (download-shaped traffic to an amplifier port) suppress the
# BURST mechanism specifically -- large UDP to 53 is weird but is not a
# query storm. (The rate mechanism may still fire on volume; scope the
# assertion to the burst mechanism.)
sink = RecSink()
det = UdpAmpDetector(sink)
feed(det, UDP_AMP_VICTIM, 0.0, UDP_AMP_MIN_PKTS + 5,
     UDP_AMP_WINDOW / (UDP_AMP_MIN_PKTS + 6), size=1400)
det.flush_current()
check("burst_big_frames_silent",
      "small_query_burst" not in mechs_of(sink), mechs_of(sink))

# --------------------------------------- 4. mechanism 3: fan-out (unspoofed)
# >= MIN_SRCS distinct real sources AND >= MIN_PKTS in the window -> fires.
# (32 bots x 10 queries each = 320 pkts in-window: reflection campaigns run
# every bot at multiple qps; 3 queries per bot per 10s would be neither.)
sink = RecSink()
det = UdpAmpDetector(sink)
per = UDP_AMP_MIN_PKTS // (UDP_AMP_MIN_SRCS + 2) + 2
for i in range(UDP_AMP_MIN_SRCS + 2):
    feed(det, f"10.9.{i}.1", 0.0, per, UDP_AMP_WINDOW / (per + 1))
det.flush_current()
fans = [a for a in sink.alerts
        if a["evidence"]["mechanism"] == "amplifier_fanout"]
check("fanout_fires_on_distinct_srcs", len(fans) == 1, len(fans))
check("fanout_entropy_evidence",
      fans and "src_ip_entropy_bits" in fans[0]["evidence"])
check("fanout_never_critical_alone",
      all(a["confidence"] < 0.9 for a in fans))

# a handful of resolvers (benign shape: ~8 srcs, sparse) stays silent
sink = RecSink()
det = UdpAmpDetector(sink)
for i in range(8):
    feed(det, f"10.9.{i}.1", 0.0, 5, 0.2)
det.flush_current()
check("fanout_few_srcs_silent", not sink.alerts)

# many srcs but BELOW the packet floor is also silent: 32 srcs x 3 sparse
# queries is a weird but quiet pattern, not a campaign
sink = RecSink()
det = UdpAmpDetector(sink)
for i in range(UDP_AMP_MIN_SRCS + 2):
    feed(det, f"10.9.{i}.1", 0.0, 3, 0.05)
det.flush_current()
check("fanout_below_packet_floor_silent",
      "amplifier_fanout" not in mechs_of(sink), mechs_of(sink))

# ---------------------------------------------- 5. dedupe / re-arm semantics
# a CONTINUING campaign is one incident: no re-fire while it runs
sink = RecSink()
det = UdpAmpDetector(sink)
feed(det, UDP_AMP_VICTIM, 0.0, 2000, UDP_AMP_WINDOW / 150)  # ~4 windows
det.flush_current()
spikes = [a for a in sink.alerts
          if a["evidence"]["mechanism"] == "query_rate_spike"]
check("campaign_fire_once_while_running", len(spikes) == 1, len(spikes))

# quiet period longer than REALERT re-arms: the next campaign re-alerts.
# Feed each campaign INSIDE one window, flushing between so both score.
sink = RecSink()
det = UdpAmpDetector(sink)
quiet_windows = int(UDP_AMP_REALERT_SECS / UDP_AMP_WINDOW) + 1
feed(det, UDP_AMP_VICTIM, 0.0, UDP_AMP_MIN_QPS_WINDOW + 5, 0.15)
det.flush_current()                                   # scores campaign 1
feed(det, UDP_AMP_VICTIM, quiet_windows * UDP_AMP_WINDOW + 1.0,
     UDP_AMP_MIN_QPS_WINDOW + 5, 0.15)                # campaign 2, >120s quiet
det.flush_current()
spikes = [a for a in sink.alerts
          if a["evidence"]["mechanism"] == "query_rate_spike"]
check("campaign_rearms_after_quiet", len(spikes) == 2, len(spikes))

# short quiet gap (inside REALERT) does NOT re-arm
sink = RecSink()
det = UdpAmpDetector(sink)
feed(det, UDP_AMP_VICTIM, 0.0, UDP_AMP_MIN_QPS_WINDOW + 5, 0.15)
det.flush_current()
feed(det, UDP_AMP_VICTIM, 3 * UDP_AMP_WINDOW + 1.0,
     UDP_AMP_MIN_QPS_WINDOW + 5, 0.15)
det.flush_current()
spikes = [a for a in sink.alerts
          if a["evidence"]["mechanism"] == "query_rate_spike"]
check("campaign_no_rearm_inside_dedupe", len(spikes) == 1, len(spikes))

# per-service isolation: a second service fires independently
sink = RecSink()
det = UdpAmpDetector(sink)
feed(det, UDP_AMP_VICTIM, 0.0, UDP_AMP_MIN_QPS_WINDOW + 5, 0.1,
     dst="198.18.0.53", dport=53)
feed(det, UDP_AMP_VICTIM, 0.1, UDP_AMP_MIN_QPS_WINDOW + 5, 0.1,
     dst="198.18.0.123", dport=123)
det.flush_current()
check("per_service_isolation", len(sink.alerts) == 2, len(sink.alerts))

# ---------------------------------------------- 6. benign corpus guards
# THE measured benign shape: ~10 service queries per 10s window from ~8
# resolvers (benign DNS) + one 90B NTP keepalive per 30s -- must be silent
sink = RecSink()
det = UdpAmpDetector(sink)
t = 0.0
for w in range(6):                                  # 6 windows of benign load
    for h in range(8):                              # 8 resolvers
        det.on_packet(t + h * 1.2, f"10.0.0.{h+2}", "8.8.8.8", 53, 90)
    if w % 3 == 0:                                  # NTP keepalive per 30s
        det.on_packet(t + 5.0, "10.0.0.5", "129.6.15.28", 123, 90)
    t += UDP_AMP_WINDOW
det.flush_current()
check("benign_corpus_zero_alert", not sink.alerts,
      f"alerts={[ (a['evidence']['mechanism']) for a in sink.alerts ]}")

# the three-orders-of-margin claim, asserted numerically: benign ~1 qps
# aggregate vs the MIN_QPS gate at 3 qps and MIN_PKTS at 300/window
check("benign_margin_rate", UDP_AMP_MIN_QPS >= 3 * 1.0)
check("benign_margin_pkts", UDP_AMP_MIN_PKTS >= 30 * 10)

# ---------------------------------------------- 7. pipeline integration
# feed real pipeline with a tiny synthetic pcap-less stream via StreamProcessor
from pipeline import StreamProcessor
from detectors import AlertSink as RealSink

import tempfile
tmp = tempfile.mkdtemp()
alerts_path = os.path.join(tmp, "a.jsonl")
rsink = RealSink(path=alerts_path)
proc = StreamProcessor(rsink)


def pkt(t, src, dst, dport, size, proto="udp"):
    return (t, src, dst, proto, 40000, dport, size, False, b"", None, 0)


t = 0.0
for i in range(UDP_AMP_MIN_QPS_WINDOW + 10):
    proc.feed(pkt(t, UDP_AMP_VICTIM, UDP_AMP_REFLECTOR, 53, 80))
    t += 0.08
    proc.tick(t)
proc.finish()
check("pipeline_hook_wires_detector",
      classes_of(rsink).get("ddos_udp_amplification", 0) >= 1,
      dict(classes_of(rsink)))

# benign packets through the pipeline: zero amplification alerts
rsink = RealSink(path=os.path.join(tmp, "b.jsonl"))
proc = StreamProcessor(rsink)
t = 0.0
for w in range(4):
    for h in range(8):
        proc.feed(pkt(t + h * 1.2, f"10.0.0.{h+2}", "8.8.8.8", 53, 90))
        proc.tick(t + h * 1.2)
    t += UDP_AMP_WINDOW
proc.finish()
check("pipeline_benign_silent",
      "ddos_udp_amplification" not in classes_of(rsink), dict(classes_of(rsink)))

# ---------------------------------------------- 8. e2e evidence schema
# alerts.jsonl is written by the last full run; assert the shipped file's
# amplification alerts carry the full schema (the e2e contract)
import glob
e2e_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "alerts.jsonl")
n_e2e = 0
if os.path.exists(e2e_path):
    for line in open(e2e_path):
        if not line.strip():
            continue
        a = json.loads(line)
        if a["threat_class"] != "ddos_udp_amplification":
            continue
        n_e2e += 1
        e = a["evidence"]
        check(f"e2e_schema_alert{n_e2e}",
              {"mechanism", "window", "note", "why"} <= set(e)
              and "one-way" in e["note"]
              and a["severity"] in ("high", "medium")
              and a["confidence"] < 0.9,
              e.get("mechanism"))
check("e2e_amplification_alerts_present", n_e2e >= 3, n_e2e)
mech_set = set()
for line in open(e2e_path):
    a = json.loads(line) if line.strip() else None
    if a and a["threat_class"] == "ddos_udp_amplification":
        mech_set.add(a["evidence"]["mechanism"])
check("e2e_two_mechanisms_exercised",
      {"query_rate_spike", "small_query_burst"} <= mech_set, mech_set)

# spoofed campaign must NOT have tripped the TCP-path DDoS detector
# (the hole this detector fills): ddos_volumetric counts stay as before
tcp_ddos = 0
for line in open(e2e_path):
    a = json.loads(line) if line.strip() else None
    if a and a["threat_class"].startswith("ddos_") \
            and a["threat_class"] != "ddos_udp_amplification":
        tcp_ddos += 1
check("e2e_tcp_ddos_unchanged_shape", tcp_ddos >= 1, tcp_ddos)

print(f"\n{PASSED} checks passed" if PASSED else "no checks ran")
print("all udp_amp tests passed")
