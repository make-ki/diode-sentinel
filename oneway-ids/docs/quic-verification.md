# QUIC Initial verification

The QUIC metadata parser supports QUIC v1 Initial packets only. The version
salt and packet-protection values are checked against the independent examples
in [RFC 9001 §5.2 and Appendix A.1/A.2](https://www.rfc-editor.org/rfc/rfc9001.html#appendix-A.2).
The frozen 1200-byte packet in `tests/fixtures/quic/rfc9001_a2_client_initial.hex`
is the RFC Appendix A.2 Client Initial, not a packet emitted by the repository's
builder.

`tests/test_quic.py` verifies the RFC's client Initial key, IV, and header
protection key, then decrypts the published packet and checks SNI `example.com`,
TLS version 1.3, cipher/extension counts, and the QUIC JA4 `q` prefix. The
packet test also exercises the published protected header. TLS parser golden
tests remain unchanged: `parse_client_hello(record)` defaults to TLS and retains
the `t` prefix; QUIC calls it with `transport="quic"` to use `q`.

Malformed or truncated fields, overlong connection IDs, an unsupported version,
reserved-bit violations, and AEAD authentication failures return no metadata.
ACK parsing consumes the First ACK Range and, for ACK_ECN, all three ECN
counters. ACK-controlled loops are bounded by the remaining packet bytes.

Run the protocol and legacy parser checks from the repository root:

```sh
.venv/bin/python tests/test_quic.py
.venv/bin/python tests/test_tls_meta.py
```

The local `build_quic_initial` round trips remain useful builder/parser smoke
tests. They keep the historical compact packet by default so the generator's
current capture size is unchanged. Pass `pad_to=1200` to insert QUIC PADDING
frames into plaintext before AEAD and produce a 1200-byte packet; this path has
its own round-trip test. Their synthetic ClientHello profiles include legacy
TLS versions and are not claimed to be standards-conforming QUIC handshake
examples. The RFC packet fixture is the independent interoperability proof.
QUIC Initial decryption exposes only the public ClientHello metadata described
by the protocol, not application data or later handshake levels.
