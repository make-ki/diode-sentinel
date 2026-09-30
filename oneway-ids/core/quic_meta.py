"""
QUIC Initial-packet ClientHello extraction (one-way, no secrets).

QUIC Initial packets (RFC 9000) are encrypted with keys derived from the
PUBLIC version salt and the destination connection ID -- no server contact
required. A passive one-way sensor can therefore decrypt them and extract
the TLS ClientHello inside the CRYPTO stream: metadata-only detection for
the QUIC leg of PS class (d).

Caveats:
  - Only Initial packets are decryptable; Handshake/1-RTT payloads are
    secret-key protected and stay opaque (by design -- we never claim to
    break encryption).
  - Only the standardized QUIC v1 version (0x00000001) is supported. Other
    versions have different packet types and/or salts and are rejected.
  - CRYPTO stream reassembly here is per-packet contiguous; a CH split
    across multiple Initial packets with gaps returns None.
"""
import hashlib
import hmac as _hmac

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# RFC 9001 §5.2: salt for QUIC v1
QUIC_V1_SALT = bytes.fromhex(
    "38762cf7f55934b34d179ae6a4c80cadccbb7f0a")
QUIC_V1_VERSION = 0x00000001

# RFC 8446-style HKDF expand-label
_TLS13_PREFIX = b"tls13 "


def _hkdf_expand_label(secret: bytes, label: str, length: int) -> bytes:
    label_b = _TLS13_PREFIX + label.encode()
    info = length.to_bytes(2, "big") + bytes([len(label_b)]) + label_b + b"\x00"
    out = b""
    prev = b""
    counter = 1
    while len(out) < length:
        prev = _hmac.new(secret, prev + info + bytes([counter]),
                         hashlib.sha256).digest()
        out += prev
        counter += 1
    return out[:length]


def _derive_keys(dcid: bytes):
    if not isinstance(dcid, bytes) or not 0 <= len(dcid) <= 20:
        raise ValueError("QUIC destination connection ID must be 0..20 bytes")
    initial_secret = _hmac.new(QUIC_V1_SALT, dcid, hashlib.sha256).digest()
    client_in = _hkdf_expand_label(initial_secret, "client in", 32)
    return {
        "key": _hkdf_expand_label(client_in, "quic key", 16),
        "iv": _hkdf_expand_label(client_in, "quic iv", 12),
        "hp": _hkdf_expand_label(client_in, "quic hp", 16),
    }


def _decrypt_hp(hp_key: bytes, first_byte: int, sample: bytes):
    """Remove header protection using AES-ECB encryption of the sample."""
    enc = Cipher(algorithms.AES(hp_key), modes.ECB())
    encryptor = enc.encryptor()
    mask = encryptor.update(sample) + encryptor.finalize()
    new_first = first_byte ^ (mask[0] & 0x0F)      # long header: low nibble
    pn_len = (new_first & 0x03) + 1
    return new_first, pn_len, mask


def _parse_varint(buf: bytes, off: int):
    """RFC 9000 variable-length integer -> (value, new_offset)."""
    if off >= len(buf):
        raise ValueError("truncated QUIC variable-length integer")
    b = buf[off]
    prefix = b >> 6
    length = 1 << prefix
    if off + length > len(buf):
        raise ValueError("truncated QUIC variable-length integer")
    val = b & 0x3F
    for i in range(1, length):
        val = (val << 8) | buf[off + i]
    return val, off + length


def _skip_ack_frame(frames: bytes, off: int, ecn: bool = False) -> int:
    """Return the first byte after an ACK/ACK_ECN frame; reject truncation."""
    _, off = _parse_varint(frames, off)       # largest acknowledged
    _, off = _parse_varint(frames, off)       # ACK delay
    range_count, off = _parse_varint(frames, off)
    _, off = _parse_varint(frames, off)       # first ACK range
    # Each additional range needs at least two one-byte varints. Bound work
    # against the packet size before iterating attacker-controlled counts.
    if range_count > (len(frames) - off) // 2:
        raise ValueError("truncated QUIC ACK ranges")
    for _ in range(range_count):
        _, off = _parse_varint(frames, off)   # gap
        _, off = _parse_varint(frames, off)   # ACK range
    if ecn:
        for _ in range(3):                    # ECT(0), ECT(1), CE
            _, off = _parse_varint(frames, off)
    return off


def is_quic_initial(payload: bytes) -> bool:
    """Whether a datagram begins with a supported QUIC v1 Initial packet."""
    if not isinstance(payload, (bytes, bytearray, memoryview)):
        return False
    try:
        payload = bytes(payload)
    except (TypeError, ValueError):
        return False
    return (len(payload) > 5 and (payload[0] & 0x80)
            and (payload[0] & 0x40) and ((payload[0] >> 4) & 0x03) == 0
            and int.from_bytes(payload[1:5], "big") == QUIC_V1_VERSION)


def extract_quic_client_hello(payload: bytes):
    """Decrypt one QUIC v1 Initial and parse its TLS ClientHello metadata.

    Unknown versions, truncated/malformed packets and authentication failures
    return None. Metadata is parsed as QUIC so JA4 uses the `q` prefix.
    """
    try:
        if not isinstance(payload, (bytes, bytearray, memoryview)):
            return None
        # Normalize once: memoryview slices cannot always be concatenated with
        # bytes when rebuilding the AEAD associated-data header.
        payload = bytes(payload)
        if not is_quic_initial(payload):
            return None
        version = int.from_bytes(payload[1:5], "big")
        if version != QUIC_V1_VERSION:
            return None
        off = 5
        if off >= len(payload):
            return None
        dcid_len = payload[off]; off += 1
        if dcid_len > 20 or off + dcid_len >= len(payload):
            return None
        dcid = bytes(payload[off:off + dcid_len]); off += dcid_len
        scid_len = payload[off]; off += 1
        if scid_len > 20 or off + scid_len > len(payload):
            return None
        off += scid_len
        token_len, off = _parse_varint(payload, off)
        if token_len > len(payload) - off:
            return None
        off += token_len
        length, off = _parse_varint(payload, off)
        pn_offset = off
        packet_end = pn_offset + length
        if length < 20 or packet_end > len(payload):
            return None
        # header protection sample sits 4 bytes past pn start (max pn len)
        sample = payload[pn_offset + 4:pn_offset + 20]
        if len(sample) < 16:
            return None
        keys = _derive_keys(dcid)
        new_first, pn_len, mask = _decrypt_hp(keys["hp"], payload[0], sample)
        if (new_first & 0x40) == 0 or (new_first & 0x0C) != 0:
            return None
        pn_bytes = bytes(payload[pn_offset + i] ^ mask[i + 1]
                         for i in range(pn_len))
        if pn_len > length:
            return None
        pn = int.from_bytes(pn_bytes, "big")

        aad = (bytes([new_first]) + payload[1:pn_offset] + pn_bytes)
        nonce = bytes(a ^ b for a, b in
                      zip(keys["iv"],
                          pn.to_bytes(12, "big")))
        ct_start = pn_offset + pn_len
        ct = payload[ct_start:packet_end]
        if len(ct) < 16:
            return None
        frames = AESGCM(keys["key"]).decrypt(nonce, ct, aad)

        # ---- CRYPTO frame reassembly (contiguous from offset 0) ----
        crypto = {}
        foff = 0
        while foff < len(frames):
            ftype = frames[foff]
            if ftype == 0x00:                       # PADDING
                foff += 1
            elif ftype == 0x01:                     # PING
                foff += 1
            elif ftype in (0x02, 0x03):             # ACK -- skip
                foff = _skip_ack_frame(frames, foff + 1, ecn=ftype == 0x03)
            elif ftype == 0x06:                     # CRYPTO
                coff, foff = _parse_varint(frames, foff + 1)
                clen, foff = _parse_varint(frames, foff)
                if clen > len(frames) - foff:
                    return None
                crypto[coff] = frames[foff:foff + clen]
                foff += clen
            else:
                break                               # other frames: stop
        if not crypto or 0 not in crypto:
            return None

        # contiguity check from offset 0
        pos, chunks = 0, []
        for k in sorted(crypto):
            if k > pos:
                break
            chunks.append(crypto[k])
            pos = k + len(crypto[k])
        stream = b"".join(chunks)

        # TLS handshake: ClientHello message (no record layer in QUIC)
        if not stream or stream[0] != 0x01:
            return None
        hs_len = int.from_bytes(stream[1:4], "big")
        ch = stream[4:4 + hs_len]
        if len(ch) < hs_len:
            return None
        # wrap as a TLS record so tls_meta can parse it unchanged
        if len(stream) > 0xffff:
            return None
        fake_record = (b"\x16\x03\x01"
                       + len(stream).to_bytes(2, "big") + stream)
        from core.tls_meta import parse_client_hello
        meta = parse_client_hello(fake_record, transport="quic")
        if meta is not None:
            meta["transport"] = "quic"
        return meta
    except (IndexError, ValueError, InvalidTag, OverflowError, TypeError):
        return None


# ---------------------------------------------------------------------------
# QUIC v1 packet builder used for synthetic parser fixtures and traffic
# ---------------------------------------------------------------------------

def _encode_varint(v: int) -> bytes:
    if v < (1 << 6):
        return bytes([v])
    if v < (1 << 14):
        return (0x40 | (v >> 8)).to_bytes(1, "big") + bytes([v & 0xFF])
    if v < (1 << 30):
        return (0x80 | (v >> 24)).to_bytes(1, "big") \
            + v.to_bytes(3, "big")
    return (0xC0 | (v >> 56)).to_bytes(1, "big") + v.to_bytes(7, "big")


def build_quic_initial(dcid: bytes, handshake_msg: bytes, pn: int = 0,
                       pad_to: int = 0) -> bytes:
    """Build a QUIC v1 Initial carrying one CRYPTO frame.

    `pad_to` is an optional minimum complete-packet size in bytes. Set it to
    1200 for a client Initial UDP datagram that meets QUIC's minimum size.
    The default zero preserves the historical compact parser-smoke fixture;
    it is not necessarily a valid client Initial datagram.

    Construction order follows RFC 9001: packet-protect FIRST (AAD = the
    header with the CLEAR pn bytes and unmasked first byte), THEN apply
    header protection to the wire bytes (mask from the ciphertext sample).
    The receiver unprotects the header first, reconstructing the same AAD.
    """
    if not isinstance(dcid, bytes) or len(dcid) > 20:
        raise ValueError("dcid must be bytes with length at most 20")
    if not isinstance(handshake_msg, bytes):
        raise ValueError("handshake_msg must be bytes")
    if isinstance(pn, bool) or not isinstance(pn, int) or not 0 <= pn < (1 << 32):
        raise ValueError("packet number must fit the fixed 4-byte encoding")
    if (isinstance(pad_to, bool) or not isinstance(pad_to, int)
            or not 0 <= pad_to <= 65527):
        raise ValueError("pad_to must be an integer from 0 through 65527")
    keys = _derive_keys(dcid)
    crypto_frame = (b"\x06" + _encode_varint(0)
                    + _encode_varint(len(handshake_msg)) + handshake_msg)
    frames = crypto_frame + b"\x01"        # PING (non-empty payload guard)

    pn_len = 4                             # fixed 4-byte pn for simplicity
    dcid_len = len(dcid)

    def packet_size(frame_bytes):
        payload_len = pn_len + len(frame_bytes) + 16  # PN + AES-GCM tag
        header_len = (1 + 4 + 1 + dcid_len + 1 + 1
                      + len(_encode_varint(payload_len)))
        return header_len + payload_len

    # Padding is plaintext PADDING frames and therefore must be included before
    # AEAD protection and in the encoded Length field. Recompute to handle a
    # varint-width transition in that field.
    while pad_to and packet_size(frames) < pad_to:
        frames += b"\x00" * (pad_to - packet_size(frames))

    ct_len = len(frames) + 16              # AES-GCM tag

    header_parts = [
        bytes([0xC3]),                     # form+fixed+Initial, pn_len bits=3
        (1).to_bytes(4, "big"),            # version 1
        bytes([dcid_len]) + dcid,
        b"\x00",                           # SCID len 0
        b"\x00",                           # token len 0
        _encode_varint(pn_len + ct_len),
    ]
    header_no_pn = b"".join(header_parts)
    pn_offset = len(header_no_pn)

    pn_bytes = pn.to_bytes(pn_len, "big")
    nonce = bytes(a ^ b for a, b in zip(keys["iv"], pn.to_bytes(12, "big")))
    # AAD = unmasked first byte + header fields + CLEAR pn bytes
    aad = bytes([0xC3]) + header_no_pn[1:] + pn_bytes
    ct = AESGCM(keys["key"]).encrypt(nonce, frames, aad)

    # Header protection sample starts 4 bytes after the PN offset. With the
    # fixed four-byte PN, it is the first 16 bytes of the AEAD ciphertext.
    sample = ct[:16]
    enc = Cipher(algorithms.AES(keys["hp"]), modes.ECB())
    encryptor = enc.encryptor()
    mask = encryptor.update(sample) + encryptor.finalize()
    wire_b0 = 0xC3 ^ (mask[0] & 0x0F)
    wire_pn = bytes(pn_bytes[i] ^ mask[i + 1] for i in range(pn_len))

    return (bytes([wire_b0]) + header_no_pn[1:]
            + wire_pn + ct)
