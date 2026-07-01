#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

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

lock_file="$repo_root/.ralph/locks/$run_id.lock"
echo "$run_id" > "$lock_file"

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
- Write execution-plan.md before coding.
- Check permissions before editing files.
- Use TDD where practical.
- Run required quality gates.
- Save evidence.
- Save changed-files.txt.
- Save risk-assessment.md.
- Save review-packet.md.
- Update state, progress, handoff, and slice status.
- Commit only if gates pass and config allows commits.
- Stop safely on ambiguity, high risk, forbidden file edits, repeated failure, or diff limit violations.

Read in this order:
1. AGENTS.md or CLAUDE.md
2. docs/working/TOKEN_RULES.md
3. docs/working/CONTEXT.md
4. docs/working/AFK_RUNBOOK.md
5. .ralph/config.yaml
6. .ralph/permissions.json
7. .ralph/state.json
8. docs/working/HANDOFF.md
9. docs/slices/$slice_file

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

"$repo_root/scripts/agent-adapters/$agent.sh" \
  RUN_ID="$run_id" \
  RUN_DIR="$run_dir" \
  WORKTREE_DIR="$worktree_dir" \
  PROMPT_FILE="$run_dir/prompt.md" \
  SELECTED_SLICE="$slice_id" \
  MODE="$mode"

(cd "$worktree_dir" && git status --short > "$run_dir/changed-files.txt")

"$repo_root/scripts/ralph-validate.sh" --run-id "$run_id" --worktree "$worktree_dir" --mode "$mode"

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

if (( no_commit == 0 )); then
  (
    cd "$worktree_dir"
    git add .
    if git diff --cached --quiet; then
      echo "No changes to commit for $slice_id."
    else
      git commit -m "chore(${slice_id}): complete Ralph AFK run"
    fi
  )
fi

rm -f "$lock_file"
echo "Ralph run complete: $run_dir"
