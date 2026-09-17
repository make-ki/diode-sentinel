"""Tests for the live capture path.

Covers the parts a root-less container CAN verify:
  - AF_PACKET plumbing helpers (kernel timestamps, drop counters, sampler)
  - idle-window closing (the behaviour that makes a silent link still score)
  - inventory persistence / warm start (restart without a cold-start storm)
  - live vs offline parity: the same pcap replayed through the live driver
    must produce the same alert distribution as the offline path
  - privilege failure produces a clear error, not a traceback

The raw socket itself cannot be exercised without CAP_NET_RAW, so the live
driver is tested through an injected source (FakeSource) and an injected clock.
Run: .venv/bin/python test_live.py
"""
import json
import os
import socket
import struct
import tempfile
import threading
import time
from datetime import datetime, timezone

import config
from config import PCAP_PATH, SIM_START
from detectors import AlertSink, TlsDetector, _iso
from live_source import (_parse_packet_stats, _cmsg_timestamp, SO_TIMESTAMP,
                         AfPacketSource, CaptureConfigError,
                         CapturePermissionError, PcapStreamSource,
                         list_interfaces)
from pipeline import WindowAggregator
from pcap_reader import iter_dpkt
from run import run_live, run_pipeline

failures = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        failures.append(name)


TMP = tempfile.mkdtemp(prefix="nids_live_")


def tmpf(name):
    return os.path.join(TMP, name)


def lines(path):
    with open(path) as fh:
        return [l for l in fh.read().splitlines() if l.strip()]


# --------------------------------------------------------------------------
# 1. AF_PACKET plumbing helpers
# --------------------------------------------------------------------------

ts64 = struct.pack("ll", 1757452800, 500000)
check("cmsg_timestamp_64bit",
      _cmsg_timestamp([(socket.SOL_SOCKET, SO_TIMESTAMP, ts64)]) == 1757452800.5)
check("cmsg_timestamp_32bit",
      _cmsg_timestamp([(socket.SOL_SOCKET, SO_TIMESTAMP,
                        struct.pack("ii", 1000, 250000))]) == 1000.25)
check("cmsg_timestamp_absent",
      _cmsg_timestamp([(socket.SOL_SOCKET, 4242, ts64)]) is None)
check("cmsg_timestamp_empty", _cmsg_timestamp([]) is None)

check("packet_stats_parse",
      _parse_packet_stats(struct.pack("II", 1234, 7)) == (1234, 7))
check("packet_stats_short", _parse_packet_stats(b"\x01\x02") == (0, 0))

# deterministic 1-in-N sampler: reproducible subsets, losses accounted
src = AfPacketSource("lo", sample=4)
kept = [src._keep() for _ in range(8)]
check("sampler_1_in_4", kept == [False, False, False, True] * 2, kept)
check("sampler_counts_skipped", src.sampled_out == 6, src.sampled_out)
src1 = AfPacketSource("lo", sample=1)
check("sampler_disabled_keeps_all", all(src1._keep() for _ in range(50)))

# dissect() shares the offline dpkt path: a crafted IP/TCP frame round-trips
from scapy.all import Ether, IP, TCP, UDP, ARP, ICMP         # noqa: E402
ETH = dict(src="aa:bb:cc:dd:ee:ff", dst="aa:bb:cc:dd:ee:00")
frame = bytes(Ether(**ETH) / IP(src="10.0.0.5", dst="1.2.3.4")
              / TCP(sport=1234, dport=443, flags="S"))
src.anchor = 0.0
pkt = src.dissect(frame, 100.0)
check("dissect_tcp_tuple", pkt == (100.0, "10.0.0.5", "1.2.3.4", "tcp", 1234,
                                   443, len(frame), True, b"", None, 0), pkt)
aframe = bytes(Ether(**ETH) / IP(src="10.0.0.6", dst="10.0.0.7")
               / UDP(sport=1, dport=9999))
check("dissect_non_tls_udp", src.dissect(aframe, 5.0)[:6]
      == (5.0, "10.0.0.6", "10.0.0.7", "udp", 1, 9999))
nonip = bytes(Ether(**ETH) / ARP())          # ARP: counted, never parsed
before = src.non_ipv4
check("dissect_non_ipv4_counted", src.dissect(nonip, 1.0) is None
      and src.non_ipv4 == before + 1, src.non_ipv4)

# IPv4 packets that are neither TCP nor UDP must be counted too, or the
# 'analysed' figure silently claims frames that were thrown away
other = bytes(Ether(**ETH) / IP(src="10.0.0.8", dst="10.0.0.9") / ICMP())
before_other = src.other_ip
check("dissect_icmp_counted", src.dissect(other, 2.0) is None
      and src.other_ip == before_other + 1, src.other_ip)

# the buckets must PARTITION the received frames: every frame lands in
# exactly one of analysed / sampled_out / non_ipv4 / other_ip / malformed,
# so the report can never imply that discarded traffic was analysed
src.seen, src.sampled_out, src.non_ipv4, src.other_ip, src.malformed = \
    10, 2, 1, 3, 1
snap = src.snapshot()
check("analysed_bucket_arithmetic", snap["analysed"] == 3, snap)
check("buckets_partition_frames",
      snap["analysed"] + snap["sampled_out"] + snap["non_ipv4"]
      + snap["other_ip"] + snap["malformed"] == snap["seen"], snap)

# --------------------------------------------------------------------------
# 2. idle windows must close without waiting for more traffic
# --------------------------------------------------------------------------

agg = WindowAggregator()
flushed = []
agg.register(lambda w: flushed.append(w["idx"]))
agg.feed(11.0, "10.0.0.1", "1.1.1.1", 443, 100, False)
agg.tick(15.0)                       # still inside the window
check("tick_does_not_close_live_window", agg.flushed == 0, agg.flushed)
agg.tick(21.0)                       # clock moved into the next window
check("tick_closes_completed_window", agg.flushed == 1 and flushed == [1],
      f"flushed={agg.flushed} idx={flushed}")
agg.tick(35.0)
check("tick_idempotent_after_close", agg.flushed == 1, agg.flushed)


class FakeSource:
    """Replays pre-built packets through the live driver, standing in for an
    AF_PACKET socket so the live path is testable without CAP_NET_RAW."""

    def __init__(self, packets, anchor=0.0, batch=64, stop_when_done=False):
        self.packets = list(packets)
        self.anchor = anchor
        self.batch = batch
        self.stop_when_done = stop_when_done
        self.i = 0
        self.seen = 0
        self.sampled_out = 0
        self.non_ipv4 = 0
        self.other_ip = 0
        self.malformed = 0
        self.sample = 1
        self.kernel_dropped = 0
        self._now = 0.0

    def drain(self, n=None):
        if self.stop_when_done and self.i >= len(self.packets):
            return None
        n = n or self.batch
        out = self.packets[self.i:self.i + n]
        self.i += len(out)
        self.seen += len(out)
        if out:
            self._now = max(p[0] for p in out)
        return out

    def now(self):
        return self._now

    def snapshot(self):
        return {"iface": "fake", "seen": self.seen, "analysed": self.seen,
                "sampled_out": 0, "non_ipv4": 0, "other_ip": 0,
                "malformed": self.malformed, "sample": self.sample,
                "kernel_dropped": 0}


# a volumetric burst finishing mid-window and then silence: 1200 SYNs from 600
# distinct (spoofed) sources inside window idx 1
flood = [(10.0 + i * 0.001, f"172.16.{i // 256}.{i % 256}", "203.0.113.10",
          "tcp", 40000 + (i % 1000), 443, 60, True, b"", None, i)
         for i in range(1200)]


def ddos_hits(by_class):
    return sum(v for k, v in by_class.items() if k.startswith("ddos"))


# Case A: the clock never advances past the last packet, so the completed
# window is never scored during the capture -- the verdict only surfaces at
# finish. This is the behaviour live mode exists to fix: on a real sensor the
# flood verdict must not wait for the next unrelated packet to arrive.
srcA = FakeSource(flood, batch=200)
seenA = []
statsA = run_live("fake0", AlertSink(tmpf("a.jsonl")), state_path=None,
                  source=srcA, clock=srcA.now, batch=200, idle_limit=2,
                  verbose=False, on_tick=lambda p: seenA.append(
                      len(p.sink.alerts)))
check("no_clock_advance_no_midrun_verdict", all(n == 0 for n in seenA), seenA)
check("verdict_still_reaches_finish", ddos_hits(statsA["by_class"]) == 1,
      dict(statsA["by_class"]))

# --duration must stop a live run early. Regression guard: this path
# referenced a clock variable that no longer existed after the refactor and
# would NameError the moment --duration was passed.
srcD = FakeSource(flood, batch=200)
statsD = run_live("fake0", AlertSink(tmpf("d.jsonl")), state_path=None,
                  source=srcD, clock=srcD.now, batch=200, idle_limit=2,
                  duration=10.5, verbose=False)
check("duration_stops_early", 0 < statsD["npkt"] < len(flood),
      f"{statsD['npkt']} of {len(flood)} packets before the cutoff")

# packet-time (archive) mode honours duration against record timestamps too
srcE = FakeSource(flood, batch=200, stop_when_done=True)
statsE = run_live("fake0", AlertSink(tmpf("e.jsonl")), state_path=None,
                  source=srcE, clock=srcE.now, batch=200, duration=10.5,
                  verbose=False)
check("duration_packet_time_mode", 0 < statsE["npkt"] < len(flood),
      statsE["npkt"])

# Case B: the link goes silent and the clock advances -> the completed window
# is scored during the capture, without waiting for the next packet
nowB = [0.0]
srcB = FakeSource(flood, batch=200)
seenB = []


def observeB(p):
    seenB.append((p.last_flush_t, len(p.sink.alerts)))
    if srcB.i >= len(srcB.packets):
        nowB[0] = max(nowB[0], 25.0)      # silence: the wall clock keeps going


statsB = run_live("fake0", AlertSink(tmpf("b.jsonl")), state_path=None,
                  source=srcB, clock=lambda: nowB[0], batch=200, idle_limit=3,
                  verbose=False, on_tick=observeB)
check("idle_clock_scores_window_midrun", seenB and seenB[-1][1] == 1, seenB)
check("idle_clock_same_verdict", ddos_hits(statsB["by_class"]) == 1,
      dict(statsB["by_class"]))

# --------------------------------------------------------------------------
# 3. live vs offline parity on the real synthetic capture
# --------------------------------------------------------------------------

packets = list(iter_dpkt(PCAP_PATH))
off_sink = AlertSink(tmpf("off.jsonl"))
off = run_pipeline(iter(packets), off_sink, tls_state_path=None)
live_sink = AlertSink(tmpf("livep.jsonl"), truncate=False)
# batch=1 keeps the simulated clock level with each frame's arrival, which is
# what a real capture does: kernel receive timestamps track the wall clock
# closely. Larger replay batches span seconds of stream time and would let the
# clock run ahead of the frames still being processed.
srcP = FakeSource(packets, stop_when_done=True)
live = run_live("fake0", live_sink, state_path=None, source=srcP,
                clock=srcP.now, batch=1, verbose=False)

check("parity_alert_classes", live["by_class"] == off["by_class"],
      f"live={dict(live['by_class'])} off={dict(off['by_class'])}")
check("parity_counts",
      (live["npkt"], live["flows"], live["windows"], live["ndns"],
       live["ntls"], live["n_alerts"], live["suppressed"])
      == (off["npkt"], off["flows"], off["windows"], off["ndns"],
          off["ntls"], off["n_alerts"], off["suppressed"]),
      f"live={live['n_alerts']} off={off['n_alerts']}")
check("parity_severity", live["by_sev"] == off["by_sev"])

# --------------------------------------------------------------------------
# 4. inventory persistence: a warm restart must not re-learn (or storm)
# --------------------------------------------------------------------------


class StubSink:
    def __init__(self):
        self.alerts, self.suppressed, self._subs = [], 0, []

    def subscribe(self, fn):
        self._subs.append(fn)

    def emit(self, t, src, dst, dport, proto, threat, conf, ev):
        rec = {"threat": threat, "conf": round(float(conf), 3), "src": src,
               "dst": dst, "t": t}
        self.alerts.append(rec)
        for fn in self._subs:
            fn(t, rec)

    def suppress(self, n=1):
        self.suppressed += n


stable = {"ja4": "t13d1806h2_a_b", "ja3": "x", "sni": "ok.com",
          "cipher_count": 18, "ext_count": 6, "version": "13"}
state = tmpf("state.json")

d1 = TlsDetector(StubSink(), state_path=state)
d1.on_hello(100, "10.0.0.50", "1.2.3.4", 443, stable)     # learned in baseline
check("persist_save", d1.save_state() is True
      and os.path.exists(state) and d1.inv_global == {"t13d1806h2_a_b"})

d2 = TlsDetector(StubSink(), state_path=state)
check("persist_load", d2.load_state() is True and d2.warm is True)
check("persist_inventory_restored", d2.inv_global == d1.inv_global
      and d2.inv_src["10.0.0.50"] == d1.inv_src["10.0.0.50"])
d2.on_hello(300, "10.0.0.50", "1.2.3.4", 443, stable)     # after restart
check("warm_start_no_storm", len(d2.sink.alerts) == 0, d2.sink.alerts)

cold = TlsDetector(StubSink())                            # no state file
cold.on_hello(300, "10.0.0.50", "1.2.3.4", 443, stable)
check("cold_start_would_storm", len(cold.sink.alerts) == 1
      and cold.sink.alerts[0]["conf"] == 0.80, cold.sink.alerts)

novel = {"ja4": "t13d1806h2_z_z", "ja3": "z", "sni": None,
         "cipher_count": 18, "ext_count": 6, "version": "13"}
d2.on_hello(310, "10.0.0.50", "1.2.3.4", 443, novel)
check("warm_start_still_detects_novel", len(d2.sink.alerts) == 1
      and d2.sink.alerts[0]["threat"] == "tls_novel_fingerprint",
      d2.sink.alerts)

# the live driver must checkpoint on its own, without an explicit save call
chk_state = tmpf("checkpoint.json")
chk_packets = [(0.0 + i * 0.05, f"10.0.0.{20 + i % 5}", "93.184.216.1", "tcp",
                40000 + (i % 500), 443, 200, i % 50 == 0, b"\x16\x03\x01", None,
                i * 100) for i in range(600)]
chk_src = FakeSource(chk_packets, stop_when_done=True)
run_live("fake0", AlertSink(tmpf("chk.jsonl"), truncate=False),
         state_path=chk_state, source=chk_src, clock=chk_src.now, batch=1,
         verbose=False)
check("live_driver_checkpoints_state", os.path.exists(chk_state),
      chk_state)
if os.path.exists(chk_state):
    with open(chk_state) as fh:
        saved = json.load(fh)
    check("checkpoint_has_versioned_inventory", saved.get("version") == 1
          and isinstance(saved.get("inv_global"), list))

# corrupted / missing state must degrade to a cold start, not crash
with open(tmpf("broken.json"), "w") as fh:
    fh.write("{not json")
d3 = TlsDetector(StubSink(), state_path=tmpf("broken.json"))
check("corrupt_state_degrades", d3.load_state() is False and d3.warm is False)
d4 = TlsDetector(StubSink(), state_path=tmpf("does_not_exist.json"))
check("missing_state_degrades", d4.load_state() is False and d4.warm is False)

# --------------------------------------------------------------------------
# 5. time anchoring
# --------------------------------------------------------------------------

config.set_time_anchor(SIM_START)
base = _iso(0.0)
config.set_time_anchor(SIM_START + 3600)
check("anchor_shifts_timestamps", _iso(0.0) != base
      and _iso(0.0).startswith("2025-09-09T22:20:00"), _iso(0.0))
check("anchor_preserves_relative", _iso(10.0).startswith("2025-09-09T22:20:10"),
      _iso(10.0))
config.set_time_anchor(SIM_START)
check("anchor_restored", _iso(0.0) == base)

# A FRACTIONAL anchor must render the true wall time. Deriving the
# milliseconds from `t % 1` while taking the seconds from TIME_ANCHOR + t
# disagrees the moment the anchor is not a whole number -- which is exactly
# what a live capture produces (anchor = time.time()).
frac = SIM_START + 0.053087
config.set_time_anchor(frac)
got = _iso(0.0)
want = (datetime.fromtimestamp(frac, tz=timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%S.") + "053Z")
check("fractional_anchor_shifts_millis_only", got == want, f"{got} vs {want}")
check("fractional_anchor_seconds_consistent",
      _iso(10.0) == want.replace(":00.053Z", ":10.053Z"), _iso(10.0))
config.set_time_anchor(SIM_START)
check("integer_anchor_millis_unchanged", _iso(30.0)
      .endswith(":30.000Z"), _iso(30.0))

# --------------------------------------------------------------------------
# 6. sink append mode (live must not truncate the dashboard's feed)
# --------------------------------------------------------------------------

apath = tmpf("app.jsonl")
AlertSink(apath, truncate=True).emit(0.0, "a", "b", 443, "tcp", "t", 0.9, {})
n1 = len(lines(apath))
AlertSink(apath, truncate=False).emit(1.0, "a", "b", 443, "tcp", "t", 0.9, {})
check("append_mode_keeps_history", len(lines(apath)) == n1 + 1, n1)
AlertSink(apath, truncate=True)
check("truncate_mode_resets", len(lines(apath)) == 0)

# --------------------------------------------------------------------------
# 7. privilege failure is reported, not thrown as a bare traceback
# --------------------------------------------------------------------------


def raw_permitted():
    try:
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                          socket.htons(3))
        s.close()
        return True
    except (PermissionError, OSError):
        return False


# a bad interface name must fail fast, before any privileged call, with the
# candidate list attached -- this path is testable WITHOUT privileges
bad = AfPacketSource("definitely-not-an-interface")
try:
    bad.open()
    check("bad_iface_rejected", False, "open() unexpectedly succeeded")
except CaptureConfigError as e:
    check("bad_iface_rejected", "definitely-not-an-interface" in str(e)
          and "Available interfaces" in str(e))
except Exception as e:                                      # noqa: BLE001
    check("bad_iface_rejected", False, f"wrong type {type(e).__name__}: {e}")

names = list_interfaces()
check("list_interfaces_nonempty", isinstance(names, list) and len(names) > 0,
      names)
check("list_interfaces_has_loopback", "lo" in names, names)

if raw_permitted():
    print("[SKIP] raw capture permitted here -- cannot test the denial path")
else:
    try:
        AfPacketSource("lo").open()
        check("permission_error_raised", False, "open() unexpectedly succeeded")
    except CapturePermissionError as e:
        check("permission_error_is_clear",
              "CAP_NET_RAW" in str(e) and "setcap" in str(e))
    except Exception as e:                                  # noqa: BLE001
        check("permission_error_raised", False, f"{type(e).__name__}: {e}")

# --------------------------------------------------------------------------
# 8. pcap-stream source: the unprivileged ingest path
# --------------------------------------------------------------------------


def pcap_bytes(records, endian="<", div=1e6):
    """Build a classic pcap stream from (timestamp, frame) pairs."""
    magic = {("<", 1e6): b"\xd4\xc3\xb2\xa1", (">", 1e6): b"\xa1\xb2\xc3\xd4",
             ("<", 1e9): b"\x4d\x3c\xb2\xa1", (">", 1e9): b"\xa1\xb2\x3c\x4d"}
    out = bytearray(magic[(endian, div)]
                    + struct.pack(endian + "HHiIII", 2, 4, 0, 0, 65535, 1))
    for ts, frame in records:
        sec = int(ts)
        frac = int(round((ts - sec) * div))
        out += struct.pack(endian + "IIII", sec, frac, len(frame), len(frame))
        out += frame
    return bytes(out)


samples = [
    (SIM_START + 1.5, bytes(Ether(**ETH) / IP(src="10.0.0.1", dst="1.2.3.4")
                            / TCP(sport=1000, dport=443, flags="S"))),
    (SIM_START + 2.5, bytes(Ether(**ETH) / IP(src="10.0.0.2", dst="5.6.7.8")
                            / UDP(sport=5353, dport=53))),
]


def drain_all(src):
    out = []
    while True:
        batch = src.drain()
        if batch is None:
            return out
        out.extend(batch)


spath = tmpf("stream.pcap")
with open(spath, "wb") as fh:
    fh.write(pcap_bytes(samples))
st = PcapStreamSource(spath)
got = drain_all(st)
st.close()
check("stream_packet_count", len(got) == 2, len(got))
# the anchor is the whole second CONTAINING the first record, so t is 0.5
check("stream_anchor_floored_to_second",
      st.anchor == float(int(samples[0][0]))
      and st.anchor == st.anchor // 1, st.anchor)
check("stream_eof_recorded", st.eof is True)
check("stream_relative_times", [round(p[0], 3) for p in got] == [0.5, 1.5],
      [round(p[0], 3) for p in got])
check("stream_tuple_matches_offline_schema",
      got[0][1:6] == ("10.0.0.1", "1.2.3.4", "tcp", 1000, 443)
      and got[0][7] is True, got[0])

# endianness and nanosecond-resolution variants
for label, endian, div in (("bigendian", ">", 1e6),
                           ("nanosecond", "<", 1e9)):
    p = tmpf(f"{label}.pcap")
    with open(p, "wb") as fh:
        fh.write(pcap_bytes(samples, endian=endian, div=div))
    s = PcapStreamSource(p)
    g = drain_all(s)
    s.close()
    check(f"stream_magic_{label}", len(g) == 2
          and round(g[0][0], 3) == 0.5, [round(x[0], 3) for x in g])

# truncated final record: emit the complete ones, wait for the rest, no bogus packet
raw_full = pcap_bytes(samples)
cut = 24 + 16 + len(samples[0][1]) + 10        # global hdr + rec1 + partial rec2
part = tmpf("partial.pcap")
with open(part, "wb") as fh:
    fh.write(raw_full[:cut])
s = PcapStreamSource(part)
g = drain_all(s)
s.close()
check("stream_partial_record_not_guessed", len(g) == 1, len(g))
check("stream_partial_reported_seen", s.seen == 1, s.seen)

# hostile inputs must fail with a clear message, never a traceback
garbage = tmpf("garbage.pcap")
with open(garbage, "wb") as fh:
    fh.write(b"NOPE" + b"\x00" * 64)
try:
    PcapStreamSource(garbage, wait=0.3).open()
    check("stream_garbage_rejected", False, "open() unexpectedly succeeded")
except CaptureConfigError as e:
    check("stream_garbage_rejected", "not a pcap stream" in str(e))

ng = tmpf("pcapng.pcap")
with open(ng, "wb") as fh:
    fh.write(b"\x0a\x0d\x0d\x0a" + b"\x00" * 64)
try:
    PcapStreamSource(ng, wait=0.3).open()
    check("stream_pcapng_rejected", False, "open() unexpectedly succeeded")
except CaptureConfigError as e:
    check("stream_pcapng_rejected", "-P" in str(e), str(e)[:60])

try:
    PcapStreamSource(tmpf("absent.pcap")).open()
    check("stream_missing_rejected", False, "open() unexpectedly succeeded")
except CaptureConfigError as e:
    check("stream_missing_rejected", "no capture stream" in str(e))

# --- a real FIFO, written in chunks by another thread while we read ---
fifo = tmpf("feed.fifo")
os.mkfifo(fifo)
raw_traffic = open(PCAP_PATH, "rb").read()


def _writer():
    with open(fifo, "wb") as fh:
        for i in range(0, len(raw_traffic), 16384):
            fh.write(raw_traffic[i:i + 16384])
            fh.flush()
            time.sleep(0.005)


th = threading.Thread(target=_writer, daemon=True)
th.start()
src_fifo = PcapStreamSource(fifo, anchor=SIM_START)   # preset: no wait needed
fifo_sink = AlertSink(tmpf("fifo.jsonl"), truncate=False)
fifo_res = run_live("fifo", fifo_sink, state_path=None, source=src_fifo,
                    verbose=False)
th.join(timeout=5)
check("fifo_stream_eof", src_fifo.eof is True)
check("fifo_path_parity_with_offline", fifo_res["by_class"] == off["by_class"],
      f"fifo={dict(fifo_res['by_class'])}")
check("fifo_path_counts",
      (fifo_res["npkt"], fifo_res["flows"], fifo_res["windows"])
      == (off["npkt"], off["flows"], off["windows"]),
      f"{fifo_res['npkt']} vs {off['npkt']}")

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    raise SystemExit(1)
print("all live-capture tests passed")
