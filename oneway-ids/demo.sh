#!/usr/bin/env bash
# Paced synthetic end-to-end demo. The capture, FIFO, alerts and sidecars live
# in a fresh temporary directory; no existing capture or runtime state is read.
set -euo pipefail
cd "$(dirname "$0")"

PY=${PY:-.venv/bin/python}
if [ -f .env-ml ]; then
    set +e
    source .env-ml
    set -e
fi

PORT=8600
SPEED=10
for arg in "$@"; do
    case "$arg" in
        --port=*) PORT="${arg#--port=}" ;;
        --speed=*) SPEED="${arg#--speed=}" ;;
        --fresh|--live) ;;
        -h|--help)
            echo "usage: $0 [--speed=10] [--port=8600] [--fresh] [--live]"
            echo "Fresh synthetic replay at 10x by default; dashboard remains open after completion."
            exit 0 ;;
        *) echo "usage: $0 [--speed=10] [--port=8600] [--fresh] [--live]" >&2; exit 2 ;;
    esac
done

fail() { echo "demo: $*" >&2; exit 1; }
[ -x "$PY" ] || fail "python not found at $PY (run uv sync)"
[[ "$SPEED" =~ ^[0-9]+([.][0-9]+)?$ ]] || fail "--speed must be a positive number"
awk "BEGIN { exit !($SPEED > 0) }" || fail "--speed must be greater than zero"
"$PY" -c 'import numpy, dpkt, scapy' 2>/dev/null || fail "demo dependencies missing (run uv sync)"
[ -f model_dga_cnn.npz ] || fail "DGA model artifact missing: model_dga_cnn.npz"

RUN_DIR=$(mktemp -d "${TMPDIR:-/tmp}/diode-sentinel-demo.XXXXXX")
FIFO="$RUN_DIR/feed.pcap"
ALERTS="$RUN_DIR/alerts.jsonl"
CAPTURE="$RUN_DIR/synthetic.pcap"
mkfifo "$FIFO"
export DIODESENTINEL_PCAP_PATH="$CAPTURE"
export DIODESENTINEL_ALERTS_PATH="$ALERTS"
export DIODESENTINEL_DEMO=1

DASH_PID= RUN_PID= REPLAY_PID=
cleanup() {
    trap - INT TERM EXIT
    for pid in "$REPLAY_PID" "$RUN_PID" "$DASH_PID"; do
        if [ -n "$pid" ]; then kill "$pid" 2>/dev/null || true; fi
    done
    for pid in "$REPLAY_PID" "$RUN_PID" "$DASH_PID"; do
        if [ -n "$pid" ]; then wait "$pid" 2>/dev/null || true; fi
    done
    rm -rf "$RUN_DIR"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# Catch a stale dashboard before starting any child process.
"$PY" - "$PORT" <<'PYEOF' || exit 1
import socket, sys
s = socket.socket(); s.settimeout(.4)
try:
    if s.connect_ex(("127.0.0.1", int(sys.argv[1]))) == 0:
        print(f"demo: port {sys.argv[1]} is already in use", file=sys.stderr)
        sys.exit(1)
finally:
    s.close()
PYEOF

echo "== 1/3  generate a fresh seeded synthetic one-way capture =="
env -u MESSY "$PY" -c 'import runpy, core.config; runpy.run_path("gen_traffic.py", run_name="__main__")' \
    || fail "capture generation failed"
[ -s "$CAPTURE" ] || fail "generator did not create the expected fresh capture"

echo "== 2/3  start synthetic demo dashboard before replay =="
"$PY" dashboard.py "$PORT" &
DASH_PID=$!
"$PY" - "$PORT" <<'PYEOF' || fail "dashboard did not become ready"
import sys, time, urllib.request
url = f"http://127.0.0.1:{sys.argv[1]}/api/stats"
for _ in range(100):
    try:
        with urllib.request.urlopen(url, timeout=.3):
            break
    except Exception:
        time.sleep(.1)
else:
    raise SystemExit(1)
PYEOF

echo "      http://localhost:$PORT  | SYNTHETIC DEMO DATA | rules + DGA CNN"
echo "      seeded synthetic threat profiles are demonstration fixtures, not live threat intelligence"
echo "== 3/3  stream capture at ${SPEED}x (dashboard stays open at EOF) =="
"$PY" run.py --pipe "$FIFO" --no-state --dga-cnn &
RUN_PID=$!
"$PY" demo_replay.py "$CAPTURE" "$FIFO" --speed "$SPEED" &
REPLAY_PID=$!

set +e
wait -n -p FIRST_PID "$REPLAY_PID" "$RUN_PID"
FIRST_STATUS=$?
set -e
if [ "$FIRST_PID" = "$REPLAY_PID" ]; then
    REPLAY_STATUS=$FIRST_STATUS
    REPLAY_PID=
    if [ "$REPLAY_STATUS" -ne 0 ]; then
        kill "$RUN_PID" 2>/dev/null || true
    fi
else
    RUN_STATUS=$FIRST_STATUS
    RUN_PID=
    if [ "$RUN_STATUS" -ne 0 ]; then
        # The reader may have died before opening the FIFO; stop a writer
        # blocked in open() so an early pipeline error cannot hang the demo.
        kill "$REPLAY_PID" 2>/dev/null || true
    fi
fi
if [ -n "$REPLAY_PID" ]; then
    set +e; wait "$REPLAY_PID"; REPLAY_STATUS=$?; set -e
    REPLAY_PID=
fi
if [ -n "$RUN_PID" ]; then
    set +e; wait "$RUN_PID"; RUN_STATUS=$?; set -e
    RUN_PID=
fi
[ "$REPLAY_STATUS" -eq 0 ] || fail "paced replay failed (status $REPLAY_STATUS)"
[ "$RUN_STATUS" -eq 0 ] || fail "pipeline failed (status $RUN_STATUS)"
echo "Replay complete. The dashboard now shows the completed synthetic run. Press Ctrl-C to close it."
wait "$DASH_PID"
