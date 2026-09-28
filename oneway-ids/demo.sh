#!/usr/bin/env bash
# One-command demo: generate the one-way capture, run every detector tier, and
# serve the dashboard. Nothing else is needed to see the system work end to end.
#
#   ./demo.sh            # replay mode (no privileges required)
#   ./demo.sh --live     # same, but through the live driver (stream clock,
#                        # drop accounting) -- still no root, because --live on
#                        # a file routes to the unprivileged pcap-stream source
#
# The dashboard is the last thing started, so a browser pointed at
# http://localhost:8600 shows the alerts as they land. Ctrl-C stops everything.

set -euo pipefail
cd "$(dirname "$0")"

PY=${PY:-.venv/bin/python}
# NixOS: libstdc++/zlib must be on the loader path or numpy fails to import.
if [ -f .env-ml ]; then source .env-ml; fi

LIVE=0
for arg in "$@"; do
    case "$arg" in
        --live) LIVE=1 ;;
        *) echo "usage: $0 [--live]"; exit 2 ;;
    esac
done

if [ ! -x "$PY" ]; then
    echo "python not found at $PY"
    echo "  uv sync            # or: python -m venv .venv && pip install -e ."
    exit 1
fi

echo "== 1/3  synthetic one-way capture (12k packets, 600 s) =="
if [ ! -f traffic.pcap ]; then
    "$PY" gen_traffic.py
fi

echo "== 2/3  pipeline: rules + ML tier + DGA CNN + category 5-7 models =="
if [ "$LIVE" -eq 1 ]; then
    # Replay through the live driver with no CAP_NET_RAW: --live on a file path
    # is routed to the pcap-stream source, so the demo works without sudo.
    "$PY" run.py --live traffic.pcap --no-state \
         --ml --dga-cnn --models-567 models567/manifest.json
else
    "$PY" run.py --ml --dga-cnn --models-567 models567/manifest.json
fi

echo "== 3/3  dashboard on http://localhost:8600 (Ctrl-C to stop) =="
exec "$PY" dashboard.py 8600
