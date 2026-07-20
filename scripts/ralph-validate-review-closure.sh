#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ralph-validate-review-closure.sh --slice PATH --run-dir PATH [--worktree PATH]

Run the exact corrective-slice semantic-closure check used by Ralph's
independent validator. This is a fast, read-only preflight for agents to run
before returning a corrective implementation.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
trusted_repo_root="$(cd "$script_dir/.." && pwd)"
worktree=""
slice_file=""
run_dir=""

while (( $# > 0 )); do
  case "$1" in
    --worktree) worktree="${2:?--worktree requires a path}"; shift 2 ;;
    --slice) slice_file="${2:?--slice requires a path}"; shift 2 ;;
    --run-dir) run_dir="${2:?--run-dir requires a path}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

worktree="${worktree:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
worktree="$(cd "$worktree" && pwd -P)"
[[ -n "$slice_file" && -n "$run_dir" ]] || {
  usage >&2
  exit 2
}
[[ "$slice_file" == /* ]] || slice_file="$worktree/$slice_file"
[[ "$run_dir" == /* ]] || run_dir="$worktree/$run_dir"

# Source the trusted integration implementation. The candidate worktree cannot
# weaken its own validator because scripts/ is protected during Ralph runs.
source "$trusted_repo_root/scripts/lib/ralph-architecture-review.sh"
ralph_validate_review_finding_closure "$worktree" "$slice_file" "$run_dir"
