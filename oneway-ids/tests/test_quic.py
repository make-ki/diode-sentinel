"""Tests for QUIC Initial ClientHello extraction.
Run: . .env-ml && .venv/bin/python test_quic.py"""
# Bootstrap: tests import core/, training/ and the root entry points, so put the
# repo root and its subpackages on sys.path regardless of the invocation CWD.
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
for _p in (_ROOT, _os.path.join(_ROOT, "training")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import os
from pathlib import Path
import random

from core.quic_meta import is_quic_initial, extract_quic_client_hello, \
    build_quic_initial, _derive_keys, _skip_ack_frame
from core.hello_profiles import malware_hello, browser_hello
from core.tls_meta import parse_client_hello

failures = []


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
    if not cond:
        failures.append(name)


FIXTURE = os.path.join(_ROOT, "tests", "fixtures", "quic",
                       "rfc9001_a2_client_initial.hex")


def read_hex_fixture(path):
    return bytes.fromhex("".join(
        line.strip() for line in Path(path).read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")))


# Published independent vectors from RFC 9001 Appendix A.1/A.2. These are
# protocol conformance checks; the local builder round trips below are only
# parser/builder smoke tests and use legacy synthetic ClientHello profiles.
dcid_rfc = bytes.fromhex("8394c8f03e515708")
keys_rfc = _derive_keys(dcid_rfc)
check("rfc_a1_client_key",
      keys_rfc["key"].hex() == "1f369613dd76d5467730efcbe3b1a22d",
      keys_rfc["key"].hex())
check("rfc_a1_client_iv",
      keys_rfc["iv"].hex() == "fa044b2f42a3fd3b46fb255c",
      keys_rfc["iv"].hex())
check("rfc_a1_client_hp",
      keys_rfc["hp"].hex() == "9f50449e04a0e810283a1e9933adedd2",
      keys_rfc["hp"].hex())

rfc_packet = read_hex_fixture(FIXTURE)
check("rfc_a2_packet_size", len(rfc_packet) == 1200, len(rfc_packet))
check("rfc_a2_protected_header",
      rfc_packet[:22].hex() ==
      "c000000001088394c8f03e5157080000449e7b9aec34",
      rfc_packet[:22].hex())
rfc_meta = extract_quic_client_hello(rfc_packet)
check("rfc_a2_parses", rfc_meta is not None)
check("rfc_a2_expected_metadata",
      rfc_meta is not None
      and (rfc_meta["sni"], rfc_meta["version"], rfc_meta["cipher_count"],
           rfc_meta["ext_count"], rfc_meta["alpn"])
      == ("example.com", "13", 2, 11, "alpn"), rfc_meta)
check("quic_ja4_transport_prefix",
      bool(rfc_meta) and rfc_meta["ja4"].startswith("q13d"),
      rfc_meta.get("ja4") if rfc_meta else None)
check("bytearray_and_memoryview_parse",
      extract_quic_client_hello(bytearray(rfc_packet)) == rfc_meta
      and extract_quic_client_hello(memoryview(rfc_packet)) == rfc_meta,
      "bytes-like input normalization")
check("noncontiguous_memoryview_rejected",
      extract_quic_client_hello(memoryview(rfc_packet)[::2]) is None)
released_view = memoryview(rfc_packet)
released_view.release()
check("released_memoryview_rejected",
      extract_quic_client_hello(released_view) is None)

# Every strict truncation of the published valid packet must fail closed. Add
# seeded mutations of protocol fields and random bytes-like inputs to exercise
# malformed input paths without relying on external fuzzing packages.
truncations_safe = all(extract_quic_client_hello(rfc_packet[:n]) is None
                       for n in range(len(rfc_packet)))
check("all_rfc_packet_truncations_rejected", truncations_safe)
mutations_safe = True
for index in (0, 1, 4, 5, 6, 13, 14, 15, 16, 17, 18, 21, 22, 100, 1199):
    damaged = bytearray(rfc_packet)
    damaged[index] ^= 0x01
    try:
        extract_quic_client_hello(damaged)
    except Exception as exc:  # malformed packets must not escape the parser
        mutations_safe = False
        print(f"[FAIL] malformed_variant_{index} raised {type(exc).__name__}")
        break
check("mutated_rfc_variants_fail_closed", mutations_safe)
fuzz = random.Random(9001)
random_inputs_safe = True
for n in range(128):
    raw = fuzz.randbytes(fuzz.randrange(0, 256))
    candidate = (raw, bytearray(raw), memoryview(raw))[(n % 3)]
    try:
        extract_quic_client_hello(candidate)
    except Exception as exc:
        random_inputs_safe = False
        print(f"[FAIL] random_malformed_{n} raised {type(exc).__name__}")
        break
check("seeded_random_byteslike_fail_closed", random_inputs_safe)

ch_rec = malware_hello()                      # legacy synthetic TLS fixture
hs_msg = ch_rec[5:]                           # smoke test only, not RFC-valid QUIC

# 1. Local synthetic builder/parser round trip: JA4 body matches direct TLS parse.
pkt = build_quic_initial(dcid=os.urandom(8), handshake_msg=hs_msg)
check("is_initial", is_quic_initial(pkt))
meta = extract_quic_client_hello(pkt)
direct = parse_client_hello(ch_rec)
check("roundtrip_parses", meta is not None)
check("roundtrip_ja4_body", meta and meta["ja4"][1:] == direct["ja4"][1:],
      f"{meta['ja4'] if meta else None} vs {direct['ja4']}")
check("tls_prefix_unchanged", direct and direct["ja4"].startswith("t"),
      direct["ja4"] if direct else None)
check("quic_prefix_differs", meta and meta["ja4"].startswith("q"),
      meta["ja4"] if meta else None)
check("quic_transport_tag", meta and meta.get("transport") == "quic")

# 2. browser profile round-trips too
pkt2 = build_quic_initial(dcid=os.urandom(8),
                          handshake_msg=browser_hello("google.com.")[5:])
m2 = extract_quic_client_hello(pkt2)
check("browser_roundtrip", m2 is not None and m2["sni"] == "google.com.",
      m2["ja4"] if m2 else "none")

# Opt-in datagram padding is inserted into plaintext before AEAD protection.
# The synthetic handshake only checks packet structure/parser behavior; the
# RFC Appendix A.2 fixture above remains the protocol-conformance proof.
padded = build_quic_initial(dcid=os.urandom(8), handshake_msg=hs_msg,
                            pad_to=1200)
check("builder_opt_in_minimum_datagram_size", len(padded) == 1200, len(padded))
check("builder_padding_precedes_aead", extract_quic_client_hello(padded)
      is not None)
builder_validation = True
for kwargs in ({"dcid": "not-bytes"}, {"dcid": bytes(21)},
               {"handshake_msg": "not-bytes"}, {"pn": -1},
               {"pn": 1 << 32}, {"pn": True}, {"pad_to": -1},
               {"pad_to": 65528}, {"pad_to": True}):
    args = {"dcid": bytes(8), "handshake_msg": hs_msg}
    args.update(kwargs)
    try:
        build_quic_initial(**args)
        builder_validation = False
        print(f"[FAIL] builder_input_rejected {kwargs}")
        break
    except (TypeError, ValueError):
        pass
check("builder_rejects_invalid_inputs", builder_validation)

# 3. tamper detection: flip one ciphertext byte -> GCM rejects -> None
bad = bytearray(pkt)
bad[-10] ^= 0xFF
check("tamper_rejected", extract_quic_client_hello(bytes(bad)) is None)

# 4. non-Initial / version-negotiation / short payloads ignored
vn = b"\xc0" + b"\x00\x00\x00\x00" + bytes(20)       # version 0 = VN
check("version_negotiation_ignored", not is_quic_initial(vn))
check("short_payload_ignored", extract_quic_client_hello(b"\xc3\x00") is None)
check("not_quic_ignored", not is_quic_initial(b"\x00" * 64))
unknown_version = bytearray(rfc_packet); unknown_version[4] = 2
check("unknown_version_rejected",
      not is_quic_initial(unknown_version)
      and extract_quic_client_hello(unknown_version) is None)
check("truncated_rfc_packet_rejected",
      extract_quic_client_hello(rfc_packet[:-1]) is None)
bad_dcid_len = bytearray(rfc_packet); bad_dcid_len[5] = 21
check("oversized_dcid_rejected",
      extract_quic_client_hello(bad_dcid_len) is None)

# ACK range layout includes First ACK Range; ACK_ECN adds three counters.
ack = bytes.fromhex("020301020004050607")
check("ack_frame_consumed", _skip_ack_frame(ack, 1) == len(ack))
ack_ecn = bytes.fromhex("03030102000405060708090a")
check("ack_ecn_frame_consumed",
      _skip_ack_frame(ack_ecn, 1, ecn=True) == len(ack_ecn))
try:
    _skip_ack_frame(bytes.fromhex("02030102"), 1)
    ack_truncated_rejected = False
except ValueError:
    ack_truncated_rejected = True
check("truncated_ack_rejected", ack_truncated_rejected)

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
