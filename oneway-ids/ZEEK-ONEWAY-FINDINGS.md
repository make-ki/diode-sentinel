# Verified findings — Zeek on a one-way (data-diode) feed

All measurements taken locally with Zeek 7.2.2
(`/nix/store/z0vsr4g58nfw5rzw2zl1mf4rpc1z6c9k-zeek-7.2.2/bin/zeek`),
on `oneway-ids/traffic.pcap` (12,295 packets, 600 s, one direction only).

## The baseline: vanilla Zeek on a diode feed

Before the generator fix:

| Metric | Value |
|---|---|
| Total flows | 5,327 |
| `conn_state == S0` | 5,322 (99.9%) — "attempt, no reply seen" |
| `service == -` | 4,511 (no app-layer analysis) |
| `ssl.log` | **did not exist — zero TLS analysis** |
| `quic.log` | 3 rows, `history=I`, `server_name=-` (no SNI parsed) |

## Root cause — NOT what the research brief predicted

The brief said the blocker was `tcp_attempt_delay` (a 5 s AttemptTimer that
removes the connection). **Ablation testing disproved this.** Setting
`redef tcp_attempt_delay = 0 secs;` alone changed `ssl.log` from 0 → **0**.

The actual root cause was in the **traffic generator**, `gen_traffic.py`:

1. **SYN carried a 6-byte zero payload.** Real stacks never do this.
   Zeek logs `SYN_with_data`. Fixed by clearing the payload when `flags == "S"`.
2. **All segments had `seq=0`.** Later segments clobbered the ClientHello
   in the reassembler. Fixed by tracking per-connection sequence state.
3. **Data began at the SYN's own ISN.** Zeek computes the first data byte's
   relative sequence as 0 — the SYN's own number — and classifies the whole
   segment `data_before_established`, so the SSL analyzer never fires.
   A SYN occupies one sequence number; data must start at **ISN + 1**.
4. **`ack=0` on data segments.** Data after a SYN acknowledges it.
5. **Source ports drawn from a 20k range collide** across the 600 s run, so
   per-4-tuple state leaks between connections. Connection state is now keyed
   to a monotonic counter.

After the generator fix, **vanilla Zeek parses the ClientHello** — 527
`ssl.log` records, 8 with a fully parsed ClientHello.

## What the shim actually contributes (measured, not assumed)

With the generator fixed, vanilla and shim produce **identical** output:

| Metric | Vanilla | With shim |
|---|---|---|
| conn.log flows | 5,088 | 5,088 |
| ssl.log records | 527 | 527 |
| malware C2 (8443) parsed | 8 | 8 |
| dns.log records | 666 | 666 |

So on this capture `tcp_attempt_delay`, `tcp_content_deliver_all_orig`,
`ignore_checksums` and `set_inactivity_timeout` are **not load-bearing**.
The brief's headline claim — "Zeek deletes the connection after 5 s" — did
not reproduce as a blocker here.

## Confirmed working, on real traffic

A real OpenSSL 3.6.3 handshake was captured on loopback, sliced to the client
direction only (`tshark -Y "tcp.dstport==8443"`), including the SYN:

- Vanilla Zeek: **no `ssl.log`**
- Shim: `ssl.log` present, `server_name = detector.local`, `ssl_history = CI`

This proves the diode configuration works on real traffic. Note the loopback
capture has bad checksums (offload), so `ignore_checksums` / `-C` matters for
that class of capture.

## Negative result: the checksum experiments were invalid

Attempts to corrupt TCP checksums and measure recovery all produced zero
flows. **Root cause: `dpkt.pcap.Writer` produces files Zeek cannot parse.**
A byte-identical round-trip (read original, write unchanged) yielded 0 flows.
Every checksum conclusion from those runs is discarded. Do not use dpkt's
Writer to build test pcaps for Zeek — use `tshark`/`editcap`.

## Honest state of the novelty claim

- **Not established:** "no one has made Zeek work one-way." The GitHub
  searches returned zero repos, but my own repro shows vanilla Zeek largely
  works once the traffic is realistic. The blocker was our generator.
- **Established:** QUIC ClientHello decryption is fully one-way (public
  version salt + DCID, no server input) — verified in Zeek source.
- **Established:** JA4 is a *client* fingerprint; needs no server response.
- **The defensible contribution is the observability contract**, not a Zeek
  config trick: enumerating which PS-requested features are observable,
  impossible, or substitutable on a directional-only feed.

## Files

> These were local working files from the investigation. **None were committed
> and none exist in the repo today** — the `.zeek` shims lived in
> `zeekfix/oneway.zeek` and the captures were gitignored. There is no Zeek in
> the shipped sensor; this file is the offline measurement record. Do not
> write a build step that expects any of these paths.

- `zeekfix/oneway.zeek` — the shim (compiles, runs, harmless on fixed traffic)
- `zeekfix/diag.zeek` — event-level probe (`ssl_client_hello` counts)
- `oneway_real_tls.pcap` / `oneway_with_syn.pcap` — real one-way TLS captures
- `realtest/oneway_real.pcap` — one-way slice of CTU IoT-23 honeypot traffic

## What to do next

1. Build the observability contract as the actual artifact (see design doc).
2. Re-run the IoT-23 validation with the fixed generator and Zeek.
3. Regenerate `.regression/alerts_*.reference.jsonl` — the generator change
   alters packet counts, so the old reference files are stale.
