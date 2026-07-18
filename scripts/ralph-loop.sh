#!/usr/bin/env bash
# Ralph Loop: run the slice queue autonomously until it is done or genuinely blocked.
# Usage: ./scripts/ralph-loop.sh [max_iterations]   (default 250)
#
# Per iteration: one normal Ralph run (preflight -> agent -> gates -> commit -> merge -> push).
# On a failed run: the same quarantined worktree is repaired until validation is
# green, an unchanged failure exhausts run.max_retries, or the progressive repair
# safety ceiling is reached. The queue never advances from a red slice.
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"
source "$repo_root/scripts/lib/ralph-exit-protocol.sh"
source "$repo_root/scripts/lib/ralph-retry-policy.sh"
source "$repo_root/scripts/lib/ralph-repair-context.sh"
source "$repo_root/scripts/lib/ralph-oversized-slice.sh"
source "$repo_root/scripts/lib/ralph-slice-selection.sh"
source "$repo_root/scripts/lib/ralph-architecture-review.sh"

if [[ "$repo_root" == *"/.ralph/worktrees/"* ]]; then
  echo "Refusing to run: current directory is inside a Ralph worktree ($repo_root)." >&2
  exit 1
fi

max_iterations="${1:-250}"
if ! [[ "$max_iterations" =~ ^[1-9][0-9]*$ ]]; then
  echo "max_iterations must be a positive integer." >&2
  exit "$RALPH_EXIT_ITERATION_LIMIT"
fi
mkdir -p .ralph/logs
loop_log=".ralph/logs/loop-$(date '+%Y-%m-%d_%H%M%S').log"
last_out=".ralph/logs/last-run-output.log"
review_failures_this_loop=0
max_repair_attempts="$(ralph_max_repair_attempts .ralph/config.yaml)"
max_progressive_repair_attempts="$(ralph_max_progressive_repair_attempts .ralph/config.yaml)"

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
  local counts complete not_started blocked superseded total remaining
  counts="$(ralph_queue_status_counts docs/slices 2>/dev/null || true)"
  if IFS=$'\t' read -r complete not_started blocked superseded total <<< "$counts" \
      && [[ "$complete" =~ ^[0-9]+$ && "$not_started" =~ ^[0-9]+$ \
          && "$blocked" =~ ^[0-9]+$ && "$superseded" =~ ^[0-9]+$ \
          && "$total" =~ ^[0-9]+$ ]]; then
    remaining=$((not_started + blocked))
    echo "Progress: $complete/$total actionable product slices complete; $remaining remaining ($not_started Not Started, $blocked Blocked); $superseded Superseded history excluded."
  else
    echo "Progress: queue status counts unavailable."
  fi
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

run_bounded_repair() {
  local repair_status="${1:-1}"
  local current_failure_signature="" next_failure_signature=""
  local repairs_for_signature=0 total_repair_attempts=0
  local repair_args=()

  if ralph_repair_context_is_resumable "$repo_root" "$repo_root/.ralph/repair-context.json"; then
    current_failure_signature="$(ralph_repair_context_value "$repo_root/.ralph/repair-context.json" failure_signature)"
    echo "Repair will reuse the quarantined failed worktree." | tee -a "$loop_log"
  fi
  echo "Run failed. Repairing the same slice until green: up to $max_repair_attempts attempt(s) per unchanged failure and $max_progressive_repair_attempts progressive attempt(s) overall." | tee -a "$loop_log"

  while (( total_repair_attempts < max_progressive_repair_attempts )); do
    if (( repairs_for_signature >= max_repair_attempts )); then
      echo "Repair reproduced the same failure signature after $repairs_for_signature attempt(s). Stopping this slice without advancing the queue." | tee -a "$loop_log"
      return "$repair_status"
    fi

    total_repair_attempts=$((total_repair_attempts + 1))
    repairs_for_signature=$((repairs_for_signature + 1))
    echo "Repair attempt $total_repair_attempts/$max_progressive_repair_attempts (failure-signature attempt $repairs_for_signature/$max_repair_attempts)." | tee -a "$loop_log"
    repair_args=(1 --mode repair)
    if ralph_repair_context_is_resumable "$repo_root" "$repo_root/.ralph/repair-context.json"; then
      repair_args+=(--resume-failed)
    fi
    run_streamed env AGENT_TOOL="$active_tool" CODEX_REASONING_EFFORT=high ./scripts/afk-dev.sh "${repair_args[@]}"
    repair_status=$?
    if (( repair_status == RALPH_EXIT_AGENT_LIMIT )); then
      switch_agent_or_stop
      echo "Retrying repair attempt $total_repair_attempts/$max_progressive_repair_attempts with $active_tool." | tee -a "$loop_log"
      run_streamed env AGENT_TOOL="$active_tool" CODEX_REASONING_EFFORT=high ./scripts/afk-dev.sh "${repair_args[@]}"
      repair_status=$?
    fi
    context_tripwire_check

    if (( repair_status == RALPH_EXIT_MERGE_FAILED )); then
      echo "Repair validation passed but final merge failed; stopping with the completed branch preserved instead of launching another product repair." | tee -a "$loop_log"
      return "$repair_status"
    fi
    if (( repair_status == RALPH_EXIT_BROWSER_INFRASTRUCTURE )); then
      echo "Browser infrastructure remains unavailable after bounded recovery; stopping outside product repair." | tee -a "$loop_log"
      return "$repair_status"
    fi

    if (( repair_status == 0 )); then
      return 0
    fi

    next_failure_signature=""
    if [[ -f "$repo_root/.ralph/repair-context.json" ]]; then
      next_failure_signature="$(ralph_repair_context_value "$repo_root/.ralph/repair-context.json" failure_signature 2>/dev/null || true)"
    fi
    if [[ -n "$next_failure_signature" && "$next_failure_signature" != "$current_failure_signature" ]]; then
      current_failure_signature="$next_failure_signature"
      repairs_for_signature=0
      echo "Independent validation progressed to a different failure signature; continuing repair in the same worktree." | tee -a "$loop_log"
    else
      echo "Independent validation reproduced the current failure signature; its bounded counter remains in force." | tee -a "$loop_log"
    fi

    echo "Repair attempt $total_repair_attempts failed; the next repair will diagnose its newly generated failure-summary.md." | tee -a "$loop_log"
  done

  echo "Progressive repair safety ceiling reached after $total_repair_attempts attempt(s). Stopping this slice without advancing the queue." | tee -a "$loop_log"
  return "$repair_status"
}

# A measured diff-limit failure is a queue-shaping problem, not a product-code
# defect. Discard the ungated implementation, then ask a clean planning run to
# replace the oversized slice with independently executable successor slices.
run_split_planning_attempt() {
  local slice_id="${1:?slice id is required}"
  local failed_run_id="${2:?failed run id is required}"
  local total_lines="${3:?total lines is required}"
  local max_lines="${4:?max lines is required}"
  local corrective_run_id="${5:-}"
  local split_env=(
    AGENT_TOOL="$active_tool"
    CODEX_REASONING_EFFORT=high
    RALPH_SPLIT_SLICE_ID="$slice_id"
    RALPH_SPLIT_FAILED_RUN_ID="$failed_run_id"
    RALPH_SPLIT_TOTAL_LINES="$total_lines"
    RALPH_SPLIT_MAX_LINES="$max_lines"
  )
  [[ -n "$corrective_run_id" ]] \
    && split_env+=(RALPH_SPLIT_CORRECTIVE_RUN_ID="$corrective_run_id")
  run_streamed env "${split_env[@]}" ./scripts/afk-dev.sh 1 --mode architecture-review
}

run_oversized_slice_split() {
  local request="${1:?trusted split request is required}"
  local slice_id failed_run_id total_lines max_lines split_status
  local split_attempt corrective_run_id="" retry_context failure_signature
  local max_split_attempts=2
  IFS=$'\t' read -r slice_id failed_run_id total_lines max_lines <<< "$request"

  echo "Slice $slice_id measured $total_lines changed lines (limit $max_lines). Replacing it with dependency-ordered successor slices before any product repair." | tee -a "$loop_log"
  if ! ./scripts/ralph-recover.sh 2>&1 | tee -a "$loop_log"; then
    echo "Unable to discard the ungated oversized worktree safely; stopping before queue maintenance." | tee -a "$loop_log"
    return 1
  fi

  for ((split_attempt = 1; split_attempt <= max_split_attempts; split_attempt++)); do
    if (( split_attempt == 1 )); then
      echo "Oversized-slice planning attempt 1/$max_split_attempts." | tee -a "$loop_log"
    else
      echo "Corrective oversized-slice planning attempt $split_attempt/$max_split_attempts using diagnostics from $corrective_run_id." | tee -a "$loop_log"
    fi

    run_split_planning_attempt \
      "$slice_id" "$failed_run_id" "$total_lines" "$max_lines" "$corrective_run_id"
    split_status=$?
    if (( split_status == RALPH_EXIT_AGENT_LIMIT )); then
      switch_agent_or_stop
      ./scripts/ralph-recover.sh 2>&1 | tee -a "$loop_log" || return 1
      echo "Retrying oversized-slice planning attempt $split_attempt/$max_split_attempts with $active_tool." | tee -a "$loop_log"
      run_split_planning_attempt \
        "$slice_id" "$failed_run_id" "$total_lines" "$max_lines" "$corrective_run_id"
      split_status=$?
      if (( split_status == RALPH_EXIT_AGENT_LIMIT )); then
        switch_agent_or_stop
      fi
    fi
    context_tripwire_check

    if (( split_status == RALPH_EXIT_SUCCESS )); then
      return 0
    fi
    if ! ralph_oversized_split_retry_allowed \
        "$split_status" "$split_attempt" "$max_split_attempts"; then
      return "$split_status"
    fi
    retry_context="$(ralph_oversized_split_retry_context \
      "$repo_root" "$repo_root/.ralph/repair-context.json" "$slice_id")" \
      || return "$split_status"
    IFS=$'\t' read -r corrective_run_id failure_signature <<< "$retry_context"
    echo "Split validation failed with signature $failure_signature; discarding the rejected planning worktree and launching one bounded corrective rewrite." | tee -a "$loop_log"
    if ! ./scripts/ralph-recover.sh 2>&1 | tee -a "$loop_log"; then
      echo "Unable to recover the rejected split-planning worktree; stopping before correction." | tee -a "$loop_log"
      return "$split_status"
    fi
    if [[ ! -s "$repo_root/.ralph/runs/$corrective_run_id/failure-summary.md" \
        || ! -s "$repo_root/.ralph/runs/$corrective_run_id/oversized-slice-split-results.md" ]]; then
      echo "Recovered split diagnostics are incomplete for $corrective_run_id; stopping safely." | tee -a "$loop_log"
      return "$split_status"
    fi
  done

  return "$split_status"
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

  if ! review_due="$(ralph_architecture_review_due .ralph/state.json)"; then
    echo "Stopping: cannot read a valid architecture-review state; refusing to run or declare completion." | tee -a "$loop_log"
    exit 2
  fi
  if [[ "$review_due" == "True" ]]; then
    # A failed review keeps architecture_review_due set (it only resets on a
    # validated success), so without a cap a persistent failure cause taxes
    # every iteration with a doomed review attempt. Two strikes per loop run,
    # then continue the queue; the review stays due for the next loop start.
    if (( review_failures_this_loop >= 2 )); then
      if [[ -z "$(ralph_remaining_slices docs/slices)" ]]; then
        echo "Stopping: the product queue is empty, but the mandatory final architecture review failed twice. Refusing to declare final completion." | tee -a "$loop_log"
        exit 2
      fi
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
        if [[ -z "$(ralph_remaining_slices docs/slices)" ]]; then
          if (( review_failures_this_loop >= 2 )); then
            echo "Stopping: the product queue is empty, but the mandatory final architecture review failed twice. Refusing to declare final completion." | tee -a "$loop_log"
            exit 2
          fi
          echo "Mandatory final architecture review failed (strike 1/2); retrying before final completion." | tee -a "$loop_log"
          continue
        fi
        echo "Architecture review failed (non-fatal, strike $review_failures_this_loop/2 this loop); continuing with the product queue." | tee -a "$loop_log"
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
      if ! review_due="$(ralph_architecture_review_due .ralph/state.json)"; then
        echo "Stopping: cannot read a valid architecture-review state; refusing to declare final completion." | tee -a "$loop_log"
        exit 2
      fi
      if [[ "$review_due" == "True" ]]; then
        echo "Stopping: the product queue is empty, but a mandatory architecture review remains due. Refusing to declare final completion." | tee -a "$loop_log"
        exit 2
      fi
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
      echo "Stopping: a validated/quarantined branch could not be safely finalized or merged into staging." | tee -a "$loop_log"
      echo "The work is kept on its ralph/* branch — inspect the commit/merge evidence in an owner chat, then integrate it safely. Do not rerun the slice." | tee -a "$loop_log"
      exit 1
      ;;
    agent_limit)
      switch_agent_or_stop
      echo "The interrupted slice will rerun with $active_tool." | tee -a "$loop_log"
      continue
      ;;
    browser_infrastructure)
      echo "Stopping: Playwright browser infrastructure is unavailable after one bounded recovery. Product repair was not started." | tee -a "$loop_log"
      echo "See the latest browser-infrastructure-results.md and browser-infrastructure-probe.log, restore a browser, then rerun the loop." | tee -a "$loop_log"
      exit "$RALPH_EXIT_BROWSER_INFRASTRUCTURE"
      ;;
  esac

  if (( status != 0 )); then
    split_request=""
    if split_request="$(ralph_oversized_slice_request "$repo_root" "$repo_root/.ralph/repair-context.json")"; then
      if run_oversized_slice_split "$split_request"; then
        echo "Oversized slice queue rewrite passed independent validation; continuing with its first successor." | tee -a "$loop_log"
        continue
      fi
      echo "Oversized slice queue rewrite failed. Stopping for human review without launching product repair." | tee -a "$loop_log"
      exit 1
    fi
    run_bounded_repair "$status"
    repair_status=$?
    if (( repair_status == RALPH_EXIT_BROWSER_INFRASTRUCTURE )); then
      echo "Stopping: Playwright browser infrastructure became unavailable during repair. No further product repair will run." | tee -a "$loop_log"
      exit "$RALPH_EXIT_BROWSER_INFRASTRUCTURE"
    fi
    if (( repair_status != 0 )); then
      echo "All bounded repair attempts failed. Stopping for human review — see $loop_log and the latest .ralph/runs/ folder." | tee -a "$loop_log"
      exit 1
    fi
  fi
done

if ! review_due="$(ralph_architecture_review_due .ralph/state.json)"; then
  echo "Stopping at the iteration limit: architecture-review state is invalid." | tee -a "$loop_log"
  exit 2
fi
if [[ "$review_due" == "True" && -z "$(ralph_remaining_slices docs/slices)" ]]; then
  echo "Stopping at the iteration limit: product work is empty but the mandatory final architecture review remains due." | tee -a "$loop_log"
  exit 2
fi
progress_line | tee -a "$loop_log"
echo "Stopped incomplete after reaching max iterations ($max_iterations). Run './scripts/ralph-loop.sh' again to continue the queue." | tee -a "$loop_log"
exit "$RALPH_EXIT_ITERATION_LIMIT"
