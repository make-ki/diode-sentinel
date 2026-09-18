# JA3, JA4, TLS Crypto, and QUIC Initial

This guide explains how the encrypted-session detector works in this project.
The short version is:

- **JA3 and JA4 are fingerprints**, not encryption and not decryption keys.
- A TLS **ClientHello** contains useful connection metadata before application
  data is encrypted.
- A QUIC v1 **Initial** packet is specially decryptable by a passive sensor
  because its protection keys are derived from public protocol inputs.
- Only the Initial handshake packet is handled here. Application payloads and
  later QUIC packets remain encrypted and opaque.

## What JA3 and JA4 mean

### JA3

JA3 turns selected fields from a TLS ClientHello into a canonical string and
then hashes that string with MD5. In this repository, the string is:

```text
client_version,ciphers,extensions,elliptic_curves,ec_point_formats
```

Values inside each list are decimal and dash-separated, for example:

```text
771,4865-4866,10-11-13,29,0
```

The implementation removes GREASE values and preserves the ClientHello order.
The MD5 output is an identifier for the observed client handshake shape. It is
not being used here as a password hash or as a security boundary.

### JA4

JA4 is a newer, more structured fingerprint. This project creates the three
parts of a client JA4 value:

```text
JA4-A_JA4-B_JA4-C
```

The A component is readable metadata:

```text
t13d1806h2
```

It represents, in order:

| Part | Meaning |
|---|---|
| `t` | TCP TLS; the parser uses TLS rather than DTLS here |
| `13` | highest supported TLS version, mapped to the JA4 version code |
| `d` / `i` | SNI/domain present or absent |
| `18` | number of non-GREASE cipher suites |
| `06` | number of non-GREASE extensions, including SNI and ALPN |
| `h2` | first and last character of the first ALPN protocol; `00` if absent |

The B component is the first 12 hexadecimal characters of a SHA-256 hash over
the sorted cipher-suite list. The C component is the first 12 hexadecimal
characters of a SHA-256 hash over sorted extension types, excluding SNI and
ALPN, followed by the signature-algorithm list in its original order.

So, in this codebase:

- JA3 uses **MD5** as a compact fingerprint hash.
- JA4 B and C use truncated **SHA-256** hashes.
- Neither hash encrypts the ClientHello or lets the sensor recover hidden data.
- GREASE values are removed so deliberately inserted compatibility values do
  not create needless fingerprint changes.

The implementation is in `tls_meta.py`, in `parse_client_hello`. The parser
also returns SNI, cipher count, extension count, mapped TLS version, ALPN, and
signature algorithms as evidence for later detectors.

## What “TLS crypto” means here

TLS has several layers that are easy to mix up:

1. The client sends a **ClientHello** containing negotiation metadata such as
   supported versions, cipher suites, extensions, SNI, and ALPN.
2. TLS negotiates keys and authenticates the server.
3. Application records are encrypted with traffic keys derived during the
   handshake.

This IDS uses step 1 only. `pipeline.py` reassembles the first TCP TLS records,
finds a ClientHello, and passes its metadata to `TlsDetector`. It does not
derive TLS application traffic keys and does not decrypt HTTP, commands,
files, or other application content.

Because the feed is one-way, the server side is unavailable. The detector
cannot calculate JA3S, inspect server certificates, or correlate a response.
That is why the alert evidence is explicitly client-side and why the README
describes TLS/QUIC detection as metadata-only.

## How the fingerprint becomes an alert

`TlsDetector` uses JA4 as an inventory key:

1. During the baseline period, ordinary JA4 values are learned per source and
   globally.
2. A known-bad JA4 from `KNOWN_BAD_JA4` produces an immediate
   `tls_known_malware` alert and is never learned as benign inventory.
3. After baseline, a JA4 never seen fleet-wide is globally novel and produces a
   higher-confidence `tls_novel_fingerprint` alert.
4. A JA4 known elsewhere but new to one source is host-novel and produces a
   lower-confidence alert.

The same JA4 seen over TLS and QUIC is kept transport-aware for deduplication:
the same client fingerprint moving from TCP TLS to QUIC is a new observable
channel in this sensor.

## QUIC Initial: why a passive sensor can read it

QUIC carries TLS 1.3 handshake messages inside QUIC packets. A QUIC v1 Initial
packet has two relevant protections:

- **Header protection**, which hides parts of the packet header, including the
  packet-number length and packet number.
- **Payload packet protection**, which encrypts frames such as the CRYPTO
  frame carrying the TLS ClientHello.

For the client side of QUIC v1, the Initial secrets are derived from:

- the public QUIC v1 version salt; and
- the destination connection ID (DCID), visible in the packet header.

This repository follows RFC 9001's construction in `quic_meta.py`:

1. Confirm the packet is a QUIC long-header Initial packet, not version
   negotiation.
2. Derive the client Initial secret with HMAC-SHA-256 using the public v1
   salt and DCID.
3. Derive the packet key, IV, and header-protection key with TLS 1.3-style
   HKDF labels: `client in`, `quic key`, `quic iv`, and `quic hp`.
4. Remove header protection with AES-128-ECB and the packet ciphertext sample.
5. Build the authenticated associated data from the unprotected header and
   packet number.
6. Decrypt the payload with AES-128-GCM.
7. Reassemble the QUIC `CRYPTO` frame at stream offset zero and extract the TLS
   ClientHello handshake message.
8. Send that ClientHello through the existing `parse_client_hello` function,
   then mark the metadata as `transport: "quic"`.

The key point is that this is **not breaking TLS** and does not require a
secret stolen from either endpoint. QUIC intentionally makes Initial packets
processable by the peer before normal session keys exist. The sensor is using
public packet inputs and the standard protocol derivation.

## What QUIC does not reveal

Only QUIC v1 Initial packets are supported here. The following remain outside
the parser's visibility:

- QUIC Handshake packets;
- QUIC 1-RTT packets;
- application payloads;
- server-side TLS metadata;
- ClientHello data split across Initial packets with missing CRYPTO offsets;
- QUIC versions with a different salt or derivation unless separately added.

Later packets use secrets established during the handshake. Without endpoint
key material, a one-way passive sensor should leave them encrypted rather than
pretend it can inspect their content.

## Tests that prove the path

`test_tls_meta.py` checks JA3/JA4 golden values, GREASE removal, SNI behavior,
malformed input rejection, TCP record reassembly, and sequence-gap handling.
`test_quic.py` builds a valid QUIC Initial, extracts the ClientHello, and checks
that its JA4 matches the direct TLS parse. It also verifies that ciphertext
tampering and a wrong DCID are rejected instead of producing a false
fingerprint.

## Source files

- [TLS metadata and JA3/JA4](../tls_meta.py)
- [QUIC Initial crypto and extraction](../quic_meta.py)
- [TLS/QUIC detector and inventory](../detectors.py)
- [Packet pipeline hooks](../pipeline.py)
- [TLS metadata tests](../test_tls_meta.py)
- [QUIC tests](../test_quic.py)