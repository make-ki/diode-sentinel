"""
TLS ClientHello profile builders for synthetic traffic.

Hand-crafted ClientHello record blobs (no external TLS library needed).
Three profiles:
  PROFILE_A "browser"     -- TLS1.3 via supported_versions, 18 ciphers,
                             SNI=benign domain, ALPN h2,http/1.1
  PROFILE_B "updater"     -- pure TLS1.2, 8 ciphers, SNI always present,
                             no ALPN
  PROFILE_MALWARE         -- legacy 0x0302, 6 deprecated ciphers, NO SNI,
                             no ALPN, 3 extensions

These blobs are shared by gen_traffic.py (traffic generation) and config.py
(KNOWN_BAD seeding) so the detector's threat-intel DB and the traffic come
from one source of truth. This module imports ONLY tls_meta (no config
import -> no circular import, no import-time pcap regeneration).
"""
from tls_meta import parse_client_hello


def make_client_hello(client_version=0x0303, ciphers=(), sni=None, alpn=None,
                      groups=(0x001D, 0x0017, 0x0018),
                      sig_algs=(0x0403, 0x0804, 0x0401, 0x0501, 0x0805,
                                0x0503, 0x0801, 0x0802),
                      formats=(0,),
                      supported_versions=None) -> bytes:
    """Build one complete TLS record containing a ClientHello."""
    exts = []

    if sni is not None:
        name = sni.encode()
        sni_data = (len(name) + 5).to_bytes(2, "big") + b"\x00" \
            + len(name).to_bytes(2, "big") + name
        exts.append((0x0000, sni_data))

    if groups:
        g = b"".join(gg.to_bytes(2, "big") for gg in groups)
        exts.append((0x000A, len(g).to_bytes(2, "big") + g))

    if formats:
        exts.append((0x000B, bytes([len(formats)])
                     + bytes(formats)))

    if sig_algs:
        s = b"".join(a.to_bytes(2, "big") for a in sig_algs)
        exts.append((0x000D, len(s).to_bytes(2, "big") + s))

    if alpn:
        protos = b"".join(bytes([len(p)]) + p.encode() for p in alpn)
        exts.append((0x0010, len(protos).to_bytes(2, "big") + protos))

    if supported_versions:
        sv = b"".join(v.to_bytes(2, "big") for v in supported_versions)
        exts.append((0x002B, bytes([len(sv)]) + sv))

    ext_blob = b"".join(t.to_bytes(2, "big") + len(d).to_bytes(2, "big") + d
                        for t, d in exts)

    hs = (client_version.to_bytes(2, "big") + bytes(32) + b"\x00"
          + sum(2 for _ in ciphers).to_bytes(2, "big")
          + b"".join(c.to_bytes(2, "big") for c in ciphers)
          + b"\x01\x00"
          + len(ext_blob).to_bytes(2, "big") + ext_blob)

    hs_full = b"\x01" + len(hs).to_bytes(3, "big") + hs
    return b"\x16\x03\x01" + len(hs_full).to_bytes(2, "big") + hs_full


CIPHERS_A = [0x1301, 0x1302, 0x1303, 0xC02B, 0xC02F, 0xC02C, 0xC030, 0xCCA9,
             0xCCA8, 0xC013, 0xC014, 0x009C, 0x009D, 0x002F, 0x0035, 0x000A,
             0x0005, 0x0004]
CIPHERS_B = [0x1301, 0xC02F, 0xC02B, 0xC030, 0xCCA9, 0x009C, 0x009D, 0x002F]
CIPHERS_MALWARE = [0x00FF, 0x0035, 0x000A, 0x0016, 0x0033, 0x0039]


def browser_hello(sni: str) -> bytes:
    return make_client_hello(ciphers=CIPHERS_A, sni=sni,
                             alpn=["h2", "http/1.1"],
                             supported_versions=[0x0304, 0x0303])


def updater_hello(sni: str = "update.microsoft.com") -> bytes:
    return make_client_hello(ciphers=CIPHERS_B, sni=sni, alpn=None,
                             supported_versions=None)


def malware_hello() -> bytes:
    return make_client_hello(client_version=0x0302, ciphers=CIPHERS_MALWARE,
                             sni=None, alpn=None,
                             groups=(0x0017,), sig_algs=(0x0401, 0x0501),
                             formats=(0,),
                             supported_versions=None)


# Fingerprints computed from the SAME builder the generator uses, so the
# threat-intel seed always matches the traffic. (Documented tautology: this
# simulates an intel feed; efficacy vs REAL malware is out of scope.)
MALWARE_JA4 = parse_client_hello(malware_hello())["ja4"]
