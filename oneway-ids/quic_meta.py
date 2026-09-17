"""
QUIC Initial-packet ClientHello extraction (one-way, no secrets).

QUIC Initial packets (RFC 9000) are encrypted with keys derived from the
PUBLIC version salt and the destination connection ID -- no server contact
required. A passive one-way sensor can therefore decrypt them and extract
the TLS ClientHello inside the CRYPTO stream: metadata-only detection for
the QUIC leg of PS class (d).

Caveats (documented):
  - Only Initial packets are decryptable; Handshake/1-RTT payloads are
    secret-key protected and stay opaque (by design -- we never claim to
    break encryption).
  - Only QUIC v1 salt implemented (the dominant version).
  - CRYPTO stream reassembly here is per-packet contiguous; a CH split
    across multiple Initial packets with gaps returns None (rare: Initials
    are padded to 1200B and CHs fit one datagram in practice).
"""
import hashlib
import hmac as _hmac

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# RFC 9001 §5.2: salt for QUIC v1
QUIC_V1_SALT = bytes.fromhex(
    "38762cf7f55934b34d179ae6a4c80cadadbb68d5b72523b3f9ca0a7e0a627b3d")

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
    initial_secret = _hmac.new(QUIC_V1_SALT, dcid, hashlib.sha256).digest()
    client_in = _hkdf_expand_label(initial_secret, "client in", 32)
    return {
        "key": _hkdf_expand_label(client_in, "quic key", 16),
        "iv": _hkdf_expand_label(client_in, "quic iv", 12),
        "hp": _hkdf_expand_label(client_in, "quic hp", 16),
    }


def _decrypt_hp(hp_key: bytes, first_byte: int, sample: bytes):
    """Header protection: AES-ECB(hp_key, sample) mask (RFC 9001 5.4)."""
    enc = Cipher(algorithms.AES(hp_key), modes.ECB())
    dec = enc.decryptor()
    mask = dec.update(sample) + dec.finalize()
    new_first = first_byte ^ (mask[0] & 0x0F)      # long header: low nibble
    pn_len = (new_first & 0x03) + 1
    return new_first, pn_len, mask


def _parse_varint(buf: bytes, off: int):
    """RFC 9000 variable-length integer -> (value, new_offset)."""
    if off >= len(buf):
        raise IndexError
    b = buf[off]
    prefix = b >> 6
    length = 1 << prefix
    if off + length > len(buf):
        raise IndexError
    val = b & 0x3F
    for i in range(1, length):
        val = (val << 8) | buf[off + i]
    return val, off + length


def is_quic_initial(payload: bytes) -> bool:
    """Long header, fixed bit, type==Initial, not version negotiation."""
    return (len(payload) > 5 and (payload[0] & 0x80)
            and (payload[0] & 0x40) and ((payload[0] >> 4) & 0x03) == 0
            and int.from_bytes(payload[1:5], "big") != 0)


def extract_quic_client_hello(payload: bytes):
    """Decrypt a QUIC v1 Initial packet; return the ClientHello meta dict
    (same shape as tls_meta.parse_client_hello output) or None."""
    try:
        if not is_quic_initial(payload):
            return None
        off = 1
        version = int.from_bytes(payload[1:5], "big")
        off = 5
        dcid_len = payload[off]; off += 1
        dcid = payload[off:off + dcid_len]; off += dcid_len
        scid_len = payload[off]; off += 1 + scid_len
        token_len, off = _parse_varint(payload, off)
        off += token_len
        length, off = _parse_varint(payload, off)
        pn_offset = off
        # header protection sample sits 4 bytes past pn start (max pn len)
        sample = payload[pn_offset + 4:pn_offset + 20]
        if len(sample) < 16:
            return None
        keys = _derive_keys(dcid)
        new_first, pn_len, mask = _decrypt_hp(keys["hp"], payload[0], sample)
        pn_bytes = bytes(payload[pn_offset + i] ^ mask[i + 1]
                         for i in range(pn_len))
        pn = int.from_bytes(pn_bytes, "big")

        aad = (bytes([new_first]) + payload[1:pn_offset] + pn_bytes)
        nonce = bytes(a ^ b for a, b in
                      zip(keys["iv"],
                          pn.to_bytes(12, "big")))
        ct_start = pn_offset + pn_len
        ct = payload[ct_start:ct_start + length - pn_len]
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
                _, foff = _parse_varint(frames, foff + 1)   # largest acked
                _, foff = _parse_varint(frames, foff)       # ack delay
                rng_cnt, foff = _parse_varint(frames, foff)
                for _ in range(rng_cnt):
                    _, foff = _parse_varint(frames, foff)
                    _, foff = _parse_varint(frames, foff)
                if ftype == 0x03:
                    _, foff = _parse_varint(frames, foff)   # ECTN
            elif ftype == 0x06:                     # CRYPTO
                coff, foff = _parse_varint(frames, foff + 1)
                clen, foff = _parse_varint(frames, foff)
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
        fake_record = (b"\x16\x03\x01"
                       + len(stream).to_bytes(2, "big") + stream)
        from tls_meta import parse_client_hello
        meta = parse_client_hello(fake_record)
        if meta is not None:
            meta["transport"] = "quic"
        return meta
    except (IndexError, ValueError, InvalidTag):
        return None


# ---------------------------------------------------------------------------
# Encryption path (generator-side): build a valid QUIC Initial carrying a CH
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


def build_quic_initial(dcid: bytes, handshake_msg: bytes, pn: int = 0) -> bytes:
    """Encrypt a QUIC v1 Initial containing one CRYPTO frame with the given
    TLS handshake message (e.g. a ClientHello). Companion to extract_...

    Construction order follows RFC 9001: packet-protect FIRST (AAD = the
    header with the CLEAR pn bytes and unmasked first byte), THEN apply
    header protection to the wire bytes (mask from the ciphertext sample).
    The receiver unprotects the header first, reconstructing the same AAD.
    """
    keys = _derive_keys(dcid)
    crypto_frame = (b"\x06" + _encode_varint(0)
                    + _encode_varint(len(handshake_msg)) + handshake_msg)
    frames = crypto_frame + b"\x01"        # PING (non-empty payload guard)

    pn_len = 4                             # fixed 4-byte pn for simplicity
    dcid_len = len(dcid)
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

    # header protection: sample = 16 bytes at pn_offset+4; with pn_len=4
    # that window sits entirely inside the ciphertext
    if len(ct) < 20:
        ct = ct + b"\x00" * 20            # Initials are padded in practice
    sample = ct[:16]
    enc = Cipher(algorithms.AES(keys["hp"]), modes.ECB())
    dec = enc.decryptor()
    mask = dec.update(sample) + dec.finalize()
    wire_b0 = 0xC3 ^ (mask[0] & 0x0F)
    wire_pn = bytes(pn_bytes[i] ^ mask[i + 1] for i in range(pn_len))

    return (bytes([wire_b0]) + header_no_pn[1:]
            + wire_pn + ct)
