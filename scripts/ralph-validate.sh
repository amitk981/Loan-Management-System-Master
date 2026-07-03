#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

run_id=""
worktree_dir="$repo_root"
mode="normal_run"
slice_id=""

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
    --slice)
      slice_id="${2:?--slice requires a value}"
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

venv_python="$repo_root/.ralph/venv/bin/python"
[[ -x "$venv_python" ]] || venv_python="python3"

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
    run_backend_gate backend-check "\"$venv_python\" $backend_dir/manage.py check" || failures=$((failures + 1))
  else
    write_skipped backend-check "disabled in .ralph/config.yaml"
  fi
  if [[ "$(enabled backend_tests)" == "true" ]]; then
    run_backend_gate backend-test "\"$venv_python\" $backend_dir/manage.py test $backend_dir.tests -v 2" || failures=$((failures + 1))
  else
    write_skipped backend-test "disabled in .ralph/config.yaml"
  fi
  if [[ "$(enabled backend_migrations)" == "true" ]]; then
    run_backend_gate backend-migrations "\"$venv_python\" $backend_dir/manage.py makemigrations --check --dry-run" || failures=$((failures + 1))
  else
    write_skipped backend-migrations "disabled in .ralph/config.yaml"
  fi
  if [[ "$(enabled backend_coverage)" == "true" ]]; then
    coverage_floor="$(awk -F': *' '/^[[:space:]]*coverage_fail_under:/ {print $2; exit}' "$config" | xargs || true)"
    coverage_floor="${coverage_floor:-85}"
    if "$venv_python" -c "import coverage" >/dev/null 2>&1; then
      run_backend_gate backend-coverage "\"$venv_python\" -m coverage run --source=$backend_dir $backend_dir/manage.py test $backend_dir.tests && \"$venv_python\" -m coverage report --fail-under=$coverage_floor" || failures=$((failures + 1))
    else
      {
        echo "# backend-coverage Results"
        echo
        echo "FAIL: coverage gate is enabled but the coverage module is not installed (pip3 install -r $backend_dir/requirements-dev.txt)."
      } > "$run_dir/backend-coverage-results.md"
      failures=$((failures + 1))
    fi
  else
    write_skipped backend-coverage "disabled in .ralph/config.yaml"
  fi
else
  write_skipped backend-check "no backend detected at ${backend_dir:-<unset>}/manage.py"
  write_skipped backend-test "no backend detected at ${backend_dir:-<unset>}/manage.py"
fi

# Protected paths: an agent run must never modify guardrail files.
guard_file="$run_dir/protected-paths-check.md"
{
  echo "# Protected Paths Check"
  echo
} > "$guard_file"
protected_paths=(
  "scripts/"
  ".github/"
  ".ralph/config.yaml"
  ".ralph/permissions.json"
  "AGENTS.md"
  "CLAUDE.md"
  ".gitignore"
  "docs/working/HIGH_RISK_APPROVALS.md"
  "docs/working/DECISION_POLICY.md"
  "docs/working/FRONTEND_DESIGN_RULES.md"
  "docs/change-requests/TEMPLATE-bug.md"
  "docs/change-requests/TEMPLATE-feature.md"
  "docs/change-requests/README.md"
  "docs/source/"
)
changed_paths="$( (cd "$worktree_dir" && git status --porcelain) | sed -E 's/^.{3}//; s/.* -> //; s/^"//; s/"$//' )"
protected_violations=0
while IFS= read -r changed; do
  [[ -z "$changed" ]] && continue
  for prot in "${protected_paths[@]}"; do
    if [[ "$changed" == "$prot" || "$changed" == "$prot"* ]]; then
      echo "- FAIL: protected path modified by this run: $changed" >> "$guard_file"
      protected_violations=$((protected_violations + 1))
    fi
  done
done <<< "$changed_paths"
if (( protected_violations > 0 )); then
  echo "" >> "$guard_file"
  echo "Protected files may only be changed by the human owner outside Ralph runs." >> "$guard_file"
  failures=$((failures + protected_violations))
else
  echo "- PASS: no protected paths were modified." >> "$guard_file"
fi

# Impact-analysis gate: change-request slices (CR-*) must map their blast
# radius before any code change is accepted.
if [[ "$mode" == "normal_run" && "$slice_id" == CR-* ]]; then
  impact_file="$run_dir/impact-analysis.md"
  ia_results="$run_dir/impact-analysis-check-results.md"
  if [[ -s "$impact_file" ]] && grep -qi "blast radius\|affected" "$impact_file" && grep -qi "regression" "$impact_file"; then
    {
      echo "# Impact Analysis Check Results"
      echo
      echo "PASS: impact-analysis.md exists and covers affected modules and regression tests."
    } > "$ia_results"
  else
    {
      echo "# Impact Analysis Check Results"
      echo
      echo "FAIL: change-request slice $slice_id requires impact-analysis.md in the run folder,"
      echo "covering affected modules (blast radius) and the regression tests to add per module."
    } > "$ia_results"
    failures=$((failures + 1))
  fi
fi

# No-op check: a normal run must actually change something outside Ralph's
# own bookkeeping, otherwise the slice would be silently marked Complete
# without any work having been done.
if [[ "$mode" == "normal_run" ]]; then
  noop_file="$run_dir/no-op-check-results.md"
  agent_changes="$(printf '%s\n' "$changed_paths" | grep -v '^\.ralph/' | grep -v '^$' || true)"
  if [[ -z "$agent_changes" ]]; then
    {
      echo "# No-Op Check Results"
      echo
      echo "FAIL: the agent produced no changes outside .ralph/ bookkeeping."
      echo "A normal run cannot complete a slice with zero product/doc changes."
    } > "$noop_file"
    failures=$((failures + 1))
  else
    {
      echo "# No-Op Check Results"
      echo
      echo "PASS: the run produced real changes:"
      printf '%s\n' "$agent_changes" | sed 's/^/- /'
    } > "$noop_file"
  fi
fi

# Artifact quality: the pre-created plan and risk assessment must have been
# replaced with real content — existence alone proves nothing.
aq_file="$run_dir/artifact-quality-check.md"
{
  echo "# Artifact Quality Check"
  echo
} > "$aq_file"
if grep -qF "must replace this template" "$run_dir/execution-plan.md" 2>/dev/null; then
  echo "- FAIL: execution-plan.md is still the unfilled template." >> "$aq_file"
  failures=$((failures + 1))
else
  echo "- PASS: execution-plan.md was filled in." >> "$aq_file"
fi
if grep -qF "To be completed by the selected agent" "$run_dir/risk-assessment.md" 2>/dev/null; then
  echo "- FAIL: risk-assessment.md is still the unfilled template." >> "$aq_file"
  failures=$((failures + 1))
else
  echo "- PASS: risk-assessment.md was filled in." >> "$aq_file"
fi

# Diff limits: catch runaway rewrites (config limits, .ralph/ excluded).
if [[ "$mode" == "normal_run" || "$mode" == "repair" ]]; then
  max_files="$(awk -F': *' '/^[[:space:]]*max_changed_files:/ {print $2; exit}' "$config" | xargs || true)"
  max_lines="$(awk -F': *' '/^[[:space:]]*max_lines_changed:/ {print $2; exit}' "$config" | xargs || true)"
  max_files="${max_files:-30}"
  max_lines="${max_lines:-2000}"

  files_changed="$(printf '%s\n' "$changed_paths" | grep -v '^\.ralph/' | grep -cv '^$' || true)"
  tracked_lines="$( (cd "$worktree_dir" && git diff --numstat HEAD -- . ':(exclude).ralph') | awk '{added=$1; deleted=$2; if (added != "-") total += added; if (deleted != "-") total += deleted} END {print total + 0}')"
  untracked_lines=0
  while IFS= read -r f; do
    [[ -z "$f" || ! -f "$worktree_dir/$f" ]] && continue
    untracked_lines=$((untracked_lines + $(wc -l < "$worktree_dir/$f" 2>/dev/null || echo 0)))
  done < <( (cd "$worktree_dir" && git ls-files --others --exclude-standard) | grep -v '^\.ralph/' || true)
  total_lines=$((tracked_lines + untracked_lines))

  dl_file="$run_dir/diff-limits-results.md"
  {
    echo "# Diff Limits Results"
    echo
    echo "- Files changed (excluding .ralph/): $files_changed (limit $max_files)"
    echo "- Lines changed (tracked + new files, excluding .ralph/): $total_lines (limit $max_lines)"
  } > "$dl_file"
  if (( files_changed > max_files )); then
    echo "- FAIL: changed-file count exceeds limits.max_changed_files." >> "$dl_file"
    failures=$((failures + 1))
  fi
  if (( total_lines > max_lines )); then
    echo "- FAIL: changed-line count exceeds limits.max_lines_changed." >> "$dl_file"
    failures=$((failures + 1))
  fi
  if (( files_changed <= max_files && total_lines <= max_lines )); then
    echo "- PASS: within diff limits." >> "$dl_file"
  fi
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
