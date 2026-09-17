"""Shared constants for the one-way NIDS prototype."""
import os

SIM_START = 1757452800.0          # epoch base for synthetic traffic
DURATION = 600.0                  # 10 minutes of simulated traffic

# Pipeline knobs
WINDOW = 10.0                     # detection window (seconds of sim time)
IDLE_TIMEOUT = 2.0                # flow idle timeout (seconds of sim time)
TICK_INTERVAL = 0.5               # stream flush cadence (seconds)

# Tier-0 allowlist: (dst_ip, dst_port) pairs that are known-periodic benign
# services. Beacon detector suppresses alerts for these (demo of Tier-0).
# OPERATOR-CURATED (not auto-learned): Item-6 pressure test surfaced the
# IoT telemetry endpoints below as beacon candidates; a real SOC reviews
# and allowlists them exactly this way (same workflow as RITA/AC-Hunter).
ALLOWLIST = {
    ("129.6.15.28", 123),         # benign NTP keepalive
    ("52.174.36.11", 443),        # IoT telemetry (pressure test)
    ("52.174.36.12", 443),        # IoT telemetry (pressure test)
    ("52.174.36.13", 443),        # IoT telemetry (pressure test)
}

# Detector thresholds (tuned for the synthetic traffic profile)
DDOS_MIN_PKT_WINDOW   = 1000      # min packets in a 10s window to consider
DDOS_MIN_SPOOF_SRCS   = 500       # distinct srcs => spoofed-source flood
DDOS_SYN_RATIO        = 0.70      # SYN ratio => SYN flood
SCAN_MIN_PAIRS        = 20        # distinct (dst,port) pairs per src per window
EXFIL_MIN_BYTES       = 500_000   # min bytes to novel dst in one window
EXFIL_RATIO           = 10.0      # vs per-src median baseline
BEACON_MAX_CV         = 0.25      # coefficient of variation of inter-flow IATs
BEACON_MIN_FLOWS      = 6         # min flows in a series before scoring
DGA_MIN_ENTROPY       = 3.3       # Shannon entropy of first qname label
DGA_MIN_LEN           = 10        # min label length
DGA_MAX_VOWEL_RATIO   = 0.25      # random alnum labels have ~14% vowels
DGA_MIN_DIGIT_RATIO   = 0.05      # ...and ~30% digits; English words have none
DGA_MIN_STREAK        = 3         # consecutive high-entropy queries from a src

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PCAP_PATH   = os.path.join(PROJECT_DIR, "traffic.pcap")
ALERTS_PATH = os.path.join(PROJECT_DIR, "alerts.jsonl")

# ---- time base: offline replay vs live capture ----------------------------
# Alert timestamps are rendered as TIME_ANCHOR + t (see detectors._iso).
# Offline runs anchor to SIM_START so replayed synthetic captures render the
# timestamps they were generated with (bit-identical to the original
# prototype output). Live runs call set_time_anchor(<wall clock at
# capture start>), so alerts carry real wall-clock timestamps rather than
# the 2025 synthetic sim dates.
TIME_ANCHOR = SIM_START          # rebased by set_time_anchor() at runtime

def set_time_anchor(epoch: float) -> None:
    """Rebase the pipeline clock. Called once by the live driver before any
    packet is processed; detectors read config.TIME_ANCHOR at emit time."""
    global TIME_ANCHOR
    TIME_ANCHOR = float(epoch)


# ---- live capture (AF_PACKET raw socket) ----------------------------------
CAPTURE_BATCH     = 64            # frames drained per recv burst
CAPTURE_RCVBUF    = 4 << 20       # SO_RCVBUF request (kernel may clamp)
CAPTURE_TIMEOUT   = 0.5           # socket recv timeout (s) -- bounds tick latency
LINE_RATE_SAMPLE  = 1             # keep 1 packet in N; 1 = analyse everything.
                                  # Guard for links whose rate exceeds the
                                  # single-core ceiling: process a deterministic
                                  # 1-in-N sample so windows stay representative
                                  # and the ringbuffer stops overflowing.

# ---- inventory persistence (restart-safe baseline) ------------------------
STATE_PATH       = os.path.join(PROJECT_DIR, "nids_state.json")
STATE_SAVE_EVERY = 30.0           # seconds between inventory checkpoints

# ---- TLS detector (Item 1) ----
from hello_profiles import MALWARE_JA4      # noqa: E402  (single source of truth)

TLS_PORTS        = {443, 8443}
BASELINE_SECONDS = 180.0        # inventory learning window (sim time)
KNOWN_BAD_JA4    = {MALWARE_JA4}  # simulated threat-intel feed
TLS_REAlert_SECS = 300.0        # dedupe window per (kind, src, ja4)

# ---- Fusion layer (Item 2) ----
FUSION_WINDOW     = 120.0       # sim-time window for cross-signal correlation
FUSION_MIN_CLASSES = 2          # distinct threat classes from one src

# ---- ML tier (Item 4) ----
# Ground-truth label rules derived from generator knowledge (the generator
# knows which hosts/destinations/times are attacking). Used ONLY by
# train_ml.py for training labels -- never by detectors.
ATTACK_HOST_ROLES = {
    "10.0.0.7":  "c2_implant",
    "10.0.0.9":  "botnet_dga",
    "10.0.0.11": "exfil",
    "10.0.0.13": "scanner",
    "10.0.0.17": "dns_tunnel",
}
VICTIM_IP      = "203.0.113.10"   # spoofed SYN-flood target
FLOOD_WINDOW   = (300.0, 320.0)
SCAN_TARGET_IP = "203.0.113.20"
EXFIL_DST_IP   = "45.33.32.156"
C2_IPS         = {"198.51.100.23", "198.51.100.99"}
ML_MODEL_PATH  = os.path.join(PROJECT_DIR, "model_ml.txt")
ML_PROBA_THRESHOLD = 0.95
ML_REAlert_SECS    = 60.0

# ---- DNS tunnelling detector (PS class c, second half) --------------------
# The PS asks for "Entropy/n-gram analysis of DNS query names, PLUS
# query-length and record-type anomalies". The DGA detector owns the lexical
# half; this owns the record-type/length/volume half: a channel that carries
# DATA inside qnames (or hides it in TXT/NULL queries) -- dnscat2, iodine,
# DNScat-style C2 channels.
#
# Discriminators are set against THIS repo's measured benign profiles, not
# guessed (see PLAN.md Item 12):
#   longest first-label the benign generator emits ......... 11  (CDN labels)
#   the DGA attack labels .................................. 14  (lexical path)
#   entropy of the CDN labels .............................. ~2.5 bits
# so a data label must be LONGER than anything benign/DGA-shaped and denser
# than anything a brand would serve:
DNS_TUNNEL_LABEL_MIN_LEN = 20      # data-carrying label length floor
DNS_TUNNEL_MIN_ENTROPY   = 3.5     # base32/base64 payload density
DNS_TUNNEL_MIN_STREAK    = 4       # consecutive encoded labels from one src
DNS_TUNNEL_MIN_QTYPE_RATIO = 0.60  # >=60% TXT/NULL queries => data channel
DNS_TUNNEL_MIN_QPS       = 2.0     # queries/s sustained => volume anomaly
DNS_TUNNEL_QPS_WINDOW    = 30.0    # trailing window for qtype/volume ratios
DNS_TUNNEL_MIN_WINDOW_QUERIES = 8  # min evidence before window paths score
DNS_TUNNEL_REALERT_SECS  = 120.0   # dedupe per (src, mechanism)

# Ground truth (ml_tier labels + generator): the compromised tunnel host and
# the authoritative domain it exfiltrates through.
DNS_TUNNEL_HOST   = "10.0.0.17"    # INTERNAL[15]
DNS_TUNNEL_DOMAIN = "tunnel.example.com"

# ---- UDP reflection/amplification detector (PS class (a), second half) -----
# The PS names "UDP reflection/amplification" inside class (a); until Item 13
# only the volumetric symptom (rate + entropy) was caught, not the reflection
# signature. Discriminators are MEASURED against this repo's benign corpus
# (see udp_amp.py docstring): benign service-query load is ~1 qps aggregate
# (~10 queries / ~8 srcs per 10s window; one 90B NTP keepalive per 30s), so
# every gate below sits 3-6x above anything benign traffic produces.
UDP_AMP_MIN_QPS_WINDOW = 60     # min queries to ONE service before rate scores
UDP_AMP_MIN_QPS        = 3.0    # sustained qps to one service => rate anomaly
UDP_AMP_MIN_PKTS       = 300    # min amplifier-port packets before burst/fanout
UDP_AMP_SMALL_SHARE    = 0.90   # >=90% tiny frames => query-storm shape
UDP_AMP_SMALL_BYTES    = 128    # small-frame floor (benign NTP keepalive=90B)
UDP_AMP_MIN_SRCS       = 30     # distinct srcs in a window => unspoofed fan-out
UDP_AMP_WINDOW         = 10.0   # detector's own window (matches WINDOW)
UDP_AMP_REALERT_SECS   = 120.0  # re-arm after this much quiet per campaign

# Ground truth (generator/ml_tier): the amplification campaign and its target.
UDP_AMP_START     = 180.0       # campaign window start (sim time)
UDP_AMP_END       = 240.0       # campaign window end
UDP_AMP_REFLECTOR = "198.18.0.53"   # open DNS reflector the botnet abuses
UDP_AMP_VICTIM    = "203.0.113.30"  # spoofed source = the victim's address

# ---- DGA character CNN (Tier-2 confirmer on the DNS path) -----------------
# The Tier-1 lexical rules stay exactly as they are; the CNN is an ADDITIONAL,
# opt-in (--dga-cnn) confirmer for the labels the rules cannot separate --
# dictionary DGA families (suppobox/matsnu) build low-entropy, perfectly
# lexical labels, so no entropy threshold can catch them.
DGA_CNN_MODEL_PATH   = os.path.join(PROJECT_DIR, "model_dga_cnn.npz")
DGA_CNN_PROB         = 0.90    # confirmer fires unaided above this prob...
DGA_CNN_MIN_STREAK   = 4       # ...after this many consecutive CNN-positive
                               #     labels from one source (quorum, not one
                               #     label: a single odd hostname is not an
                               #     incident)
#
# 4 is MEASURED, not guessed. bench_dga.py sweeps it against a real benign
# corpus (andrewaeva/DGA, Alexa top-1M): per-string the CNN scores 16.5% of
# 1,000,000 real benign first-labels above 0.5, so a 2-label quorum fired on
# 17.3 alerts/hour OF A PURELY BENIGN HOST (tier2_cnn_only; the Tier-1
# 3-streak path stayed near-silent at ~0.02/h). Full-corpus sweep, benign
# alerts/hour vs DGA families still hit:
#     k=2  17.33/h  8/8        k=4  0.46/h  7/8   <- shipped
#     k=3   3.60/h  8/8        k=5  0.07/h  6/8
#     k=6   0.05/h  6/8        k=8   0.05/h 5/8
# k=5 buys no further separation over the noise floor and starts costing
# pushdo (164 queries to first alert vs 13 at k=4). Full-corpus numbers are
# the record (dga_bench.json / BENCH-DGA.md); they slightly REVISED the
# earlier quick-run estimates (0.36/h, 6/8), which is the point of running
# the whole corpus rather than shipping a 20k-sample guess.
DGA_CNN_REALERT_SECS = 120.0   # re-alert window per (src, kind)
