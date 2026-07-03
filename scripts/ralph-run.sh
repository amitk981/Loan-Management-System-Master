#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

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

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id) run_id="${2:?--run-id requires a value}"; shift 2 ;;
    --mode) mode="${2:?--mode requires a value}"; shift 2 ;;
    --agent) agent="${2:?--agent requires a value}"; shift 2 ;;
    --slice) selected_slice="${2:?--slice requires a value}"; shift 2 ;;
    --no-commit) no_commit=1; shift ;;
    --no-worktree) no_worktree=1; shift ;;
    --continue-failed) continue_failed=1; shift ;;
    *) echo "Unknown run argument: $1" >&2; exit 2 ;;
  esac
done

integration_branch="$(awk -F': *' '/^[[:space:]]*integration_branch:/ {print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
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
  local file status
  for file in $(find docs/slices -maxdepth 1 -type f -name '*.md' | sort); do
    status="$(awk '/^## Status/ { getline; print; exit }' "$file")"
    if [[ "$status" == "Not Started" ]]; then
      basename "$file"
      return
    fi
  done
}

slice_file=""
if [[ "$mode" == "architecture_review" ]]; then
  slice_id="architecture-review"
else
  slice_file="$(select_slice || true)"
  if [[ -z "$slice_file" ]]; then
    mkdir -p "$run_dir"
    cat > "$run_dir/final-summary.md" <<'EOF'
# Final Summary

Result: Success

No eligible slice was found.
EOF
    echo "No eligible slice found."
    exit 0
  fi
  slice_id="${slice_file%.md}"
fi

if [[ "$mode" != "architecture_review" ]]; then
  risk_level="$(awk '/^## Risk Level/ { getline; print; exit }' "docs/slices/$slice_file" | xargs || true)"
  approvals_file="docs/working/HIGH_RISK_APPROVALS.md"
  if grep -qF -- "[revoked] $slice_id" "$approvals_file" 2>/dev/null; then
    echo "Slice $slice_id has been vetoed by the owner in $approvals_file; refusing to run it." >&2
    exit 3
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
  branch_name="ralph/${run_id}_${slice_id}"
  worktree_dir="$repo_root/.ralph/worktrees/$run_id"
  git worktree add -b "$branch_name" "$worktree_dir" HEAD
  run_dir="$worktree_dir/.ralph/runs/$run_id"
  mkdir -p "$run_dir"
  if [[ -d "$main_run_dir" ]]; then
    cp -R "$main_run_dir/." "$run_dir/"
    rm -rf "$main_run_dir"
  fi
fi

mkdir -p "$run_dir/evidence/screenshots" "$run_dir/evidence/videos" "$run_dir/evidence/api-responses" "$run_dir/evidence/terminal-logs"

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
- Never modify protected files: scripts/, .ralph/config.yaml, .ralph/permissions.json, AGENTS.md, CLAUDE.md, .gitignore, docs/working/HIGH_RISK_APPROVALS.md, docs/working/DECISION_POLICY.md. Validation fails the run if you do.
- Write execution-plan.md before coding.
- Check permissions before editing files.
- TDD is mandatory for backend and business logic: write the failing test first, then implement, and save red/green output to evidence/terminal-logs/.
- Frontend changes must follow docs/working/FRONTEND_DESIGN_RULES.md exactly: reuse existing components and patterns; never introduce new styling, colours, typography, layouts, or components. If the documents require a screen the prototype lacks, building it from existing patterns and wiring it to the backend is part of the slice.
- Run required quality gates.
- Save evidence.
- Save changed-files.txt.
- Save risk-assessment.md.
- Save review-packet.md.
- Update state, progress, handoff, and slice status.
- Never run git commit, git add, or git push: your sandbox cannot write the worktree's git metadata and the attempt will fail your run. The orchestrator independently validates and commits passing work after you finish.
- High-risk slices proceed under the owner's standing approval (docs/working/HIGH_RISK_APPROVALS.md); record risk honestly in risk-assessment.md. Never implement a slice marked [revoked] there.
- When requirements are ambiguous, follow docs/working/DECISION_POLICY.md: choose the source-doc-compliant option, or the industry-standard default, record it in docs/working/ASSUMPTIONS.md, and continue. Do not stop to ask. Never invent business rules the documents do not state — stub them, record the open question, and continue.
- Before finishing, sharpen the next 1-2 'Not Started' slice files with concrete requirements (fields, endpoints, validation rules, role rules) from the source documents you already opened.
- Prefer docs/working/digests/ over re-reading large docs/source files; if you extract requirements from a large source file, save the distilled version into the matching digest.
- Stop only for the never-do list in DECISION_POLICY.md, forbidden/protected file edits, repeated gate failure, or diff limit violations.
- In repair mode: first diagnose the most recent failure — read the newest .ralph/runs/*/ folder containing FAIL results, and inspect any leftover .ralph/worktrees/ from the failed attempt before starting fresh.
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

agent_timeout="$(awk -F': *' '/^[[:space:]]*agent_timeout_seconds:/ {print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"

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
  echo "WARN: agent adapter exited $agent_rc; proceeding to independent validation — the gates decide pass or fail." >&2
fi

(cd "$worktree_dir" && git status --short > "$run_dir/changed-files.txt")

"$repo_root/scripts/ralph-validate.sh" --run-id "$run_id" --worktree "$worktree_dir" --mode "$mode" --slice "$slice_id"

cat > "$run_dir/final-summary.md" <<EOF
# Final Summary

Result: Success

Ralph run completed for $slice_id.
EOF

arch_threshold="$(awk -F': *' '/^[[:space:]]*architecture_review_every_completed_slices:/ {print $2; exit}' "$worktree_dir/.ralph/config.yaml" | xargs || true)"
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
    state["slices_completed_since_architecture_review"] = state.get("slices_completed_since_architecture_review", 0) + 1
    threshold = int("$arch_threshold")
    state["architecture_review_due"] = state["slices_completed_since_architecture_review"] >= threshold
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

cat > "$worktree_dir/docs/working/HANDOFF.md" <<EOF
# Ralph Handoff

## Last Run
$run_id

## Current Status
Run completed for $slice_id.

## Current Slice
None selected.

## What Completed
See $run_dir/.

## Current Blocker
None known.

## Next Recommended Action
Review $run_dir/review-packet.md.
EOF

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
  (
    cd "$worktree_dir"
    git add .
    if git diff --cached --quiet; then
      echo "No changes to commit for $slice_id."
      exit 10
    else
      git commit -m "chore(${slice_id}): complete Ralph AFK run"
    fi
  ) && committed=1 || true
fi

merged=0
if (( committed == 1 )) && (( no_worktree == 0 )); then
  auto_merge="$(awk -F': *' '/^[[:space:]]*auto_merge:/ {print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
  if [[ "$auto_merge" == "true" ]]; then
    if git -C "$repo_root" merge --ff-only "$branch_name"; then
      git -C "$repo_root" worktree remove --force "$worktree_dir"
      git -C "$repo_root" branch -d "$branch_name"
      run_dir="$repo_root/.ralph/runs/$run_id"
      merged=1
      echo "Merged $branch_name into $integration_branch and removed the worktree."
    else
      echo "Auto-merge into $integration_branch failed; branch $branch_name kept for manual review." >&2
    fi
  else
    echo "auto_merge is disabled; review and merge branch $branch_name manually." >&2
  fi
fi

if (( merged == 1 )); then
  auto_push="$(awk -F': *' '/^[[:space:]]*auto_push:/ {print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
  push_remote="$(awk -F': *' '/^[[:space:]]*push_remote:/ {print $2; exit}' "$repo_root/.ralph/config.yaml" | xargs || true)"
  if [[ "$auto_push" == "true" && -n "$push_remote" ]]; then
    if git -C "$repo_root" push "$push_remote" "$integration_branch"; then
      echo "Pushed $integration_branch to $push_remote."
    else
      echo "WARN: push to $push_remote failed (non-fatal); push manually later." >&2
    fi
  fi
fi

rm -f "$lock_file"
echo "Ralph run complete: $run_dir"
