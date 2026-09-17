#!/usr/bin/env python3
"""
Generate a synthetic ONE-WAY pcap for feasibility testing.

Simulates what a monitoring enclave sees on the receive side of a data
diode: every packet is client->server (outbound of the protected network).
No responses, no SYN-ACKs, no return traffic -- by construction.

Contents (10 min sim time, ~13k packets):
  BENIGN
    - ~20 internal hosts web-browsing external servers (TCP 80/443)
    - DNS queries to 8.8.8.8 for normal domains
    - NTP keepalive every 30s from one host (allowlisted periodic service)
  ATTACKS
    - SYN flood, spoofed sources      t in [300, 320)  -> 203.0.113.10:443
    - C2 beaconing every 5s +- jitter t in [0, 600)    -> 198.51.100.23:443
    - DGA domain queries every 10s    t in [0, 600)
    - DNS tunnelling (dnscat2-style)  t in [120, 600)  -> tunnel.example.com
    - Vertical port scan (500 ports)  t in [400, 415)  -> 203.0.113.20
    - Data exfiltration (2.8 MB)      t in [480, 540)  -> 45.33.32.156:8443
"""
import random
from scapy.all import Ether, IP, TCP, UDP, DNS, DNSQR, Raw, wrpcap

from config import (SIM_START, DURATION, PCAP_PATH, BASELINE_SECONDS,
                    DNS_TUNNEL_HOST, DNS_TUNNEL_DOMAIN)
from hello_profiles import browser_hello, updater_hello, malware_hello

random.seed(42)

INTERNAL = ["10.0.0.%d" % i for i in range(2, 22)]          # 20 benign hosts
BENIGN_EXT = (["93.184.216.%d" % i for i in range(1, 25)]
              + ["151.101.1.%d" % i for i in range(1, 25)]
              + ["104.16.132.%d" % i for i in range(1, 25)])
BENIGN_DOMAINS = ["google.com", "facebook.com", "amazon.com", "wikipedia.org",
                  "github.com", "netflix.com", "microsoft.com", "apple.com",
                  "stackoverflow.com", "youtube.com"]
DNS_SERVER, NTP_SERVER = "8.8.8.8", "129.6.15.28"
VICTIM, SCAN_TARGET = "203.0.113.10", "203.0.113.20"
C2_SERVER, EXFIL_DST = "198.51.100.23", "45.33.32.156"

events = []  # (t, packet)


def _sport():
    return random.randint(40000, 60000)


def _spoofed_ip():
    first = random.choice([o for o in range(1, 224) if o not in (10, 127, 172, 192)])
    return "%d.%d.%d.%d" % (first, random.randint(0, 255),
                            random.randint(0, 255), random.randint(1, 254))


def _tcp(t, src, dst, sport, dport, size, flags, payload=None):
    if payload is None:
        payload = b"\x00" * max(0, size - 54)   # Eth(14)+IP(20)+TCP(20)
    events.append((t, Ether() / IP(src=src, dst=dst) /
                   TCP(sport=sport, dport=dport, flags=flags) / Raw(payload)))


def _udp(t, src, dst, sport, dport, size):
    payload = b"\x00" * max(0, size - 42)      # Eth(14)+IP(20)+UDP(8)
    events.append((t, Ether() / IP(src=src, dst=dst) /
                   UDP(sport=sport, dport=dport) / Raw(payload)))


def _dns_query(t, src, qname, qtype="A"):
    events.append((t, Ether() / IP(src=src, dst=DNS_SERVER) /
                   UDP(sport=_sport(), dport=53) /
                   DNS(rd=1, qd=DNSQR(qname=qname, qtype=qtype))))


# ---------------- TLS profile assignment (stable per host) ----------------
# 10.0.0.7  -> malware host (raw-TCP beacon + TLS C2 on 8443, malware profile)
# 10.0.0.15 -> app-update host: browser profile until t=300, updater after
# 10.0.0.18-20 -> updater profile B (deterministic SNI)
TLS_B_HOSTS = {INTERNAL[16], INTERNAL[17], INTERNAL[18]}
UPDATE_HOST, UPDATE_AT = INTERNAL[13], 300.0


def _profile_hello(host, t):
    if host in TLS_B_HOSTS:
        return updater_hello()
    if host == UPDATE_HOST and t >= UPDATE_AT:
        return updater_hello()
    return browser_hello(random.choice(BENIGN_DOMAINS) + ".")


# ---------------- benign web sessions ----------------
for host in INTERNAL:
    t = 0.0
    while t < DURATION:
        t += random.expovariate(1 / 15.0)      # avg one session per 15s
        if t >= DURATION - 3:
            break
        dst = random.choice(BENIGN_EXT)
        dport = random.choice([443, 443, 80])
        sp = _sport()
        _tcp(t, host, dst, sp, dport, 60, "S")             # SYN
        _tcp(t + 0.02, host, dst, sp, dport, 0, "PA",
             payload=(_profile_hello(host, t) if dport == 443 else None))
        for _ in range(random.randint(3, 8)):              # data packets
            _tcp(t + random.uniform(0.05, 1.5), host, dst, sp, dport,
                 random.randint(120, 1400), "PA")

# ---------------- benign DNS ----------------
for host in INTERNAL:
    t = random.uniform(0, 5)
    while t < DURATION:
        _dns_query(t, host, random.choice(BENIGN_DOMAINS) + ".")
        t += random.expovariate(1 / 20.0)

# a few benign TXT lookups (service discovery: real, but sparse and short)
for host in INTERNAL[2:8]:
    for k in range(3):
        _dns_query(random.uniform(0, DURATION), host,
                   random.choice(["_dmarc", "_domainkey", "_acme-challenge"])
                   + "." + random.choice(BENIGN_DOMAINS) + ".", qtype="TXT")

# ---------------- benign NTP keepalive (allowlisted, periodic) ----------------
for i in range(int(DURATION / 30)):
    _udp(5 + i * 30 + random.uniform(0, 0.05), INTERNAL[3], NTP_SERVER,
         123, 123, 90)

# ---------------- ATTACK 1: C2 beaconing (every 5s, low jitter) ----------------
for i in range(int(DURATION / 5) - 2):
    t = 8 + i * 5.0 + random.uniform(-0.15, 0.15)
    _tcp(t, INTERNAL[5], C2_SERVER, 51515, 443, 60, "S")
    _tcp(t + 0.01, INTERNAL[5], C2_SERVER, 51515, 443, 120, "PA")

# ---------------- ATTACK 1b: TLS C2 channel (every 45s, after baseline) ----
# Same malware host, encrypted C2 with its own distinctive TLS stack.
# Port 8443 so the 45s IATs don't pollute the 5s beacon series on 443.
MALWARE_TLS_START = 200.0
# Guard: malware TLS must start AFTER the inventory baseline closes,
# otherwise its fingerprint is learned as benign and novelty mode is blind.
assert MALWARE_TLS_START > BASELINE_SECONDS, "baseline would poison inventory"
for i in range(int((DURATION - MALWARE_TLS_START) / 45)):
    t = MALWARE_TLS_START + i * 45 + random.uniform(-0.3, 0.3)
    sp = _sport()
    _tcp(t, INTERNAL[5], C2_SERVER, sp, 8443, 60, "S")
    _tcp(t + 0.01, INTERNAL[5], C2_SERVER, sp, 8443, 0, "PA",
         payload=malware_hello())
    _tcp(t + 0.02, INTERNAL[5], C2_SERVER, sp, 8443, 200, "PA")

# ---------------- ATTACK 1c: malware moves C2 to QUIC (t=250+) ------------
# Same malware TLS stack, now inside QUIC Initial packets (UDP:443).
# Exercises the QUIC leg of class (d): one-way JA4 from QUIC crypto stream.
from hello_profiles import malware_hello as _mal_hello_raw
from quic_meta import build_quic_initial
_mal_hs = _mal_hello_raw()[5:]         # strip TLS record layer -> hs message
import os as _os2
for i in range(3):
    t = 250 + i * 10 + random.uniform(-0.2, 0.2)
    pkt_bytes = build_quic_initial(dcid=_os2.urandom(8), handshake_msg=_mal_hs)
    events.append((t, Ether() / IP(src=INTERNAL[5], dst=C2_SERVER)
                   / UDP(sport=_sport(), dport=443) / Raw(pkt_bytes)))

# ---------------- ATTACK 2: DGA domain queries (every 10s) ----------------
ALPHA = "abcdefghijklmnopqrstuvwxyz0123456789"
for i in range(int(DURATION / 10) - 2):
    label = "".join(random.choices(ALPHA, k=14))
    _dns_query(10 + i * 10, INTERNAL[7], label + ".com.")

# ---------------- ATTACK 2b: same DGA host also beacons (fusion fodder) ---
# Realistic botnet: DGA-resolved C2 + periodic beaconing from one host.
C2_ALT = "198.51.100.99"
for i in range(int((DURATION - 350) / 30)):
    t = 350 + i * 30 + random.uniform(-0.5, 0.5)
    sp = _sport()
    _tcp(t, INTERNAL[7], C2_ALT, sp, 443, 60, "S")
    _tcp(t + 0.01, INTERNAL[7], C2_ALT, sp, 443, 120, "PA")

# ---------------- ATTACK 2c: DNS tunnelling (dnscat2-style, t=120+) -------
# A compromised host runs a DNS C2 channel: data is base32-encoded, chunked
# into a long first label (dnscat2 frames subdomains exactly this way), and
# queried as TXT against ONE authoritative zone. Realistic cadence, learned
# the hard way (first draft was uniform-jittered 2qps continuous and BOTH
# other DNS-path detectors fired ~95 re-alerts on it):
#   - keepalives (short 'ping' labels, benign to every lexical gate) between
#     bursts -- which also RESET the DGA streak, as a real channel does;
#   - exponential IATs (RTT-dominated response waits), NOT uniform jitter --
#     CV~1.0, so the beacon detector correctly ignores it; a robotic 2qps
#     series IS legitimately periodic and beacon would be right to fire;
#   - three data bursts of 40 queries at ~3qps (250B chunks), 140s apart
#     (outside the tunnel detector's 120s dedupe, so each burst is scored).
# Exercises the record-type/length/volume half of PS class (c) that the
# lexical gate cannot classify: the tunnel labels DO trip the DGA gate
# (they are high-entropy strings -- expected cross-signal, fusion
# correlates the two), but the dga_domain class cannot tell you it was a
# tunnel; this detector names the mechanism.
import base64 as _b64
TUNNEL_HOST, TUNNEL_DOMAIN = DNS_TUNNEL_HOST, DNS_TUNNEL_DOMAIN
TUNNEL_START, TUNNEL_BURSTS, TUNNEL_BURST_N = 120.0, (120.0, 260.0, 400.0), 40
# keepalives: short first label, TXT, exponential inter-arrival (mean 10s)
_t = TUNNEL_START
while _t < DURATION - 5:
    _dns_query(_t, TUNNEL_HOST, f"ping.s{_t:04.0f}.{TUNNEL_DOMAIN}.",
               qtype="TXT")
    _t += random.expovariate(1 / 10.0)
# data bursts: long base32 first label, TXT, exponential IATs (mean 1/3 s)
for _t0 in TUNNEL_BURSTS:
    for _i in range(TUNNEL_BURST_N):
        t = _t0 + random.expovariate(3.0)
        chunk = _b64.b32encode(bytes([random.randrange(256)
                                      for _ in range(24)])).decode().lower()
        _dns_query(min(t, DURATION - 1), TUNNEL_HOST,
                   f"{chunk[:24]}.s{_t0:04.0f}.{TUNNEL_DOMAIN}.", qtype="TXT")

# ---------------- ATTACK 3: SYN flood, spoofed sources ----------------
for _ in range(3000):
    _tcp(random.uniform(300, 320), _spoofed_ip(), VICTIM,
         _sport(), 443, 60, "S")

# ---------------- ATTACK 3b: UDP reflection/amplification (t in [180,240)) --
# CLASS (a) second half, closed by Item 13. A botnet floods an open DNS
# reflector with spoofed queries: src = VICTIM's address (classic bounce-off),
# dst = the reflector, UDP/53, tiny query frames. The diode sees ONLY the
# query half; the amplified replies go victim-ward and never appear.
#   Shape (measured against the detector's gates, and against the OTHER
#   detectors -- the Item 12 lesson: a scenario that fires everything is a
#   generator artifact, not coverage):
#   - 120 qps mean with EXPONENTIAL IATs (CV~1.0): a robotic 0.0083s grid
#     is legitimately periodic and the beacon detector would be RIGHT to
#     fire on it; Poisson query storms are not periodic. Beacon stays silent
#     by construction (and it sees one flow-less UDP stream anyway: every
#     packet gets a fresh sport, so FlowAssembler never closes a series).
#   - qnames are short benign single labels ('check', 'a', 'pool'...): the
#     DGA gate needs >=10 chars/high entropy and the tunnel gate needs a
#     20-char base32 label -- both correctly ignore resolver chatter.
#     (Queries to 8.8.8.8 in the benign stream look identical; the ONLY
#     discriminators are rate, and rate is the point: ~1 qps benign vs
#     120 qps here.)
#   - payload is a real 17B DNS query (header + 1 label + qtype) so the
#     frame lands <=128B (small-frame gate) and pcap size stays honest.
#   - all srcs = the victim: distinct-srcs = 1, so DDosDetector's spoofed
#     gate (500+) and SYN gate are structurally silent -- that hole is what
#     the new detector fills (rate mechanism: 1200 queries/window >> 60).
from config import UDP_AMP_START, UDP_AMP_END, UDP_AMP_REFLECTOR, UDP_AMP_VICTIM
import struct as _struct
_UDP_BENIGN_QNAMES = ("check", "pool", "time", "a", "relay")

def _amp_query(t, src, dst, name):
    q = name.encode() + b"\x00" + _struct.pack(">HH", 1, 1)  # A, IN
    hdr = _struct.pack(">HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
    events.append((t, Ether() / IP(src=src, dst=dst)
                   / UDP(sport=random.randint(40000, 60000), dport=53)
                   / Raw(hdr + q)))

_t = UDP_AMP_START
while _t < UDP_AMP_END:
    _amp_query(_t, UDP_AMP_VICTIM, UDP_AMP_REFLECTOR,
               random.choice(_UDP_BENIGN_QNAMES))
    _t += random.expovariate(120.0)

# UNSPOOFED companion burst (t in [500,530)): a dumb botnet queries the
# reflector from real IPs -- exercises the fanout mechanism (30+ distinct
# srcs) without spoofing. Exponential IATs for the same beacon guard.
for i in range(INTERNAL.__len__()):            # all 20 hosts participate
    _t = 500.0 + random.expovariate(1.0)       # staggered joins
    while _t < 530.0:
        _amp_query(_t, INTERNAL[i], UDP_AMP_REFLECTOR,
                   random.choice(_UDP_BENIGN_QNAMES))
        _t += random.expovariate(0.6)          # ~0.6s IAT => ~1.7 qps/host

# ---------------- ATTACK 4: vertical port scan (500 ports) ----------------
for i in range(500):
    _tcp(400 + i * 0.03, INTERNAL[11], SCAN_TARGET, _sport(),
         20 + i * 2, 60, "S")

# ---------------- ATTACK 5: data exfiltration (2.8 MB to novel dst) ----------------
for i in range(2000):
    _tcp(480 + i * 0.03, INTERNAL[9], EXFIL_DST, 51000, 8443, 1400, "PA")

# ---------------- MESSY MODE (Item 6 FP pressure test) ----------------
# MESSY=1 env injects benign traffic patterns that stress the detectors:
#   - IoT-style periodic polling (low jitter, unlearned -> beacon FP risk)
#   - first-time large cloud-backup upload (-> exfil FP risk)
#   - CDN-style subdomain DNS (-> DGA FP risk)
import os as _os
if _os.environ.get("MESSY"):
    IOT_HOSTS = [(INTERNAL[15], "52.174.36.11", 20.0),   # periodic telemetry
                 (INTERNAL[16], "52.174.36.12", 15.0),
                 (INTERNAL[19], "52.174.36.13", 25.0)]
    for h, ip, period in IOT_HOSTS:
        n = int(DURATION / period)
        for i in range(n):
            tt = 2 + i * period + random.uniform(-0.1, 0.1)
            sp = _sport()
            _tcp(tt, h, ip, sp, 443, 60, "S")
            _tcp(tt + 0.01, h, ip, sp, 443, 90, "PA")
    # first-time 3MB cloud-backup upload from a benign host (t=150)
    for i in range(1200):
        _tcp(150 + i * 0.04, INTERNAL[4], "13.107.42.16", 53000, 443,
             1400, "PA")
    # CDN-style subdomain DNS (long labels with digits, benign brands)
    CDN_LABELS = ["edgecache01", "lbuseast5", "nodepool07", "assetsx91"]
    for h in INTERNAL[3:9]:
        t = random.uniform(0, 10)
        while t < DURATION:
            _dns_query(t, h, random.choice(CDN_LABELS) + "."
                       + random.choice(BENIGN_DOMAINS) + ".")
            t += random.expovariate(1 / 25.0)

# ---------------- write pcap (one direction only) ----------------
events.sort(key=lambda e: e[0])
pkts = []
for t, pkt in events:
    pkt.time = SIM_START + t
    pkts.append(pkt)

wrpcap(PCAP_PATH, pkts)
print(f"wrote {len(pkts)} packets over {DURATION:.0f}s sim time -> {PCAP_PATH}")
