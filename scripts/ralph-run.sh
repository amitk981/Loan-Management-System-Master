#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"
source "$repo_root/scripts/lib/ralph-exit-protocol.sh"
source "$repo_root/scripts/lib/ralph-postgresql-acceptance.sh"
source "$repo_root/scripts/lib/ralph-slice-selection.sh"
source "$repo_root/scripts/lib/ralph-repair-context.sh"
source "$repo_root/scripts/lib/ralph-merge-guard.sh"
source "$repo_root/scripts/lib/ralph-node-runtime.sh"
source "$repo_root/scripts/lib/ralph-runtime-capabilities.sh"
source "$repo_root/scripts/lib/ralph-browser-runtime.sh"
source "$repo_root/scripts/lib/ralph-architecture-review.sh"
source "$repo_root/scripts/lib/ralph-worktree-ownership.sh"

if [[ "$repo_root" == *"/.ralph/worktrees/"* ]]; then
  echo "Refusing to run: current directory is inside a Ralph worktree ($repo_root)." >&2
  echo "Run Ralph from the main repository root so worktrees never nest." >&2
  exit 1
fi

run_id=""
mode="normal_run"
agent="${AGENT_TOOL:-codex}"
selected_slice=""
no_commit=0
no_worktree=0
continue_failed=0
resume_worktree=""
failed_run_id=""
branch_name=""
split_slice_id="${RALPH_SPLIT_SLICE_ID:-}"
split_failed_run_id="${RALPH_SPLIT_FAILED_RUN_ID:-}"
split_total_lines="${RALPH_SPLIT_TOTAL_LINES:-}"
split_max_lines="${RALPH_SPLIT_MAX_LINES:-}"
split_corrective_run_id="${RALPH_SPLIT_CORRECTIVE_RUN_ID:-}"
architecture_finalizer_epic=""
architecture_finalizer_root=""
architecture_terminal_repair_epic=""
architecture_terminal_repair_root=""
architecture_terminal_repair_finalizer=""
terminal_finalizer_rewrite="${RALPH_TERMINAL_FINALIZER_REWRITE:-0}"
terminal_recurrence_rewrite="${RALPH_TERMINAL_RECURRENCE_REWRITE:-0}"
[[ "$terminal_finalizer_rewrite" == "0" || "$terminal_finalizer_rewrite" == "1" ]] || {
  echo "RALPH_TERMINAL_FINALIZER_REWRITE must be 0 or 1." >&2
  exit 2
}
[[ "$terminal_recurrence_rewrite" == "0" || "$terminal_recurrence_rewrite" == "1" ]] || {
  echo "RALPH_TERMINAL_RECURRENCE_REWRITE must be 0 or 1." >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id) run_id="${2:?--run-id requires a value}"; shift 2 ;;
    --mode) mode="${2:?--mode requires a value}"; shift 2 ;;
    --agent) agent="${2:?--agent requires a value}"; shift 2 ;;
    --slice) selected_slice="${2:?--slice requires a value}"; shift 2 ;;
    --no-commit) no_commit=1; shift ;;
    --no-worktree) no_worktree=1; shift ;;
    --continue-failed) continue_failed=1; shift ;;
    --resume-worktree) resume_worktree="${2:?--resume-worktree requires a value}"; shift 2 ;;
    --failed-run-id) failed_run_id="${2:?--failed-run-id requires a value}"; shift 2 ;;
    *) echo "Unknown run argument: $1" >&2; exit 2 ;;
  esac
done

if [[ -n "$split_slice_id" ]]; then
  if [[ "$mode" != "architecture_review" \
      || ! "$split_slice_id" =~ ^[A-Za-z0-9]+$ \
      || ! "$split_failed_run_id" =~ ^[A-Za-z0-9_.-]+$ \
      || ! "$split_total_lines" =~ ^[0-9]+$ \
      || ! "$split_max_lines" =~ ^[0-9]+$ \
      || ( -n "$split_corrective_run_id" && ! "$split_corrective_run_id" =~ ^[A-Za-z0-9_.-]+$ ) \
      || "$split_total_lines" -le "$split_max_lines" ]]; then
    echo "Invalid oversized-slice planning environment." >&2
    exit 2
  fi
  split_slice_file="$(find docs/slices -maxdepth 1 -type f -name "${split_slice_id}-*.md" | sort | head -n 1)"
  if [[ -z "$split_slice_file" ]]; then
    echo "Oversized source slice is missing: $split_slice_id" >&2
    exit 2
  fi
  if [[ -n "$split_corrective_run_id" ]]; then
    split_corrective_run_dir="$repo_root/.ralph/runs/$split_corrective_run_id"
    if [[ ! -s "$split_corrective_run_dir/failure-summary.md" \
        || ! -s "$split_corrective_run_dir/oversized-slice-split-results.md" ]]; then
      echo "Corrective oversized-slice evidence is missing for run: $split_corrective_run_id" >&2
      exit 2
    fi
  fi
fi

if [[ -n "$resume_worktree" || -n "$failed_run_id" ]]; then
  if [[ ( "$mode" != "repair" && "$mode" != "architecture_review" ) \
      || -z "$resume_worktree" || -z "$failed_run_id" || "$no_worktree" == 1 || "$no_commit" == 1 ]]; then
    echo "Same-worktree resume requires repair or architecture-review mode, commit/validation enabled, --resume-worktree, and --failed-run-id." >&2
    exit 2
  fi
fi

integration_branch="$(awk -F': *' '/^[[:space:]]*integration_branch:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
integration_branch="${integration_branch:-staging}"
current_branch="$(git symbolic-ref --short HEAD 2>/dev/null || echo detached)"
if [[ "$current_branch" != "$integration_branch" ]]; then
  echo "Refusing to run: repository is on '$current_branch' but agent work integrates only into '$integration_branch'." >&2
  echo "Fix: git checkout $integration_branch   (only the owner promotes $integration_branch to main)." >&2
  exit 1
fi

run_id="${run_id:-$(date '+%Y-%m-%d_%H%M%S')_$mode}"
main_run_dir="$repo_root/.ralph/runs/$run_id"
run_dir="$main_run_dir"

select_slice() {
  if [[ -n "$selected_slice" ]]; then
    ralph_resolve_explicit_slice \
      "$selected_slice" docs/slices "$mode" .ralph/repair-context.json
    return
  fi
  ralph_first_grabbable_slice docs/slices
}

slice_file=""
if [[ "$mode" == "architecture_review" ]]; then
  if [[ -n "$selected_slice" ]]; then
    echo "Explicit product slice selection is invalid in architecture-review mode." >&2
    exit 2
  fi
  slice_id="architecture-review"
  slice_file="architecture-review.md"
else
  if [[ -n "$selected_slice" ]]; then
    slice_file="$(select_slice)" || exit 2
  else
    slice_file="$(select_slice || true)"
  fi
  if [[ -z "$slice_file" ]]; then
    remaining_slices="$(ralph_remaining_slices)"
    mkdir -p "$run_dir"
    if [[ -n "$remaining_slices" ]]; then
      {
        echo "# Final Summary"
        echo
        echo "Result: Blocked — Dependency-Blocked Queue"
        echo
        echo "Unfinished slices remain, but none is grabbable: each is waiting on an unmet"
        echo "Depends On prerequisite (missing slice or dependency cycle) or parked as Blocked:"
        echo
        while IFS= read -r remaining_line; do
          if [[ -n "$remaining_line" ]]; then
            echo "- $remaining_line"
          fi
        done <<< "$remaining_slices"
      } > "$run_dir/final-summary.md"
      echo "Queue blocked: unfinished slices remain but none is grabbable." >&2
      exit "$RALPH_EXIT_QUEUE_BLOCKED"
    fi
    cat > "$run_dir/final-summary.md" <<'EOF'
# Final Summary

Result: Success

No eligible slice was found.
EOF
    echo "No eligible slice found."
    exit "$RALPH_EXIT_QUEUE_EMPTY"
  fi
  slice_id="${slice_file%.md}"
fi

if [[ "$mode" != "architecture_review" ]]; then
  selected_slice_path="docs/slices/$slice_file"
  if ! ralph_validate_slice_runtime_requirements "$selected_slice_path"; then
    echo "Selected slice has an invalid or incomplete trusted runtime contract: $slice_file" >&2
    exit 2
  fi
  if ralph_slice_has_capability \
      "$selected_slice_path" "$RALPH_CAPABILITY_POSTGRESQL_FIVE_RACE_ACCEPTANCE" \
      && ! ralph_validate_trusted_postgresql_acceptance "$selected_slice_path"; then
    echo "Selected slice has a malformed trusted PostgreSQL acceptance contract: $slice_file" >&2
    exit 2
  fi
  risk_level="$(awk '/^## Risk Level/ { getline; print; exit }' "docs/slices/$slice_file" | xargs || true)"
  approvals_file="docs/working/HIGH_RISK_APPROVALS.md"
  if grep -qF -- "[revoked] $slice_id" "$approvals_file" 2>/dev/null; then
    echo "Slice $slice_id has been vetoed by the owner in $approvals_file; refusing to run it." >&2
    exit "$RALPH_EXIT_OWNER_VETO"
  fi
  if [[ "$risk_level" == "High" ]]; then
    echo "High-risk slice $slice_id proceeding under the owner's standing approval (see $approvals_file)."
  fi
  if grep -q '^## Architecture Review Finalizer[[:space:]]*$' "$selected_slice_path"; then
    if ! architecture_finalizer_contract="$(ralph_architecture_review_finalizer_contract \
        "$repo_root/.ralph/config.yaml" "$repo_root/.ralph/state.json" \
        "$repo_root/$selected_slice_path" "$repo_root/$approvals_file")"; then
      echo "Slice $slice_id declares an invalid, unapproved, or non-exhausted architecture-review finalizer; refusing to run it." >&2
      exit 2
    fi
    IFS=$'\t' read -r architecture_finalizer_epic architecture_finalizer_root \
      <<< "$architecture_finalizer_contract"
    echo "Owner-approved Epic $architecture_finalizer_epic finalizer for $architecture_finalizer_root: successful full gates will close the exhausted root without another immediate review."
  fi
  if grep -q '^## Architecture Review Recurrence Repair[[:space:]]*$' "$selected_slice_path"; then
    if ! architecture_terminal_repair_contract="$(ralph_architecture_review_terminal_repair_contract \
        "$repo_root/.ralph/config.yaml" "$repo_root/.ralph/state.json" \
        "$repo_root/$selected_slice_path")"; then
      echo "Slice $slice_id declares an invalid, exhausted, or untrusted terminal recurrence repair; refusing to run it." >&2
      exit 2
    fi
    IFS=$'\t' read -r architecture_terminal_repair_epic \
      architecture_terminal_repair_root architecture_terminal_repair_finalizer \
      <<< "$architecture_terminal_repair_contract"
    echo "Bounded Epic $architecture_terminal_repair_epic repair episode for $architecture_terminal_repair_finalizer and $architecture_terminal_repair_root: successful full gates retain an independent verification barrier."
  fi
fi

mkdir -p "$repo_root/.ralph/locks"
lock_file="$repo_root/.ralph/locks/$run_id.lock"
lock_worktree_hint=""
if (( no_worktree == 0 )); then
  if [[ -n "$resume_worktree" ]]; then
    lock_worktree_hint="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$resume_worktree")"
  else
    lock_worktree_hint="$repo_root/.ralph/worktrees/$run_id"
  fi
fi
printf '%s\n%s\n%s\n' "$run_id" "$$" "$lock_worktree_hint" > "$lock_file"
worktree_owner_recorded=0

on_exit() {
  local status=$?
  if ! ralph_release_run_lock "$repo_root" "$lock_file" "$lock_worktree_hint" \
      "$worktree_owner_recorded" "$no_worktree"; then
    echo "WARN: run-lock cleanup could not prove safe removal; preserving $lock_file for recovery." >&2
  fi
  if (( status != 0 )) && [[ "$run_dir" != "$main_run_dir" && -d "$run_dir" ]]; then
    mkdir -p "$main_run_dir"
    cp -R "$run_dir/." "$main_run_dir/" 2>/dev/null || true
    echo "Run failed (exit $status); artifacts copied to $main_run_dir for diagnosis." >&2
  fi
}
trap on_exit EXIT

worktree_dir="$repo_root"
if (( no_worktree == 0 )); then
  if [[ -n "$resume_worktree" ]]; then
    expected_worktree_root="$(cd "$repo_root/.ralph/worktrees" && pwd -P)"
    worktree_dir="$(cd "$resume_worktree" 2>/dev/null && pwd -P)" || {
      echo "Refusing repair: failed worktree does not exist: $resume_worktree" >&2
      exit 1
    }
    if [[ "$worktree_dir" != "$expected_worktree_root/"* ]] \
        || ! git -C "$repo_root" worktree list --porcelain | awk '$1 == "worktree" {print substr($0, 10)}' | grep -Fxq "$worktree_dir"; then
      echo "Refusing repair: resume path is not a registered Ralph worktree: $worktree_dir" >&2
      exit 1
    fi
    branch_name="$(git -C "$worktree_dir" symbolic-ref --short HEAD 2>/dev/null || true)"
    if [[ "$branch_name" != ralph/* ]]; then
      echo "Refusing repair: resume worktree is not on a Ralph branch: $branch_name" >&2
      exit 1
    fi
    repair_context="$repo_root/.ralph/repair-context.json"
    if ! ralph_repair_context_is_resumable "$repo_root" "$repair_context" \
        || [[ "$(ralph_repair_context_value "$repair_context" worktree)" != "$worktree_dir" ]] \
        || [[ "$(ralph_repair_context_value "$repair_context" run_id)" != "$failed_run_id" ]] \
        || [[ "$(ralph_repair_context_value "$repair_context" slice_id)" != "$slice_id" ]] \
        || [[ "$(ralph_repair_context_value "$repair_context" branch)" != "$branch_name" ]]; then
      echo "Refusing repair: resume arguments do not match the trusted repair context." >&2
      exit 1
    fi
    previous_failure_summary="$worktree_dir/.ralph/runs/$failed_run_id/failure-summary.md"
    if [[ ! -s "$previous_failure_summary" ]]; then
      echo "Refusing repair: previous failure summary is missing: $previous_failure_summary" >&2
      exit 1
    fi
    echo "Resuming quarantined worktree $worktree_dir from failed run $failed_run_id."
  else
    branch_name="ralph/${run_id}_${slice_id}"
    worktree_dir="$repo_root/.ralph/worktrees/$run_id"
    git worktree add -b "$branch_name" "$worktree_dir" HEAD
  fi
  stable_worktree_id="$(basename "$worktree_dir")"
  worktree_owner_slice_id="$slice_id"
  [[ -n "$split_slice_id" ]] && worktree_owner_slice_id="$split_slice_id"
  ralph_record_worktree_owner \
    "$repo_root" "$worktree_dir" "$branch_name" \
    "$stable_worktree_id" "$run_id" "$worktree_owner_slice_id" >/dev/null || exit 1
  worktree_owner_recorded=1
  ralph_restore_worktree_bookkeeping "$repo_root" "$worktree_dir" || exit 1
  ralph_restore_selected_slice_status \
    "$worktree_dir" "docs/slices/$slice_file" || exit 1
  run_dir="$worktree_dir/.ralph/runs/$run_id"
  mkdir -p "$run_dir"
  if [[ -d "$main_run_dir" ]]; then
    cp -R "$main_run_dir/." "$run_dir/"
    rm -rf "$main_run_dir"
  fi
fi

# Mechanical queue facts never belong to an implementation or repair agent.
# Worktree setup above restores trusted state/progress and the selected status
# before creating any candidate-local run path; substantive repair edits stay.

mkdir -p "$run_dir/evidence/screenshots" "$run_dir/evidence/videos" "$run_dir/evidence/api-responses" "$run_dir/evidence/terminal-logs"

backend_python="$(awk -F': *' '/^[[:space:]]*backend_python:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
backend_python="${backend_python:-python3}"
backend_dir_cfg="$(awk -F': *' '/^[[:space:]]*backend_dir:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | tr -d '"' | xargs || true)"
venv_dir="$repo_root/.ralph/venv"
environment_setup_timeout="$(awk -F': *' '/^[[:space:]]*environment_setup_timeout_seconds:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
run_environment_command() {
  local label="${1:?environment command label is required}"
  shift
  python3 "$repo_root/scripts/lib/ralph-run-with-timeout.py" \
    --timeout "${environment_setup_timeout:-900}" \
    --label "$label" \
    -- "$@"
}
run_postgresql_timeout_cleanup() {
  local python_bin="${1:?cleanup Python executable is required}"
  local database_name="${2:?cleanup database name is required}"
  python3 "$repo_root/scripts/lib/ralph-run-with-timeout.py" \
    --timeout 60 \
    --grace 5 \
    --label "PostgreSQL timeout cleanup for $database_name" \
    -- \
    /bin/bash -c \
      'source "$1"; postgresql_drop_test_database "$2" "$3" "$4"' \
      ralph-postgresql-cleanup \
      "$repo_root/scripts/lib/ralph-postgresql-acceptance.sh" \
      "$python_bin" \
      "$worktree_dir" \
      "$database_name"
}
# On Apple Silicon the x86_64 codex CLI spawns x86_64 children, so a plain
# venv python loads no arm64 native wheels (coverage C tracer, cffi) and the
# coverage gate silently degrades. Keep bin/python an arm64-forcing wrapper;
# a venv rebuild restores plain symlinks, so re-install it on every run.
ensure_backend_python_arch_wrapper() {
  [[ "$(uname -s)" == "Darwin" ]] || return 0
  [[ "$(sysctl -n hw.optional.arm64 2>/dev/null || true)" == "1" ]] || return 0
  [[ -x /usr/bin/arch ]] || return 0
  local py="$venv_dir/bin/python" real
  [[ -e "$py" ]] || return 0
  if [[ -f "$py" ]] && grep -q "arch -arm64" "$py" 2>/dev/null; then
    return 0
  fi
  real="$(cd "$venv_dir/bin" && ls python3.[0-9]* 2>/dev/null | sort | head -n 1 || true)"
  if [[ -z "$real" ]]; then
    echo "WARN: no versioned interpreter in $venv_dir/bin; cannot install the arm64 python wrapper." >&2
    return 0
  fi
  rm -f "$py"
  cat > "$py" <<WRAP
#!/bin/sh
# Orchestrator-maintained (ralph-run.sh): force the arm64 slice of the
# universal CPython so native arm64 wheels (coverage C tracer, cffi) load
# even when the caller runs under Rosetta (the x86_64 codex CLI spawns
# x86_64 children). Recreated automatically after any venv rebuild.
exec /usr/bin/arch -arm64 "\$(dirname "\$0")/$real" "\$@"
WRAP
  chmod +x "$py"
  echo "Installed the arm64-forcing python wrapper at $py (real interpreter: $real)."
}
ensure_backend_env() {
  local req="$worktree_dir/${backend_dir_cfg}/requirements-dev.txt"
  [[ -n "$backend_dir_cfg" && -f "$req" ]] || return 0
  if [[ ! -x "$venv_dir/bin/python" ]]; then
    if ! run_environment_command "backend virtual environment creation" \
        "$backend_python" -m venv "$venv_dir"; then
      echo "WARN: backend virtual environment creation failed or timed out; gates will surface it." >&2
      return 0
    fi
  fi
  ensure_backend_python_arch_wrapper
  if ! run_environment_command "backend dependency installation" \
      "$venv_dir/bin/python" -m pip install --quiet --disable-pip-version-check -r "$req" \
      >> "$run_dir/evidence/terminal-logs/orchestrator-backend-deps.log" 2>&1; then
    echo "WARN: backend dependency install failed or timed out; gates will surface any missing module." >&2
  fi
}
project_dir_cfg="$(awk -F': *' '/^[[:space:]]*project_dir:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | tr -d '"' | xargs || true)"
ralph_activate_pinned_node "$repo_root" "$project_dir_cfg" || exit 1
ensure_frontend_env() {
  local fe_dir="$worktree_dir/${project_dir_cfg}"
  [[ -n "$project_dir_cfg" && -f "$fe_dir/package-lock.json" ]] || return 0
  if [[ ! -d "$fe_dir/node_modules" ]]; then
    if ! (cd "$fe_dir" && run_environment_command "frontend dependency installation" \
        npm ci --prefer-offline --no-audit --no-fund) \
        >> "$run_dir/evidence/terminal-logs/orchestrator-frontend-deps.log" 2>&1; then
      echo "WARN: frontend dependency install failed or timed out; gates will surface it." >&2
    fi
  else
    if ! (cd "$fe_dir" && run_environment_command "frontend dependency synchronization" \
        npm install --prefer-offline --no-audit --no-fund) \
        >> "$run_dir/evidence/terminal-logs/orchestrator-frontend-deps.log" 2>&1; then
      echo "WARN: frontend dependency sync failed or timed out; gates will surface it." >&2
    fi
  fi
}
ensure_backend_env
ensure_frontend_env

# Browser availability is infrastructure owned by the orchestrator, not a
# product concern for the coding agent. Probe only slices that declare the
# localhost E2E capability, recover the Playwright browser once, and stop with
# a structured infrastructure outcome before implementation if launch remains
# unavailable.
if [[ "$mode" =~ ^(normal_run|repair)$ ]] \
    && ralph_slice_has_capability "$worktree_dir/docs/slices/$slice_file" \
      "$RALPH_CAPABILITY_LOCALHOST_E2E_SERVER"; then
  browser_probe_log="$run_dir/evidence/terminal-logs/browser-infrastructure-probe.log"
  if ! ralph_ensure_browser_runtime \
      "$worktree_dir/$project_dir_cfg" \
      "$browser_probe_log" \
      "$repo_root/scripts/lib/ralph-run-with-timeout.py" \
      300; then
    cat > "$run_dir/browser-infrastructure-results.md" <<EOF
# Browser Infrastructure Results

FAIL: the central Playwright launch probe still fails after one bounded Chromium recovery.
This is an orchestrator infrastructure stop; no coding agent or product repair was started.
See evidence/terminal-logs/browser-infrastructure-probe.log.
EOF
    cat > "$run_dir/final-summary.md" <<EOF
# Final Summary

Result: Browser Infrastructure Unavailable

Ralph stopped before implementation for $slice_id because neither the centrally selected browser
nor one bounded Playwright Chromium recovery could create a page. No product changes were made.
EOF
    if [[ -z "$resume_worktree" && "$no_worktree" == 0 ]]; then
      mkdir -p "$main_run_dir"
      cp -R "$run_dir/." "$main_run_dir/" 2>/dev/null || true
      git -C "$repo_root" worktree remove --force "$worktree_dir"
      ralph_remove_worktree_owner "$repo_root" "$worktree_dir"
      git -C "$repo_root" branch -D "$branch_name" >/dev/null 2>&1 || true
      run_dir="$main_run_dir"
    fi
    exit "$RALPH_EXIT_BROWSER_INFRASTRUCTURE"
  fi
fi

if [[ -n "$resume_worktree" ]]; then
  repair_instruction="- In same-worktree repair: diagnose $previous_failure_summary first and preserve the current candidate. Fix only the demonstrated validation domain; within that domain, rerun the exact named validator until it passes and correct every error it reports or subsequently reveals. In architecture-review mode, retain documentation-only scope and do not repeat the product critique from scratch. Newly exposed errors from the same validator are part of the same bounded repair, not permission to change unrelated product scope. Rely on full independent revalidation before any commit."
else
  repair_instruction="- In repair mode: first diagnose the most recent failure — read failure-summary.md in the newest failed .ralph/runs/*/ folder (failed checks, last log lines, changed files); open the full gate logs only if that summary is insufficient, and inspect any leftover .ralph/worktrees/ from the failed attempt before starting fresh."
fi

closure_preflight_instruction=""
if [[ "$mode" != "architecture_review" \
    && -f "$worktree_dir/docs/slices/$slice_file" ]] \
    && grep -q '^## Review Finding Closure[[:space:]]*$' \
      "$worktree_dir/docs/slices/$slice_file"; then
  closure_preflight_instruction="- This corrective slice has a machine-readable closure contract. Before returning, run exactly: ./scripts/ralph-validate-review-closure.sh --slice docs/slices/$slice_file --run-dir .ralph/runs/$run_id . Keep rerunning that fast check until it prints PASS. Markdown prose may follow a table only after a blank line; Python tests may use an exact path::selector or exact Django dotted test label. If this slice declares Architecture Review Finalizer or Architecture Review Recurrence Repair, rerun every original review log's exact one-line Command and add '## Reproducer Replay Evidence' with the exact columns 'Finding ID | Command | Evidence'; each current-run evidence log must contain that exact command, a positive pass signal, and Exit code: 0. Do not replace the original probe with a narrower proxy test. Do not defer a failure from this command to the orchestrator."
fi

split_instruction=""
split_corrective_instruction=""
split_read_target="docs/slices/$slice_file"
architecture_instruction="- In architecture-review mode: do NOT modify production code. Review the diffs of slices merged since the last review as an independent critic: test quality (real assertions, edge cases), doc fidelity against source references, duplication, architecture drift. Append findings to docs/working/REVIEW_FINDINGS.md. Only Critical/High correctness, security, financial/data-integrity, or binding source-contract findings create immediate corrective work. Bundle Medium findings into the owning slice or epic closure and record Low findings unless they naturally combine with higher-severity work. Group related symptoms by root owner instead of creating one slice per symptom. Report findings closed, new findings by severity, and corrective slices added in review-packet.md under '## Convergence Metrics' using the exact lines '- Findings closed: N', '- New Critical: N', '- New High: N', '- New Medium: N', '- New Low: N', and '- Corrective slices added: N'. A normal new corrective must be a numeric Not Started slice with a valid Depends On contract. Exception: when the scope instruction says a carried root is already at the configured generation cap and it genuinely needs a different successor, create exactly one next-numbered CR-NNN terminal finalizer instead of another numeric leaf. Its filename may add a descriptive slug, but every Finding Closure Manifest row must use the CR-NNN identity. It must be Not Started, High risk, owned by the same Parent Epic, group every related Critical/High root into its Review Finding Closure contract, and contain exactly '## Architecture Review Finalizer' followed by '- Epic: NNN', '- Root ID: ROOT-NNN-*', and '- Exhausted corrective generation: N'. The standing owner policy admits only one such terminal CR per root. If executable evidence later disproves that finalizer, preserve the same stable roots and group them into one correction; the orchestrator may rewrite it as one bounded same-finalizer repair episode, never generation 3 or a second finalizer. Product gates leave that episode open until a later independent review explicitly closes every grouped root. A genuine later regression opens the next bounded episode on the same stable roots instead of silently restarting generations or globally stopping unrelated work. When an actionable existing root-owner slice already covers a new Critical/High finding, do not duplicate it; add one exact '- Existing corrective slice: ID' line per mapped slice under the convergence metrics. Validation requires every mapped ID to resolve to one tracked Not Started or Blocked slice. If corrective additions exceed closures across two reviews, recommend one root-cause boundary correction instead of further leaf patches."
architecture_runtime_instruction='- Every generated corrective slice must declare exactly one `## Runtime Capabilities` section. Declare `postgresql-five-race-acceptance` when its text or Trusted PostgreSQL Acceptance requires PostgreSQL, concurrency, locking, or race evidence; declare `localhost-e2e-server` when it requires browser, screenshot, Playwright, or trusted-browser evidence; otherwise declare `none`. Before returning, source `scripts/lib/ralph-runtime-capabilities.sh` and `scripts/lib/ralph-postgresql-acceptance.sh`, run `ralph_validate_slice_runtime_requirements` against every untracked `docs/slices/*.md` candidate, and run `ralph_validate_trusted_postgresql_acceptance` for every candidate declaring the PostgreSQL capability. A failure is part of this review candidate and must be corrected here, not deferred to the next product run.'
architecture_instruction="$architecture_instruction $architecture_runtime_instruction"
architecture_scope_instruction="$(ralph_architecture_review_scope_instruction \
  "$repo_root/.ralph/state.json")"
if [[ -n "$architecture_scope_instruction" ]]; then
  architecture_instruction="$architecture_instruction $architecture_scope_instruction"
fi
if [[ "$terminal_finalizer_rewrite" == "1" ]]; then
  architecture_instruction="$architecture_instruction This is the single bounded terminal-finalizer rewrite after independent convergence validation rejected an ordinary successor. Do not repeat the architecture critique or change its findings. Read the previous failure-summary.md, rename the one proposed numeric corrective to the next unused CR-NNN terminal finalizer, replace its old ID consistently in the manifest/findings/dependencies, add the exact finalizer section for the exhausted root, retain every acceptance/reproducer contract, and run the fast queue/semantic validators before returning."
fi
if [[ "$terminal_recurrence_rewrite" == "1" ]]; then
  architecture_instruction="$architecture_instruction This is a bounded terminal-recurrence rewrite after independent validation proved that a terminal finalizer remains incomplete or later regressed. Do not repeat the architecture critique or change any finding, reproducer, acceptance criterion, or unrelated corrective slice. Preserve the one grouped recurrence corrective, include every Root ID inherited from that finalizer, add exactly '## Architecture Review Recurrence Repair' followed by '- Epic: NNN', '- Root ID: ROOT-NNN-*', '- Terminal finalizer: <exact completed slice id>', and '- Repair attempt: 1', and revise prose that previously described the candidate as permanently rejected. This continues or opens an auditable repair episode for the same terminal contract; it is not generation 3 or a second finalizer. Run the fast queue/semantic validators before returning."
fi
if [[ -n "$split_slice_id" ]]; then
  split_read_target="$split_slice_file"
  printf -v split_origin_marker 'Oversized slice: `%s`' "$split_slice_id"
  split_instruction="- This is an oversized-slice queue rewrite, not a general architecture review. Do not modify production code or review unrelated slices. Read $split_slice_file and the retained evidence for failed run $split_failed_run_id. The failed candidate measured $split_total_lines lines against a $split_max_lines-line limit. Mark $split_slice_id Superseded and create at least two dependency-ordered Not Started successor slices named ${split_slice_id}A, ${split_slice_id}B, and so on. Each successor must contain an Origin section with the exact marker $split_origin_marker. The first successor inherits every original prerequisite; each later successor depends on the previous one; every existing downstream dependency on $split_slice_id must point to the terminal successor. Preserve every original requirement, test, evidence, and risk across the successors. Each successor must be independently implementable and independently green, with a predicted diff comfortably below the configured limit. Update queue handoff or digest documents only when needed. Do not sharpen or change unrelated slices."
  if [[ -n "$split_corrective_run_id" ]]; then
    split_corrective_instruction="- This is the one bounded corrective queue-rewrite attempt after run $split_corrective_run_id failed independent validation. Before editing, read $split_corrective_run_dir/failure-summary.md and $split_corrective_run_dir/oversized-slice-split-results.md. Start from this clean worktree; do not salvage the rejected planning diff. Correct every exact validator finding, change only permitted queue/bookkeeping paths, and run local scope/semantics checks before handing back."
  fi
  architecture_instruction="- In this queue-rewrite architecture mode, perform only the oversized-slice split described above."
fi

cat > "$run_dir/prompt.md" <<EOF
You are running Ralph AFK mode.

Run ID:
$run_id

Mode:
$mode

Selected slice:
$slice_id

Working directory:
$worktree_dir

You must follow the Ralph workflow exactly.

Core requirements:
- Do not rely on chat history.
- Work only inside the active worktree.
- Implement only the selected vertical slice.
- Read only the required context files first.
- Do not modify docs/source.
- Never modify protected files: scripts/, .ralph/config.yaml, .ralph/permissions.json, .codex/config.toml, AGENTS.md, CLAUDE.md, .gitignore, docs/working/HIGH_RISK_APPROVALS.md, docs/working/DECISION_POLICY.md. Validation fails the run if you do.
- Write execution-plan.md before coding.
- Check permissions before editing files.
- TDD is mandatory for backend and business logic: write the failing test first, then implement, and save red/green output to evidence/terminal-logs/.
- Backend Python interpreter: use "$venv_dir/bin/python" for every backend command (manage.py, tests, coverage). Never use bare python3 — it resolves to the wrong interpreter.
- Frontend node_modules are pre-installed in the worktree by the orchestrator. Do not run npm install unless you add a new pinned package; if that install fails offline, note it in final-summary.md and finish — the orchestrator installs from the lockfile before validation.
- Your sandbox has no network access: never run pip install. If a dependency you just pinned in requirements is not importable yet, still write the code, tests, and pin; note the missing module in final-summary.md and finish — the orchestrator installs pinned requirements before independent validation. That situation is expected, not a failure.
- Frontend changes must follow docs/working/FRONTEND_DESIGN_RULES.md exactly: reuse existing components and patterns; never introduce new styling, colours, typography, layouts, or components. If the documents require a screen the prototype lacks, building it from existing patterns and wiring it to the backend is part of the slice.
- During implementation, run focused red/green tests for the changed backend/business behavior and the impacted frontend tests, typecheck, lint, and build as appropriate.
- Batch related searches, reads, edits, and focused tests. Aim to stay below roughly 80 tool calls; after that, return to execution-plan.md and finish through focused work instead of rediscovering context.
- After roughly 500 changed lines, use diff stats and targeted hunks; never repeatedly print the complete cumulative diff.
- Do not run the complete backend suite or full coverage yourself. The orchestrator runs the authoritative complete backend suite once under coverage after you finish, and rejects any test failure or coverage below the configured floor. This avoids paying for identical full-suite executions without removing any acceptance gate.
- For a slice declaring 'localhost-e2e-server', implement the exact specs and screenshot outputs in its '## Trusted Browser Acceptance' section. Your coding sandbox may deny Chromium's macOS services: use Playwright collection or non-browser tests for your local feedback, do not fabricate screenshots, and do not declare the run failed solely because Chromium cannot launch. The orchestrator runs the declared browser contract twice outside your sandbox after you finish; that independent gate decides browser acceptance.
- Save evidence.
- Save risk-assessment.md.
- Save review-packet.md.
- Before finishing successfully, set the review-packet.md Result section to exactly 'Ready for independent validation'. Missing, partial, or any other result fails closed.
- The orchestrator owns changed-files.txt, .ralph/state.json, .ralph/progress.md, the selected slice Status transition, and mechanical handoff/progress bookkeeping. Do not edit those mechanical facts. Put substantive next-run risks or decisions in review-packet.md; edit HANDOFF only when it needs non-mechanical context the orchestrator cannot derive.
- Never run git commit, git add, or git push: your sandbox cannot write the worktree's git metadata and the attempt will fail your run. The orchestrator independently validates and commits passing work after you finish.
- High-risk slices proceed under the owner's standing approval (docs/working/HIGH_RISK_APPROVALS.md); record risk honestly in risk-assessment.md. Never implement a slice marked [revoked] there.
- When requirements are ambiguous, follow docs/working/DECISION_POLICY.md: choose the source-doc-compliant option, or the industry-standard default, record it in docs/working/ASSUMPTIONS.md, and continue. Do not stop to ask. Never invent business rules the documents do not state — stub them, record the open question, and continue.
- If the selected slice file is still an unsharpened template stub (its Goal reads "Deliver this narrow capability as a small, testable Ralph implementation slice" or its scope sections say only "Implement the named backend/API capability only"), your FIRST deliverable is sharpening that slice file with concrete requirements from the epic digest, docs/working/maps/, and the slice's cited source sections — before writing execution-plan.md. Never implement directly from an unsharpened stub.
- Do not sharpen or edit unrelated future slices during an implementation run. Owner/architecture preparation maintains a bounded ready runway outside the product session.
- Prefer docs/working/digests/ over re-reading large docs/source files. Read only the digest shared invariants and the selected slice section by default. If the selected section lacks a required source fact, locate that fact with docs/working/maps/ and rg, then save only the missing distilled fact.
- Stop only for the never-do list in DECISION_POLICY.md, forbidden/protected file edits, repeated gate failure, or diff limit violations.
$repair_instruction
$closure_preflight_instruction
$split_instruction
$split_corrective_instruction
$architecture_instruction
- In an ordinary architecture review, read the bounded active docs/working/REVIEW_FINDINGS.md first. Open its historical archive only when a current diff reproduces an archived issue or an exact prior citation is required; never ingest the entire archive by default.
- If you are Claude Code, use skills at the stages defined in docs/working/SKILL_REGISTRY.md (tdd during implementation, diagnosing-bugs in repair, code-review with the slice file as spec during architecture review). If a skill is unavailable, follow the baked-in rules; never stall on a missing skill.
- If the selected slice is a change request (CR-*): write impact-analysis.md in the run folder BEFORE editing any code — affected backend/frontend pieces, blast radius across modules, and the regression tests to add in each affected module. Validation fails the run without it. Then add those regression tests as part of the fix.

Read in this order:
1. AGENTS.md or CLAUDE.md
2. docs/working/TOKEN_RULES.md
3. docs/working/CONTEXT.md
4. docs/working/AFK_RUNBOOK.md
5. .ralph/config.yaml
6. .ralph/permissions.json
7. .ralph/state.json
8. docs/working/HANDOFF.md
9. docs/working/DECISION_POLICY.md
10. docs/working/FRONTEND_DESIGN_RULES.md (mandatory before any frontend change)
11. $split_read_target
12. The matching docs/working/digests/ shared invariants and selected-slice section, if it exists

Do not load all docs/source during a normal run unless the selected slice explicitly requires it.
EOF

cat > "$run_dir/execution-plan.md" <<EOF
# Execution Plan

Selected slice: $slice_id

The selected agent must replace this template with a slice-specific execution plan before editing product code.
EOF

cat > "$run_dir/risk-assessment.md" <<EOF
# Risk Assessment

Risk level: To be completed by the selected agent.

- Selected slice: $slice_id
- Mode: $mode
- Manual review required: yes until agent completes this file.
EOF

cat > "$run_dir/review-packet.md" <<EOF
# Review Packet: $run_id

## Result
In Progress

## Slice
$slice_id

## Recommended Next Action
Wait for the selected agent and validation to complete.
EOF

cat > "$run_dir/final-summary.md" <<EOF
# Final Summary

Result: In Progress

Ralph run started for $slice_id.
EOF

agent_timeout="$(awk -F': *' '/^[[:space:]]*agent_timeout_seconds:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
validation_timeout="$(awk -F': *' '/^[[:space:]]*validation_timeout_seconds:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"

# The orchestrator is the single owner of the review-cadence counter. Capture
# the pre-run value now, from the integration checkout the agent never touches:
# agents also edit state.json inside the worktree, and trusting their copy
# double-counted completed slices (reviews fired at 2x the configured cadence).
pre_run_arch_count="$(python3 -c "import json; print(json.load(open('$repo_root/.ralph/state.json')).get('slices_completed_since_architecture_review', 0))" 2>/dev/null || echo 0)"
pre_run_arch_clean_streak="$(python3 -c "import json; print(json.load(open('$repo_root/.ralph/state.json')).get('architecture_review_clean_streak', 0))" 2>/dev/null || echo 0)"
pre_run_arch_due="$(ralph_architecture_review_due "$repo_root/.ralph/state.json")" || exit 1
if ! [[ "$pre_run_arch_count" =~ ^[0-9]+$ \
    && "$pre_run_arch_clean_streak" =~ ^[0-9]+$ ]]; then
  echo "Trusted architecture-review counters are invalid." >&2
  exit 1
fi

agent_rc=0
"$repo_root/scripts/agent-adapters/$agent.sh" \
  RUN_ID="$run_id" \
  RUN_DIR="$run_dir" \
  WORKTREE_DIR="$worktree_dir" \
  PROMPT_FILE="$run_dir/prompt.md" \
  SELECTED_SLICE="$slice_id" \
  MODE="$mode" \
  AGENT_TIMEOUT_SECONDS="${agent_timeout:-7200}" || agent_rc=$?
if (( agent_rc != 0 )); then
  if (( agent_rc == RALPH_EXIT_AGENT_LIMIT )); then
    echo "Agent usage limit exhausted; returning the structured limit outcome to the outer loop." >&2
    exit "$RALPH_EXIT_AGENT_LIMIT"
  fi
  echo "WARN: agent adapter exited $agent_rc; proceeding to independent validation — the gates decide pass or fail." >&2
fi

(cd "$worktree_dir" && git status --short > "$run_dir/changed-files.txt")

ensure_backend_env
ensure_frontend_env

validation_rc=0
python3 "$repo_root/scripts/lib/ralph-run-with-timeout.py" \
  --timeout "${validation_timeout:-3600}" \
  --label "Ralph independent validation for $slice_id" \
  -- \
  "$repo_root/scripts/ralph-validate.sh" \
  --run-id "$run_id" \
  --worktree "$worktree_dir" \
  --mode "$mode" \
  --slice "$slice_id" || validation_rc=$?

if (( validation_rc != 0 )); then
  if (( validation_rc == 124 )); then
    cleanup_python="$venv_dir/bin/python"
    [[ -x "$cleanup_python" ]] || cleanup_python="$backend_python"
    cleanup_log="$run_dir/evidence/terminal-logs/postgresql-timeout-cleanup.log"
    for ordinal in 1 2; do
      postgres_test_db="$(postgresql_test_database_name "$run_id" "$ordinal")"
      run_postgresql_timeout_cleanup "$cleanup_python" "$postgres_test_db" \
        >> "$cleanup_log" 2>&1 || true
    done
    cat > "$run_dir/validation-timeout-results.md" <<EOF
# Validation Timeout Results

FAIL: independent validation exceeded ${validation_timeout:-3600} seconds.
The watchdog terminated the validator and its child process group so the outer
loop can enter the bounded repair path instead of waiting indefinitely.
EOF
    cat > "$run_dir/failure-summary.md" <<EOF
# Validation Failure Summary

## validation-timeout-results.md

Independent validation for $slice_id exceeded ${validation_timeout:-3600} seconds.
Inspect the most recently updated gate result and terminal log for the blocked command.
EOF
  elif [[ ! -s "$run_dir/failure-summary.md" ]]; then
    cat > "$run_dir/failure-summary.md" <<EOF
# Validation Failure Summary

The independent validation runner exited with status $validation_rc before it
could write a detailed failure summary. Inspect the run's gate result files.
EOF
  fi
  if (( no_worktree == 0 )); then
    repair_slice_id="$slice_id"
    [[ -n "$split_slice_id" ]] && repair_slice_id="$split_slice_id"
    ralph_write_repair_context \
      "$repo_root/.ralph/repair-context.json" \
      "$run_id" "$worktree_dir" "$repair_slice_id" "$branch_name" \
      "$run_dir/failure-summary.md"
  fi
  exit "$validation_rc"
fi

if [[ -n "$architecture_finalizer_epic" ]]; then
  finalizer_results="$run_dir/architecture-review-finalizer-results.md"
  candidate_finalizer_contract="$(ralph_architecture_review_finalizer_contract \
    "$worktree_dir/.ralph/config.yaml" "$worktree_dir/.ralph/state.json" \
    "$worktree_dir/docs/slices/$slice_file" \
    "$worktree_dir/docs/working/HIGH_RISK_APPROVALS.md" 2>/dev/null || true)"
  if [[ "$candidate_finalizer_contract" != \
      "$architecture_finalizer_epic"$'\t'"$architecture_finalizer_root" ]]; then
    cat > "$finalizer_results" <<EOF
# Architecture Review Finalizer Results

FAIL: the independently validated candidate did not preserve the exact protected
Epic $architecture_finalizer_epic finalizer contract.
EOF
    cat > "$run_dir/failure-summary.md" <<EOF
# Validation Failure Summary

architecture-review-finalizer-results.md:- FAIL: the candidate changed or invalidated the owner-approved finalizer contract.
EOF
    if (( no_worktree == 0 )); then
      ralph_write_repair_context \
        "$repo_root/.ralph/repair-context.json" \
        "$run_id" "$worktree_dir" "$slice_id" "$branch_name" \
        "$run_dir/failure-summary.md"
    fi
    exit 1
  fi
  cat > "$finalizer_results" <<EOF
# Architecture Review Finalizer Results

PASS: protected owner approval, Epic $architecture_finalizer_epic ownership,
exhausted root $architecture_finalizer_root, and candidate declaration remain exact.
Successful full product gates authorize this run to close the exhausted boundary.
EOF
fi

if [[ -n "$architecture_terminal_repair_epic" ]]; then
  terminal_repair_results="$run_dir/architecture-review-terminal-repair-results.md"
  candidate_terminal_repair_contract="$(ralph_architecture_review_terminal_repair_contract \
    "$worktree_dir/.ralph/config.yaml" "$worktree_dir/.ralph/state.json" \
    "$worktree_dir/docs/slices/$slice_file" 2>/dev/null || true)"
  expected_terminal_repair_contract="$architecture_terminal_repair_epic"$'\t'"$architecture_terminal_repair_root"$'\t'"$architecture_terminal_repair_finalizer"
  if [[ "$candidate_terminal_repair_contract" != "$expected_terminal_repair_contract" ]]; then
    cat > "$terminal_repair_results" <<EOF
# Architecture Review Terminal Repair Results

FAIL: the independently validated candidate did not preserve the exact bounded
repair of $architecture_terminal_repair_finalizer for $architecture_terminal_repair_root.
EOF
    cat > "$run_dir/failure-summary.md" <<EOF
# Validation Failure Summary

architecture-review-terminal-repair-results.md:- FAIL: the candidate changed or invalidated the trusted recurrence-repair contract.
EOF
    if (( no_worktree == 0 )); then
      ralph_write_repair_context \
        "$repo_root/.ralph/repair-context.json" \
        "$run_id" "$worktree_dir" "$slice_id" "$branch_name" \
        "$run_dir/failure-summary.md"
    fi
    exit 1
  fi
  cat > "$terminal_repair_results" <<EOF
# Architecture Review Terminal Repair Results

PASS: retained one bounded repair episode for $architecture_terminal_repair_finalizer
and $architecture_terminal_repair_root. Successful full gates await independent review.
EOF
fi

cat > "$run_dir/final-summary.md" <<EOF
# Final Summary

Result: Success

Ralph run completed for $slice_id.
EOF

arch_threshold="$(ralph_architecture_review_interval \
  "$worktree_dir/.ralph/config.yaml" "$repo_root/.ralph/state.json")" || exit 1
arch_base_threshold="$(awk -F': *' '/^[[:space:]]*architecture_review_every_completed_slices:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$worktree_dir/.ralph/config.yaml" | xargs || true)"
arch_clean_threshold="$(awk -F': *' '/^[[:space:]]*architecture_review_clean_every_completed_slices:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$worktree_dir/.ralph/config.yaml" | xargs || true)"
arch_clean_required="$(awk -F': *' '/^[[:space:]]*architecture_review_clean_streak_required:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$worktree_dir/.ralph/config.yaml" | xargs || true)"
arch_base_threshold="${arch_base_threshold:-4}"
arch_clean_threshold="${arch_clean_threshold:-$arch_base_threshold}"
arch_clean_required="${arch_clean_required:-2}"
review_findings_closed=0
review_new_critical=0
review_new_high=0
review_new_medium=0
review_new_low=0
review_corrective_added=0
if [[ "$mode" == "architecture_review" && -z "$split_slice_id" ]]; then
  review_metrics="$(ralph_architecture_review_metrics "$run_dir/review-packet.md")" || exit 1
  IFS=$'\t' read -r review_findings_closed review_new_critical review_new_high \
    review_new_medium review_new_low review_corrective_added <<< "$review_metrics"
fi
arch_due_after_product=False
if [[ "$mode" != "architecture_review" ]]; then
  arch_due_after_product="$(ralph_architecture_review_due_after_product \
    "$pre_run_arch_due" "$((pre_run_arch_count + 1))" "$arch_threshold")" || exit 1
fi

python3 - <<PY
import json
from pathlib import Path
path = Path("$worktree_dir/.ralph/state.json")
trusted_path = Path("$repo_root/.ralph/state.json")
state = json.loads(trusted_path.read_text())
state["last_run_id"] = "$run_id"
state["last_run_status"] = "success"
state["current_slice"] = None
state["active_worktree"] = None
state["retry_count"] = 0
slice_id = "$slice_id"
if "$mode" != "architecture_review" and slice_id not in state["completed_slices"]:
    state["completed_slices"].append(slice_id)
state["failed_slices"] = [item for item in state["failed_slices"] if item != slice_id]
state["blocked_slices"] = [item for item in state["blocked_slices"] if item != slice_id]
if "$mode" != "architecture_review":
    # Recompute from the orchestrator's pre-run snapshot instead of the
    # worktree value: agents may have incremented state.json themselves,
    # which double-counted slices and fired reviews at 2x the cadence.
    count = int("$pre_run_arch_count") + 1
    threshold = int("$arch_threshold")
    state["slices_completed_since_architecture_review"] = count
    prior_due = state.get("architecture_review_due") is True
    prior_reason = state.get("architecture_review_due_reason")
    cadence_due = count >= threshold
    state["architecture_review_due"] = "$arch_due_after_product" == "True"
    state["architecture_review_interval"] = threshold
    if prior_due:
        state["architecture_review_due_reason"] = prior_reason or "carried_mandatory_review"
    elif cadence_due:
        state["architecture_review_due_reason"] = f"cadence:{threshold}"
    else:
        state.pop("architecture_review_due_reason", None)
elif not "$split_slice_id":
    metrics = {
        "findings_closed": int("$review_findings_closed"),
        "new_critical": int("$review_new_critical"),
        "new_high": int("$review_new_high"),
        "new_medium": int("$review_new_medium"),
        "new_low": int("$review_new_low"),
        "corrective_slices_added": int("$review_corrective_added"),
    }
    clean_streak = int("$pre_run_arch_clean_streak")
    if metrics["new_critical"] == 0 and metrics["new_high"] == 0:
        clean_streak += 1
    else:
        clean_streak = 0
    state["architecture_review_clean_streak"] = clean_streak
    state["architecture_review_interval"] = (
        int("$arch_clean_threshold")
        if clean_streak >= int("$arch_clean_required")
        else int("$arch_base_threshold")
    )
    state["last_architecture_review_metrics"] = metrics
    state["slices_completed_since_architecture_review"] = 0
    state["architecture_review_due"] = False
    state.pop("architecture_review_due_reason", None)
path.write_text(json.dumps(state, indent=2) + "\n")

slice_path = Path("$worktree_dir/docs/slices") / f"{slice_id}.md"
if slice_path.exists():
    lines = slice_path.read_text().splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## Status" and index + 1 < len(lines):
            lines[index + 1] = "Complete"
            break
    slice_path.write_text("\n".join(lines) + "\n")

blocked = []
for candidate in sorted(Path("$worktree_dir/docs/slices").glob("*.md")):
    if candidate.name == "architecture-review.md":
        continue
    lines = candidate.read_text().splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## Status" and index + 1 < len(lines):
            if lines[index + 1].strip() == "Blocked":
                blocked.append(candidate.stem)
            break
state["blocked_slices"] = blocked
path.write_text(json.dumps(state, indent=2) + "\n")
PY

if [[ "$mode" == "architecture_review" && -z "$split_slice_id" ]]; then
  ralph_apply_architecture_review_root_transitions \
    "$worktree_dir/.ralph/config.yaml" "$worktree_dir/.ralph/state.json" \
    "$run_dir/review-packet.md" "$worktree_dir/docs/slices" \
    "$worktree_dir/docs/working/HIGH_RISK_APPROVALS.md" || exit 1
  ralph_reconcile_architecture_review_terminal_repair_verification \
    "$worktree_dir/.ralph/state.json" "$run_dir/review-packet.md" || exit 1
  ralph_mark_architecture_review_terminal_finalizer_due \
    "$worktree_dir/.ralph/config.yaml" "$worktree_dir/.ralph/state.json" \
    "$worktree_dir/docs/slices" \
    "$worktree_dir/docs/working/HIGH_RISK_APPROVALS.md" || exit 1
  ralph_mark_architecture_review_terminal_repair_due \
    "$worktree_dir/.ralph/config.yaml" "$worktree_dir/.ralph/state.json" \
    "$worktree_dir/docs/slices" || exit 1
fi

if [[ "$mode" != "architecture_review" && -n "$architecture_finalizer_epic" ]]; then
  ralph_finalize_architecture_review_cycle \
    "$worktree_dir/.ralph/state.json" "$architecture_finalizer_epic" \
    "$architecture_finalizer_root" "$slice_id" "$run_id" || exit 1
fi

if [[ "$mode" != "architecture_review" && -n "$architecture_terminal_repair_epic" ]]; then
  ralph_finalize_architecture_review_terminal_repair \
    "$worktree_dir/.ralph/state.json" "$architecture_terminal_repair_epic" \
    "$architecture_terminal_repair_root" "$architecture_terminal_repair_finalizer" \
    "$slice_id" "$run_id" || exit 1
fi

# An epic boundary is always a review checkpoint, even after the cadence has
# safely expanded. Determine the next grabbable product slice only after the
# orchestrator has completed the selected slice's status transition.
if [[ "$mode" != "architecture_review" && -z "$architecture_finalizer_epic" \
    && -z "$architecture_terminal_repair_epic" ]]; then
  next_slice_file="$(ralph_first_grabbable_slice "$worktree_dir/docs/slices" 2>/dev/null || true)"
  next_slice_id="${next_slice_file%.md}"
  remaining_after="$(ralph_remaining_slices "$worktree_dir/docs/slices")"
  boundary_reason="$(ralph_architecture_review_boundary_reason \
    "$slice_id" "$next_slice_id" "$remaining_after" "$worktree_dir/docs/slices")"
  if [[ -n "$boundary_reason" ]]; then
    python3 - "$worktree_dir/.ralph/state.json" "$boundary_reason" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
state = json.loads(path.read_text())
state["architecture_review_due"] = True
prior = state.get("architecture_review_due_reason")
boundary = sys.argv[2]
state["architecture_review_due_reason"] = (
    f"{prior}+{boundary}" if prior and prior != boundary else boundary
)
path.write_text(json.dumps(state, indent=2) + "\n")
PY
  fi
fi

# Keep the agent's handoff when it wrote one this run — it carries context the
# next run needs. The generic template below is only a fallback so the file
# never goes silently stale, and it must reference the post-merge run path
# (.ralph/runs/<id>), never the worktree path, which is deleted after merge.
if ! git -C "$worktree_dir" status --porcelain -- docs/working/HANDOFF.md | grep -q .; then
  cat > "$worktree_dir/docs/working/HANDOFF.md" <<EOF
# Ralph Handoff

## Last Run
$run_id

## Current Status
Run completed for $slice_id.

## Current Slice
None selected.

## What Completed
See .ralph/runs/$run_id/ in the repository.

## Current Blocker
None known.

## Next Recommended Action
Review .ralph/runs/$run_id/review-packet.md.
EOF
fi

cat >> "$worktree_dir/.ralph/progress.md" <<EOF

## $(date '+%Y-%m-%d %H:%M:%S') - $run_id
- Agent tool used: $agent
- Slice attempted: $slice_id
- Summary: Ralph run completed.
- Tests run: See $run_dir/.
- Evidence saved: $run_dir/
- Result: Success
- Risk level: See risk assessment.
- Next action: Review packet.
EOF

committed=0
if (( no_commit == 0 )); then
  if (
    cd "$worktree_dir"
    git add .
    if git diff --cached --quiet; then
      echo "No changes to commit for $slice_id."
      exit 10
    fi
    expected_candidate_hash="$(cat "$run_dir/validated-commit-candidate.sha256" 2>/dev/null || true)"
    actual_candidate_hash="$(python3 "$repo_root/scripts/lib/ralph-candidate-hash.py" \
      "$worktree_dir" \
      --exclude "docs/slices/${slice_id}.md" \
      --exclude "docs/working/HANDOFF.md")"
    {
      echo
      echo "Before commit: $actual_candidate_hash"
    } >> "$run_dir/candidate-hash-results.md"
    if [[ -z "$expected_candidate_hash" || "$actual_candidate_hash" != "$expected_candidate_hash" ]]; then
      echo "Candidate changed after validation; refusing to commit." >&2
      exit 11
    fi

    git commit -m "chore(${slice_id}): complete Ralph AFK run"

    committed_candidate_hash="$(python3 "$repo_root/scripts/lib/ralph-candidate-hash.py" \
      "$worktree_dir" \
      --target HEAD \
      --exclude "docs/slices/${slice_id}.md" \
      --exclude "docs/working/HANDOFF.md")"
    {
      echo "Committed candidate: $committed_candidate_hash"
      if [[ "$committed_candidate_hash" == "$expected_candidate_hash" ]]; then
        echo "PASS: committed product candidate exactly matches the validated candidate."
      else
        echo "FAIL: committed product candidate differs from the validated candidate."
      fi
    } >> "$run_dir/candidate-hash-results.md"
    if [[ "$committed_candidate_hash" != "$expected_candidate_hash" ]]; then
      echo "Commit hook changed the validated candidate; refusing to merge." >&2
      exit 12
    fi
    if [[ -n "$(git status --porcelain -- . \
        ':(exclude).ralph' \
        ":(exclude)docs/slices/${slice_id}.md" \
        ':(exclude)docs/working/HANDOFF.md')" ]]; then
      echo "Commit left unvalidated product changes behind; refusing to merge." >&2
      exit 13
    fi
  ); then
    committed=1
  else
    commit_rc=$?
    cat > "$run_dir/commit-results.md" <<EOF
# Commit Results

FAIL: validated work could not be committed (exit $commit_rc).
The work remains isolated in $worktree_dir and must not be merged or pushed.
EOF
    cat > "$run_dir/failure-summary.md" <<EOF
# Commit Failure Summary

commit-results.md:- FAIL: validated work could not be committed.
Inspect the staged diff and commit hooks in $worktree_dir.
EOF
    if (( no_worktree == 0 )) \
        && ralph_quarantined_commit_exists "$repo_root" "$branch_name"; then
      # The validated candidate is already in a quarantined commit (for
      # example exit 12/13). Re-entering product repair would treat that commit
      # as a new baseline and conflict with orchestrator-owned state/status.
      # Preserve the branch and stop at the integration boundary instead.
      ralph_clear_repair_context "$repo_root/.ralph/repair-context.json"
      echo "COMMIT_QUARANTINED: post-commit integrity failure; branch $branch_name is preserved for owner review." >&2
      exit "$RALPH_EXIT_MERGE_FAILED"
    fi
    if [[ "$mode" != "architecture_review" && "$no_worktree" == 0 ]]; then
      ralph_write_repair_context \
        "$repo_root/.ralph/repair-context.json" \
        "$run_id" "$worktree_dir" "$slice_id" "$branch_name" \
        "$run_dir/failure-summary.md"
    fi
    echo "COMMIT_FAILED: validated work for $slice_id remains quarantined in $worktree_dir." >&2
    exit "$commit_rc"
  fi
fi

merged=0
if (( committed == 1 )) && (( no_worktree == 0 )); then
  auto_merge="$(awk -F': *' '/^[[:space:]]*auto_merge:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
  if [[ "$auto_merge" == "true" ]]; then
    if ralph_prepare_worktree_for_ff_merge "$repo_root" "$branch_name" \
        && git -C "$repo_root" merge --ff-only "$branch_name"; then
      git -C "$repo_root" worktree remove --force "$worktree_dir"
      ralph_remove_worktree_owner "$repo_root" "$worktree_dir"
      git -C "$repo_root" branch -d "$branch_name"
      run_dir="$repo_root/.ralph/runs/$run_id"
      merged=1
      echo "Merged $branch_name into $integration_branch and removed the worktree."
    else
      # A failed preparation/ff-only merge means staging moved or an unsafe
      # non-generated collision exists. Exiting 0 here made the loop rerun the
      # slice while the finished branch sat stranded. Fail loudly instead.
      echo "MERGE_FAILED: auto-merge into $integration_branch failed; branch $branch_name kept with the completed work." >&2
      exit "$RALPH_EXIT_MERGE_FAILED"
    fi
  else
    echo "auto_merge is disabled; review and merge branch $branch_name manually." >&2
  fi
fi

if (( merged == 1 )); then
  auto_push="$(awk -F': *' '/^[[:space:]]*auto_push:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
  push_remote="$(awk -F': *' '/^[[:space:]]*push_remote:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
  if [[ "$auto_push" == "true" && -n "$push_remote" ]]; then
    if git -C "$repo_root" push "$push_remote" "$integration_branch"; then
      echo "Pushed $integration_branch to $push_remote."
    else
      echo "WARN: push to $push_remote failed (non-fatal); push manually later." >&2
    fi
  fi
fi

if [[ -n "$resume_worktree" && "$committed" == 1 ]]; then
  ralph_clear_repair_context "$repo_root/.ralph/repair-context.json"
fi

rm -f "$lock_file"
echo "Ralph run complete: $run_dir"
