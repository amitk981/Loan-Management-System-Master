#!/usr/bin/env bash
set -euo pipefail

# Run the independently derived backend impact pack. This is intentionally a
# plain Django test lane: global coverage is enforced by bounded full-suite
# checkpoints, while every backend candidate still gets focused regression
# evidence before it can be accepted.

python_bin="${1:?Python executable is required}"
worktree_dir="${2:?worktree directory is required}"
backend_dir="${3:?Backend directory is required}"
workers="${4:?Parallel worker count is required}"
shift 4
test_labels=("$@")

if [[ ! -x "$python_bin" ]]; then
  echo "Backend Python is unavailable: $python_bin" >&2
  exit 2
fi
if [[ ! -f "$worktree_dir/$backend_dir/manage.py" ]]; then
  echo "Backend is unavailable at $worktree_dir/$backend_dir/manage.py" >&2
  exit 2
fi
if ! [[ "$workers" =~ ^[1-9][0-9]*$ ]]; then
  echo "Impacted-test worker count must be a positive integer." >&2
  exit 2
fi
if (( ${#test_labels[@]} == 0 )); then
  echo "At least one impacted Django test label is required." >&2
  exit 2
fi

cd "$worktree_dir"
"$python_bin" "$backend_dir/manage.py" test "${test_labels[@]}" \
  --parallel "$workers" --timing --failfast
