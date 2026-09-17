"""
DNS tunnelling detector -- the record-type/length/volume half of PS class (c).

The problem statement splits class (c) in two halves: "Entropy/n-gram analysis
of DNS query names" (DGADetector's job, the lexical gate + CNN) "plus
query-length and record-type anomalies" (this module's job). A tunnel is a C2
or exfiltration channel that hides data IN the DNS protocol itself:

  dnscat2: long base32hex labels in qnames, usually TXT, one query per chunk
  iodine:  NULL/TXT records, data in the question AND the (invisible) response
  generic: whatever encodes bytes -- qnames stay the one field a one-way feed
           always sees, so qname-carried data is the primary signal here

Why not fold it into DGADetector? Different question, different thresholds.
The lexical gate answers "does this label LOOK machine-generated" on labels
>= 10 chars and rejects dense base32 below 3.3 bits of entropy only by luck
(it is a rejector of randomness, not a detector of encoding). A tunnel label
is not random -- it is high-entropy AND long AND part of a high-rate series
to ONE authoritative domain. Scoring it here keeps both detectors' thresholds
measurable against their own corpora instead of compromising one gate for two
adversaries (the same reason the CNN is a separate tier, not a bigger gate).

One-way constraint, stated: no responses are observed, so "did the resolver
answer with a big TXT" is unknowable. Every signal here is question-side
only -- that is the honest maximum for this feed.

Wire parsing note: qtype lives in the question section of the raw DNS
payload, which the packet tuple already carries. Parsing it here (rather
than extending the tuple schema in pcap_reader/live_source) keeps the
dpkt/scapy parity surface, the live dissection path and every recorded
pcap byte-identical -- the same reasoning as the QUIC hook.
"""
import math
from collections import Counter, defaultdict, deque

import config
from config import (DNS_TUNNEL_LABEL_MIN_LEN, DNS_TUNNEL_MIN_ENTROPY,
                    DNS_TUNNEL_MIN_STREAK, DNS_TUNNEL_MIN_QTYPE_RATIO,
                    DNS_TUNNEL_MIN_QPS, DNS_TUNNEL_QPS_WINDOW,
                    DNS_TUNNEL_MIN_WINDOW_QUERIES, DNS_TUNNEL_REALERT_SECS)

# RFC 1035 / 883 + modern data records a tunnel can abuse. NULL (10) is
# iodine's favourite; TXT (16) is dnscat2's; others appear in the wild.
DATA_QTYPES = frozenset({0, 10, 16, 17, 99})   # ANY, NULL, TXT, RP, SPF

_B32 = set("abcdefghijklmnopqrstuvwxyz234567")


def parse_qtype(payload: bytes):
    """(qtype, labels) from a raw DNS query payload, or None.

    labels: the question name split into labels (lowercased), [] when the
    name cannot be decoded. Returns None for non-queries (qr=1), truncated
    payloads, malformed names and compression pointers (responses).
    """
    if len(payload) < 17:                      # 12B header + minimal question
        return None
    flags = int.from_bytes(payload[2:4], "big")
    if flags & 0x8000:                         # qr=1: a response, not a query
        return None
    qdcount = int.from_bytes(payload[4:6], "big")
    if qdcount < 1:
        return None
    off = 12
    labels = []
    try:
        while True:
            n = payload[off]
            if n == 0:
                off += 1
                break
            if n & 0xC0:                       # compression pointer: response
                return None                    #   trick, never in a question
            off += 1
            if off + n > len(payload):
                return None
            labels.append(payload[off:off + n].decode("ascii", "replace")
                          .lower())
            off += n
        if off + 4 > len(payload):
            return None
        qtype = int.from_bytes(payload[off:off + 2], "big")
    except IndexError:
        return None
    return qtype, labels


def shannon_entropy(counter) -> float:
    n = sum(counter.values())
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in counter.values())


def looks_encoded(label: str) -> bool:
    """The per-label verdict: LONG + DENSE, as a pure function.

    Long: DNS_TUNNEL_LABEL_MIN_LEN+ chars -- above anything this repo's
    benign corpus produces (11-char CDN labels) and above DGA labels (14).
    Dense: high base32/base64-style entropy AND a high share of the
    unreserved encoding alphabet, so a long ENGLISH compound (low entropy,
    mostly a-z but human) fails on density while 0-9/a-f hex blobs fail on
    entropy (16-symbol alphabet tops out at 4.0 bits).
    """
    if len(label) < DNS_TUNNEL_LABEL_MIN_LEN:
        return False
    ent = shannon_entropy(Counter(label))
    alnum = sum(1 for ch in label if ch.isalnum())
    if alnum / len(label) < 0.95:
        return False
    b32ish = sum(1 for ch in label.lower() if ch in _B32) / len(label)
    return ent >= DNS_TUNNEL_MIN_ENTROPY and b32ish >= 0.95


class DnsTunnelDetector:
    """Per-source DNS anomaly scoring across three independent mechanisms.

    Mechanism 1 -- encoded qname labels (works on A/TXT/anything):
      a STREAK of consecutive looks_encoded() labels from one source. A
      single 24-char label is a long hostname; a series of them every few
      hundred milliseconds to one authoritative domain is a chunked upload.
      Same streak logic as the lexical gate (benign label breaks it) with
      its own quorum and dedupe.

    Mechanism 2 -- data-record volume:
      a source sending >= MIN_QTYPE_RATIO of its queries as TXT/NULL/ANY in
      a trailing window, at >= MIN_QPS sustained. Catches tunnels that
      fragment across short labels (qname-carried evidence fails) by their
      record-type profile instead.

    Mechanism 3 -- query-rate anomaly:
      >= MIN_QPS sustained to a single <src, qname-suffix> pair, no record
      type or label assumptions. The pure volume signature of chunked
      transfer (iodine pings qps hard).

    All three share the alert path and dedupe per (src, mechanism) with
    DNS_TUNNEL_REALERT_SECS. Confidence bands differ per mechanism: a
    qname-encoded streak is the strongest single signal (the data is right
    there in the alert), record-type and rate anomalies are corroborating
    shapes and land lower.
    """

    MECH_ENCODED = "encoded_qname_streak"
    MECH_QTYPE = "data_record_volume"
    MECH_QPS = "query_rate_anomaly"

    _CONF = {MECH_ENCODED: (0.72, 0.95),      # (base, ceiling)
             MECH_QTYPE: (0.60, 0.90),
             MECH_QPS: (0.55, 0.85)}

    def __init__(self, sink):
        self.sink = sink
        self.streak = defaultdict(int)          # src -> consecutive encoded
        self.armed_encoded = set()              # srcs whose streak may fire
        self.last_alert = {}                    # (src, mech) -> t
        self.recent = defaultdict(lambda: deque(maxlen=256))
        # per-src recent window: deque of (t, qtype, suffix) -- bounded;
        # a host hammering DNS for hours cannot grow this structure.

    # ---- ingest ------------------------------------------------------------

    def on_query(self, t, src, qtype, labels):
        """One DNS query. labels = parsed question-name labels (lowercase)."""
        suffix = ".".join(labels[1:]) if len(labels) > 1 else ""
        first = labels[0] if labels else ""
        self.recent[src].append((t, qtype, suffix))
        self._prune(src, t)

        # Mechanism 1: encoded-label streak (per query, like the lexical
        # gate). Fire-once-per-streak: a streak that stays alive past the
        # alert is ONE continuing upload, so it must not re-fire every
        # REALERT_SECS on identical evidence; a non-encoded label (a benign
        # lookup, or a dnscat2-style short 'ping' keepalive) breaks the
        # streak and re-arms, so the next burst is a fresh incident. A
        # wall-interval refire here would turn a 600s continuous tunnel
        # into an alert-storm the fusion layer then amplifies.
        if looks_encoded(first):
            self.streak[src] += 1
            if (self.streak[src] >= DNS_TUNNEL_MIN_STREAK
                    and src not in self.armed_encoded):
                self.armed_encoded.add(src)
                self._emit(t, src, self.MECH_ENCODED, suffix, {
                    "encoded_label": first,
                    "label_length": len(first),
                    "streak": self.streak[src],
                    "queries_in_window": len(self.recent[src]),
                })
        else:
            self.streak[src] = 0
            self.armed_encoded.discard(src)

        # Mechanisms 2/3 need enough evidence to mean anything
        rec = self.recent[src]
        if len(rec) < DNS_TUNNEL_MIN_WINDOW_QUERIES:
            return

        # Mechanism 2: data-record ratio + sustained rate
        span = t - rec[0][0]
        if span <= 0:
            return
        qps = (len(rec) - 1) / span
        data_share = sum(1 for _, qt, _ in rec if qt in DATA_QTYPES) / len(rec)
        if (data_share >= DNS_TUNNEL_MIN_QTYPE_RATIO
                and qps >= DNS_TUNNEL_MIN_QPS):
            self._emit(t, src, self.MECH_QTYPE, suffix, {
                "data_record_share": round(data_share, 2),
                "queries_in_window": len(rec),
                "window_qps": round(qps, 2),
                "dominant_qtypes": self._top_qtypes(rec),
            })

        # Mechanism 3: sustained rate to one zone, any record type
        by_suffix = defaultdict(int)
        for _, _, sfx in rec:
            by_suffix[sfx] += 1
        top_suffix, top_n = max(by_suffix.items(), key=lambda kv: kv[1])
        pair_qps = (top_n - 1) / span if top_n > 1 else 0.0
        if top_n >= DNS_TUNNEL_MIN_WINDOW_QUERIES and pair_qps >= DNS_TUNNEL_MIN_QPS:
            self._emit(t, src, self.MECH_QPS, suffix, {
                "queries_in_window": top_n,
                "window_qps": round(pair_qps, 2),
                "target_zone": top_suffix or "(root)",
                "distinct_zones": len(by_suffix),
            })

    # ---- internals ---------------------------------------------------------

    def _prune(self, src, t):
        rec = self.recent[src]
        horizon = t - DNS_TUNNEL_QPS_WINDOW
        while rec and rec[0][0] < horizon:
            rec.popleft()

    @staticmethod
    def _top_qtypes(rec):
        names = {0: "ANY", 10: "NULL", 16: "TXT", 17: "RP", 99: "SPF"}
        counts = defaultdict(int)
        for _, qt, _ in rec:
            counts[names.get(qt, str(qt))] += 1
        return dict(sorted(counts.items(), key=lambda kv: -kv[1])[:3])

    def _emit(self, t, src, mech, suffix, evidence):
        # Dedupe policy per mechanism: the encoded streak dedupes ITSELF
        # (fire-once-per-streak; a benign label re-arms), so a wall
        # interval here would eat the legitimately re-armed second burst
        # (e2e bursts are 140s apart, but a fast repeated attack cycle is
        # not). The rate-shape mechanisms have no such boundary -- their
        # only stopper is the wall interval, so a persistent rate shape
        # cannot re-fire on every query.
        if mech != self.MECH_ENCODED:
            last = self.last_alert.get((src, mech), -1e18)
            if t - last < DNS_TUNNEL_REALERT_SECS:
                return
        self.last_alert[(src, mech)] = t
        lo, hi = self._CONF[mech]
        # Confidence grows with corroborating shape: queries/s above the
        # floor pushes toward the ceiling, capped so no mechanism self-
        # reports critical (0.90+) -- a tunnel alert should fuse with
        # beacon/exfil evidence for that, not mint it alone.
        qps = evidence.get("window_qps") or 0.0
        boost = min((qps - DNS_TUNNEL_MIN_QPS) / 10.0, 0.18) if qps else 0.0
        if mech == self.MECH_ENCODED:
            boost = min(evidence["streak"] / 40.0, 0.15)
        conf = min(hi, lo + boost)
        self.sink.emit(t, src, "*", 53, "udp", "dns_tunneling", conf, {
            "mechanism": mech,
            "target_zone": suffix or "(root)",
            "note": "question-side evidence only (one-way feed): response "
                    "records and sizes are unobservable",
            "why": self._WHY[mech],
            **evidence,
        })

    _WHY = {
        MECH_ENCODED: "series of long high-entropy encoded labels in query "
                      "names => data being uploaded through DNS",
        MECH_QTYPE: "query stream dominated by data-carrying record types "
                    "(TXT/NULL) at sustained rate => DNS data channel",
        MECH_QPS: "sustained high query rate to a single zone => chunked "
                  "transfer over DNS regardless of encoding",
    }
