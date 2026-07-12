#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"
source "$repo_root/scripts/lib/ralph-exit-protocol.sh"
source "$repo_root/scripts/lib/ralph-postgresql-acceptance.sh"
source "$repo_root/scripts/lib/ralph-slice-selection.sh"
source "$repo_root/scripts/lib/ralph-repair-context.sh"

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

if [[ -n "$resume_worktree" || -n "$failed_run_id" ]]; then
  if [[ "$mode" != "repair" || -z "$resume_worktree" || -z "$failed_run_id" || "$no_worktree" == 1 || "$no_commit" == 1 ]]; then
    echo "Same-worktree resume requires repair mode, commit/validation enabled, --resume-worktree, and --failed-run-id." >&2
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
    if [[ -f "$selected_slice" ]]; then
      basename "$selected_slice"
      return
    fi
    local found
    found="$(find docs/slices -maxdepth 1 -type f -name "${selected_slice}*.md" | sort | head -n 1)"
    [[ -n "$found" ]] && basename "$found" && return
  fi
  local file unmet
  for file in $(find docs/slices -maxdepth 1 -type f -name '*.md' | sort); do
    [[ "$(ralph_slice_status "$file")" == "Not Started" ]] || continue
    if unmet="$(ralph_slice_unmet_dependencies "$file")"; then
      basename "$file"
      return
    fi
    echo "Skipping $(basename "$file" .md): waiting on $(printf '%s' "$unmet" | tr '\n' ' ' | sed 's/ $//')" >&2
  done
}

slice_file=""
if [[ "$mode" == "architecture_review" ]]; then
  slice_id="architecture-review"
else
  slice_file="$(select_slice || true)"
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
  risk_level="$(awk '/^## Risk Level/ { getline; print; exit }' "docs/slices/$slice_file" | xargs || true)"
  approvals_file="docs/working/HIGH_RISK_APPROVALS.md"
  if grep -qF -- "[revoked] $slice_id" "$approvals_file" 2>/dev/null; then
    echo "Slice $slice_id has been vetoed by the owner in $approvals_file; refusing to run it." >&2
    exit "$RALPH_EXIT_OWNER_VETO"
  fi
  if [[ "$risk_level" == "High" ]]; then
    echo "High-risk slice $slice_id proceeding under the owner's standing approval (see $approvals_file)."
  fi
fi

mkdir -p "$repo_root/.ralph/locks"
lock_file="$repo_root/.ralph/locks/$run_id.lock"
printf '%s\n%s\n' "$run_id" "$$" > "$lock_file"

on_exit() {
  local status=$?
  rm -f "$lock_file"
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
  run_dir="$worktree_dir/.ralph/runs/$run_id"
  mkdir -p "$run_dir"
  if [[ -d "$main_run_dir" ]]; then
    cp -R "$main_run_dir/." "$run_dir/"
    rm -rf "$main_run_dir"
  fi
fi

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

if [[ -n "$resume_worktree" ]]; then
  repair_instruction="- In repair mode: work in this existing quarantined worktree. Diagnose $previous_failure_summary first, preserve the slice's current uncommitted implementation, fix only the demonstrated failure, and rely on full independent revalidation before any commit."
else
  repair_instruction="- In repair mode: first diagnose the most recent failure — read failure-summary.md in the newest failed .ralph/runs/*/ folder (failed checks, last log lines, changed files); open the full gate logs only if that summary is insufficient, and inspect any leftover .ralph/worktrees/ from the failed attempt before starting fresh."
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
- Run required quality gates.
- For a slice declaring `localhost-e2e-server`, implement the exact specs and screenshot outputs in its `## Trusted Browser Acceptance` section. Your coding sandbox may deny Chromium's macOS services: use Playwright collection or non-browser tests for your local feedback, do not fabricate screenshots, and do not declare the run failed solely because Chromium cannot launch. The orchestrator runs the declared browser contract twice outside your sandbox after you finish; that independent gate decides browser acceptance.
- Save evidence.
- Save changed-files.txt.
- Save risk-assessment.md.
- Save review-packet.md.
- Update state, progress, handoff, and slice status.
- Never run git commit, git add, or git push: your sandbox cannot write the worktree's git metadata and the attempt will fail your run. The orchestrator independently validates and commits passing work after you finish.
- High-risk slices proceed under the owner's standing approval (docs/working/HIGH_RISK_APPROVALS.md); record risk honestly in risk-assessment.md. Never implement a slice marked [revoked] there.
- When requirements are ambiguous, follow docs/working/DECISION_POLICY.md: choose the source-doc-compliant option, or the industry-standard default, record it in docs/working/ASSUMPTIONS.md, and continue. Do not stop to ask. Never invent business rules the documents do not state — stub them, record the open question, and continue.
- If the selected slice file is still an unsharpened template stub (its Goal reads "Deliver this narrow capability as a small, testable Ralph implementation slice" or its scope sections say only "Implement the named backend/API capability only"), your FIRST deliverable is sharpening that slice file with concrete requirements from the epic digest, docs/working/maps/, and the slice's cited source sections — before writing execution-plan.md. Never implement directly from an unsharpened stub.
- Before finishing, sharpen the next 1-2 'Not Started' slice files with concrete requirements (fields, endpoints, validation rules, role rules) from the source documents you already opened.
- Prefer docs/working/digests/ over re-reading large docs/source files; if you extract requirements from a large source file, save the distilled version into the matching digest.
- Stop only for the never-do list in DECISION_POLICY.md, forbidden/protected file edits, repeated gate failure, or diff limit violations.
$repair_instruction
- In architecture-review mode: do NOT modify production code. Review the diffs of slices merged since the last review as an independent critic: test quality (real assertions, edge cases), doc fidelity against source references, duplication, architecture drift. Append findings to docs/working/REVIEW_FINDINGS.md and create or sharpen corrective slices for significant issues.
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
11. docs/slices/$slice_file
12. The matching docs/working/digests/ file for this epic, if it exists

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
  if [[ "$mode" != "architecture_review" ]]; then
    ralph_write_repair_context \
      "$repo_root/.ralph/repair-context.json" \
      "$run_id" "$worktree_dir" "$slice_id" "$branch_name" \
      "$run_dir/failure-summary.md"
  fi
  exit "$validation_rc"
fi

cat > "$run_dir/final-summary.md" <<EOF
# Final Summary

Result: Success

Ralph run completed for $slice_id.
EOF

arch_threshold="$(awk -F': *' '/^[[:space:]]*architecture_review_every_completed_slices:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$worktree_dir/.ralph/config.yaml" | xargs || true)"
arch_threshold="${arch_threshold:-4}"

python3 - <<PY
import json
from pathlib import Path
path = Path("$worktree_dir/.ralph/state.json")
state = json.loads(path.read_text())
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
    state["architecture_review_due"] = count >= threshold
else:
    state["slices_completed_since_architecture_review"] = 0
    state["architecture_review_due"] = False
path.write_text(json.dumps(state, indent=2) + "\n")

slice_path = Path("$worktree_dir/docs/slices") / f"{slice_id}.md"
if slice_path.exists():
    lines = slice_path.read_text().splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## Status" and index + 1 < len(lines):
            lines[index + 1] = "Complete"
            break
    slice_path.write_text("\n".join(lines) + "\n")
PY

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
    else
      git commit -m "chore(${slice_id}): complete Ralph AFK run"
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
    if git -C "$repo_root" merge --ff-only "$branch_name"; then
      git -C "$repo_root" worktree remove --force "$worktree_dir"
      git -C "$repo_root" branch -d "$branch_name"
      run_dir="$repo_root/.ralph/runs/$run_id"
      merged=1
      echo "Merged $branch_name into $integration_branch and removed the worktree."
    else
      # A failed ff-only merge means staging moved during the run. Exiting 0 here
      # made the loop rerun the slice from scratch (silent duplicate work) while
      # the finished branch sat stranded. Fail loudly instead; the loop stops.
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
