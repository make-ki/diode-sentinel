"""UDP reflection/amplification detector -- the unmodelled half of PS class (a).

The problem statement splits class (a) three ways: "SYN floods,
UDP reflection/amplification, and spoofed-source floods". SYN floods and
spoofed floods are covered by DDosDetector's rate/entropy/SYN-ratio path.
Reflection/amplification was not separately modelled -- the honest gap
PRESENTATION.md section 3(iii) and judge-question #2 concede. This module
closes it.

The attack, one-way observable:
  A botnet sends small spoofed UDP queries (DNS, NTP/Monlist, memcached,
  SSDP, SNMP, Chargen, ...) to open amplifiers with the VICTIM's address as
  source. The amplifiers send large replies TO THE VICTIM. A diode on the
  protected network's outbound side sees only the query half. Two shapes:

  - SPOOFED (classic): every query carries src = the victim's IP, so the
    visible stream is ONE source address firing thousands of tiny queries
    per second at ONE reflector service. DDosDetector is structurally
    silent here: distinct srcs = 1 (< 500 spoof gate), syn_ratio = 0 (UDP),
    and the per-flow ML tier sees only single-packet flows. Nothing else in
    the pipeline has a story for this traffic. That hole is exactly what
    mechanisms 1 and 2 below fill.
  - UNSPOOFED (dumb botnet): real bot IPs query the amplifiers directly, so
    many distinct internal sources converge on one service. Mechanism 3.

What one-way observation cannot see (stated in every alert's evidence):
  the amplified replies travelling victim-ward never cross this diode, so
  no bounce ratio, no reply sizes, no victim-side impact. Only the
  initiation signature is observable -- which is sufficient: launching the
  attack means emitting exactly this pattern.

Discriminators are MEASURED against this repo's own benign corpus, not
guessed (the Item 12 lesson, applied):
  - Benign UDP to amplifier ports in the stream: DNS queries to 8.8.8.8
    (~1 query/20s per host => ~1 qps aggregate across 20 hosts, ~8 distinct
    srcs per 10s window) and one NTP keepalive (90B frame) every 30s. A
    10s window therefore holds ~10 benign service queries from ~8 srcs.
  - An amplification campaign holds 1000+ queries per 10s window at
    100+ qps. Thresholds sit 3-6x above the benign numbers:
    rate gate 3 qps and 60 queries/window (benign ~1 qps, ~10/window),
    fan-out gate 30 distinct srcs (benign ~8), burst gate 300 small
    packets/window at >=90% small share (benign ~11 packets).
  - The 128B small-frame floor is measured too: benign NTP keepalives are
    90B frames and DO count as small -- but at 1 packet/30s they are three
    orders of magnitude below the burst gate, so the floor is honest.

Three mechanisms, one detector (mirrors dns_tunnel's structure):
  1. query_rate_spike   sustained >= 3 qps to ONE (dst, amplifier-port)
  2. small_query_burst  >= 300 tiny (<=128B) query frames to amplifier
                        ports in one window at >= 90% small share
  3. amplifier_fanout   >= 30 distinct sources querying amplifier ports in
                        one window (unspoofed-bot shape)

Dedupe: fire-once-per-campaign per (mechanism, service) with re-arm after
UDP_AMP_REALERT_SECS of quiet windows -- a continuing campaign is ONE
incident (dns_tunnel BUG 2's lesson: wall-clock refires on a continuing
event spam identical alerts; a genuinely re-armed campaign must re-alert).

Confidence bands: rate 0.65-0.899, burst 0.72-0.80, fan-out 0.72-0.899 --
never critical (0.90+) alone (the _severity flip point; same policy as the
tunnel detector): a critical verdict must come from FUSION with an
independent signal (ml_flow_suspicious on the same spoofed src, or a
beaconing verdict), not from one window shape.

Zero schema change: fed from the packet tuple the pipeline ALREADY carries
(a UDP hook in StreamProcessor.feed, exactly like the QUIC hook).
pcap_reader/live_source untouched => the dpkt/scapy parity surface stays
byte-identical. Old pcap must replay byte-identical against the reference
BEFORE any new traffic is generated.
"""
import math
from collections import defaultdict

from config import (UDP_AMP_MIN_SRCS, UDP_AMP_MIN_PKTS,
                    UDP_AMP_MIN_QPS_WINDOW, UDP_AMP_MIN_QPS,
                    UDP_AMP_SMALL_SHARE, UDP_AMP_SMALL_BYTES,
                    UDP_AMP_WINDOW, UDP_AMP_REALERT_SECS)

# Ports whose UDP services are the classic amplifiers (the record-type list
# dns_tunnel.DATA_QTYPES is the analogous gate on the DNS path). Traffic to
# any other UDP port is not scored by this detector: benign QUIC (443) and
# everything else stay out of its windows by construction.
AMPLIFIER_PORTS = frozenset({53, 123, 111, 161, 389, 1900, 5353, 11211,
                             17, 19})

PORT_NAMES = {53: "DNS", 123: "NTP", 111: "Portmap", 161: "SNMP", 389: "LDAP",
              1900: "SSDP", 5353: "mDNS", 11211: "memcached", 17: "QOTD",
              19: "Chargen"}

_ONE_WAY_NOTE = ("one-way feed: the amplified replies travel victim-ward and "
                 "never cross this diode; only the query half is observable")


def _shannon(counter) -> float:
    n = sum(counter.values())
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in counter.values())


class UdpAmpDetector:
    """Per-window UDP reflection/amplification scoring.

    Fed per PACKET by pipeline.py's UDP hook. Window state is accumulated
    here (not in WindowAggregator) so the hook is zero-schema-change: the
    aggregate window carries TCP-centric counters, and a self-contained
    window keyed by stream time keeps replay and live behaviour identical
    (both drive the same StreamProcessor.feed).
    """

    def __init__(self, sink):
        self.sink = sink
        self.cur_idx = None
        self.cur = None
        self.flushed_windows = 0
        # campaign memory: (mechanism, service-key) -> window idx of the
        # last alerting window; a campaign re-arms only after
        # UDP_AMP_REALERT_SECS worth of QUIET windows.
        self.last_alert = {}
        # continuity: service-key -> window idx of its last ACTIVE window
        # (folded in during that window's flush, not at packet time -- the
        # trigger packet for window N's flush belongs to N+1 and must not
        # make window N look busy). A gap of >= REALERT windows with no
        # service packets kills the campaign (re-arms dedupe); continuous
        # service traffic never does. This is what stops a wall-clock alert
        # at window N re-arming at N+12 while packets never stopped (the
        # dns_tunnel BUG 2 shape).
        self.last_pkt_idx = {}

    # ---- packet intake ----------------------------------------------------
    def on_packet(self, t, src, dst, dport, size):
        if dport not in AMPLIFIER_PORTS:
            return
        idx = int(t // UDP_AMP_WINDOW)
        if self.cur_idx is not None and idx > self.cur_idx:
            self._flush(self.cur_idx)
            self.cur = None
        if self.cur is None:
            self.cur_idx = idx
            self.cur = dict(t0=idx * UDP_AMP_WINDOW,
                            t1=(idx + 1) * UDP_AMP_WINDOW,
                            pkts=0, small=0,
                            srcs=defaultdict(int),       # src -> pkt count
                            services=defaultdict(        # (dst,dport) -> []
                                lambda: [0, set()]))     # [pkts, {srcs}]
        w = self.cur
        w["pkts"] += 1
        w["srcs"][src] += 1
        if size <= UDP_AMP_SMALL_BYTES:
            w["small"] += 1
        svc = w["services"][(dst, dport)]
        svc[0] += 1
        svc[1].add(src)

    # ---- window close -----------------------------------------------------
    def flush_current(self):
        """Score the trailing (incomplete) window -- end-of-capture drain.

        Also clears cur_idx: a packet arriving AFTER this drain must not
        trigger _flush on the already-drained (None) state.
        """
        if self.cur is not None:
            self._flush(self.cur_idx)
            self.cur = None
        self.cur_idx = None

    def _flush(self, idx):
        self.flushed_windows += 1
        w = self.cur
        t_end = w["t1"] - 1

        # NOTE: do NOT fold this window's activity into last_pkt_idx before
        # scoring -- that erases the quiet gap the re-arm decision must see.
        # The fold happens AFTER the mechanism scoring below.

        # mechanism 1, per service
        for (dst, dport), (n, srcs) in w["services"].items():
            if n < UDP_AMP_MIN_QPS_WINDOW:
                continue
            qps = n / UDP_AMP_WINDOW
            if qps < UDP_AMP_MIN_QPS:
                continue
            key = ("query_rate_spike", dst, dport)
            if not self._rearmed(key, idx):
                continue
            self.last_alert[key] = idx
            # hard cap 0.899: severity '_severity' flips to critical at 0.90,
            # and the design policy is a single window shape NEVER reaches
            # critical alone -- fusion must supply the escalation.
            conf = min(0.899, 0.65 + min(qps / 100.0, 0.25))
            self.sink.emit(t_end, "*", dst, dport, "udp",
                           "ddos_udp_amplification", conf, {
                               "mechanism": "query_rate_spike",
                               "service": PORT_NAMES.get(dport, str(dport)),
                               "window": f"{w['t0']:.0f}-{w['t1']:.0f}s",
                               "window_qps": round(qps, 1),
                               "window_queries": n,
                               "distinct_src_ips": len(srcs),
                               "note": _ONE_WAY_NOTE,
                               "why": f"sustained {qps:.1f} qps of small "
                                      f"queries to one "
                                      f"{PORT_NAMES.get(dport, dport)} "
                                      f"service => reflection/amplification "
                                      f"campaign initiation",
                           })

        # mechanism 2, cross-service burst shape
        if w["pkts"] >= UDP_AMP_MIN_PKTS:
            small_share = w["small"] / w["pkts"]
            if small_share >= UDP_AMP_SMALL_SHARE:
                key = ("small_query_burst",)
                if self._rearmed(key, idx):
                    self.last_alert[key] = idx
                    self.sink.emit(t_end, "*", "*", "*", "udp",
                                   "ddos_udp_amplification",
                                   min(0.80, 0.72 + (small_share - 0.9)), {
                                       "mechanism": "small_query_burst",
                                       "window": f"{w['t0']:.0f}-{w['t1']:.0f}s",
                                       "window_qps": round(w["pkts"]
                                                           / UDP_AMP_WINDOW, 1),
                                       "window_queries": w["pkts"],
                                       "small_packet_share": round(small_share, 2),
                                       "small_frame_floor_bytes": UDP_AMP_SMALL_BYTES,
                                       "note": _ONE_WAY_NOTE,
                                       "why": "window dominated by tiny query "
                                              "frames to reflection services "
                                              "=> query-storm shape of an "
                                              "amplification campaign",
                                   })

        # mechanism 3, distinct-source fan-out (unspoofed bots)
        distinct = len(w["srcs"])
        if w["pkts"] >= UDP_AMP_MIN_PKTS and distinct >= UDP_AMP_MIN_SRCS:
            key = ("amplifier_fanout",)
            if self._rearmed(key, idx):
                self.last_alert[key] = idx
                ent = _shannon(w["srcs"])
                conf = min(0.899, 0.72 + min(distinct / 1000, 0.18))
                self.sink.emit(t_end, "*", "*", "*", "udp",
                               "ddos_udp_amplification", conf, {
                                   "mechanism": "amplifier_fanout",
                                   "window": f"{w['t0']:.0f}-{w['t1']:.0f}s",
                                   "window_qps": round(w["pkts"]
                                                       / UDP_AMP_WINDOW, 1),
                                   "distinct_src_ips": distinct,
                                   "src_ip_entropy_bits": round(ent, 2),
                                   "note": _ONE_WAY_NOTE,
                                   "why": "many distinct sources querying "
                                          "reflection services in one "
                                          "window => unspoofed botnet "
                                          "amplification campaign",
                               })

        # fold THIS window's service activity into campaign continuity LAST:
        # a window is 'active' for a service if it saw any packet for it.
        # Folding after scoring preserves the quiet-gap semantics the
        # re-arm decision reads (previous fold -> current window busy).
        for (dst, dport) in w["services"]:
            self.last_pkt_idx[(dst, dport)] = idx

    def _rearmed(self, key, idx):
        """True when the campaign behind key has actually DIED.

        For the per-service rate mechanism the key ends in (dst, dport).
        The campaign is dead iff BOTH hold:
          - no packet reached that service for >= REALERT windows before the
            current one (service went quiet after the last alert), and
          - the last alert itself is >= REALERT windows old.
        The first alert of a campaign has no last_alert -> fires; a still-
        busy service blocks re-alerting even if the last alert is old (the
        dns_tunnel BUG 2 shape: a wall-clock refire on packets that never
        stopped); a genuinely quiet gap re-arms.
        Cross-service keys (burst/fanout) keep the plain alert-age rule:
        those shapes are lumpy by nature and there is no single service to
        watch for continuity.
        """
        if len(key) == 3 and key[0] == "query_rate_spike":
            _, dst, dport = key
            last_pkt = self.last_pkt_idx.get((dst, dport))
            quiet_windows = UDP_AMP_REALERT_SECS / UDP_AMP_WINDOW
            if (last_pkt is not None
                    and idx - last_pkt < quiet_windows):
                # service saw packets recently; if we ever alerted on this
                # campaign, the campaign is CONTINUOUS -> still one incident
                if self.last_alert.get(key) is not None:
                    return False
        last = self.last_alert.get(key)
        return (last is None
                or idx - last >= UDP_AMP_REALERT_SECS / UDP_AMP_WINDOW)
