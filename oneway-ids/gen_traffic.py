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
    - Vertical port scan (500 ports)  t in [400, 415)  -> 203.0.113.20
    - Data exfiltration (2.8 MB)      t in [480, 540)  -> 45.33.32.156:8443
"""
import random
from scapy.all import Ether, IP, TCP, UDP, DNS, DNSQR, Raw, wrpcap

from config import SIM_START, DURATION, PCAP_PATH, BASELINE_SECONDS
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


def _dns_query(t, src, qname):
    events.append((t, Ether() / IP(src=src, dst=DNS_SERVER) /
                   UDP(sport=_sport(), dport=53) /
                   DNS(rd=1, qd=DNSQR(qname=qname))))


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

# ---------------- ATTACK 3: SYN flood, spoofed sources ----------------
for _ in range(3000):
    _tcp(random.uniform(300, 320), _spoofed_ip(), VICTIM,
         _sport(), 443, 60, "S")

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
