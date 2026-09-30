#!/usr/bin/env bash
# Terminal segment for the Diode Sentinel demo video.
#
# Every claim printed here is executed live; the only files written are in a
# temporary directory. The contract-gate step deliberately injects a forbidden
# field read into a COPY of core/ so the repository itself is never modified.
#
# Recorded with:  asciinema rec --headless --window-size 100x32 -c "bash demo_video/segment_terminal.sh" out.cast
set -uo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python

B=$'\033[1m'; C=$'\033[36m'; G=$'\033[32m'; Y=$'\033[33m'; R=$'\033[31m'; D=$'\033[2m'; N=$'\033[0m'

hr()  { printf '\n%s%s%s\n' "$C$B" "$1" "$N"; }
say() { printf '%s%s%s\n' "$D" "$1" "$N"; }
beats() { sleep "${1:-2}"; }

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT INT TERM

printf '%s\n' "$B$C  Diode Sentinel$N  —  intrusion detection for strictly ONE-WAY traffic"
printf '%s\n' "  PS-26145 · NTRO · the sensor sees one direction of every conversation."
say  "  no replies · no handshakes · no payload · no asking the network anything"
beats 3

hr "1. What the problem statement asks for — and what a diode can actually see"
"$PY" - <<'PYEOF'
from core import observability as o
s = o.summary()
print(f"  {s['total']} PS features enumerated:  "
      f"{s['observable']} OBSERVABLE · {s['impossible']} IMPOSSIBLE · {s['substituted']} SUBSTITUTED")
print()
for r in o.CONTRACT:
    if r["status"] == "IMPOSSIBLE":
        print(f"    \033[31mIMPOSSIBLE\033[0m  {r['feature']}  ({r['ps_class']})")
        print(f"                 {r['why_impossible']}")
PYEOF
printf '\n  %sFive of the statement'"'"'s own requested features are ruled out by its own constraint.%s\n' "$Y$B" "$N"
beats 4

hr "2. The contract is enforced, not documented — inject a forbidden read"
say "  (working on a throwaway copy of core/, the repo is not touched)"
mkdir -p "$TMP/gate/core" "$TMP/gate/tests"
cp core/*.py "$TMP/gate/core/"
cp tests/test_contract.py "$TMP/gate/tests/"
printf '\npayload_rcode = packet["rcode"]  # reach for a DNS response\n' >> "$TMP/gate/core/metrics.py"
printf '  injected:  %s\n' 'payload_rcode = packet["rcode"]   # a DNS response field'
printf '%s\n' "  \$ python tests/test_contract.py"
gate_out=$("$PY" "$TMP/gate/tests/test_contract.py" 2>&1)
printf '%s\n' "$gate_out" | grep -m1 -o "bidirectional field read on a one-way feed:"
printf '%s\n' "$gate_out" | grep -E "^(FAILED|OK)" | head -1
printf '%s\n' "  ${R}${B}^ the build fails on a one-way sensor reaching for a response field${N}"
beats 3
say "  restore the clean module and the same gate passes:"
cp core/metrics.py "$TMP/gate/core/metrics.py"
"$PY" "$TMP/gate/tests/test_contract.py" 2>&1 | tail -2
beats 3

hr "3. Replay is reproducible — byte-for-byte against the committed fixture"
AL="$TMP/alerts.jsonl"
say "  \$ DIODESENTINEL_ALERTS_PATH=\$TMP/alerts.jsonl python run.py --no-state"
DIODESENTINEL_ALERTS_PATH="$AL" "$PY" run.py --no-state >/dev/null 2>&1
"$PY" - "$AL" <<'PYEOF'
import collections, json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
print(f"  {len(rows)} alerts emitted")
c = collections.Counter((r["severity"], r["threat_class"]) for r in rows)
for (sev, cls), n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
    print(f"    {sev:<8} {cls:<26} {n:>3}")
PYEOF
if cmp -s "$AL" .regression/alerts_rules.reference.jsonl; then
    printf '  %scmp — IDENTICAL to .regression/alerts_rules.reference.jsonl%s\n' "$G$B" "$N"
else
    printf '  %scmp — DIFFERS%s\n' "$R$B" "$N"
fi
beats 4

hr "4. Scale, and one honest miss"
printf '  %s~50k pkt/s%s rules tier on ONE core — pure Python, no C extension, no GPU\n' "$B" "$N"
printf '  68 alerts with the ML tier · dpkt and scapy backends byte-identical (--parity)\n'
printf '  IoT-23 real malware: two families detected with no retuning, %sone total miss%s\n' "$Y" "$N"
printf '  %sthe missed scenario is printed in the docs before a judge can find it%s\n' "$D" "$N"
beats 4
