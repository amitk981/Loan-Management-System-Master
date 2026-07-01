#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

run_id=""
force=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id)
      run_id="${2:?--run-id requires a value}"
      shift 2
      ;;
    --force)
      force=1
      shift
      ;;
    *)
      echo "Unknown bootstrap argument: $1" >&2
      exit 2
      ;;
  esac
done

run_id="${run_id:-$(date '+%Y-%m-%d_%H%M%S')_bootstrap}"
run_dir=".ralph/runs/$run_id"

mkdir -p docs/source docs/working docs/slices docs/adr
mkdir -p .ralph/runs .ralph/logs .ralph/locks .ralph/worktrees
mkdir -p "$run_dir/evidence/screenshots" "$run_dir/evidence/videos" "$run_dir/evidence/api-responses" "$run_dir/evidence/terminal-logs"
mkdir -p scripts/agent-adapters

missing=0
for required in \
  AGENTS.md CLAUDE.md .ralph/config.yaml .ralph/permissions.json .ralph/state.json .ralph/progress.md \
  docs/working/CONTEXT.md docs/working/FEATURE_MATRIX.md docs/working/API_SCREEN_MAP.md docs/working/API_CONTRACTS.md \
  docs/working/PROTOTYPE_INVENTORY.md docs/working/PROTOTYPE_GAP_REPORT.md docs/working/VISUAL_ACCEPTANCE.md \
  docs/working/TOKEN_RULES.md docs/working/AFK_RUNBOOK.md docs/working/HANDOFF.md docs/working/ASSUMPTIONS.md \
  docs/working/DEPENDENCY_POLICY.md docs/working/DATABASE_RULES.md docs/working/SKILL_REGISTRY.md docs/working/RISK_REGISTER.md \
  scripts/afk-dev.sh scripts/ralph-preflight.sh scripts/ralph-run.sh scripts/ralph-validate.sh scripts/ralph-cleanup.sh \
  scripts/agent-adapters/claude.sh scripts/agent-adapters/codex.sh; do
  if [[ ! -f "$required" ]]; then
    echo "Missing required file: $required" | tee -a "$run_dir/bootstrap-results.md"
    missing=1
  fi
done

if ! find docs/source -maxdepth 1 -type f | grep -q .; then
  echo "docs/source exists but contains no source files." | tee -a "$run_dir/bootstrap-results.md"
  missing=1
fi

cat > "$run_dir/prompt.md" <<EOF
Ralph bootstrap verification run.

Run ID: $run_id
Mode: bootstrap

Verify Ralph scaffolding only. Do not implement product features. Do not modify docs/source.
EOF

cat > "$run_dir/execution-plan.md" <<'EOF'
# Execution Plan

- Verify required Ralph folders and files.
- Validate JSON/YAML through preflight.
- Run the current configured build gate.
- Save bootstrap summary and review packet.
EOF

git status --short > "$run_dir/changed-files.txt" || true

cat > "$run_dir/risk-assessment.md" <<'EOF'
# Risk Assessment

Risk level: Low

- User-facing impact: Adds automation scaffolding only.
- Database impact: None.
- Auth/permission impact: None to product code.
- Payment/financial impact: None.
- Security impact: Adds file permission boundaries for future agents.
- Dependency impact: None.
- Manual review required: No for scaffold, yes before product feature automation.
EOF

if [[ "$missing" == 0 ]]; then
  result="Success"
else
  result="Blocked"
fi

cat > "$run_dir/final-summary.md" <<EOF
# Final Summary

Result: $result

Ralph bootstrap verification created/checked the required folder structure and scaffold files.

No product features were implemented.
EOF

cat > "$run_dir/review-packet.md" <<EOF
# Review Packet: $run_id

## Result
$result

## Slice
Slice 001: Ralph Bootstrap Verification

## What Changed
Ralph repo-memory files, scripts, adapters, and initial working docs are present.

## Evidence
- Bootstrap results: $run_dir/bootstrap-results.md
- Final summary: $run_dir/final-summary.md

## Risk Level
Low

## Manual Review Needed
No, but review scripts before unattended AFK use.

## Recommended Next Action
Run ./scripts/afk-dev.sh --dry-run, then approve the first product slice.
EOF

cat > docs/working/HANDOFF.md <<EOF
# Ralph Handoff

## Last Run
$run_id

## Current Status
Bootstrap verification result: $result.

## Current Slice
Slice 001: Ralph Bootstrap Verification

## What Completed
Ralph scaffold verified. See $run_dir/.

## Current Blocker
$([[ "$missing" == 0 ]] && echo "None known." || echo "Required Ralph files are missing; inspect bootstrap-results.md.")

## Next Recommended Action
Run ./scripts/afk-dev.sh --dry-run before starting the first AFK implementation iteration.
EOF

cat >> .ralph/progress.md <<EOF

## $(date '+%Y-%m-%d %H:%M:%S') - $run_id
- Agent tool used: local bootstrap script
- Slice attempted: 001-ralph-bootstrap-verification
- Summary: Verified Ralph scaffold.
- Tests run: bootstrap file checks
- Evidence saved: $run_dir/
- Result: $result
- Risk level: Low
- Next action: Run dry-run or first normal iteration.
EOF

python3 - <<PY
import json
from pathlib import Path
path = Path(".ralph/state.json")
state = json.loads(path.read_text())
state["current_phase"] = "normal_run"
state["last_run_id"] = "$run_id"
state["last_run_status"] = "success" if "$missing" == "0" else "blocked"
state["current_tool_preference"] = state.get("current_tool_preference") or "codex"
path.write_text(json.dumps(state, indent=2) + "\n")
PY

if [[ "$missing" != 0 ]]; then
  exit 1
fi

echo "Ralph bootstrap verification complete: $run_dir"
