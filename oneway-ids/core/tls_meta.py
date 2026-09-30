"""
One-way TLS metadata extraction: ClientHello parsing + JA4/JA3 fingerprints.

Spec fidelity notes (FoxIO JA4 + Salesforce JA3, reviewed against specs):
  - JA4 B/C hashes: SHA-256 truncated to 12 hex chars (NOT MD5 -- that's JA3).
  - JA4 A-component: 't' + version(2) + 'd'/'i' + cipher_count(2, decimal)
    + ext_count(2, decimal) + alpn(2). Counts INCLUDE SNI and ALPN
    extensions; only GREASE is excluded. No ALPN -> "00".
  - JA4 C-hash input: sorted extensions EXCLUDING SNI(0000)/ALPN(0010),
    then "_" + signature_algorithms IN ORIGINAL ORDER (not sorted);
    no trailing underscore when sig_algs is absent. Empty lists hash the
    literal placeholder "000000000000".
  - GREASE (RFC 8701, 0x?a?a) stripped from ciphers, extensions, groups,
    formats, and sig_algs before counting/hashing (both JA4 and JA3).
  - Version: highest non-GREASE supported_versions entry, else client
    version; mapped via FoxIO TLS_MAPPER-style table.
  - JA3: MD5 over "ver,ciphers,exts,curves,formats" -- decimal, unsorted,
    dash-separated, GREASE stripped.

Limitations (documented, one-way constraint):
  - Server-side fields (JA3S, certificates) are never observable.
  - Record-layer reassembly is provided (TlsRecordReassembler); TCP-layer
    sequencing (retransmits/gaps) is handled by SeqTracker -- feeding
    duplicated or gapped segments to the reassembler silently corrupts
    fingerprints, so run.py drops duplicates and kills gapped flows.
"""
import hashlib

# FoxIO TLS_MAPPER-style version table (TLS 't' variants; DTLS 'd' not used)
_TLS_MAP = {0x0304: "13", 0x0303: "12", 0x0302: "11", 0x0301: "10",
            0x0300: "s3", 0x0002: "s2", 0xFEFF: "d1", 0xFEFD: "d2",
            0xFDFD: "d3"}
_EMPTY_HASH_INPUT = "000000000000"


def _is_grease(v: int) -> bool:
    """GREASE = 0x?a?a values (RFC 8701): both bytes equal, low nibble 'a'."""
    return (v & 0x0F) == 0x0A and (v & 0xFF) == ((v >> 8) & 0xFF)


def _ver2(version: int) -> str:
    return _TLS_MAP.get(version, "00")


def _alpn_ab(p) -> str:
    """First+last char of the first ALPN protocol; non-alnum bytes map to
    their hex representation (0xAB -> 'ab'); >127 -> '99'."""
    if not p:
        return "00"

    def ch(c):
        o = ord(c)
        if 48 <= o <= 57 or 65 <= o <= 90 or 97 <= o <= 122:
            return c
        if o > 127:
            return "99"
        return format(o, "02x")

    return ch(p[0]) + ch(p[-1])


class TlsRecordReassembler:
    """Reassembles TCP segments into complete TLS records, per flow."""

    MAX_RECORD = 2 ** 14            # TLS spec: records never exceed 16KiB

    def __init__(self):
        self.buf = b""
        self.dead = False            # non-TLS / malformed flow marker

    def feed(self, payload: bytes):
        """Returns list of complete TLS record byte-strings."""
        if self.dead or not payload:
            return []
        self.buf += payload
        records = []
        while len(self.buf) >= 5:
            if self.buf[0] not in (0x14, 0x15, 0x16, 0x17):
                self.dead = True     # not TLS
                self.buf = b""
                break
            rec_len = int.from_bytes(self.buf[3:5], "big")
            if rec_len > self.MAX_RECORD:
                self.dead = True     # invalid record length
                self.buf = b""
                break
            if len(self.buf) < 5 + rec_len:
                break                # wait for more segments
            records.append(self.buf[:5 + rec_len])
            self.buf = self.buf[5 + rec_len:]
        return records


class SeqTracker:
    """TCP sequence sanity for one-way feeds.

    One-way means no ACK clock, so retransmits are invisible to normal
    flow logic. Feeding a retransmitted segment to a byte-append
    reassembler silently produces a WRONG fingerprint (worst failure mode),
    and a gap does too. Policy:
      - duplicates/overlaps (seq < next_expected): dropped silently
      - in-order (seq == next_expected): accepted
      - gap (seq > next_expected): flow marked unusable -- losing one
        fingerprint is always better than computing a wrong one.
    """

    def __init__(self):
        self.next_seq = None

    def update(self, seq: int, length: int) -> str:
        """Classify a segment; call BEFORE feeding. Returns
        'in_order' | 'duplicate' | 'gap'. For SYN use length=1."""
        if self.next_seq is None:
            self.next_seq = (seq + max(length, 1)) & 0xFFFFFFFF
            return "in_order"
        rel = (seq - self.next_seq) & 0xFFFFFFFF
        if rel > 0x7FFFFFFF:                      # negative => old data
            return "duplicate"
        if rel != 0:
            return "gap"
        self.next_seq = (seq + max(length, 1)) & 0xFFFFFFFF
        return "in_order"


def parse_client_hello(record: bytes, transport: str = "tls"):
    """Parse one complete ClientHello record and return its TLS/QUIC metadata.

    `transport` selects the JA4 transport prefix (`t` for TLS-over-TCP,
    `q` for QUIC). The default preserves the existing TLS output exactly.
    """
    try:
        if transport not in {"tls", "quic"}:
            return None
        if len(record) < 11 or record[0] != 0x16:
            return None
        if record[5] != 0x01:                     # handshake type
            return None
        hs_len = int.from_bytes(record[6:9], "big")
        body = record[9:9 + hs_len]
        if len(body) < hs_len or hs_len < 34:
            return None

        off = 0
        client_version = int.from_bytes(body[0:2], "big")
        off = 2 + 32                                  # version + random
        sid_len = body[off]; off += 1 + sid_len
        if off + 2 > len(body):
            return None
        cs_len = int.from_bytes(body[off:off + 2], "big"); off += 2
        if cs_len % 2 != 0 or off + cs_len > len(body):
            return None                               # malformed cipher list
        ciphers = [int.from_bytes(body[off + i:off + i + 2], "big")
                   for i in range(0, cs_len, 2)]
        off += cs_len
        if off >= len(body):
            return None
        comp_len = body[off]; off += 1 + comp_len
        if off + 2 > len(body):
            return None
        ext_len = int.from_bytes(body[off:off + 2], "big"); off += 2
        ext_end = min(off + ext_len, len(body))

        sni = None
        alpn_first = None
        supported_versions = []
        groups, formats, sig_algs = [], [], []
        ext_types = []

        p = off
        while p + 4 <= ext_end:
            etype = int.from_bytes(body[p:p + 2], "big")
            elen = int.from_bytes(body[p + 2:p + 4], "big")
            if p + 4 + elen > ext_end:
                return None                           # malformed extension
            data = body[p + 4:p + 4 + elen]
            p += 4 + elen
            if _is_grease(etype):
                continue
            ext_types.append(etype)
            if etype == 0x0000 and len(data) >= 5 and data[2] == 0:   # SNI host_name
                name_len = int.from_bytes(data[3:5], "big")
                sni = data[5:5 + name_len].decode(errors="replace")
            elif etype == 0x0010 and len(data) >= 3:          # ALPN
                proto_len = data[2]
                alpn_first = data[3:3 + proto_len].decode(errors="replace")
            elif etype == 0x000A and len(data) >= 2:          # supported_groups
                glen = int.from_bytes(data[0:2], "big")
                groups = [int.from_bytes(data[i:i + 2], "big")
                          for i in range(2, min(2 + glen, len(data)), 2)]
            elif etype == 0x000B and len(data) >= 1:          # ec_point_formats
                formats = list(data[1:1 + data[0]])
            elif etype == 0x000D and len(data) >= 2:          # signature_algorithms
                alen = int.from_bytes(data[0:2], "big")
                sig_algs = [int.from_bytes(data[i:i + 2], "big")
                            for i in range(2, min(2 + alen, len(data)), 2)]
            elif etype == 0x002B and len(data) >= 2:          # supported_versions
                for i in range(1, len(data) - 1, 2):
                    v = int.from_bytes(data[i:i + 2], "big")
                    if not _is_grease(v):
                        supported_versions.append(v)

        version = max(supported_versions) if supported_versions else client_version
        nciphers = [c for c in ciphers if not _is_grease(c)]
        # Ext count INCLUDES SNI and ALPN (FoxIO: "Include SNI and ALPN");
        # GREASE already excluded at append time.
        n_exts = len(ext_types)

        ja4_a = (("q" if transport == "quic" else "t")
                 + _ver2(version) + ("d" if sni else "i")
                 + f"{min(len(nciphers), 99):02d}"
                 + f"{min(n_exts, 99):02d}"
                 + _alpn_ab(alpn_first))
        cipher_str = ",".join(sorted(f"{c:04x}" for c in nciphers)) or _EMPTY_HASH_INPUT
        ja4_b = hashlib.sha256(cipher_str.encode()).hexdigest()[:12]
        c_exts = sorted(f"{e:04x}" for e in ext_types
                        if e not in (0x0000, 0x0010))
        c_input = ",".join(c_exts) or _EMPTY_HASH_INPUT
        clean_sig = [a for a in sig_algs if not _is_grease(a)]
        if clean_sig:
            # original order, NOT sorted (FoxIO spec)
            c_input += "_" + ",".join(f"{a:04x}" for a in clean_sig)
        ja4_c = hashlib.sha256(c_input.encode()).hexdigest()[:12]

        # JA3: decimal, unsorted, dash-separated values, comma-separated
        # fields, GREASE stripped everywhere
        ja3_str = ",".join([
            str(client_version),
            "-".join(str(c) for c in nciphers),
            "-".join(str(e) for e in ext_types),
            "-".join(str(g) for g in groups if not _is_grease(g)),
            "-".join(str(f) for f in formats if not _is_grease(f)),
        ])
        ja3 = hashlib.md5(ja3_str.encode()).hexdigest()

        return dict(ja4=f"{ja4_a}_{ja4_b}_{ja4_c}", ja3=ja3, sni=sni,
                    cipher_count=len(nciphers), ext_count=n_exts,
                    version=_ver2(version),
                    alpn=alpn_first, sig_algs=sig_algs)
    except (IndexError, ValueError):
        return None
