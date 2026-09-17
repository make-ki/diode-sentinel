"""Tests for tls_meta + TlsDetector. Run: .venv/bin/python test_tls_meta.py"""
import hashlib
from collections import defaultdict

from tls_meta import (TlsRecordReassembler, SeqTracker, parse_client_hello,
                      _is_grease)
import hello_profiles as hp
from detectors import TlsDetector


failures = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name} {detail}")
    if not cond:
        failures.append(name)


class StubSink:
    def __init__(self):
        self.alerts = []

    def emit(self, t, src, dst, dport, proto, threat, conf, ev):
        self.alerts.append(dict(t=t, src=src, threat=threat, conf=conf,
                                scope=ev.get("novelty_scope")))

    def suppress(self, n=1):
        pass


# 1. All three profiles parse and produce distinct JA4s
metas = {}
for name, blob in [("browser", hp.browser_hello("example.com.")),
                   ("updater", hp.updater_hello()),
                   ("malware", hp.malware_hello())]:
    m = parse_client_hello(blob)
    check(f"parse_{name}", m is not None)
    if m:
        metas[name] = m
check("profiles_distinct",
      len({m["ja4"] for m in metas.values()}) == 3)

# 2. Golden A-components (hand-computed from FoxIO rules):
#    browser: t13 + d + 18 ciphers + 6 exts (SNI INCLUDED) + alpn "h2"
check("golden_browser_A", metas["browser"]["ja4"].startswith("t13d1806h2"),
      metas["browser"]["ja4"])
check("golden_updater_A", metas["updater"]["ja4"].startswith("t12d0804"),
      metas["updater"]["ja4"])          # 8 ciphers, 4 exts (sni,groups,formats,sig_algs)
check("golden_malware_A", metas["malware"]["ja4"].startswith("t11i0603"),
      metas["malware"]["ja4"])          # 6 ciphers, 3 exts, no alpn -> "00"
check("malware_not_learned_seed",
      hp.MALWARE_JA4 == metas["malware"]["ja4"])

# 3. JA3 golden: minimal hello, expected string built INDEPENDENTLY here.
blob = hp.make_client_hello(ciphers=[0x1301, 0x1302], sni=None, alpn=None,
                            supported_versions=None,
                            groups=(0x001D,), sig_algs=(0x0401,),
                            formats=(0,))
m = parse_client_hello(blob)
expected_ja3_str = "771,4865-4866,10-11-13,29,0"   # ver,ciphers,exts,curves,formats
check("golden_ja3", m["ja3"] == hashlib.md5(expected_ja3_str.encode()).hexdigest(),
      f"{m['ja3']} vs md5('{expected_ja3_str}')")

# 4. sig_algs ORDER matters in C hash (unsorted per spec)
c1 = parse_client_hello(hp.make_client_hello(
    ciphers=[0x1301], sni=None, alpn=None, supported_versions=None,
    sig_algs=(0x0403, 0x0804, 0x0401), groups=(), formats=()))
c2 = parse_client_hello(hp.make_client_hello(
    ciphers=[0x1301], sni=None, alpn=None, supported_versions=None,
    sig_algs=(0x0401, 0x0804, 0x0403), groups=(), formats=()))
check("sigalg_order_matters", c1["ja4"] != c2["ja4"])

# 5. Same profile, different SNI -> same JA4 (SNI only flips d/i)
b1 = parse_client_hello(hp.browser_hello("google.com."))
b2 = parse_client_hello(hp.browser_hello("zzzzqqlongname.io."))
check("sni_invariant", b1["ja4"] == b2["ja4"])

# 6. SNI presence flips d/i AND changes ext count (SNI included in count)
nosni = parse_client_hello(hp.make_client_hello(
    ciphers=[0x1301, 0xC02F], sni=None, alpn=None, supported_versions=None,
    groups=(), formats=(), sig_algs=()))
withsni = parse_client_hello(hp.make_client_hello(
    ciphers=[0x1301, 0xC02F], sni="x.com", alpn=None, supported_versions=None,
    groups=(), formats=(), sig_algs=()))
a1, a2 = nosni["ja4"].split("_")[0], withsni["ja4"].split("_")[0]
check("di_flip", a1[3] == "i" and a2[3] == "d", f"{a1} vs {a2}")
check("di_count_includes_sni", int(a1[6:8]) + 1 == int(a2[6:8]),
      f"{a1} vs {a2}")

# 7. GREASE stripped end-to-end (ciphers + curve)
base = parse_client_hello(hp.make_client_hello(
    ciphers=[0x1301, 0xC02F], sni=None, alpn=None, supported_versions=None,
    groups=(0x001D,), formats=(), sig_algs=()))
greased = parse_client_hello(hp.make_client_hello(
    ciphers=[0x1301, 0xC02F, 0x0A0A], sni=None, alpn=None,
    supported_versions=None, groups=(0x001D, 0x0A0A), formats=(),
    sig_algs=()))
check("grease_stripped", base["ja4"] == greased["ja4"] and base["ja3"] == greased["ja3"])
check("grease_fn", _is_grease(0x0A0A) and _is_grease(0xFAFA)
      and not _is_grease(0x1301) and not _is_grease(0x00FF))

# 8. Malformed / hostile inputs rejected (not fingerprinted)
blob = hp.browser_hello("x.com.")
for cut in (3, 9, 20, 60, len(blob) // 2, len(blob) - 1):
    check(f"truncated_{cut}", parse_client_hello(blob[:cut]) is None)
sh = b"\x16\x03\x03\x00\x2a" + b"\x02\x00\x00\x26" + b"\x03\x03" + bytes(39)
check("serverhello_rejected", parse_client_hello(sh) is None)
check("appdata_rejected", parse_client_hello(b"\x17\x03\x03\x00\x05hello") is None)
# malformed ext length (claims 0xFFFF)
bad_ext = (b"\x16\x03\x01\x00\x20\x01\x00\x00\x1c\x03\x03" + bytes(32)
           + b"\x00\x00\x02\x00\x02\x13\x01\x01\x00\x00\x00\xff\xff")
check("malformed_ext_rejected", parse_client_hello(bad_ext) is None)

# 9. Record reassembly: split across segments, multi-record, hostile
big = hp.browser_hello("a" * 300 + ".com")
mid = len(big) // 2
rt = TlsRecordReassembler()
check("split_no_early_parse", rt.feed(big[:mid]) == [])
out = rt.feed(big[mid:])
check("split_reassembled", len(out) == 1 and parse_client_hello(out[0]) is not None)
rt2 = TlsRecordReassembler()
check("nontls_dead", rt2.feed(b"\x00" * 100) == [] and rt2.dead)
rt3 = TlsRecordReassembler()
rt3.feed(b"\x16\x03\x03\xff\xff" + b"\x00" * 50)   # claims 64KB record
check("oversized_record_dead", rt3.dead)
two = hp.browser_hello("x.com.") + b"\x17\x03\x03\x00\x03abc"
recs = TlsRecordReassembler().feed(two)
check("two_records", len(recs) == 2 and parse_client_hello(recs[0]) is not None)

# 10. SeqTracker: retransmit dropped, gap kills, in-order passes
st = SeqTracker()
check("seq_first", st.update(1000, 100) == "in_order")
check("seq_dup", st.update(1000, 100) == "duplicate")      # full retransmit
check("seq_overlap", st.update(1050, 100) == "duplicate")  # partial overlap
check("seq_next", st.update(1100, 50) == "in_order")
check("seq_gap", st.update(1300, 10) == "gap")

# 11. TlsDetector unit behavior
sink = StubSink()
det = TlsDetector(sink)
good = {"ja4": "t13d1806h2_a_b", "ja3": "x", "sni": "ok.com",
        "cipher_count": 18, "ext_count": 6, "version": "13"}
bad = dict(metas["malware"]) if "malware" in metas else {
    "ja4": hp.MALWARE_JA4, "ja3": "y", "sni": None,
    "cipher_count": 6, "ext_count": 3, "version": "11"}

det.on_hello(50, "10.0.0.50", "1.2.3.4", 443, bad)          # known-bad BEFORE baseline
check("knownbad_pre_baseline", len(sink.alerts) == 1
      and sink.alerts[0]["threat"] == "tls_known_malware")
det.on_hello(100, "10.0.0.50", "1.2.3.4", 443, good)        # baseline learning
check("baseline_quiet", len(sink.alerts) == 1)
det.on_hello(179.9, "10.0.0.50", "1.2.3.4", 443, good)      # still baseline
check("baseline_boundary_quiet", len(sink.alerts) == 1)
novel = {"ja4": "t13d1806h2_z_z", "ja3": "z", "sni": None,
         "cipher_count": 18, "ext_count": 6, "version": "13"}
det.on_hello(200, "10.0.0.60", "1.2.3.4", 443, novel)       # global novel
check("novel_global", len(sink.alerts) == 2
      and sink.alerts[-1]["scope"] == "global" and sink.alerts[-1]["conf"] == 0.80)
det.on_hello(250, "10.0.0.61", "1.2.3.4", 443, novel)       # lateral movement
check("novel_host_tier", len(sink.alerts) == 3
      and sink.alerts[-1]["scope"] == "host" and sink.alerts[-1]["conf"] == 0.60)
det.on_hello(260, "10.0.0.61", "1.2.3.4", 443, novel)       # learned: silent
check("novel_once_per_pair", len(sink.alerts) == 3)
det.on_hello(200 + 301, "10.0.0.60", "1.2.3.4", 443, bad)   # known-bad re-alert
check("knownbad_realerts", len(sink.alerts) == 4)
det.on_hello(300, "10.0.0.60", "1.2.3.4", 443, bad)         # within dedupe
check("knownbad_dedupe", len(sink.alerts) == 4)

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    raise SystemExit(1)
print("all tls_meta + TlsDetector tests passed")
