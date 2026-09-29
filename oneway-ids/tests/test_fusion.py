"""Tests for FusionEngine + DDosDetector attribution.
Run: .venv/bin/python test_fusion.py"""
# Bootstrap: tests import core/, training/ and the root entry points, so put the
# repo root and its subpackages on sys.path regardless of the invocation CWD.
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in (_ROOT, _os.path.join(_ROOT, "training")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
from core.detectors import FusionEngine, DDosDetector, ScanDetector, ExfilDetector

failures = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        failures.append(name)


class Sink:
    """Standalone stub matching AlertSink's interface (no file writes)."""
    def __init__(self):
        self.alerts, self.suppressed, self._subs = [], 0, []

    def subscribe(self, fn):
        self._subs.append(fn)

    def emit(self, t, src, dst, dport, proto, threat, conf, ev):
        rec = {"threat_class": threat, "confidence": round(float(conf), 3),
               "src": src, "dst": dst, "dport": dport,
               "flow_id": f"{src}:*->{dst}:{dport}/{proto}", "evidence": ev,
               "t": t}
        self.alerts.append(rec)
        for fn in self._subs:
            fn(t, rec)

    def suppress(self, n=1):
        self.suppressed += n


def mk(cls, conf, t, src="10.0.0.9", dst="1.1.1.1", dport=0):
    return {"threat_class": cls, "confidence": conf, "src": src, "dst": dst,
            "dport": dport, "flow_id": f"{src}:*->{dst}:{dport}/*"}


sink = Sink()
fus = FusionEngine(sink, window=120, min_classes=2)

# 1. single class repeated -> no fusion
for t in (10, 20, 30):
    fus.on_alert(t, mk("dga_domain", 0.7, t))
check("single_class_no_fire", len(sink.alerts) == 0)

# 2. second class within window -> fires with noisy-OR confidence
fus.on_alert(50, mk("c2_beaconing", 0.9, 50))
check("fused_fires", len(sink.alerts) == 1)
rec = sink.alerts[0]
check("scenario_tag", rec["threat_class"] == "botnet_c2_with_dga",
      rec["threat_class"])

# 3. dedupe: same pair re-alerting within window -> silent (no new evidence)
fus.on_alert(60, mk("dga_domain", 0.8, 60))
check("no_refire_same_set", len(sink.alerts) == 1)

# 4. escalation: class-set GAINS exfil -> fires with exfil-priority tag
fus.on_alert(100, mk("data_exfiltration", 0.9, 100))
check("escalation_fires", len(sink.alerts) == 2
      and sink.alerts[-1]["threat_class"] == "confirmed_exfiltration",
      sink.alerts[-1]["threat_class"])

# 5. shrink back down -> no refire (nothing NEW)
fus.on_alert(110, mk("c2_beaconing", 0.9, 110))
check("shrink_no_refire", len(sink.alerts) == 2)

# 6. window expiry: classes older than window don't count
s2 = Sink(); f2 = FusionEngine(s2, window=120)
f2.on_alert(10, mk("dga_domain", 0.7, 10))
f2.on_alert(500, mk("c2_beaconing", 0.9, 500))     # dga@10 evicted
check("window_expiry_no_fire", len(s2.alerts) == 0)

# 7. ongoing incident: persistent 2-class activity must NOT re-fire
s3 = Sink(); f3 = FusionEngine(s3, window=120)
for base in (1, 121, 241, 361):                    # every 120s, same pair
    f3.on_alert(base, mk("dga_domain", 0.7, base))
    f3.on_alert(base + 1, mk("c2_beaconing", 0.9, base + 1))
check("no_120s_cadence_storm", len(s3.alerts) == 1,
      f"got {len(s3.alerts)}")

# 8. weak signals don't participate
s4 = Sink(); f4 = FusionEngine(s4)
f4.on_alert(10, mk("dga_domain", 0.3, 10))         # below MIN_FUSE_CONF
f4.on_alert(20, mk("c2_beaconing", 0.9, 20))
check("weak_signal_excluded", len(s4.alerts) == 0)

# 9. direct recursion-guard test (replaces vacuous all([]) check)
n = len(sink.alerts)
fus.on_alert(200, mk("botnet_c2_with_dga", 0.99, 200))
fus.on_alert(201, mk("multi_signal_fusion", 0.99, 201))
check("no_recursion", len(sink.alerts) == n)

# 10. 'confirmed_exfiltration' requires strong exfil signal (>=0.8)
s5 = Sink(); f5 = FusionEngine(s5)
f5.on_alert(10, mk("dga_domain", 0.7, 10))
f5.on_alert(20, mk("data_exfiltration", 0.6, 20))  # weak exfil
check("weak_exfil_not_confirmed",
      s5.alerts and s5.alerts[-1]["threat_class"] == "multi_signal_fusion",
      s5.alerts[-1]["threat_class"] if s5.alerts else "none")

# 11. decayed noisy-OR: old strong signal contributes less
s6 = Sink(); f6 = FusionEngine(s6, window=120)
f6.on_alert(10, mk("dga_domain", 0.99, 10))        # ages 119s
f6.on_alert(129, mk("c2_beaconing", 0.51, 129))
check("decay_applied", s6.alerts
      and s6.alerts[0]["confidence"] < 0.95,
      s6.alerts[0]["confidence"] if s6.alerts else "none")
check("decay_evidence", s6.alerts and
      any("effective_confidence" in c for c in
          s6.alerts[0]["evidence"]["contributing_signals"]))

# 12. DDosDetector: dominant-src SYN flood gets attributed
sink7 = Sink()
ddos = DDosDetector(sink7)
from collections import Counter, defaultdict
w = dict(idx=3, t0=30.0, t1=40.0, npkt=1200, nbytes=90000, nsyn=1100,
         srcs=Counter({"10.0.0.42": 1050, "10.0.0.2": 80, "10.0.0.3": 70}),
         pairs=defaultdict(set), src_bytes=defaultdict(float),
         pair_bytes=defaultdict(float), novel_dsts=set(),
         novel_bytes=defaultdict(float))
ddos.on_window(w)
check("syn_flood_attributed",
      any(a["src"] == "10.0.0.42" and a["threat_class"] == "ddos_syn_flood"
          for a in sink7.alerts),
      [a["src"] for a in sink7.alerts])
# spoofed case stays unattributed
w2 = dict(w, srcs=Counter({f"1.2.3.{i}": 10 for i in range(1500)}))
sink8 = Sink()
DDosDetector(sink8).on_window(w2)
check("spoofed_unattributed",
      all(a["src"] == "*" for a in sink8.alerts))

# 13. Recon detector distinguishes vertical and horizontal fan-out.
scan_sink = Sink()
scan = ScanDetector(scan_sink)
vertical_pairs = {("203.0.113.20", 1000 + i) for i in range(20)}
scan.on_window(dict(t0=40.0, t1=50.0,
              pairs={"10.0.0.13": vertical_pairs}))
check("vertical_scan", scan_sink.alerts
    and scan_sink.alerts[0]["threat_class"] == "recon_vertical_scan"
    and scan_sink.alerts[0]["dst"] == "203.0.113.20")

horizontal_pairs = {(f"203.0.113.{i}", 443) for i in range(20)}
scan.on_window(dict(t0=50.0, t1=60.0,
              pairs={"10.0.0.13": horizontal_pairs}))
check("horizontal_scan", scan_sink.alerts[-1]["threat_class"] ==
    "recon_horizontal_scan" and scan_sink.alerts[-1]["dst"] == "*")

# 14. Exfil detector requires a destination that is genuinely new to the
# stream, then carries the transfer across windows until the byte threshold.
exfil_sink = Sink()
exfil = ExfilDetector(exfil_sink)
from collections import defaultdict

def exfil_window(idx, dst, pair_bytes, novel_dsts=()):
    return dict(idx=idx, t0=idx * 10.0, t1=(idx + 1) * 10.0,
            pair_bytes=defaultdict(float, pair_bytes),
            novel_dsts=set(novel_dsts), src_bytes={"10.0.0.11": 1000})

exfil.on_window(exfil_window(0, "198.51.100.10",
                     {("10.0.0.11", "198.51.100.10"): 600000}))
check("known_destination_not_exfil", not exfil_sink.alerts)
exfil.on_window(exfil_window(1, "45.33.32.156",
                     {("10.0.0.11", "45.33.32.156"): 300000},
                     ["45.33.32.156"]))
exfil.on_window(exfil_window(2, "45.33.32.156",
                     {("10.0.0.11", "45.33.32.156"): 300000}))
check("novel_destination_exfil", exfil_sink.alerts
    and exfil_sink.alerts[0]["threat_class"] == "data_exfiltration"
    and exfil_sink.alerts[0]["evidence"]["novel_destination"] is True)

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    raise SystemExit(1)
print("all fusion + attribution tests passed")
