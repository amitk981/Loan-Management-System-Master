#!/usr/bin/env bash
set -euo pipefail

# Run the complete Django backend suite with bounded process concurrency while
# collecting coverage from every worker. All binary coverage data is ephemeral;
# callers receive normal test/report output and may optionally request JSON.

python_bin="${1:?Python executable is required}"
worktree_dir="${2:?worktree directory is required}"
backend_dir="${3:?backend directory is required}"
workers="${4:?parallel worker count is required}"
coverage_floor="${5:?coverage floor is required}"
json_output="${6:-}"

if [[ ! -x "$python_bin" ]]; then
  echo "Backend Python is unavailable: $python_bin" >&2
  exit 2
fi
if [[ ! -d "$worktree_dir" || ! -f "$worktree_dir/$backend_dir/manage.py" ]]; then
  echo "Backend is unavailable at $worktree_dir/$backend_dir/manage.py" >&2
  exit 2
fi
if ! [[ "$workers" =~ ^[1-9][0-9]*$ ]]; then
  echo "Parallel worker count must be a positive integer." >&2
  exit 2
fi
if ! [[ "$coverage_floor" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "Coverage floor must be numeric." >&2
  exit 2
fi

temp_dir="$(mktemp -d "${TMPDIR:-/tmp}/ralph-parallel-coverage.XXXXXX")"
trap 'rm -rf "$temp_dir"' EXIT
coverage_rcfile="$temp_dir/coveragerc"
coverage_data="$temp_dir/.coverage"

cat > "$coverage_rcfile" <<EOF
[run]
source = $backend_dir
concurrency = multiprocessing
parallel = true
data_file = $coverage_data
EOF

cd "$worktree_dir"
COVERAGE_RCFILE="$coverage_rcfile" COVERAGE_FILE="$coverage_data" \
  "$python_bin" -m coverage run --rcfile "$coverage_rcfile" \
  "$backend_dir/manage.py" test "$backend_dir.tests" \
  --parallel "$workers" --timing --failfast

COVERAGE_FILE="$coverage_data" "$python_bin" -m coverage combine \
  --rcfile "$coverage_rcfile" --data-file "$coverage_data" \
  --keep "$temp_dir"

if [[ -n "$json_output" ]]; then
  mkdir -p "$(dirname "$json_output")"
  COVERAGE_FILE="$coverage_data" "$python_bin" -m coverage json \
    --rcfile "$coverage_rcfile" --data-file "$coverage_data" \
    -o "$json_output" --pretty-print
fi

COVERAGE_FILE="$coverage_data" "$python_bin" -m coverage report \
  --rcfile "$coverage_rcfile" --data-file "$coverage_data" \
  --fail-under="$coverage_floor"
