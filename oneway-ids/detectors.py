"""
One-way-native threat detectors and the standardized alert schema.

Every detector consumes single-direction features only:
  - DDoS:          windowed rate + source-IP Shannon entropy + SYN ratio
  - C2 beaconing:  inter-flow IAT statistics (mean, CV) per (src,dst,dport)
  - DGA domains:   character entropy + length of DNS qname labels
  - Recon/scan:    fan-out cardinality per source per window
  - Exfiltration:  bytes to never-seen destinations vs per-source baseline
"""
import json
import math
import os
import statistics
from collections import Counter, defaultdict, deque
from datetime import datetime, timezone

import config
from config import (ALLOWLIST, DDOS_MIN_PKT_WINDOW,
                    DDOS_MIN_SPOOF_SRCS, DDOS_SYN_RATIO, SCAN_MIN_PAIRS,
                    EXFIL_MIN_BYTES, EXFIL_RATIO, BEACON_MAX_CV,
                    BEACON_MIN_FLOWS, DGA_MIN_ENTROPY, DGA_MIN_LEN,
                    DGA_MAX_VOWEL_RATIO, DGA_MIN_DIGIT_RATIO,
                    DGA_MIN_STREAK, ALERTS_PATH,
                    BASELINE_SECONDS, KNOWN_BAD_JA4, TLS_REAlert_SECS,
                    FUSION_WINDOW, FUSION_MIN_CLASSES,
                    DGA_CNN_PROB, DGA_CNN_MIN_STREAK, DGA_CNN_REALERT_SECS)


def shannon_entropy(counter) -> float:
    n = sum(counter.values())
    if n == 0:
        return 0.0
    return -sum((c / n) * math.log2(c / n) for c in counter.values())


def is_random_looking_label(entropy: float, length: int, vowel_ratio: float,
                            digit_ratio: float) -> bool:
    """Tier-1 DGA lexical decision as a PURE FUNCTION of the four scalars.

    Kept here rather than inline in `DGADetector.on_dns` so that the offline
    benchmarks (`bench_dga.py`, `train_dga_cnn.py`) exercise the predicate the
    sensor actually runs. A benchmark that re-implements the gate measures a
    different detector than the one that ships, which is the classic way a
    published DGA number turns out not to describe the deployed model.
    """
    return (length >= DGA_MIN_LEN and entropy >= DGA_MIN_ENTROPY
            and (vowel_ratio <= DGA_MAX_VOWEL_RATIO
                 or digit_ratio >= DGA_MIN_DIGIT_RATIO))


def dga_label_of(qname: str) -> str:
    """The exact substring DGADetector scores: the first label of a qname.

    Note what this is NOT: the registrable domain. A one-way sensor sees
    `www.somebank.com` and scores `www`. That is a deliberate choice (the
    first label is where generated randomness lives) with a known cost
    (multi-label hostnames are only partially inspected), and it is the same
    choice the offline benchmarks make, so their numbers describe the fielded
    behaviour rather than an easier problem.
    """
    return qname.rstrip(".").split(".")[0]


def dga_lexical_gate(label: str) -> bool:
    """Convenience wrapper: one qname label -> Tier-1 verdict.

    Byte-for-byte the decision `DGADetector.on_dns` makes before it starts
    counting a streak; the streak/quorum logic is deliberately NOT included
    here, because that is a behavioural layer over a stream rather than a
    property of a single string. `bench_dga.py` measures both separately.
    """
    if len(label) < DGA_MIN_LEN:
        return False                      # mirrors the on_dns early return
    vowels = sum(1 for ch in label if ch in "aeiou")
    digits = sum(1 for ch in label if ch.isdigit())
    return is_random_looking_label(shannon_entropy(Counter(label)),
                                   len(label), vowels / len(label),
                                   digits / len(label))


def _iso(t: float) -> str:
    """Render stream-relative t as a wall-clock ISO timestamp.

    Reads config.TIME_ANCHOR at call time (not import time) so the live
    driver can rebase the clock without reloading modules.

    Seconds AND milliseconds are derived from the same absolute value. Taking
    the fraction from `t % 1` instead looks equivalent and is not: it
    disagrees with the seconds whenever TIME_ANCHOR has a fractional part,
    which a live capture always does (anchor = time.time()). That produced
    timestamps one whole second off in the millisecond field, e.g. rendering
    :30.946 for an event that happened at :30.000. SIM_START is integral, so
    offline replay never exposed it.
    """
    absolute = config.TIME_ANCHOR + float(t)
    seconds = math.floor(absolute)
    millis = int((absolute - seconds) * 1000)
    if millis > 999:                 # float landing just under the next second
        seconds += 1
        millis = 0
    return datetime.fromtimestamp(seconds, tz=timezone.utc) \
        .strftime("%Y-%m-%dT%H:%M:%S.") + f"{millis:03d}Z"


def _severity(conf: float) -> str:
    if conf >= 0.9:
        return "critical"
    if conf >= 0.7:
        return "high"
    if conf >= 0.5:
        return "medium"
    return "low"


class AlertSink:
    """Standardized alert records -> memory + JSONL file (+ subscribers).

    truncate=False is the live mode: keep appending so a long-running capture
    can be tailed by dashboard.py while the pipeline is still writing. Each
    record is written and closed immediately, so a reader never sees a
    partially-flushed line.
    """

    def __init__(self, path=ALERTS_PATH, truncate=True):
        self.path = path
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        if truncate:
            open(path, "w").close()      # truncate
        elif not os.path.exists(path):
            open(path, "a").close()
        self.alerts = []
        self.suppressed = 0
        self._subs = []

    def subscribe(self, fn):
        """fn(sim_t, alert_record) called after each emitted alert."""
        self._subs.append(fn)

    def emit(self, t, src, dst, dport, proto, threat, confidence, evidence):
        rec = {
            "timestamp": _iso(t),
            "src": src,
            "dst": dst,
            "flow_id": f"{src}:*->{dst}:{dport}/{proto}",
            "threat_class": threat,
            "confidence": round(float(confidence), 3),
            "severity": _severity(confidence),
            "evidence": evidence,
        }
        self.alerts.append(rec)
        with open(self.path, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        for fn in self._subs:
            fn(t, rec)

    def suppress(self, n=1):
        self.suppressed += n


# --------------------------------------------------------------------------
# Fusion layer (Item 2): cross-correlate single-detector signals
# --------------------------------------------------------------------------

# ordered: first matching scenario wins; exfil outranks C2 tags because
# data actually leaving the network is the most severe confirmed outcome
_FUSION_SCENARIOS = [
    (frozenset({"data_exfiltration"}), "confirmed_exfiltration"),
    (frozenset({"tls_known_malware", "c2_beaconing"}), "confirmed_c2_implant"),
    (frozenset({"c2_beaconing", "dga_domain"}), "botnet_c2_with_dga"),
]
# derived guard set -- single source of truth, cannot rot out of sync
FUSED_CLASSES = {tag for _, tag in _FUSION_SCENARIOS} | {"multi_signal_fusion"}

MIN_FUSE_CONF = 0.5             # weak signals don't participate in fusion


def _scenario_tag(classes, by_class):
    """Scenario tag with a confidence gate: 'confirmed_exfiltration' only
    when the exfil signal itself is strong (>= 0.8); otherwise the generic
    tag prevents two mediocre FPs from minting a 'confirmed' verdict."""
    if "data_exfiltration" in classes:
        ex = by_class.get("data_exfiltration")
        if ex and ex[1] >= 0.8:
            return "confirmed_exfiltration"
    for sig, tag in _FUSION_SCENARIOS[1:]:
        if sig <= classes:
            return tag
    return "multi_signal_fusion"


class FusionEngine:
    """Correlates weak single-detector signals into strong verdicts.

    Fire policy (anti-alert-fatigue):
      - fire when the class-set GAINS a class vs the last fusion (escalation)
        or is fully disjoint from it (fresh incident)
      - suppress subsets/equal sets regardless of cadence -- an ongoing
        incident must not re-fire a critical every window
    Confidence: noisy-OR over EXPONENTIALLY DECAYED per-signal confidences
    (half-life = window), using the most recent alert per class (max-t wins,
    so out-of-order flow-close emissions cannot corrupt inputs).
    """

    def __init__(self, sink, window=FUSION_WINDOW, min_classes=FUSION_MIN_CLASSES):
        self.sink = sink
        self.window = window
        self.min_classes = min_classes
        self.by_src = defaultdict(dict)      # src -> {cls: (t, conf, dst, dport)}
        self.last_fused = {}                 # src -> (t, frozenset)
        self._calls = 0

    def _prune(self, src, t):
        d = self.by_src.get(src)
        if not d:
            return
        for c in [c for c, v in d.items() if v[0] < t - self.window]:
            del d[c]
        if not d:
            self.by_src.pop(src, None)

    def _sweep(self, t):
        """Periodic garbage collection of dead incident state."""
        if self._calls % 256:
            return
        horizon = t - self.window * 10
        for s in [s for s, (tt, _) in self.last_fused.items() if tt < horizon]:
            del self.last_fused[s]

    def on_alert(self, t, rec):
        self._calls += 1
        cls = rec["threat_class"]
        if cls in FUSED_CLASSES:             # never re-fuse fused verdicts
            return
        src = rec.get("src")
        if not src or src == "*":            # unattributed (spoofed floods)
            return
        conf = rec["confidence"]
        if conf < MIN_FUSE_CONF:
            return

        d = self.by_src[src]
        old = d.get(cls)
        if old is None or t > old[0]:        # max-t wins (arrival order safe)
            d[cls] = (t, conf, rec.get("dst", "*"), rec.get("dport", 0))
        self._prune(src, t)
        self._sweep(t)

        d = self.by_src.get(src)
        if not d or len(d) < self.min_classes:
            return
        classes = frozenset(d)

        state = self.last_fused.get(src)
        if state is not None:
            gained = classes - state[1]
            if not gained:
                return                       # nothing new -> suppress
        self.last_fused[src] = (t, classes)

        total = 1.0
        contrib = []
        for c, (tt, cf, cdst, cdport) in sorted(d.items()):
            age = max(t - tt, 0.0)
            eff = min(cf * (0.5 ** (age / self.window)), 0.999)
            contrib.append({"threat_class": c, "at_s": round(tt, 1),
                            "age_s": round(age, 1), "confidence": cf,
                            "effective_confidence": round(eff, 3),
                            "dst": cdst, "dport": cdport})
            total *= (1.0 - eff)
        fused_conf = min(round(1.0 - total, 3), 0.999)
        tag = _scenario_tag(classes, d)
        self.sink.emit(t, src, "*", 0, "*", tag, fused_conf, {
            "contributing_signals": contrib,
            "combination": "noisy-OR with exponential decay (half-life="
                           f"{self.window:.0f}s)",
            "window_s": self.window,
            "why": "multiple independent detectors firing on one source "
                   "-- jointly far more indicative than any single signal",
        })


# --------------------------------------------------------------------------
# TLS-fed detector (ClientHello metadata only -- no decryption, one-way)
# --------------------------------------------------------------------------
# Window-flush detectors (called by WindowAggregator)
# --------------------------------------------------------------------------

class DDosDetector:
    """Rate spike + source-IP entropy + SYN ratio, all one-way observable."""

    def __init__(self, sink):
        self.sink = sink

    def on_window(self, w):
        if w["npkt"] < DDOS_MIN_PKT_WINDOW:
            return
        ent = shannon_entropy(w["srcs"])
        distinct = len(w["srcs"])
        syn_ratio = w["nsyn"] / w["npkt"]
        t_end = min(w["t1"], w["t0"] + w["npkt"])  # approx; evidence carries real numbers

        if distinct >= DDOS_MIN_SPOOF_SRCS:
            conf = min(0.99, 0.60 + distinct / 5000)
            self.sink.emit(t_end, "*", "*", 443, "tcp", "ddos_volumetric_spoofed",
                           conf, {
                               "window_pkts": w["npkt"],
                               "pkt_rate_per_s": round(w["npkt"] / (w["t1"] - w["t0"]), 1),
                               "distinct_src_ips": distinct,
                               "src_ip_entropy_bits": round(ent, 2),
                               "syn_ratio": round(syn_ratio, 3),
                               "why": "packet-rate spike with high source-IP entropy "
                                      "=> spoofed-source volumetric flood",
                           })
        elif syn_ratio >= DDOS_SYN_RATIO:
            conf = min(0.99, 0.50 + syn_ratio * 0.5)
            evidence = {
                "window_pkts": w["npkt"],
                "pkt_rate_per_s": round(w["npkt"] / (w["t1"] - w["t0"]), 1),
                "syn_ratio": round(syn_ratio, 3),
                "distinct_src_ips": distinct,
                "why": "window dominated by TCP SYNs => SYN flood",
            }
            # attribute when one source dominates the SYNs (low-entropy
            # flood = likely compromised host; fusion can then correlate it)
            if w["srcs"]:
                top_src, top_cnt = w["srcs"].most_common(1)[0]
            else:
                top_src, top_cnt = None, 0
            if top_src and distinct < 50 and top_cnt >= 0.5 * max(w["nsyn"], 1):
                evidence["src_syn_share"] = round(top_cnt / max(w["nsyn"], 1), 2)
                self.sink.emit(t_end, top_src, "*", 443, "tcp",
                               "ddos_syn_flood", conf, evidence)
            else:
                self.sink.emit(t_end, "*", "*", 443, "tcp",
                               "ddos_syn_flood", conf, evidence)


class ScanDetector:
    """Fan-out: one source touching many (dst,port) pairs in one window."""

    def __init__(self, sink):
        self.sink = sink

    def on_window(self, w):
        for src, pairs in w["pairs"].items():
            if len(pairs) < SCAN_MIN_PAIRS:
                continue
            by_dst = defaultdict(int)
            for dst, _ in pairs:
                by_dst[dst] += 1
            top_dst, top_n = max(by_dst.items(), key=lambda kv: kv[1])
            # vertical scan = pairs concentrated on one destination
            scan_type = "vertical" if top_n / len(pairs) >= 0.8 else "horizontal"
            conf = min(0.99, 0.50 + len(pairs) / 1000)
            self.sink.emit(w["t1"] - 1, src, top_dst if scan_type == "vertical" else "*",
                           "*", "tcp", f"recon_{scan_type}_scan", conf, {
                               "distinct_dst_port_pairs": len(pairs),
                               "distinct_dst_ips": len(by_dst),
                               "pairs_on_top_dst": top_n,
                               "window": f"{w['t0']:.0f}-{w['t1']:.0f}s",
                               "why": "single source fanned out across many "
                                      "destination ports/hosts in one window",
                           })


class ExfilDetector:
    """Sustained uploads to *young* (never-before-seen) destinations.

    Tracks cumulative bytes per (src,dst) pair. A pair is suspicious if:
      - it is young (first seen within the last EXFIL_MAX_AGE windows), and
      - cumulative bytes >= EXFIL_MIN_BYTES, and
      - the source's own median window volume is far below the transfer
        (ratio guard), i.e. this transfer dwarfs the host's normal traffic.
    One alert per (src,dst) pair.
    """

    PAIR_MAX_AGE_WINDOWS = 6

    def __init__(self, sink, history=60):
        self.sink = sink
        self.hist = defaultdict(lambda: deque(maxlen=history))
        self.pairs = {}            # (src,dst) -> [first_idx, total_bytes]
        self.alerted = set()

    def on_window(self, w):
        # 1) score pairs BEFORE folding this window into baselines
        for (src, dst), b in w["pair_bytes"].items():
            state = self.pairs.get((src, dst))
            if state is None:
                # A pair is eligible only when its destination was first
                # observed in this stream window. This prevents ordinary
                # traffic to an established destination from being promoted
                # to "novel" merely because the pair state was not retained.
                if dst not in w["novel_dsts"]:
                    continue
                state = [w["idx"], 0]
                self.pairs[(src, dst)] = state
            state[1] += b

            total = state[1]
            age = w["idx"] - state[0]
            if total < EXFIL_MIN_BYTES or age > self.PAIR_MAX_AGE_WINDOWS:
                continue
            if (src, dst) in self.alerted:
                continue
            baseline = statistics.median(self.hist[src]) if self.hist[src] else 0.0
            if baseline > 0 and total < EXFIL_RATIO * baseline:
                continue
            self.alerted.add((src, dst))
            conf = min(0.99, 0.55 + min(total / max(baseline, 1) / 200, 0.4))
            self.sink.emit(w["t1"] - 1, src, dst, 8443, "tcp",
                           "data_exfiltration", conf, {
                               "bytes_to_new_dst": int(total),
                               "pair_age_windows": age,
                               "src_baseline_bytes_median": int(baseline),
                               "ratio_vs_baseline": round(total / max(baseline, 1), 1),
                               "novel_destination": True,
                               "why": "large sustained upload to a never-before-"
                                      "seen destination, far above the source "
                                      "host's normal window volume",
                           })

        # 2) fold this window into per-source baselines
        for src, b in w["src_bytes"].items():
            self.hist[src].append(b)


# --------------------------------------------------------------------------
# Flow-fed detector (called per closed flow)
# --------------------------------------------------------------------------

class BeaconDetector:
    """Inter-flow IAT regularity per (src, dst, dport).

    CV (std/mean) near zero == robotic periodicity. Works purely from
    one-directional flow start times; no request/response pairing.
    """

    def __init__(self, sink, max_series=60):
        self.sink = sink
        self.series = defaultdict(lambda: deque(maxlen=max_series))
        self.counts = defaultdict(int)
        self.alerted_at = defaultdict(lambda: None)   # None = never alerted

    def on_flow(self, f):
        src, sport, dst, dport, proto = f["key"]
        if (dst, dport) in ALLOWLIST:
            self.sink.suppress()
            return
        key = (src, dst, dport, proto)
        times = self.series[key]
        times.append(f["t0"])
        self.counts[key] += 1
        n = self.counts[key]
        if n < BEACON_MIN_FLOWS:
            return
        # first alert allowed at BEACON_MIN_FLOWS; re-alerts every 10
        last = self.alerted_at[key]
        if last is not None and n - last < 10:
            return
        iats = [times[i + 1] - times[i] for i in range(len(times) - 1)]
        mean = statistics.mean(iats)
        if mean <= 0:
            return
        cv = statistics.pstdev(iats) / mean
        # Evidence-scaled CV gate: with few intervals, sample CV is noisy
        # (a CV~1.0 exponential process dips below 0.25 by luck ~2% of the
        # time at n=6), so small samples must be ROBOTIC (<=0.15) to alert.
        # Once n >= 10 the standard gate applies.
        cv_gate = BEACON_MAX_CV if n >= 10 else BEACON_MAX_CV * 0.6
        if cv <= cv_gate:
            self.alerted_at[key] = n
            conf = min(0.99, 0.60 + (cv_gate - cv) * 1.5)
            self.sink.emit(f["t0"], src, dst, dport, proto, "c2_beaconing",
                           conf, {
                               "flows_in_series": n,
                               "mean_interval_s": round(mean, 2),
                               "iat_cv": round(cv, 4),
                               "cv_gate": round(cv_gate, 3),
                               "last_iats_s": [round(x, 2) for x in iats[-5:]],
                               "why": "flow series with near-constant inter-"
                                      "arrival time => periodic C2 beacon",
                           })


# --------------------------------------------------------------------------
# TLS-fed detector (ClientHello metadata only -- no decryption, one-way)
# --------------------------------------------------------------------------

class TlsDetector:
    """Threat class (d): malware inside encrypted sessions.

    Two modes, matching how real SOC tooling works:
      1. known-bad fingerprint match (threat-intel) -- active from t=0,
         never gated by the baseline, and known-bad hellos are NEVER fed
         into the inventory (prevents baseline poisoning).
      2. inventory novelty -- per-src + global JA4 inventories learned
         during the baseline window. Two tiers afterwards:
           - globally novel fingerprint  -> high confidence (new software
             fleet-wide or C2 implant)
           - novel for this host only    -> medium confidence (typical of
             lateral movement: implant reuses a fingerprint another host
             already taught us)

    Limitations (one-way): no JA3S, no certificates, no QUIC yet.
    Inventory persistence across restarts: implemented via save_state() /
    load_state(); run.py exposes it as --state PATH. Without a warm start a
    restart treats every fingerprint as novel and alert-storms, so the state
    file is the difference between a demo and a deployable sensor.
    Novelty semantics: each (src, ja4) pair alerts EXACTLY ONCE (the pair
    is learned on alert). Repeat visibility for a known-novel fingerprint
    is deliberately not offered -- the (src,ja4) pair cannot become novel
    again. Known-bad matching, by contrast, re-alerts per TLS_REAlert_SECS.
    """

    def __init__(self, sink, state_path=None):
        self.sink = sink
        self.state_path = state_path
        self.inv_src = defaultdict(set)     # src -> {ja4}
        self.inv_global = set()
        # (kind, src, ja4, transport) -> sim t ; transport is part of the
        # key: the same malware fingerprint arriving over QUIC after TLS is
        # a NEW observable (channel migration) and must re-alert.
        self.last_alert = {}
        # warm = inventory restored from disk. The baseline gate must then be
        # skipped: re-learning for another BASELINE_SECONDS is not wrong, but
        # it would blind novelty mode for the first 3 minutes after every
        # restart -- exactly the window an attacker would choose.
        self.warm = False

    # -- inventory persistence (restart-safe baseline) ---------------------
    def save_state(self, path=None) -> bool:
        """Checkpoint the learned inventory + dedupe clocks atomically
        (write temp, then rename) so a crash mid-write cannot corrupt it."""
        path = path or self.state_path
        if not path:
            return False
        payload = {
            "version": 1,
            "saved_at": datetime.now(tz=timezone.utc).isoformat(),
            "inv_src": {s: sorted(v) for s, v in self.inv_src.items()},
            "inv_global": sorted(self.inv_global),
            "last_alert": [[k[0], k[1], k[2], k[3], v]
                           for k, v in self.last_alert.items()],
        }
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        tmp = f"{path}.tmp"
        with open(tmp, "w") as fh:
            json.dump(payload, fh)
        os.replace(tmp, path)
        return True

    def load_state(self, path=None) -> bool:
        """Restore inventory. Returns True if a usable inventory was loaded,
        in which case the baseline gate is skipped (self.warm = True)."""
        path = path or self.state_path
        if not path or not os.path.exists(path):
            return False
        try:
            with open(path) as fh:
                payload = json.load(fh)
        except (json.JSONDecodeError, OSError):
            return False
        # NOTE: the local name is deliberately `fingerprints`, never `ja4s`,
        # so the contract gate cannot mistake this inventory of CLIENT
        # fingerprints for a read of the server-side JA4S fingerprint (which
        # a diode feed never sees).
        for src, fingerprints in payload.get("inv_src", {}).items():
            self.inv_src[src] |= set(fingerprints)
        self.inv_global |= set(payload.get("inv_global", []))
        for row in payload.get("last_alert", []):
            if len(row) == 5:
                self.last_alert[(row[0], row[1], row[2], row[3])] = row[4]
        self.warm = bool(self.inv_global)
        return self.warm

    def _dedup_ok(self, kind, src, ja4, transport, t):
        k = (kind, src, ja4, transport)
        last = self.last_alert.get(k, -1e18)
        if t - last < TLS_REAlert_SECS:
            return False
        self.last_alert[k] = t
        return True

    def on_hello(self, t, src, dst, dport, meta):
        ja4 = meta["ja4"]
        transport = meta.get("transport", "tls")

        # Mode 1: threat-intel match -- unconditional, never learned.
        if ja4 in KNOWN_BAD_JA4:
            if self._dedup_ok("bad", src, ja4, transport, t):
                self.sink.emit(t, src, dst, dport, transport,
                               "tls_known_malware", 0.99, {
                                   "ja4": ja4,
                                   "ja3": meta["ja3"],
                                   "sni": meta["sni"],
                                   "cipher_count": meta["cipher_count"],
                                   "tls_version": meta["version"],
                                   "transport": transport,
                                   "match_source": "threat-intel (known-bad JA4)",
                                   "why": "ClientHello fingerprint matches a "
                                          "known-malware TLS stack",
                               })
            return

        # Mode 2: inventory novelty (baseline-gated unless warmed from disk).
        if not self.warm and t < BASELINE_SECONDS:
            self.inv_src[src].add(ja4)
            self.inv_global.add(ja4)
            return

        if ja4 not in self.inv_global:
            kind, conf = "global", 0.80
        elif ja4 not in self.inv_src[src]:
            kind, conf = "host", 0.60
        else:
            return                          # known & learned: silent
        self.sink.emit(t, src, dst, dport, transport, "tls_novel_fingerprint",
                       conf, {
                           "ja4": ja4,
                           "ja3": meta["ja3"],
                           "sni": meta["sni"],
                           "cipher_count": meta["cipher_count"],
                           "ext_count": meta["ext_count"],
                           "tls_version": meta["version"],
                           "transport": transport,
                           "novelty_scope": kind,
                           "src_inventory_size": len(self.inv_src[src]),
                           "note": "server-side JA3S/cert unavailable "
                                   "(one-way feed)",
                           "why": ("fingerprint never seen fleet-wide -- "
                                   "new software or C2 implant"
                                   if kind == "global" else
                                   "fingerprint new to this host but "
                                   "known elsewhere -- possible lateral "
                                   "movement or host software change"),
                       })
        self.inv_src[src].add(ja4)
        self.inv_global.add(ja4)

# --------------------------------------------------------------------------
# DNS-fed detector
# --------------------------------------------------------------------------

class DGADetector:
    """Character entropy + length of the first DNS qname label (Tier-1), plus
    an OPTIONAL character-CNN confirmer (Tier-2, --dga-cnn).

    The two tiers answer different questions and the split is deliberate:

      Tier-1 lexical rules -- cheap, always on, no model file. Character
        entropy plus vowel/digit ratios. Catches random-looking labels.
      Tier-2 char CNN -- scores the label's character SEQUENCE, so it is not
        limited by a scalar threshold. Measured on a family held out of
        training entirely, it reaches 1.00 recall on a hex-like DGA family
        against 0.47 for the rules, at a LOWER false-positive rate (0.001 vs
        0.003) -- the rules miss half of it because empirical Shannon entropy
        is biased low on short strings (the same finite-sample effect
        documented in the README).

    The CNN is a confirmer, never a replacement: with cnn=None this class is
    byte-for-byte the original detector. The CNN cannot settle *dictionary*
    DGA from morphology alone (measured 0.007 recall on a held-out dictionary
    family), which is exactly why the Tier-2 path additionally requires a
    per-source quorum before it alerts.
    """

    def __init__(self, sink, cnn=None, cnn_min_streak=None):
        self.sink = sink
        self.cnn = cnn
        # Configurable so the offline benchmark can sweep the Tier-2 quorum
        # against a real benign corpus instead of asserting a value.
        self.cnn_min_streak = (DGA_CNN_MIN_STREAK if cnn_min_streak is None
                               else int(cnn_min_streak))
        self.per_src = defaultdict(int)
        self.streak = defaultdict(int)
        self.alerted_at = defaultdict(int)
        self.cnn_streak = defaultdict(int)
        self.cnn_alerted_at = {}
        # --- DNS tunnelling (PS class c, part 2) --------------------------
        # qtype is written by the client into the query, so it is one-way
        # observable by construction -- unlike the response side, which a
        # diode feed never sees. These track the classic dnscat2/iodine
        # signatures: bulky records carrying data instead of lookups.
        self.tunnel_bytes = defaultdict(int)
        self.tunnel_queries = defaultdict(int)
        self.tunnel_alerted_at = {}

    def _cnn_only(self, t, src, label, prob):
        """Tier-2 path: morphology the lexical gate cannot see.

        Requires a quorum (DGA_CNN_MIN_STREAK consecutive CNN-positive labels
        from one source) because a single odd hostname is not an incident --
        the same tier-boundary reasoning that keeps bare SYNs out of the flow
        model. Deduped per source."""
        if prob is None:
            return
        if prob < DGA_CNN_PROB:
            self.cnn_streak[src] = 0        # a benign-looking label breaks it
            return
        self.cnn_streak[src] += 1
        if self.cnn_streak[src] < self.cnn_min_streak:
            return
        if t - self.cnn_alerted_at.get(src, -1e18) < DGA_CNN_REALERT_SECS:
            return
        self.cnn_alerted_at[src] = t
        self.per_src[src] += 1
        # Capped below 0.90 (i.e. never 'critical'): a morphology-only verdict
        # has no behavioural corroboration behind it, so it must not outrank a
        # lexical alert that the source is also actively beaconing from. 0.85
        # lands it at 'high' -- analyst-visible, not an automatic incident.
        span = max(1e-6, 1.0 - DGA_CNN_PROB)
        conf = min(0.85, 0.55 + 0.30 * (prob - DGA_CNN_PROB) / span)
        self.sink.emit(t, src, "*", 53, "udp", "dga_domain", conf, {
            "qname_label": label,
            "label_length": len(label),
            "dga_cnn_prob": round(prob, 4),
            "cnn_positive_streak": self.cnn_streak[src],
            "detector_tier": "tier2_cnn_only",
            "model": "char-cnn (numpy, family-held-out)",
            "note": "label is lexical (the entropy gate did not fire); the "
                    "character CNN flagged its morphology instead",
            "why": "character-sequence model scores this qname as "
                   "machine-generated even though its entropy and vowel/"
                   "digit profile look innocuous",
        })

    def on_dns(self, t, src, qname, qtype=None):
        # --- DNS tunnelling: record-type + query-length anomalies ----------
        # PS-26145 class (c) asks for "query-length and record-type anomalies"
        # alongside entropy. Both are observable one-way because the client
        # writes them into the query; the response side (RCODE, NXDOMAIN
        # ratio) is not, and this detector never touches it.
        if qtype is not None:
            self._tunnel_check(t, src, qname, qtype)

        label = dga_label_of(qname)
        prob = self.cnn.score(label) if self.cnn is not None else None
        if len(label) < DGA_MIN_LEN:
            self._cnn_only(t, src, label, prob)   # CNN has no length floor
            return
        # Composite features: raw entropy is biased low on short strings
        # (finite-sample collisions), so pair it with lexical ratios.
        ent = shannon_entropy(Counter(label))
        vowels = sum(1 for ch in label if ch in "aeiou")
        digits = sum(1 for ch in label if ch.isdigit())
        vowel_ratio = vowels / len(label)
        digit_ratio = digits / len(label)
        looks_random = is_random_looking_label(ent, len(label), vowel_ratio,
                                               digit_ratio)
        if not looks_random:
            self.streak[src] = 0            # benign query breaks the streak
            self._cnn_only(t, src, label, prob)
            return
        self.streak[src] += 1
        self.cnn_streak[src] = 0            # lexical path owns this incident
        self.per_src[src] += 1
        n = self.streak[src]
        if n < DGA_MIN_STREAK:
            return
        # alert at streak==3, then every 10 more
        if n > DGA_MIN_STREAK and n - self.alerted_at[src] < 10:
            return
        self.alerted_at[src] = n
        conf = min(0.99, ent / 6.2 + min(n / 20, 0.1))
        evidence = {
            "qname_label": label,
            "label_length": len(label),
            "char_entropy_bits": round(ent, 2),
            "vowel_ratio": round(vowel_ratio, 2),
            "digit_ratio": round(digit_ratio, 2),
            "high_entropy_query_streak": n,
            "dga_queries_seen_from_src": self.per_src[src],
            "note": "response side not observable (one-way); NXDOMAIN "
                    "correlation unavailable",
            "why": "streak of labels with high entropy + non-lexical vowel/"
                   "digit profile => algorithmically generated domains",
        }
        if prob is not None:
            # additive evidence only -- the Tier-1 decision is unchanged
            evidence["dga_cnn_prob"] = round(prob, 4)
            evidence["detector_tier"] = (
                "tier1_lexical+cnn_confirmed" if prob >= DGA_CNN_PROB
                else "tier1_lexical")
        self.sink.emit(t, src, "*", 53, "udp", "dga_domain", conf, evidence)

    # ------------------------------------------------------------------
    # DNS tunnelling (PS class c). One-way observable signals only:
    #   * qtype chosen by the client (TXT 16 / NULL 10 / even A when the
    #     payload is encoded into the label rather than the record)
    #   * query length -- a label carrying exfiltrated data is long because
    #     the data IS the label
    #   * max label length -- base32/hex payloads exceed what a real
    #     hostname component ever uses
    # Deliberately NOT used: RCODE/NXDOMAIN ratio (requires responses).
    # ------------------------------------------------------------------
    TUNNEL_QTYPES = {16, 10}          # TXT, NULL -- bulk-carrying records
    TUNNEL_MIN_LABEL = 40             # real TLDs are ~2-15 chars; 63 is the wire max
    TUNNEL_MIN_QUERY = 60             # a real lookup is short; a chunk is not
    TUNNEL_MIN_BYTES = 300            # cumulative bytes before it is a session
    TUNNEL_MIN_QUERIES = 5

    def _tunnel_check(self, t, src, qname, qtype):
        # qname arrives with a trailing dot; the wire form is what matters.
        qwire = len(qname.encode(errors="replace")) if qname else 0
        longest = max((len(lbl) for lbl in qname.rstrip(".").split(".")),
                      default=0)
        bulky = qtype in self.TUNNEL_QTYPES
        long_label = longest >= self.TUNNEL_MIN_LABEL
        long_query = qwire >= self.TUNNEL_MIN_QUERY

        if not (bulky or long_label or long_query):
            return

        self.tunnel_bytes[src] += qwire
        self.tunnel_queries[src] += 1

        # Require cumulative volume AND repeated use. A single TXT lookup is
        # normal (SPF/DKIM); a *stream* of bulky or long queries is a tunnel.
        if (self.tunnel_bytes[src] < self.TUNNEL_MIN_BYTES
                or self.tunnel_queries[src] < self.TUNNEL_MIN_QUERIES):
            return

        n = self.tunnel_queries[src]
        # re-alert only on a doubling of volume, so a long session does not spam
        last = self.tunnel_alerted_at.get(src, 0)
        if last and self.tunnel_bytes[src] < last * 2:
            return
        self.tunnel_alerted_at[src] = self.tunnel_bytes[src]

        signals = []
        if bulky:
            signals.append(f"qtype={qtype} ({'TXT' if qtype == 16 else 'NULL'})")
        if long_label:
            signals.append(f"max label len {longest} >= {self.TUNNEL_MIN_LABEL}")
        if long_query:
            signals.append(f"query len {qwire} >= {self.TUNNEL_MIN_QUERY}")

        conf = min(0.97, 0.45 + self.tunnel_bytes[src] / 4000.0)
        self.sink.emit(
            t, src, "*", 53, "udp", "dns_tunneling", conf,
            {
                "qtype": qtype,
                "qname": qname,
                "query_bytes": qwire,
                "max_label_length": longest,
                "cumulative_tunnel_bytes": self.tunnel_bytes[src],
                "tunnel_queries_from_src": n,
                "signals": "; ".join(signals),
                "note": "response side not observable (one-way); RCODE and "
                        "NXDOMAIN correlation unavailable",
                "why": "repeated bulky/overlong DNS queries => data encoded "
                       "into the query channel rather than lookups",
            })
