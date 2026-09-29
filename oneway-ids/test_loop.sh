#!/usr/bin/env bash
# Continuous test loop for the one-way NIDS (dev tool; not committed).
#
# Usage:  test_loop.sh [passes|inf] [sleep-seconds]
#         test_loop.sh 1        # one pass
#         test_loop.sh inf 30   # forever, 30s between passes
#
# Each pass:
#   1. every unit suite that exists (test_*.py)
#   2. offline replay of traffic.pcap, byte-parity vs .regression reference
#      (rules run; plus --ml run when model_ml.txt exists)
#   3. dashboard.py API smoke on :8613
#   4. metrics.py endpoint smoke on :9199 (only if the exporter exists)
#
# Repo safety: alerts.jsonl and run_stats.json are backed up to .loop_backup/
# at loop start and restored after every replay (replays truncate and rewrite
# alerts.jsonl as a side effect of the sink). Everything else is read-only:
# the loop TESTS, it never edits source.
#
# State: per-pass summary in .loop_results/last.json, full log in
# .loop_results/log.txt. Exit code: 0 if every pass green, 1 on any failure.
set -u
cd "$(dirname "$0")"
ROOT="$(pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY=python3
RES="$ROOT/.loop_results"
BAK="$ROOT/.loop_backup"
PASSES="${1:-1}"
SLEEP="${2:-20}"
DASH_PORT=8613
METRICS_PORT=9199
mkdir -p "$RES" "$BAK"

# ------------------------------------------------------------- repo safety --
# snapshot refreshed IMMEDIATELY BEFORE each replay (not once at loop start):
# alerts.jsonl / run_stats.json are live files another session may be writing,
# so the restore must put back the newest pre-replay content, never a stale
# loop-start copy.
snapshot() {
    for f in alerts.jsonl run_stats.json; do
        [ -e "$ROOT/$f" ] && cp -p "$ROOT/$f" "$BAK/$f" 2>/dev/null
    done
}

restore() {
    for f in alerts.jsonl run_stats.json; do
        if [ -e "$BAK/$f" ] && ! cmp -s "$ROOT/$f" "$BAK/$f" 2>/dev/null; then
            cp -p "$BAK/$f" "$ROOT/$f"
            echo "[$(date +%T)] restored $f from .loop_backup/" >> "$RES/log.txt"
        fi
    done
}
trap restore EXIT

summary_line() {  # summary_line <pass> <status> <detail>
    printf '[%s] pass %s: %s %s\n' "$(date +%T)" "$1" "$2" "$3" | tee -a "$RES/log.txt"
}

run_one_pass() {
    local pass="$1" failures=0
    local head dirty
    head=$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo "nogit")
    dirty=$(git -C "$ROOT" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    echo "===== pass $pass | $(date +%F' '%T) | HEAD $head | dirty:$dirty =====" >> "$RES/log.txt"

    # ---- 1. unit suites -----------------------------------------------------
    declare -A suite_rc
    for t in "$ROOT"/tests/test_*.py; do
        name=$(basename "$t" .py)
        s=$SECONDS
        timeout 120 "$PY" "$t" > "$RES/$name.out" 2>&1
        rc=$?
        suite_rc[$name]=$rc
        echo "  suite $name: rc=$rc ($((SECONDS-s))s)" >> "$RES/log.txt"
        [ $rc -ne 0 ] && { failures=$((failures+1)); tail -5 "$RES/$name.out" >> "$RES/log.txt"; }
    done

    # ---- 2. replay + regression parity --------------------------------------
    snapshot
    s=$SECONDS
    timeout 60 "$PY" run.py > "$RES/replay.out" 2>&1
    replay_rc=$?
    echo "  replay: rc=$replay_rc ($((SECONDS-s))s)" >> "$RES/log.txt"
    [ $replay_rc -ne 0 ] && { failures=$((failures+1)); tail -5 "$RES/replay.out" >> "$RES/log.txt"; }

    if [ -e "$ROOT/.regression/alerts_rules.reference.jsonl" ]; then
        if cmp -s "$ROOT/alerts.jsonl" "$ROOT/.regression/alerts_rules.reference.jsonl"; then
            echo "  parity(rules): BYTE-IDENTICAL" >> "$RES/log.txt"
        else
            echo "  parity(rules): DIVERGED" >> "$RES/log.txt"
            failures=$((failures+1))
        fi
    fi
    if [ -e "$ROOT/model_ml.txt" ] && [ -e "$ROOT/.regression/alerts_ml.reference.jsonl" ]; then
        s=$SECONDS
        timeout 90 "$PY" run.py --ml > "$RES/replay_ml.out" 2>&1
        ml_rc=$?
        echo "  replay --ml: rc=$ml_rc ($((SECONDS-s))s)" >> "$RES/log.txt"
        if cmp -s "$ROOT/alerts.jsonl" "$ROOT/.regression/alerts_ml.reference.jsonl"; then
            echo "  parity(ml): BYTE-IDENTICAL" >> "$RES/log.txt"
        else
            echo "  parity(ml): DIVERGED" >> "$RES/log.txt"
            failures=$((failures+1))
        fi
    fi
    restore

    # ---- 3. dashboard smoke ---------------------------------------------------
    if [ -e "$ROOT/dashboard.py" ]; then
        "$PY" dashboard.py $DASH_PORT > "$RES/dashboard.out" 2>&1 &
        dash_pid=$!
        dash_rc=1
        for _ in 1 2 3 4 5 6; do
            sleep 0.5
            if curl -fsS --max-time 3 "http://127.0.0.1:$DASH_PORT/api/stats" \
                    | grep -q '"total"'; then
                if curl -fsS --max-time 3 "http://127.0.0.1:$DASH_PORT/" | grep -qi "<html"; then
                    dash_rc=0
                fi
                break
            fi
        done
        kill $dash_pid 2>/dev/null; wait $dash_pid 2>/dev/null
        echo "  dashboard(:$DASH_PORT): rc=$dash_rc" >> "$RES/log.txt"
        [ $dash_rc -ne 0 ] && { failures=$((failures+1)); tail -5 "$RES/dashboard.out" >> "$RES/log.txt"; }
    fi

    # ---- 4. metrics exporter smoke --------------------------------------------
    if [ -e "$ROOT/core/metrics.py" ]; then
        "$PY" - "$METRICS_PORT" > "$RES/metrics.out" 2>&1 <<'PYEOF' &
import sys, time
sys.path.insert(0, "core")          # run via stdin: CWD is root, core/ is a package
from core.detectors import AlertSink
from core.metrics import NidsMetrics
m = NidsMetrics(AlertSink(path="/dev/null", truncate=False))
m.serve(int(sys.argv[1]), host="127.0.0.1")
time.sleep(30)
PYEOF
        met_pid=$!
        met_status=skip
        for _ in 1 2 3 4 5 6; do
            sleep 0.5
            body=$(curl -fsS --max-time 3 "http://127.0.0.1:$METRICS_PORT/metrics" 2>/dev/null) || continue
            if printf '%s' "$body" | grep -q '^nids_process_start_time_seconds'; then
                met_status=ok
            else
                met_status=bad
            fi
            break
        done
        kill $met_pid 2>/dev/null; wait $met_pid 2>/dev/null
        echo "  metrics(:$METRICS_PORT): $met_status" >> "$RES/log.txt"
        case $met_status in
            ok)  : ;;
            bad) failures=$((failures+1)) ;;
            skip) [ -e "$ROOT/core/metrics.py" ] && failures=$((failures+1)) ;;
        esac
    else
        echo "  metrics: skipped (no core/metrics.py on this tree)" >> "$RES/log.txt"
    fi

    # ---- summary ---------------------------------------------------------------
    if [ $failures -eq 0 ]; then
        summary_line "$pass" "PASS" "(HEAD $head, dirty:$dirty)"
    else
        summary_line "$pass" "FAIL" "($failures failing checks, HEAD $head, dirty:$dirty)"
        printf 'pass %s (%s) failed\n' "$pass" "$(date +%F' '%T)" > "$RES/last_failure.txt"
    fi
    printf '{"pass": %s, "ts": "%s", "head": "%s", "dirty": %s, "failures": %s}\n' \
        "$pass" "$(date -Iseconds)" "$head" "$dirty" "$failures" > "$RES/last.json"
    return $failures
}

# ---------------------------------------------------------------- main loop --
i=1
overall=0
while : ; do
    run_one_pass "$i"
    rc=$?
    [ $rc -ne 0 ] && overall=1
    [ "$PASSES" = "inf" ] || [ "$i" -ge "$PASSES" ] 2>/dev/null && break
    i=$((i+1))
    sleep "$SLEEP"
done
echo "loop finished after $i pass(es), overall=$overall" | tee -a "$RES/log.txt"
exit $overall
