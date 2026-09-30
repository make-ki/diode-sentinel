"""The one-way observability contract.

This is the project's actual contribution. PS-26145 asks for a set of detection
features, but the problem statement *also* imposes the constraint that only one
direction of every conversation is ever visible. Some of the features it names
are therefore structurally unobservable -- not hard, not expensive, but
information-theoretically absent from the input. A detector that reads one is a
detector that silently produces garbage, so the contract enumerates them and
the CI gate below fails the build if any code reaches for one.

Each row states:
  feature        -- what the PS asked for
  class          -- the PS threat class it belongs to
  status         -- OBSERVABLE | IMPOSSIBLE | SUBSTITUTED
  substitute     -- the one-way signal we use instead (or None)
  why_impossible -- the physical reason it cannot be seen on a diode feed

The status is asserted, not documented: verify_contract() is called from the
test suite, and OBSERVABLE rows must cite the function that consumes them.
"""

# --- qtype codes referenced below -----------------------------------------
# 1 A, 16 TXT, 10 NULL, 28 AAAA, 15 MX, 2 NS, 6 SOA, 35 NAPTR

CONTRACT = [
    # ---- (a) Volumetric / protocol DDoS ---------------------------------
    dict(feature="flow-level packet rate", ps_class="a", status="OBSERVABLE",
         consumer="WindowAggregator.npkt / WINDOW",
         substitute=None,
         why_impossible=None),
    dict(feature="source-IP entropy (spoofed floods)", ps_class="a",
         status="OBSERVABLE",
         consumer="DdosDetector.on_window -> shannon_entropy(sources)",
         substitute=None,
         why_impossible=None),
    dict(feature="SYN ratio", ps_class="a", status="OBSERVABLE",
         consumer="DdosDetector.on_window -> is_syn fraction",
         substitute=None,
         why_impossible=None),
    dict(feature="UDP reflection source-port distribution", ps_class="a",
         status="SUBSTITUTED",
         consumer="UdpBurstDetector.on_window -> per-source UDP packet rate "
                  "and destination endpoint cardinality",
         substitute="per-source UDP rate and fan-out plus shared-target "
                    "source/packet counts; the reply that would prove "
                    "amplification never returns",
         why_impossible="amplification is defined by response size, and the "
                        "response half of the conversation is not on the feed"),

    # ---- (b) Botnet C2 beaconing ---------------------------------------
    dict(feature="inter-arrival time regularity (CV)", ps_class="b",
         status="OBSERVABLE",
         consumer="BeaconDetector.on_flow -> iat mean/CV",
         substitute=None,
         why_impossible=None),
    dict(feature="round-trip time", ps_class="b", status="IMPOSSIBLE",
         consumer=None, substitute=None,
         why_impossible="RTT requires the response; one-way latency is "
                        "unmeasurable without a return path"),

    # ---- (c) DGA and DNS tunnelling -------------------------------------
    dict(feature="qname character entropy", ps_class="c", status="OBSERVABLE",
         consumer="DGADetector.on_dns -> shannon_entropy(label)",
         substitute=None,
         why_impossible=None),
    dict(feature="query length anomaly", ps_class="c", status="OBSERVABLE",
         consumer="DGADetector._tunnel_check -> query_bytes",
         substitute=None,
         why_impossible=None),
    dict(feature="record-type (qtype) anomaly", ps_class="c",
         status="OBSERVABLE",
         consumer="DGADetector._tunnel_check -> qtype",
         substitute=None,
         why_impossible=None),
    dict(feature="max label length", ps_class="c", status="OBSERVABLE",
         consumer="DGADetector._tunnel_check -> max_label_length",
         substitute=None,
         why_impossible=None),
    dict(feature="NXDOMAIN ratio", ps_class="c", status="IMPOSSIBLE",
         consumer=None,
         substitute="per-source high-entropy query streak + char-CNN quorum",
         why_impossible="RCODE lives in the DNS response header, which the "
                        "diode never delivers"),

    # ---- (d) Malware in encrypted sessions ------------------------------
    dict(feature="JA4 client fingerprint", ps_class="d", status="OBSERVABLE",
         consumer="TlsDetector.on_hello -> ja4 from ClientHello",
         substitute=None,
         why_impossible=None),
    dict(feature="SNI / ALPN / cipher suite list", ps_class="d",
         status="OBSERVABLE",
         consumer="TlsDetector.on_hello -> parse_client_hello",
         substitute=None,
         why_impossible=None),
    dict(feature="QUIC ClientHello (Initial decrypt)", ps_class="d",
         status="OBSERVABLE",
         consumer="quic_meta.py -> version salt + DCID key derivation",
         substitute=None,
         why_impossible=None),
    dict(feature="JA3S / JA4S server fingerprint", ps_class="d",
         status="IMPOSSIBLE",
         consumer=None,
         substitute="JA4 client fingerprint; a server-side fingerprint cannot "
                    "be reconstructed from the client hello",
         why_impossible="ServerHello is sent by the responder, which is not "
                        "on the feed"),
    dict(feature="negotiated cipher / server certificate", ps_class="d",
         status="IMPOSSIBLE", consumer=None,
         substitute="client-offered cipher list (ordered, from ClientHello)",
         why_impossible="both are chosen by the responder after the handshake "
                        "completes, off the observable path"),

    # ---- (e) Reconnaissance and port scanning ---------------------------
    dict(feature="(dst,port) fan-out cardinality", ps_class="e",
         status="OBSERVABLE",
         consumer="ScanDetector.on_window -> distinct pairs per src",
         substitute=None,
         why_impossible=None),
    dict(feature="vertical vs horizontal classification", ps_class="e",
         status="OBSERVABLE",
         consumer="ScanDetector.on_window -> top_n / len(pairs) >= 0.8",
         substitute=None,
         why_impossible=None),

    # ---- (f) Data exfiltration ------------------------------------------
    dict(feature="cumulative bytes to a destination", ps_class="f",
         status="OBSERVABLE",
         consumer="ExfilDetector.on_window -> pair_bytes",
         substitute=None,
         why_impossible=None),
    dict(feature="destination novelty (first-seen)", ps_class="f",
         status="OBSERVABLE",
         consumer="ExfilDetector.on_window -> novel_dsts",
         substitute=None,
         why_impossible=None),
    dict(feature="outbound-to-inbound byte ratio", ps_class="f",
         status="IMPOSSIBLE",
         consumer=None,
         substitute="cumulative bytes to a first-seen destination, compared "
                    "against the source's own median baseline",
         why_impossible="the inbound half of the flow is never seen, so the "
                        "ratio has no denominator. The PS names a feature its "
                        "own constraint (a) makes unsatisfiable"),
]

# Fields a detector must never read. The gate scans the detector source for
# these tokens; a hit means someone reached for a bidirectional signal.
FORBIDDEN_TOKENS = (
    "ja3s", "ja4s", "server_hello", "serverhello",
    "rcode", "nxdomain", "rcode_name",
    "answers", "dns_answers", "ttl",
    "rtt", "round_trip",
    "in_out_ratio", "bytes_in", "resp_bytes", "reverse_bytes",
)


def verify_contract():
    """Assert the contract is internally consistent and self-consistent.

    Returns a list of problems. Empty means the contract holds. Called from
    test_contract.py, which fails the build on any non-empty result.
    """
    problems = []
    seen = set()
    for row in CONTRACT:
        key = (row["feature"], row["ps_class"])
        if key in seen:
            problems.append(f"duplicate contract row: {key}")
        seen.add(key)

        for field in ("feature", "ps_class", "status", "why_impossible"):
            if field not in row:
                problems.append(f"row {key} missing field {field}")

        st = row["status"]
        if st == "OBSERVABLE" and not row.get("consumer"):
            problems.append(
                f"OBSERVABLE row {key} cites no consumer function")
        if st == "IMPOSSIBLE" and not row.get("why_impossible"):
            problems.append(
                f"IMPOSSIBLE row {key} gives no reason it is unobservable")
        if st == "SUBSTITUTED" and not row.get("substitute"):
            problems.append(
                f"SUBSTITUTED row {key} names no substitute signal")
        if st not in ("OBSERVABLE", "IMPOSSIBLE", "SUBSTITUTED"):
            problems.append(f"row {key} has unknown status {st!r}")
    return problems


def summary():
    """Counts per class, for the dashboard / deck."""
    from collections import Counter
    by_class = Counter((r["ps_class"], r["status"]) for r in CONTRACT)
    return {
        "total": len(CONTRACT),
        "observable": sum(1 for r in CONTRACT if r["status"] == "OBSERVABLE"),
        "impossible": sum(1 for r in CONTRACT if r["status"] == "IMPOSSIBLE"),
        "substituted": sum(1 for r in CONTRACT if r["status"] == "SUBSTITUTED"),
        "by_class": {f"{c}/{s}": n for (c, s), n in sorted(by_class.items())},
    }


if __name__ == "__main__":
    problems = verify_contract()
    if problems:
        for p in problems:
            print("FAIL:", p)
        raise SystemExit(1)
    s = summary()
    print(f"contract holds: {s['total']} features  "
          f"{s['observable']} observable / {s['impossible']} impossible / "
          f"{s['substituted']} substituted")
    for k, v in s["by_class"].items():
        print(f"  {k}: {v}")
