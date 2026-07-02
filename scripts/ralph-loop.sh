#!/usr/bin/env bash
# Ralph Loop: run the slice queue autonomously until it is done or genuinely blocked.
# Usage: ./scripts/ralph-loop.sh [max_iterations]   (default 25)
#
# Per iteration: one normal Ralph run (preflight -> agent -> gates -> commit -> merge -> push).
# On a failed run: one repair run is attempted, then the slice is retried once.
# The loop stops when: the queue is empty, a slice still fails after repair,
# 3 total failures accumulate, or a slice is vetoed by the owner.
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

if [[ "$repo_root" == *"/.ralph/worktrees/"* ]]; then
  echo "Refusing to run: current directory is inside a Ralph worktree ($repo_root)." >&2
  exit 1
fi

max_iterations="${1:-25}"
mkdir -p .ralph/logs
loop_log=".ralph/logs/loop-$(date '+%Y-%m-%d_%H%M%S').log"
total_failures=0

echo "Ralph loop starting (max $max_iterations iterations). Log: $loop_log"

# Recover from any interrupted previous session (limit exhaustion, crash),
# no matter which agent was driving it.
./scripts/ralph-recover.sh 2>&1 | tee -a "$loop_log"

for ((i = 1; i <= max_iterations; i++)); do
  echo "" | tee -a "$loop_log"
  echo "=== Ralph loop iteration $i/$max_iterations — $(date '+%Y-%m-%d %H:%M:%S') ===" | tee -a "$loop_log"

  review_due="$(python3 -c "import json; print(json.load(open('.ralph/state.json')).get('architecture_review_due', False))" 2>/dev/null || echo False)"
  if [[ "$review_due" == "True" ]]; then
    echo "Architecture review is due; running it before the next slice." | tee -a "$loop_log"
    review_output="$(CODEX_REASONING_EFFORT=high ./scripts/afk-dev.sh 1 --mode architecture-review 2>&1)"
    review_status=$?
    echo "$review_output" | tee -a "$loop_log"
    if (( review_status != 0 )); then
      echo "Architecture review failed (non-fatal); continuing with the queue." | tee -a "$loop_log"
    fi
  fi

  output="$(./scripts/afk-dev.sh 1 --mode normal 2>&1)"
  status=$?
  echo "$output" | tee -a "$loop_log"

  if echo "$output" | grep -q "No eligible slice found"; then
    echo "Queue complete: no eligible slices remain. Ralph loop finished." | tee -a "$loop_log"
    exit 0
  fi

  if echo "$output" | grep -q "has been vetoed by the owner"; then
    echo "Stopping: the next slice is vetoed. Remove the [revoked] line or run another slice with --slice." | tee -a "$loop_log"
    exit 2
  fi

  if (( status != 0 )); then
    total_failures=$((total_failures + 1))
    echo "Run failed (failure $total_failures/3). Attempting one repair run." | tee -a "$loop_log"

    repair_output="$(CODEX_REASONING_EFFORT=high ./scripts/afk-dev.sh 1 --mode repair 2>&1)"
    repair_status=$?
    echo "$repair_output" | tee -a "$loop_log"

    if (( repair_status != 0 )); then
      echo "Repair run also failed. Stopping the loop for human review — see $loop_log and the latest .ralph/runs/ folder." | tee -a "$loop_log"
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
