"""Tests for QUIC Initial ClientHello extraction.
Run: . .env-ml && .venv/bin/python test_quic.py"""
import os

from quic_meta import is_quic_initial, extract_quic_client_hello, \
    build_quic_initial
from hello_profiles import malware_hello, browser_hello
from tls_meta import parse_client_hello

failures = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        failures.append(name)


ch_rec = malware_hello()                      # full TLS record
hs_msg = ch_rec[5:]                           # handshake message only

# 1. round-trip: build -> extract -> same JA4 as direct parse
pkt = build_quic_initial(dcid=os.urandom(8), handshake_msg=hs_msg)
check("is_initial", is_quic_initial(pkt))
meta = extract_quic_client_hello(pkt)
direct = parse_client_hello(ch_rec)
check("roundtrip_parses", meta is not None)
check("roundtrip_ja4", meta and meta["ja4"] == direct["ja4"],
      f"{meta['ja4'] if meta else None} vs {direct['ja4']}")
check("quic_transport_tag", meta and meta.get("transport") == "quic")

# 2. browser profile round-trips too
pkt2 = build_quic_initial(dcid=os.urandom(8),
                          handshake_msg=browser_hello("google.com.")[5:])
m2 = extract_quic_client_hello(pkt2)
check("browser_roundtrip", m2 is not None and m2["sni"] == "google.com.",
      m2["ja4"] if m2 else "none")

# 3. tamper detection: flip one ciphertext byte -> GCM rejects -> None
bad = bytearray(pkt)
bad[-10] ^= 0xFF
check("tamper_rejected", extract_quic_client_hello(bytes(bad)) is None)

# 4. non-Initial / version-negotiation / short payloads ignored
vn = b"\xc0" + b"\x00\x00\x00\x00" + bytes(20)       # version 0 = VN
check("version_negotiation_ignored", not is_quic_initial(vn))
check("short_payload_ignored", extract_quic_client_hello(b"\xc3\x00") is None)
check("not_quic_ignored", not is_quic_initial(b"\x00" * 64))

# 5. distinct dcid -> distinct keys -> cross-decryption fails
pkt3 = build_quic_initial(dcid=os.urandom(8), handshake_msg=hs_msg, pn=1)
pkt4 = build_quic_initial(dcid=os.urandom(8), handshake_msg=hs_msg, pn=1)
# splice pkt4's ciphertext tail into pkt3's header (wrong keys)
spliced = pkt3[:len(pkt3) - 40] + pkt4[len(pkt4) - 40:]
check("wrong_dcid_rejected", extract_quic_client_hello(spliced) is None)

print()
if failures:
    print(f"{len(failures)} FAILURES: {failures}")
    raise SystemExit(1)
print("all quic tests passed")
