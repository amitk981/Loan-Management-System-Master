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
agent="${AGENT_TOOL:-}"
selected_slice=""
dry_run=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id)
      run_id="${2:?--run-id requires a value}"
      shift 2
      ;;
    --mode)
      mode="${2:?--mode requires a value}"
      shift 2
      ;;
    --agent)
      agent="${2:?--agent requires a value}"
      shift 2
      ;;
    --slice)
      selected_slice="${2:?--slice requires a value}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    *)
      echo "Unknown preflight argument: $1" >&2
      exit 2
      ;;
  esac
done

config=".ralph/config.yaml"
run_id="${run_id:-$(date '+%Y-%m-%d_%H%M%S')_preflight}"
run_dir=".ralph/runs/$run_id"

if (( dry_run == 0 )); then
  mkdir -p "$run_dir/evidence/terminal-logs"
  output="$run_dir/preflight-results.md"
else
  output="$(mktemp)"
  trap 'cat "$output"; rm -f "$output"' EXIT
fi

failures=0
note() { echo "$*" >> "$output"; }
fail() { note "- FAIL: $*"; failures=$((failures + 1)); }
pass() { note "- PASS: $*"; }
warn() { note "- WARN: $*"; }

: > "$output"
note "# Preflight Results"
note ""
note "Run ID: $run_id"
note "Mode: $mode"
note "Agent: ${agent:-unset}"
note ""

git rev-parse --is-inside-work-tree >/dev/null 2>&1 && pass "Git repository detected." || fail "Not inside a git repository."

for required in AGENTS.md .ralph/config.yaml .ralph/permissions.json .ralph/state.json docs/working/CONTEXT.md docs/working/AFK_RUNBOOK.md docs/working/TOKEN_RULES.md docs/working/HANDOFF.md docs/working/HIGH_RISK_APPROVALS.md docs/working/DECISION_POLICY.md docs/working/FRONTEND_DESIGN_RULES.md; do
  [[ -f "$required" ]] && pass "$required exists." || fail "$required is missing."
done

if command -v python3 >/dev/null 2>&1; then
  python3 -m json.tool .ralph/state.json >/dev/null && pass "state.json is valid JSON." || fail "state.json is invalid JSON."
  python3 -m json.tool .ralph/permissions.json >/dev/null && pass "permissions.json is valid JSON." || fail "permissions.json is invalid JSON."
else
  fail "python3 is required for JSON validation."
fi

if command -v ruby >/dev/null 2>&1; then
  ruby -e 'require "yaml"; YAML.load_file(ARGV[0])' "$config" >/dev/null 2>&1 && pass "config.yaml is parseable YAML." || fail "config.yaml is invalid YAML."
else
  for section in agent run limits quality_gates risk worktree commands docs; do
    grep -q "^$section:" "$config" && pass "config section '$section' exists." || fail "config section '$section' is missing."
  done
fi

default_tool="$(awk -F': *' '/^[[:space:]]*default_tool:/ {print $2; exit}' "$config" | tr -d '"' | xargs || true)"
agent="${agent:-$default_tool}"
if [[ -z "$agent" ]]; then
  fail "No selected agent and no agent.default_tool configured."
elif command -v "$agent" >/dev/null 2>&1; then
  pass "Agent command '$agent' is available."
else
  fail "Agent command '$agent' is not available."
fi

if [[ -n "$selected_slice" ]]; then
  if [[ -f "$selected_slice" ]]; then
    pass "Selected slice file exists: $selected_slice"
  elif compgen -G "docs/slices/${selected_slice}*.md" >/dev/null; then
    pass "Selected slice exists: $selected_slice"
  else
    fail "Selected slice not found: $selected_slice"
  fi
else
  find docs/slices -maxdepth 1 -type f -name '*.md' | grep -q . && pass "At least one slice file exists." || fail "No slice files found."
fi

mkdir -p .ralph/locks
for lock in .ralph/locks/*.lock; do
  [[ -f "$lock" ]] || continue
  lock_pid="$(sed -n '2p' "$lock" 2>/dev/null || true)"
  if [[ -z "$lock_pid" ]] || ! kill -0 "$lock_pid" 2>/dev/null; then
    rm -f "$lock"
    warn "Removed stale lock $(basename "$lock") — owning process is no longer running (previous session interrupted)."
  fi
done
if find .ralph/locks -maxdepth 1 -type f -name '*.lock' | grep -q .; then
  fail "Another Ralph run is active right now (live lock). Wait for it or stop it before starting a new run."
else
  pass "No active Ralph locks."
fi

project_dir="$(awk -F': *' '/^[[:space:]]*project_dir:/ {print $2; exit}' "$config" | tr -d '"' | xargs || true)"
project_dir="${project_dir:-.}"
if [[ -f "$project_dir/package-lock.json" ]]; then
  pm="npm"
elif [[ -f "$project_dir/pnpm-lock.yaml" ]]; then
  pm="pnpm"
elif [[ -f "$project_dir/yarn.lock" ]]; then
  pm="yarn"
elif [[ -f "$project_dir/bun.lock" || -f "$project_dir/bun.lockb" ]]; then
  pm="bun"
elif [[ -f "$project_dir/package.json" ]]; then
  pm="npm"
else
  pm=""
fi

if [[ -n "$pm" ]]; then
  pass "Package manager detected: $pm in $project_dir."
  if [[ -f "$project_dir/package.json" ]]; then
    grep -q '"build"' "$project_dir/package.json" && pass "Build script detected." || warn "No build script detected."
    grep -q '"lint"' "$project_dir/package.json" && pass "Lint script detected." || warn "No lint script detected."
    grep -q '"typecheck"' "$project_dir/package.json" && pass "Typecheck script detected." || warn "No typecheck script detected."
  fi
else
  warn "No package manager detected."
fi

if [[ "$mode" != "bootstrap" ]]; then
  require_clean="$(awk -F': *' '/^[[:space:]]*require_clean_git:/ {print $2; exit}' "$config" | xargs || true)"
  if [[ "$require_clean" == "true" && "$dry_run" == 0 ]]; then
    status_before="$(git status --porcelain --untracked-files=no || true)"
    if [[ -n "$status_before" ]]; then
      fail "Tracked working tree changes exist. Commit or stash before normal AFK runs."
    else
      pass "Tracked working tree is clean."
    fi
  fi
fi

if (( failures > 0 )); then
  note ""
  note "Preflight failed with $failures failure(s)."
  exit 1
fi

note ""
note "Preflight passed."
