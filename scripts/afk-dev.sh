#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./scripts/afk-dev.sh [iterations] [options]

Options:
  --mode bootstrap|normal|repair|architecture-review
  --slice <slice-id-or-file>
  --agent claude|codex
  --dry-run
  --no-commit
  --no-worktree
  --continue-failed
  --resume-failed
  --help

Examples:
  ./scripts/afk-dev.sh
  ./scripts/afk-dev.sh --mode bootstrap
  AGENT_TOOL=claude ./scripts/afk-dev.sh 1
  ./scripts/afk-dev.sh --dry-run
EOF
}

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"
source "$repo_root/scripts/lib/ralph-repair-context.sh"

if [[ "$repo_root" == *"/.ralph/worktrees/"* ]]; then
  echo "Refusing to run: current directory is inside a Ralph worktree ($repo_root)." >&2
  echo "Run Ralph from the main repository root so worktrees never nest." >&2
  exit 1
fi

mode="normal"
iterations=""
selected_slice=""
agent_flag=""
dry_run=0
no_commit=0
no_worktree=0
continue_failed=0
resume_failed=0
resume_worktree=""
failed_run_id=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      mode="${2:?--mode requires a value}"
      shift 2
      ;;
    --slice)
      selected_slice="${2:?--slice requires a value}"
      shift 2
      ;;
    --agent)
      agent_flag="${2:?--agent requires a value}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    --no-commit)
      no_commit=1
      shift
      ;;
    --no-worktree)
      no_worktree=1
      shift
      ;;
    --continue-failed)
      continue_failed=1
      shift
      ;;
    --resume-failed)
      resume_failed=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    ''|*[!0-9]*)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      iterations="$1"
      shift
      ;;
  esac
done

case "$mode" in
  normal) normalized_mode="normal_run" ;;
  normal_run) normalized_mode="normal_run" ;;
  bootstrap) normalized_mode="bootstrap" ;;
  repair) normalized_mode="repair" ;;
  architecture-review|architecture_review) normalized_mode="architecture_review" ;;
  *)
    echo "Unsupported mode: $mode" >&2
    exit 2
    ;;
esac

if (( resume_failed == 1 )); then
  repair_context="$repo_root/.ralph/repair-context.json"
  if [[ "$normalized_mode" != "repair" && "$normalized_mode" != "architecture_review" ]]; then
    echo "--resume-failed is valid only in repair or architecture-review mode." >&2
    exit 2
  fi
  if ! ralph_repair_context_is_resumable "$repo_root" "$repair_context"; then
    echo "Refusing same-worktree repair: structured repair context is missing, stale, or unsafe." >&2
    exit 1
  fi
  context_slice="$(ralph_repair_context_value "$repair_context" slice_id)"
  if [[ "$normalized_mode" == "architecture_review" ]]; then
    [[ "$context_slice" == "architecture-review" ]] || {
      echo "Refusing architecture-review resume for non-review context: $context_slice" >&2
      exit 1
    }
  else
    selected_slice="$context_slice"
  fi
  resume_worktree="$(ralph_repair_context_value "$repair_context" worktree)"
  failed_run_id="$(ralph_repair_context_value "$repair_context" run_id)"
fi

config=".ralph/config.yaml"
if [[ ! -f "$config" ]]; then
  echo "Missing .ralph/config.yaml. Run ./scripts/afk-dev.sh --mode bootstrap after setup." >&2
  exit 1
fi

yaml_value() {
  local key="$1"
  awk -F': *' -v key="$key" '$1 ~ "^[[:space:]]*" key "$" {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | tr -d '"' | xargs
}

default_iterations="$(yaml_value default_iterations)"
max_iterations="$(yaml_value max_iterations)"
default_tool="$(yaml_value default_tool)"

iterations="${iterations:-${default_iterations:-1}}"
max_iterations="${max_iterations:-3}"
selected_agent="${agent_flag:-${AGENT_TOOL:-${default_tool:-codex}}}"

if (( iterations < 1 )); then
  echo "Iterations must be at least 1." >&2
  exit 2
fi

if (( iterations > max_iterations )); then
  echo "Iterations ($iterations) exceed run.max_iterations ($max_iterations)." >&2
  exit 2
fi

if (( dry_run == 1 )); then
  echo "Ralph dry run"
  echo "  repo: $repo_root"
  echo "  mode: $normalized_mode"
  echo "  iterations: $iterations"
  echo "  agent: $selected_agent"
  [[ -n "$selected_slice" ]] && echo "  slice: $selected_slice"
  preflight_args=(--mode "$normalized_mode" --agent "$selected_agent" --dry-run)
  [[ -n "$selected_slice" ]] && preflight_args+=(--slice "$selected_slice")
  ./scripts/ralph-preflight.sh "${preflight_args[@]}"
  exit 0
fi

run_once() {
  local run_id
  run_id="$(date '+%Y-%m-%d_%H%M%S')_${normalized_mode}"

  case "$normalized_mode" in
    bootstrap)
      ./scripts/ralph-bootstrap.sh --run-id "$run_id"
      ;;
    normal_run|repair|architecture_review)
      preflight_args=(--run-id "$run_id" --mode "$normalized_mode" --agent "$selected_agent")
      run_args=(--run-id "$run_id" --mode "$normalized_mode" --agent "$selected_agent")
      [[ -n "$selected_slice" ]] && preflight_args+=(--slice "$selected_slice")
      [[ -n "$selected_slice" ]] && run_args+=(--slice "$selected_slice")
      [[ "$no_commit" == 1 ]] && run_args+=(--no-commit)
      [[ "$no_worktree" == 1 ]] && run_args+=(--no-worktree)
      [[ "$continue_failed" == 1 ]] && run_args+=(--continue-failed)
      if (( resume_failed == 1 )); then
        run_args+=(--resume-worktree "$resume_worktree" --failed-run-id "$failed_run_id")
      fi
      ./scripts/ralph-preflight.sh "${preflight_args[@]}"
      ./scripts/ralph-run.sh "${run_args[@]}"
      ;;
  esac
}

for ((i = 1; i <= iterations; i++)); do
  run_once
done
