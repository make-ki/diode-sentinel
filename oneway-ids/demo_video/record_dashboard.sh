#!/usr/bin/env bash
# Record the cursor-driven tour of the live dashboard.
#
# Playwright has to come from the flake (the PyPI wheel ships a prebuilt node
# driver NixOS cannot exec), so this always re-enters the dev shell rather
# than assuming the caller is already inside it.
#
#   demo_video/record_dashboard.sh                       # ML fixture, 1920x1080
#   demo_video/record_dashboard.sh --no-mp4              # keep only the WebM
#   demo_video/record_dashboard.sh --alerts path.jsonl --size 1280x720
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE/.."

exec nix develop --command demo-python demo_video/record_dashboard.py "$@"
