#!/usr/bin/env bash
# Ralph Loop: run the slice queue autonomously until it is done or genuinely blocked.
# Usage: ./scripts/ralph-loop.sh [max_iterations]   (default 25)
#
# Per iteration: one normal Ralph run (preflight -> agent -> gates -> commit -> merge -> push).
# On a failed run: the bounded repair budget from run.max_retries is attempted.
# The loop stops when: the queue is empty, a slice still fails after that budget,
# 3 total failures accumulate, or a slice is vetoed by the owner.
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"
source "$repo_root/scripts/lib/ralph-exit-protocol.sh"
source "$repo_root/scripts/lib/ralph-retry-policy.sh"

if [[ "$repo_root" == *"/.ralph/worktrees/"* ]]; then
  echo "Refusing to run: current directory is inside a Ralph worktree ($repo_root)." >&2
  exit 1
fi

max_iterations="${1:-25}"
mkdir -p .ralph/logs
loop_log=".ralph/logs/loop-$(date '+%Y-%m-%d_%H%M%S').log"
last_out=".ralph/logs/last-run-output.log"
total_failures=0
review_failures_this_loop=0
max_repair_attempts="$(ralph_max_repair_attempts .ralph/config.yaml)"

# Loop mutex: a second concurrent loop makes every run fail preflight on the
# other loop's live run lock, burning this loop's failure budget on collisions.
# Named loop.pid (not *.lock) so preflight's run-lock check never sees it.
mkdir -p .ralph/locks
loop_lock=".ralph/locks/loop.pid"
if [[ -f "$loop_lock" ]]; then
  existing_pid="$(sed -n '2p' "$loop_lock" 2>/dev/null || true)"
  if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
    echo "Refusing to start: another Ralph loop is already running (PID $existing_pid)." >&2
    echo "Wait for it or stop it first; two loops interleaving corrupt each other's failure budget." >&2
    exit 1
  fi
fi
printf 'ralph-loop\n%s\n' "$$" > "$loop_lock"
trap 'rm -f "$loop_lock"' EXIT

# Stream a run's output live to the terminal and the loop log instead of
# buffering it in a command substitution: buffering shows a blank screen for
# the entire run, and a straggler child holding the pipe hangs the loop.
# $last_out keeps a copy of just this run for the marker greps below.
run_streamed() {
  "$@" 2>&1 | tee "$last_out" | tee -a "$loop_log"
  return "${PIPESTATUS[0]}"
}

progress_line() {
  local completed total
  completed="$(python3 -c "import json; print(len(json.load(open('.ralph/state.json'))['completed_slices']))" 2>/dev/null || echo '?')"
  total="$(ls docs/slices/*.md 2>/dev/null | wc -l | xargs)"
  echo "Progress: $completed of $total slices complete."
}

# Usage-limit fallback (agent.limit_fallback in .ralph/config.yaml): when the
# active agent's usage limit is exhausted (adapters emit AGENT_LIMIT_EXHAUSTED),
# switch to the other allowed agent and retry; when both are exhausted, stop
# cleanly — every completed slice is already committed and pushed, and the
# interrupted slice reruns on the next loop.
default_tool="$(awk -F': *' '/^[[:space:]]*default_tool:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' .ralph/config.yaml | xargs || true)"
active_tool="${AGENT_TOOL:-${default_tool:-codex}}"
limit_fallback="$(awk -F': *' '/^[[:space:]]*limit_fallback:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' .ralph/config.yaml | xargs || true)"
limit_fallback="${limit_fallback:-true}"
exhausted_tools=""

# Advisory context-occupancy monitor. After a run, report the agent's PEAK
# per-call context vs the model window and record a note when it enters the
# watch/breach band. Strictly non-fatal: it never changes a run's exit status
# or the loop's control flow — splitting a slice stays an owner decision.
# Thresholds are tunable via env without editing this file.
context_watch_log=".ralph/logs/context-watch.log"
context_tripwire_check() {
  command -v python3 >/dev/null 2>&1 || return 0
  [[ -f scripts/ralph-context-tripwire.py ]] || return 0
  # Look at the last few runs, not just the newest-named one: right after a
  # failed review (no agent log) a --last 1 check analyses nothing at all.
  local fail="${CONTEXT_TRIPWIRE_FAIL:-0.85}" watch="${CONTEXT_TRIPWIRE_WATCH:-0.70}" out rc
  out="$(python3 scripts/ralph-context-tripwire.py --last "${CONTEXT_TRIPWIRE_LAST:-5}" --threshold "$fail" --watch "$watch" 2>/dev/null)"
  rc=$?
  printf '%s\n' "$out" | tee -a "$loop_log"
  if (( rc != 0 )) || printf '%s' "$out" | grep -q '\[watch \]'; then
    printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$(printf '%s' "$out" | grep -E '\[(watch |BREACH)\]')" >> "$context_watch_log"
    echo "Context trip-wire: run entered the watch/breach band (advisory; run NOT failed). History: $context_watch_log" | tee -a "$loop_log"
  fi
  return 0
}

# Switches active_tool to the other agent, or exits 3 when no usable agent
# remains (fallback disabled, other tool already exhausted, or not installed).
switch_agent_or_stop() {
  exhausted_tools="$exhausted_tools $active_tool"
  local next="claude"
  [[ "$active_tool" == "claude" ]] && next="codex"
  if [[ "$limit_fallback" != "true" ]]; then
    echo "Usage limit exhausted for $active_tool and agent.limit_fallback is disabled. Stopping; completed slices are committed — run './scripts/ralph-loop.sh' again after the limit resets." | tee -a "$loop_log"
    exit 3
  fi
  if [[ " $exhausted_tools " == *" $next "* ]] || ! command -v "$next" >/dev/null 2>&1; then
    echo "Usage limits exhausted for:$exhausted_tools — no agent left to switch to. Completed slices are committed; run './scripts/ralph-loop.sh' again after the limits reset." | tee -a "$loop_log"
    exit 3
  fi
  active_tool="$next"
  echo "Usage limit exhausted; switching agent to $active_tool and retrying." | tee -a "$loop_log"
}

echo "Ralph loop starting (max $max_iterations iterations). Log: $loop_log"

# Recover from any interrupted previous session (limit exhaustion, crash),
# no matter which agent was driving it.
./scripts/ralph-recover.sh 2>&1 | tee -a "$loop_log"

for ((i = 1; i <= max_iterations; i++)); do
  echo "" | tee -a "$loop_log"
  echo "=== Ralph loop iteration $i/$max_iterations — $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a "$loop_log"
  progress_line | tee -a "$loop_log"
  echo "Agent: $active_tool" | tee -a "$loop_log"

  review_due="$(python3 -c "import json; print(json.load(open('.ralph/state.json')).get('architecture_review_due', False))" 2>/dev/null || echo False)"
  if [[ "$review_due" == "True" ]]; then
    # A failed review keeps architecture_review_due set (it only resets on a
    # validated success), so without a cap a persistent failure cause taxes
    # every iteration with a doomed review attempt. Two strikes per loop run,
    # then continue the queue; the review stays due for the next loop start.
    if (( review_failures_this_loop >= 2 )); then
      echo "Architecture review already failed $review_failures_this_loop times this loop; skipping further attempts and continuing the queue (it stays due for the next loop run)." | tee -a "$loop_log"
    else
      echo "Architecture review is due; running it before the next slice." | tee -a "$loop_log"
      run_streamed env AGENT_TOOL="$active_tool" CODEX_REASONING_EFFORT=high ./scripts/afk-dev.sh 1 --mode architecture-review
      review_status=$?
      context_tripwire_check
      if (( review_status != 0 )); then
        if (( review_status == RALPH_EXIT_AGENT_LIMIT )); then
          switch_agent_or_stop
          continue
        fi
        review_failures_this_loop=$((review_failures_this_loop + 1))
        echo "Architecture review failed (non-fatal, strike $review_failures_this_loop/2 this loop); continuing with the queue." | tee -a "$loop_log"
      else
        review_failures_this_loop=0
      fi
    fi
  fi

  run_streamed env AGENT_TOOL="$active_tool" ./scripts/afk-dev.sh 1 --mode normal
  status=$?
  context_tripwire_check

  outcome="$(ralph_outcome_for_status "$status")"
  case "$outcome" in
    queue_empty)
      echo "Queue complete: no eligible slices remain. Ralph loop finished." | tee -a "$loop_log"
      exit 0
      ;;
    queue_blocked)
      echo "Stopping: unfinished slices remain but none is grabbable — each is waiting on an unmet Depends On prerequisite (missing slice or dependency cycle) or parked as Blocked." | tee -a "$loop_log"
      echo "See the Skipping lines above and the latest .ralph/runs/ final-summary.md, fix the Depends On graph or unblock the parked slices, then rerun the loop." | tee -a "$loop_log"
      exit 2
      ;;
    owner_veto)
      echo "Stopping: the next slice is vetoed. Remove the [revoked] line or run another slice with --slice." | tee -a "$loop_log"
      exit 2
      ;;
    merge_failed)
      echo "Stopping: a completed run could not merge into staging (staging moved during the run)." | tee -a "$loop_log"
      echo "The finished work is kept on its ralph/* branch — ask an agent in a chat session to merge it, then rerun the loop. Do not rerun the slice." | tee -a "$loop_log"
      exit 1
      ;;
    agent_limit)
      switch_agent_or_stop
      echo "The interrupted slice will rerun with $active_tool." | tee -a "$loop_log"
      continue
      ;;
  esac

  if (( status != 0 )); then
    total_failures=$((total_failures + 1))
    echo "Run failed (failure $total_failures/3). Up to $max_repair_attempts bounded repair attempt(s) are available." | tee -a "$loop_log"

    repair_status=$status
    for ((repair_attempt = 1; repair_attempt <= max_repair_attempts; repair_attempt++)); do
      echo "Repair attempt $repair_attempt/$max_repair_attempts." | tee -a "$loop_log"
      run_streamed env AGENT_TOOL="$active_tool" CODEX_REASONING_EFFORT=high ./scripts/afk-dev.sh 1 --mode repair
      repair_status=$?
      if (( repair_status == RALPH_EXIT_AGENT_LIMIT )); then
        switch_agent_or_stop
        echo "Retrying repair attempt $repair_attempt/$max_repair_attempts with $active_tool." | tee -a "$loop_log"
        run_streamed env AGENT_TOOL="$active_tool" CODEX_REASONING_EFFORT=high ./scripts/afk-dev.sh 1 --mode repair
        repair_status=$?
      fi
      context_tripwire_check

      if (( repair_status == 0 )); then
        break
      fi
      if (( repair_attempt < max_repair_attempts )); then
        echo "Repair attempt $repair_attempt failed; the next repair will diagnose its newly generated failure-summary.md." | tee -a "$loop_log"
      fi
    done

    if (( repair_status != 0 )); then
      echo "All $max_repair_attempts bounded repair attempts failed. Stopping for human review — see $loop_log and the latest .ralph/runs/ folder." | tee -a "$loop_log"
      exit 1
    fi

    if (( total_failures >= 3 )); then
      echo "Three failures in this loop. Stopping for human review — see $loop_log." | tee -a "$loop_log"
      exit 1
    fi
  fi
done

echo "Reached max iterations ($max_iterations). Run './scripts/ralph-loop.sh' again to continue the queue." | tee -a "$loop_log"
exit 0
