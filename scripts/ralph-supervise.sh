#!/usr/bin/env bash
# Durable outer supervisor for unattended Ralph execution. It restarts only
# outcomes classified as replay-safe; the loop's startup recovery removes dead
# worktrees and requeues unfinished slices before product work resumes.
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"
source "$repo_root/scripts/lib/ralph-exit-protocol.sh"
source "$repo_root/scripts/lib/ralph-supervisor.sh"

max_restarts="${RALPH_SUPERVISOR_MAX_RESTARTS:-48}"
base_delay="${RALPH_SUPERVISOR_BASE_DELAY_SECONDS:-30}"
max_delay="${RALPH_SUPERVISOR_MAX_DELAY_SECONDS:-300}"
for value in "$max_restarts" "$base_delay" "$max_delay"; do
  [[ "$value" =~ ^[0-9]+$ ]] || {
    echo "Supervisor limits must be non-negative integers." >&2
    exit 2
  }
done
(( max_restarts > 0 && max_delay > 0 )) || {
  echo "Supervisor restart count and maximum delay must be positive." >&2
  exit 2
}

mkdir -p .ralph/logs
supervisor_log=".ralph/logs/supervisor-$(date '+%Y-%m-%d_%H%M%S').log"
restart=0
stop_requested=0
child_pid=""
child_is_process_group=0
request_stop() {
  local signal="${1:-TERM}"
  stop_requested=1
  if [[ "$child_pid" =~ ^[1-9][0-9]*$ ]] && kill -0 "$child_pid" 2>/dev/null; then
    if (( child_is_process_group == 1 )); then
      kill -s "$signal" -- "-$child_pid" 2>/dev/null || true
    else
      kill -s "$signal" "$child_pid" 2>/dev/null || true
    fi
  fi
}
trap 'request_stop INT' INT
trap 'request_stop TERM' TERM

echo "Ralph supervisor starting. Log: $supervisor_log" | tee -a "$supervisor_log"
while (( stop_requested == 0 )); do
  status=0
  # Python is already a required Ralph runtime. Make it a new session leader,
  # then replace it with the loop so every agent/validator descendant belongs
  # to one process group that owner signals can stop atomically.
  python3 - "$repo_root/scripts/ralph-loop.sh" "$@" <<'PY' &
import os
import signal
import sys

script, *arguments = sys.argv[1:]
os.setsid()
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)
os.execv(script, [script, *arguments])
PY
  child_pid=$!
  child_is_process_group=1
  wait "$child_pid" || status=$?
  if (( stop_requested != 0 )); then
    # A trap can interrupt wait before the group leader is reaped. Wait for it,
    # then give descendants a short TERM grace period and kill only this
    # isolated group if anything ignored the owner stop.
    wait "$child_pid" 2>/dev/null || true
    for _ in {1..50}; do
      kill -0 -- "-$child_pid" 2>/dev/null || break
      sleep 0.1
    done
    if kill -0 -- "-$child_pid" 2>/dev/null; then
      kill -KILL -- "-$child_pid" 2>/dev/null || true
    fi
    child_pid=""
    child_is_process_group=0
    echo "Supervisor stopped by owner signal." | tee -a "$supervisor_log"
    exit 130
  fi
  child_pid=""
  child_is_process_group=0
  outcome="$(ralph_supervisor_outcome_for_status "$status")"
  printf 'Ralph loop exited %s (%s).\n' "$status" "$outcome" | tee -a "$supervisor_log"

  case "$outcome" in
    complete)
      echo "Ralph queue completed; supervisor finished." | tee -a "$supervisor_log"
      exit 0
      ;;
    stop)
      echo "Supervisor preserved the fail-closed outcome; inspect the latest loop log." \
        | tee -a "$supervisor_log"
      exit "$status"
      ;;
    retry) ;;
  esac

  restart=$((restart + 1))
  if (( restart > max_restarts )); then
    echo "Supervisor exhausted $max_restarts safe restarts; stopping for diagnosis." \
      | tee -a "$supervisor_log"
    exit "$status"
  fi
  delay=$((base_delay * restart))
  (( delay > max_delay )) && delay=$max_delay
  echo "Recoverable outcome; restarting after ${delay}s ($restart/$max_restarts)." \
    | tee -a "$supervisor_log"
  sleep "$delay" &
  child_pid=$!
  child_is_process_group=0
  wait "$child_pid" || true
  child_pid=""
done

echo "Supervisor stopped by owner signal." | tee -a "$supervisor_log"
exit 130
