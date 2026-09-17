"""Tests for the DNS tunnelling detector (PS class c, record-type/length
half). Run: python3 test_dns_tunnel.py

Covers, in the repo's flat-assertion style:
  1. wire parser: qtype extraction, response rejection, truncation,
     compression pointers, multi-label names
  2. looks_encoded(): the measured benign corpus must NOT encode
     (11-char CDN labels, DGA 14-char labels, English compounds, hex),
     tunnel labels MUST
  3. mechanism 1: encoded streak, quorum semantics, benign-label reset,
     dedupe window
  4. mechanism 2: data-record ratio needs BOTH ratio and sustained qps
  5. mechanism 3: single-zone rate anomaly, multi-zone split must not fire
  6. benign traffic guards: real-world-ish DNS (A lookups, sparse TXT
     service discovery, CDN labels, DGA queries) -- zero alerts
  7. streaming integration: the real pipeline over synthetic packets emits
     dns_tunneling, on the tunnel host only
"""
import base64
import time
from collections import Counter

from config import (DNS_TUNNEL_MIN_QTYPE_RATIO, DNS_TUNNEL_MIN_QPS,
                    DNS_TUNNEL_MIN_STREAK, DNS_TUNNEL_LABEL_MIN_LEN,
                    DNS_TUNNEL_REALERT_SECS, DNS_TUNNEL_QPS_WINDOW)
import detectors as _det
from detectors import AlertSink
from dns_tunnel import (DnsTunnelDetector, parse_qtype, looks_encoded,
                        shannon_entropy, DATA_QTYPES)

failures = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        failures.append(name)


def dns_query_bytes(qname, qtype=16, response=False):
    """Minimal DNS query wire format for parser tests."""
    header = bytes([0x12, 0x34, 0x01, 0x00, 0x00, 0x01, 0, 0, 0, 0, 0, 0])
    if response:
        header = bytes([0x12, 0x34, 0x81, 0x80, 0x00, 0x01, 0, 0, 0, 0, 0, 0])
    q = b""
    for label in qname.rstrip(".").split("."):
        q += bytes([len(label)]) + label.encode()
    q += b"\x00" + qtype.to_bytes(2, "big") + b"\x00\x01"
    return header + q


# ---------------------------------------------------------------- 1. parser --

m = parse_qtype(dns_query_bytes("abcd1234.tunnel.example.com", qtype=16))
check("parse_basic", m is not None and m[0] == 16, m)
check("parse_labels", m and m[1] == ["abcd1234", "tunnel", "example", "com"], m[1] if m else None)

m = parse_qtype(dns_query_bytes("abc.def", qtype=1))
check("parse_qtype_A", m and m[0] == 1)

m = parse_qtype(dns_query_bytes("x.y", qtype=10, response=True))
check("response_rejected", m is None)

check("short_rejected", parse_qtype(b"\x00" * 10) is None)
check("empty_rejected", parse_qtype(b"") is None)
check("qdcount0_rejected", parse_qtype(dns_query_bytes("a.b")[:5] + b"\x00" * 14) is None)

# truncated inside a label -> None, never an exception
trunc = dns_query_bytes("averylonglabel.com")[:18]
check("truncated_label_rejected", parse_qtype(trunc) is None)
# truncated before qtype -> None
head = dns_query_bytes("abc.example.com")
check("truncated_qtype_rejected", parse_qtype(head[:-2]) is None)
# compression pointer inside the question (never legal) -> rejected
ptr = dns_query_bytes("ab.cd")[:14] + b"\xc0\x0c" + b"\x00\x10\x00\x01"
check("compression_pointer_rejected", parse_qtype(ptr) is None)
# uppercase labels normalize to lowercase
m = parse_qtype(dns_query_bytes("AbC.Example.COM"))
check("labels_lowercased", m and m[1] == ["abc", "example", "com"])

# ------------------------------------------------- 2. looks_encoded corpus --

# The measured benign corpus of THIS repo must all be rejected.
benign_corpus = [
    "edgecache01", "lbuseast5", "nodepool07", "assetsx91",   # CDN labels
    "8yuxczaumapqpp", "k3jx02mdqazxvt",                       # DGA-length labels
    "helpdeskupdate", "drivercenter",                         # dictionary DGA
    "stackoverflo", "wikipediaread",                          # compounds
    "0123456789abcdef0123",                                   # long hex (low ent)
    "aaaaaaaabbbbccccdddd",                                   # repetitive
]
for label in benign_corpus:
    check(f"benign_not_encoded:{label[:16]}", not looks_encoded(label),
          f"ent={shannon_entropy(Counter(label)):.2f}")

# Tunnel labels: base32 of 24 random bytes (24 chars) MUST encode.
tunnel_labels = []
for _ in range(30):
    tunnel_labels.append(base64.b32encode(bytes(range(24))).decode().lower())
check("tunnel_label_encoded", all(looks_encoded(l) for l in tunnel_labels),
      tunnel_labels[0])

# base64-style payload (mixed alphabet, high entropy) must also encode
b64ish = base64.b64encode(
    bytes([37, 149, 91, 203, 17, 88, 222, 66, 131, 240, 5, 199, 74, 158, 31])
).decode().rstrip("=").lower()
check("b64ish_encoded", looks_encoded(b64ish),
      f"{b64ish} ent={shannon_entropy(Counter(b64ish)):.2f}")
# below the length floor: never, however dense
check("short_dense_not_encoded", not looks_encoded("abcdefghijklmnopqrs"),
      "19 chars")

# ------------------------------------------------- detector scaffolding -----

class RecSink(AlertSink):
    """In-memory sink that does not touch the alerts file. Carries the same
    record schema as production (severity included) so pipeline.finish()'s
    Counter aggregation works unchanged."""

    def __init__(self):
        self.alerts = []
        self.suppressed = 0
        self._subs = []

    def emit(self, t, src, dst, dport, proto, threat, confidence, evidence):
        self.alerts.append(dict(timestamp=t, src=src, dst=dst, dport=dport,
                                proto=proto, threat_class=threat,
                                confidence=round(float(confidence), 3),
                                severity=_det._severity(confidence),
                                evidence=evidence))


def enc_label(seed=0):
    rng = _Rand(seed)
    return base64.b32encode(bytes(rng.next() % 256 for _ in range(24))).decode().lower()


class _Rand:
    """Small xorshift so encoded labels differ from each other (a single
    static seed repeats one label; identical labels would under-test the
    streak logic, which is built to consume a series of DISTINCT labels)."""

    def __init__(self, seed=0):
        self.s = seed * 2654435761 % 0xFFFFFFFF or 2463534242

    def next(self):
        s = self.s
        s ^= (s << 13) & 0xFFFFFFFF
        s ^= s >> 17
        s ^= (s << 5) & 0xFFFFFFFF
        self.s = s
        return s


def feed_encoded(det, src, t0, n, step=0.25, seed0=0, qtype=16,
                 suffix="tunnel.example.com"):
    for i in range(n):
        det.on_query(t0 + i * step, src, qtype,
                     [enc_label(seed0 + i), suffix.split(".")[0], "example",
                      "com"])


def classes_of(sink):
    return Counter(a["threat_class"] for a in sink.alerts)


# ----------------------------------------------------- 3. mechanism 1: streak

sink = RecSink()
det = DnsTunnelDetector(sink)
feed_encoded(det, "10.9.0.1", 100.0, DNS_TUNNEL_MIN_STREAK, qtype=1)
check("streak_fires_at_quorum",
      classes_of(sink)["dns_tunneling"] == 1,
      f"n={DNS_TUNNEL_MIN_STREAK} alerts={len(sink.alerts)}")
check("streak_mech_named",
      sink.alerts[0]["evidence"]["mechanism"] == "encoded_qname_streak")
check("streak_no_length_floor_excuse",
      sink.alerts[0]["evidence"]["label_length"] >= DNS_TUNNEL_LABEL_MIN_LEN)

# below quorum: silent
sink = RecSink()
det = DnsTunnelDetector(sink)
feed_encoded(det, "10.9.0.2", 100.0, DNS_TUNNEL_MIN_STREAK - 1)
check("streak_below_quorum_silent", not sink.alerts)

# a benign (non-encoded) label RESETS the streak
sink = RecSink()
det = DnsTunnelDetector(sink)
feed_encoded(det, "10.9.0.3", 100.0, DNS_TUNNEL_MIN_STREAK - 1)
det.on_query(101.0, "10.9.0.3", 1, ["www", "example", "com"])   # breaks it
feed_encoded(det, "10.9.0.3", 102.0, DNS_TUNNEL_MIN_STREAK - 1, seed0=50)
check("streak_reset_by_benign", not sink.alerts,
      f"alerts={len(sink.alerts)}")

# fire-once-per-streak: a CONTINUING streak is one incident -- no re-fire
# while it runs. Other mechanisms may legitimately fire on the same series
# (10qps TXT is also a rate anomaly), so assert on the encoded mechanism.
sink = RecSink()
det = DnsTunnelDetector(sink)
feed_encoded(det, "10.9.0.4", 100.0, 60, step=0.1)
mechs = [a["evidence"]["mechanism"] for a in sink.alerts]
check("streak_fire_once_while_running",
      mechs.count("encoded_qname_streak") == 1, mechs)
# ...and a benign label between bursts re-arms it: the next burst alerts
# again, even immediately (the e2e keepalive-burst shape)
det.on_query(107.0, "10.9.0.4", 16, ["ping", "tunnel", "example", "com"])
feed_encoded(det, "10.9.0.4", 108.0, DNS_TUNNEL_MIN_STREAK, step=0.1, seed0=90)
mechs = [a["evidence"]["mechanism"] for a in sink.alerts]
check("streak_rearmed_by_benign_label",
      mechs.count("encoded_qname_streak") == 2, mechs)
# per-src isolation: another host with its own streak fires independently
sink = RecSink()
det = DnsTunnelDetector(sink)
feed_encoded(det, "10.9.0.5", 100.0, DNS_TUNNEL_MIN_STREAK, step=0.1)
feed_encoded(det, "10.9.0.6", 100.5, DNS_TUNNEL_MIN_STREAK, step=0.1, seed0=9)
srcs = {a["src"] for a in sink.alerts}
check("streak_per_src", srcs == {"10.9.0.5", "10.9.0.6"}, srcs)

# ------------------------------------------------ 4. mechanism 2: qtype ratio

# >=ratio TXT at sustained qps -> fires
sink = RecSink()
det = DnsTunnelDetector(sink)
for i in range(20):
    det.on_query(100.0 + i * 0.2, "10.9.1.1", 16,
                 [f"probe{i:02d}", "svc", "example", "com"])
mechs = [a["evidence"]["mechanism"] for a in sink.alerts]
check("qtype_volume_fires", "data_record_volume" in mechs, mechs)

# TXT share below the ratio (mostly A queries) -> mechanism 2 silent
sink = RecSink()
det = DnsTunnelDetector(sink)
for i in range(20):
    qt = 16 if i % 5 == 0 else 1
    det.on_query(100.0 + i * 0.2, "10.9.1.2", qt,
                 [f"probe{i:02d}", "svc", "example", "com"])
mechs = [a["evidence"]["mechanism"] for a in sink.alerts]
check("qtype_below_ratio_silent", "data_record_volume" not in mechs, mechs)

# TXT-heavy but SLOW (below MIN_QPS) -> mechanism 2 silent (sparse TXT is
# exactly what real service discovery looks like)
sink = RecSink()
det = DnsTunnelDetector(sink)
n_slow = int(DNS_TUNNEL_QPS_WINDOW * DNS_TUNNEL_MIN_QPS) + 4
step = DNS_TUNNEL_QPS_WINDOW / n_slow + 1.0 / DNS_TUNNEL_MIN_QPS
for i in range(n_slow):
    det.on_query(100.0 + i * step, "10.9.1.3", 16,
                 [f"probe{i:02d}", "svc", "example", "com"])
mechs = [a["evidence"]["mechanism"] for a in sink.alerts]
check("qtype_slow_silent", "data_record_volume" not in mechs, mechs)

# too little evidence overall -> nothing at all
sink = RecSink()
det = DnsTunnelDetector(sink)
for i in range(5):
    det.on_query(100.0 + i * 0.1, "10.9.1.4", 16, [f"p{i}", "a", "com"])
check("qtype_low_evidence_silent", not sink.alerts)

# --------------------------------------------------- 5. mechanism 3: qps ----

# high rate to ONE zone fires even with ordinary labels/qtypes
sink = RecSink()
det = DnsTunnelDetector(sink)
for i in range(40):
    det.on_query(100.0 + i * 0.15, "10.9.2.1", 1,
                 [f"host{i:03d}", "bigzone", "example", "com"])
mechs = [a["evidence"]["mechanism"] for a in sink.alerts]
check("qps_anomaly_fires", "query_rate_anomaly" in mechs, mechs)

# the same rate SPLIT across many zones does not (normal resolver behaviour)
sink = RecSink()
det = DnsTunnelDetector(sink)
for i in range(40):
    det.on_query(100.0 + i * 0.15, "10.9.2.2", 1,
                 [f"host{i:03d}", f"zone{i % 12}", "example", "com"])
mechs = [a["evidence"]["mechanism"] for a in sink.alerts]
check("qps_multi_zone_silent", "query_rate_anomaly" not in mechs, mechs)

# trailing-window mechanics: old records age out, so qps is measured over
# QPS_WINDOW only -- feed a 10qps burst, verify the retained tail is bounded
# by the window (a burst legitimately fires ONCE; the per-(src,mech) dedupe
# is what stops an identical re-fire, and that is covered above)
sink = RecSink()
det = DnsTunnelDetector(sink)
for i in range(20):
    det.on_query(100.0 + i * 0.1, "10.9.2.3", 1, [f"h{i}", "z", "example", "com"])
check("window_retains_burst", len(det.recent["10.9.2.3"]) == 20)
# 2 x QPS_WINDOW of silence later, everything before is gone
det.on_query(100.0 + 2 * DNS_TUNNEL_QPS_WINDOW, "10.9.2.3", 1,
             ["h", "z", "example", "com"])
check("window_ages_out", len(det.recent["10.9.2.3"]) == 1,
      len(det.recent["10.9.2.3"]))
# and after the pruning, the aged-out burst cannot keep a rate alert alive:
# a NEW slow series on the same src stays silent (burst 1 fired legitimately
# at ~100.8 and burst 2 was dedupe-suppressed; nothing NEW may appear now)
n_before = len(sink.alerts)
for i in range(8):
    det.on_query(160.0 + i * 5.0, "10.9.2.3", 1,
                 [f"s{i}", "z", "example", "com"])
check("aged_burst_does_not_pollute_qps", len(sink.alerts) == n_before,
      [a["evidence"]["mechanism"] for a in sink.alerts[n_before:]])

# --------------------------------------------------- 6. benign FP guards ----

sink = RecSink()
det = DnsTunnelDetector(sink)
t = 100.0
# 20 hosts doing ordinary A lookups at human cadence + sparse TXT discovery
for h in range(20):
    src = f"10.9.3.{h + 1}"
    t = 100.0 + h * 0.7
    for k in range(30):
        det.on_query(t, src, 1, [f"www{k}", "some-site", "com"])
        det.on_query(t + 0.3, src, 1, ["cdn01", "images", "example", "com"])
        if k % 10 == 0:
            det.on_query(t + 0.6, src, 16,
                         ["_dmarc", "some-site", "com"])
        t += 18.0
check("benign_corpus_zero_alerts", not sink.alerts,
      f"alerts={len(sink.alerts)}")

# DGA traffic (the lexical gate's domain) must not trip THIS detector
sink = RecSink()
det = DnsTunnelDetector(sink)
for i in range(40):
    det.on_query(100.0 + i * 10.0, "10.9.4.1", 1,
                 ["8yuxczaumapqpp", "com"])
check("dga_queries_not_tunnel", not sink.alerts, len(sink.alerts))

# responses mixed in are ignored entirely
sink = RecSink()
det = DnsTunnelDetector(sink)
for i in range(30):
    det.on_query(100.0 + i * 0.1, "10.9.5.1", 16, [enc_label(i), "x", "com"])
check("encoded_only_via_on_query", classes_of(sink)["dns_tunneling"] >= 1)

# ------------------------------------------ 7. streaming integration --------

import pcap_reader
import pipeline as pl


def run_packets(pkts, sink):
    proc = pl.StreamProcessor(sink)
    for p in pkts:
        proc.feed(p)
        proc.tick(p[0])
    proc.finish()
    return proc


# StreamProcessor.finish() aggregates severity/class over the sink's
# records, which RecSink now carries.


def udp53(t, src, payload):
    return (t, src, "8.8.8.8", "udp", 40000 + int(t * 7) % 20000, 53,
            len(payload) + 42, False, payload, None, 0)


# real wire-format tunnel through the FULL pipeline: alerts, and ONLY on
# the tunnel host
sink = RecSink()
pkts = []
base = 400.0     # past the DGA window start, standalone run
for i in range(24):
    q = dns_query_bytes(f"{enc_label(i)}.s01.tunnel.example.com", qtype=16)
    pkts.append(udp53(base + i * 0.2, "10.9.9.9", q))
run_packets(pkts, sink)
cls = classes_of(sink)
check("pipeline_emits_tunnel", cls["dns_tunneling"] >= 1, dict(cls))
check("pipeline_tunnel_src_only",
      {a["src"] for a in sink.alerts} == {"10.9.9.9"},
      {a["src"] for a in sink.alerts})

# the same host doing ONLY ordinary lookups emits nothing. The inter-
# arrival must be POISSON, not exact 5.000s steps: exact cadence has CV=0
# and the BEACON detector is right to flag that (it is robotic by
# construction) -- a real resolver is exponential.
import random as _rnd
_rnd.seed(7)
sink = RecSink()
_t = 400.0
pkts = []
for i in range(40):
    pkts.append(udp53(_t, "10.9.9.9",
                      dns_query_bytes("www.example.com", qtype=1)))
    _t += _rnd.expovariate(1 / 5.0)
run_packets(pkts, sink)
check("pipeline_benign_silent", not sink.alerts,
      [a["threat_class"] for a in sink.alerts])

# e2e evidence quality on the real recorded pcap: every tunnel alert names
# a mechanism and a zone, confidence never reaches critical alone
import json
import os
if os.path.exists("alerts.jsonl"):
    tunnel_alerts = []
    for line in open("alerts.jsonl"):
        a = json.loads(line)
        if a.get("threat_class") == "dns_tunneling":
            tunnel_alerts.append(a)
    if tunnel_alerts:
        check("e2e_alerts_have_mechanism",
              all("mechanism" in a["evidence"] for a in tunnel_alerts))
        check("e2e_alerts_have_zone",
              all("target_zone" in a["evidence"] for a in tunnel_alerts))
        check("e2e_never_critical_alone",
              all(a["severity"] != "critical" for a in tunnel_alerts),
              {a["severity"] for a in tunnel_alerts})
        check("e2e_one_way_note",
              all("one-way" in a["evidence"]["note"] for a in tunnel_alerts))
        check("e2e_port_53_udp",
              all(a["flow_id"].endswith(":53/udp") for a in tunnel_alerts),
              {a["flow_id"] for a in tunnel_alerts})
        print(f"       (e2e: {len(tunnel_alerts)} tunnel alerts in alerts.jsonl)")
    else:
        print("       (no tunnel alerts in alerts.jsonl -- regenerate pcap "
              "for e2e evidence checks)")

# DATA_QTYPES sanity: NULL/TXT/ANY are the data carriers, A/AAAA/PTR are not
check("data_qtypes_member", {0, 10, 16} <= DATA_QTYPES)
check("data_qtypes_excludes_a", 1 not in DATA_QTYPES and 12 not in DATA_QTYPES
      and 28 not in DATA_QTYPES)

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    raise SystemExit(1)
print("all dns_tunnel tests passed")
