#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

run_id=""
worktree_dir="$repo_root"
mode="normal_run"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id)
      run_id="${2:?--run-id requires a value}"
      shift 2
      ;;
    --worktree)
      worktree_dir="${2:?--worktree requires a value}"
      shift 2
      ;;
    --mode)
      mode="${2:?--mode requires a value}"
      shift 2
      ;;
    *)
      echo "Unknown validate argument: $1" >&2
      exit 2
      ;;
  esac
done

run_id="${run_id:-$(date '+%Y-%m-%d_%H%M%S')_validate}"
run_dir="$worktree_dir/.ralph/runs/$run_id"
mkdir -p "$run_dir"

config="$worktree_dir/.ralph/config.yaml"
project_dir="$(awk -F': *' '/^[[:space:]]*project_dir:/ {print $2; exit}' "$config" | tr -d '"' | xargs || true)"
project_dir="${project_dir:-.}"
project_path="$worktree_dir/$project_dir"

enabled() {
  local key="$1"
  awk -F': *' -v key="$key" '$1 ~ "^[[:space:]]*" key "$" {print $2; exit}' "$config" | xargs
}

run_gate() {
  local name="$1"
  local command="$2"
  local file="$run_dir/${name}-results.md"
  {
    echo "# $name Results"
    echo
    echo "Command: $command"
    echo
  } > "$file"
  if [[ ! -d "$project_path" ]]; then
    echo "Project directory not found: $project_path" >> "$file"
    return 1
  fi
  (cd "$project_path" && bash -lc "$command") >> "$file" 2>&1
}

write_skipped() {
  local name="$1"
  local reason="$2"
  {
    echo "# $name Results"
    echo
    echo "Skipped: $reason"
  } > "$run_dir/${name}-results.md"
}

failures=0

if [[ "$(enabled build)" == "true" ]]; then
  run_gate build "npm run build" || failures=$((failures + 1))
else
  write_skipped build "disabled in .ralph/config.yaml"
fi

if [[ "$(enabled install)" == "true" ]]; then
  run_gate install "npm install" || failures=$((failures + 1))
else
  write_skipped install "disabled in .ralph/config.yaml"
fi

if [[ "$(enabled typecheck)" == "true" ]]; then
  run_gate typecheck "npm run typecheck --if-present" || failures=$((failures + 1))
else
  write_skipped typecheck "disabled in .ralph/config.yaml"
fi

if [[ "$(enabled lint)" == "true" ]]; then
  run_gate lint "npm run lint --if-present" || failures=$((failures + 1))
else
  write_skipped lint "disabled in .ralph/config.yaml"
fi

if [[ "$(enabled unit_tests)" == "true" ]]; then
  run_gate test "npm test --if-present" || failures=$((failures + 1))
else
  write_skipped test "disabled in .ralph/config.yaml"
fi

backend_dir="$(awk -F': *' '/^[[:space:]]*backend_dir:/ {print $2; exit}' "$config" | tr -d '"' | xargs || true)"
run_backend_gate() {
  local name="$1"
  local command="$2"
  local file="$run_dir/${name}-results.md"
  {
    echo "# $name Results"
    echo
    echo "Command: $command"
    echo
  } > "$file"
  (cd "$worktree_dir" && bash -lc "$command") >> "$file" 2>&1
}

if [[ -n "$backend_dir" && -f "$worktree_dir/$backend_dir/manage.py" ]]; then
  if [[ "$(enabled backend_check)" == "true" ]]; then
    run_backend_gate backend-check "python3 $backend_dir/manage.py check" || failures=$((failures + 1))
  else
    write_skipped backend-check "disabled in .ralph/config.yaml"
  fi
  if [[ "$(enabled backend_tests)" == "true" ]]; then
    run_backend_gate backend-test "python3 $backend_dir/manage.py test $backend_dir.tests -v 2" || failures=$((failures + 1))
  else
    write_skipped backend-test "disabled in .ralph/config.yaml"
  fi
else
  write_skipped backend-check "no backend detected at ${backend_dir:-<unset>}/manage.py"
  write_skipped backend-test "no backend detected at ${backend_dir:-<unset>}/manage.py"
fi

artifact_file="$run_dir/ralph-artifact-validation.md"
{
  echo "# Ralph Artifact Validation"
  echo
  echo "- Run folder: $run_dir"
} > "$artifact_file"

for required in prompt.md execution-plan.md changed-files.txt risk-assessment.md final-summary.md review-packet.md; do
  if [[ -f "$run_dir/$required" ]]; then
    echo "- PASS: $required exists." >> "$artifact_file"
  else
    echo "- FAIL: $required is missing." >> "$artifact_file"
    failures=$((failures + 1))
  fi
done

python3 -m json.tool "$worktree_dir/.ralph/state.json" >/dev/null && echo "- PASS: state.json is valid." >> "$artifact_file" || { echo "- FAIL: state.json invalid." >> "$artifact_file"; failures=$((failures + 1)); }
python3 -m json.tool "$worktree_dir/.ralph/permissions.json" >/dev/null && echo "- PASS: permissions.json is valid." >> "$artifact_file" || { echo "- FAIL: permissions.json invalid." >> "$artifact_file"; failures=$((failures + 1)); }

if command -v ruby >/dev/null 2>&1; then
  ruby -e 'require "yaml"; YAML.load_file(ARGV[0])' "$config" >/dev/null 2>&1 && echo "- PASS: config.yaml is parseable." >> "$artifact_file" || { echo "- FAIL: config.yaml invalid." >> "$artifact_file"; failures=$((failures + 1)); }
fi

if (( failures > 0 )); then
  echo "Validation failed with $failures issue(s)." >> "$artifact_file"
  exit 1
fi

echo "Validation passed." >> "$artifact_file"
echo "Ralph validation passed: $run_dir"
