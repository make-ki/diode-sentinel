#!/usr/bin/env bash
# One-command demo: generate the one-way capture, run every detector tier, and
# serve the dashboard. Nothing else is needed to see the system work end to end.
#
#   ./demo.sh            # replay mode (no privileges required)
#   ./demo.sh --live     # same, but through the live driver (stream clock,
#                        # drop accounting) -- still no root, because --live on
#                        # a file routes to the unprivileged pcap-stream source
#   ./demo.sh --fresh    # regenerate the capture instead of reusing the one
#                        # on disk (use this on stage, so the demo can never
#                        # show a stale or hand-edited capture)
#
# The dashboard is the last thing started, so a browser pointed at
# http://localhost:8600 shows the alerts as they land. Ctrl-C stops everything.
#
# The script is defensive by design: every stage is checked before it runs, so
# a failure on stage prints one readable line instead of a traceback.

set -euo pipefail
cd "$(dirname "$0")"

PY=${PY:-.venv/bin/python}
# NixOS: libstdc++/zlib must be on the loader path or numpy fails to import.
if [ -f .env-ml ]; then source .env-ml; fi

PORT=8600
LIVE=0
FRESH=0
for arg in "$@"; do
    case "$arg" in
        --live)  LIVE=1 ;;
        --fresh) FRESH=1 ;;
        --port=*) PORT="${arg#--port=}" ;;
        *) echo "usage: $0 [--live] [--fresh] [--port=NNNN]"; exit 2 ;;
    esac
done

# --- preflight: fail fast with one readable line, never a traceback ---------
fail() { echo "demo: $*"; exit 1; }

[ -x "$PY" ] || fail "python not found at $PY (run: uv sync, or python -m venv .venv && pip install -e .)"

# Import the heavy deps now: a missing/incompatible numpy or lightgbm must not
# surface for the first time two minutes into the demo.
"$PY" -c 'import numpy, lightgbm, dpkt' 2>/dev/null \
  || fail "python deps missing (numpy/lightgbm/dpkt) -- run: uv sync"

for f in model_ml.txt model_dga_cnn.npz models567/manifest.json; do
    [ -f "$f" ] || fail "model artifact missing: $f"
done

# The dashboard must bind the port itself; probe first so a stale occupier
# produces a message, not an address-already-in-use traceback mid-stage.
"$PY" - "$PORT" <<'PYEOF' 2>/dev/null || exit 1
import socket, sys
s = socket.socket(); s.settimeout(1)
try:
    if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0:
        print(f"demo: port {sys.argv[1]} is already in use -- close the other "
              f"dashboard, or run: ./demo.sh --port={int(sys.argv[1]) + 1}")
        sys.exit(1)
finally:
    s.close()
PYEOF

echo "== 1/3  synthetic one-way capture (12k packets, 600 s) =="
if [ "$FRESH" -eq 1 ] || [ ! -f traffic.pcap ]; then
    "$PY" gen_traffic.py || fail "capture generation failed"
else
    echo "      reusing traffic.pcap (--fresh to regenerate)"
fi

echo "== 2/3  pipeline: rules + ML tier + DGA CNN + category 5-7 models =="
if [ "$LIVE" -eq 1 ]; then
    # Replay through the live driver with no CAP_NET_RAW: --live on a file path
    # is routed to the pcap-stream source, so the demo works without sudo.
    "$PY" run.py --live traffic.pcap --no-state \
         --ml --dga-cnn --models-567 models567/manifest.json \
      || fail "pipeline failed"
else
    "$PY" run.py --ml --dga-cnn --models-567 models567/manifest.json \
      || fail "pipeline failed"
fi

echo "== 3/3  dashboard on http://localhost:$PORT (Ctrl-C to stop) =="
exec "$PY" dashboard.py "$PORT"
