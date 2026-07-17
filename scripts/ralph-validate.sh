#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"
source "$repo_root/scripts/lib/ralph-postgresql-acceptance.sh"
source "$repo_root/scripts/lib/ralph-runtime-capabilities.sh"
source "$repo_root/scripts/lib/ralph-browser-acceptance.sh"
source "$repo_root/scripts/lib/ralph-slice-selection.sh"
source "$repo_root/scripts/lib/ralph-fast-candidate-checks.sh"
source "$repo_root/scripts/lib/ralph-oversized-slice.sh"
source "$repo_root/scripts/lib/ralph-architecture-review.sh"

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

slice_file="$worktree_dir/docs/slices/${slice_id}.md"
split_slice_id="${RALPH_SPLIT_SLICE_ID:-}"
postgres_acceptance_required=0
localhost_e2e_required=0
if [[ -n "$split_slice_id" ]]; then
  if [[ "$mode" != "architecture_review" || ! "$split_slice_id" =~ ^[A-Za-z0-9]+$ ]]; then
    echo "Invalid oversized-slice validation environment." >&2
    exit 2
  fi
elif [[ -n "$slice_id" && "$mode" != "architecture_review" ]]; then
  if [[ ! -f "$slice_file" ]]; then
    echo "Selected slice file is missing: $slice_file" >&2
    exit 2
  fi
  ralph_validate_slice_capabilities "$slice_file" || exit 2
  if ralph_slice_has_capability "$slice_file" "$RALPH_CAPABILITY_POSTGRESQL_FIVE_RACE_ACCEPTANCE"; then
    postgres_acceptance_required=1
  fi
  if ralph_slice_has_capability "$slice_file" "$RALPH_CAPABILITY_LOCALHOST_E2E_SERVER"; then
    localhost_e2e_required=1
  fi
fi

run_id="${run_id:-$(date '+%Y-%m-%d_%H%M%S')_validate}"
run_dir="$worktree_dir/.ralph/runs/$run_id"
mkdir -p "$run_dir"

if [[ -n "$split_slice_id" ]]; then
  split_results="$run_dir/oversized-slice-split-results.md"
  {
    echo "# Oversized Slice Split Results"
    echo
    split_semantics=0
    split_scope=0
    ralph_validate_oversized_slice_split "$worktree_dir" "$split_slice_id" && split_semantics=1
    ralph_validate_oversized_split_change_scope "$worktree_dir" "$split_slice_id" && split_scope=1
    (( split_semantics == 1 )) \
      && echo "PASS: $split_slice_id was replaced by a dependency-ordered, drainable successor chain." \
      || echo "FAIL: the queue rewrite for $split_slice_id is incomplete or unsafe."
    (( split_scope == 1 )) \
      && echo "PASS: the planning run changed queue metadata only." \
      || echo "FAIL: the planning run changed files outside the queue-metadata allowlist."
    if (( split_semantics != 1 || split_scope != 1 )); then
      exit 1
    fi
  } > "$split_results"
fi

config="$worktree_dir/.ralph/config.yaml"
project_dir="$(awk -F': *' '/^[[:space:]]*project_dir:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | tr -d '"' | xargs || true)"
project_dir="${project_dir:-.}"
project_path="$worktree_dir/$project_dir"

venv_python="$repo_root/.ralph/venv/bin/python"
[[ -x "$venv_python" ]] || venv_python="python3"

# Gates must use the same node/npm that installed the worktree's node_modules
# (the orchestrator's inherited PATH). A login shell can resolve a different
# node — or the same universal binary under a different architecture (Rosetta
# terminals) — and then native deps like rollup's platform package are missing.
node_bin_dir=""
if command -v npm >/dev/null 2>&1; then
  node_bin_dir="$(cd "$(dirname "$(command -v npm)")" && pwd)"
fi

enabled() {
  local key="$1"
  awk -F': *' -v key="$key" '$1 ~ "^[[:space:]]*" key "$" {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs
}

ralph_monotonic_ms() {
  python3 -c 'import time; print(time.monotonic_ns() // 1_000_000)'
}

ralph_candidate_hash() {
  local candidate_worktree="${1:?worktree directory is required}"
  shift
  python3 "$repo_root/scripts/lib/ralph-candidate-hash.py" \
    "$candidate_worktree" "$@"
}

ralph_append_gate_timing() {
  local file="${1:?result file is required}"
  local started_ms="${2:?start time is required}"
  local rc="${3:?exit code is required}"
  local ended_ms
  ended_ms="$(ralph_monotonic_ms)"
  {
    echo
    echo "Duration milliseconds: $((ended_ms - started_ms))"
    echo "Exit code: $rc"
  } >> "$file"
}

run_gate() {
  local name="$1"
  local command="$2"
  local file="$run_dir/${name}-results.md"
  local started_ms rc=0
  started_ms="$(ralph_monotonic_ms)"
  {
    echo "# $name Results"
    echo
    echo "Command: $command"
    echo
  } > "$file"
  if [[ ! -d "$project_path" ]]; then
    echo "Project directory not found: $project_path" >> "$file"
    ralph_append_gate_timing "$file" "$started_ms" 1
    failed_gate_logs+=("${name}-results.md")
    return 1
  fi
  if [[ -n "$node_bin_dir" ]]; then
    echo "Node PATH pin: $node_bin_dir" >> "$file"
    echo >> "$file"
    command="export PATH=\"$node_bin_dir:\$PATH\"; $command"
  fi
  (cd "$project_path" && bash -lc "$command") >> "$file" 2>&1 || rc=$?
  ralph_append_gate_timing "$file" "$started_ms" "$rc"
  if (( rc != 0 )); then
    failed_gate_logs+=("${name}-results.md")
    return "$rc"
  fi
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
# Results files of gates that failed, for the compact failure-summary.md that
# repair mode reads instead of multi-MB terminal logs.
failed_gate_logs=()
backend_dir="$(awk -F': *' '/^[[:space:]]*backend_dir:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | tr -d '"' | xargs || true)"
postgres_acceptance_passed=0
required_browser_failed=0

# Reject protected edits, invalid queue state, unfilled artifacts, declared
# failures, and oversized diffs before any expensive validation command runs.
if ! ralph_run_fast_candidate_checks \
    "$worktree_dir" "$run_dir" "$config" "$mode" "$slice_id" \
    "$postgres_acceptance_required"; then
  echo "Candidate failed cheap validation; expensive gates were not started." >&2
  exit 1
fi
artifact_file="$run_dir/ralph-artifact-validation.md"
changed_paths="$( (cd "$worktree_dir" && git status --porcelain) \
  | sed -E 's/^.{3}//; s/.* -> //; s/^"//; s/"$//' )"

candidate_hash_before="$(ralph_candidate_hash "$worktree_dir")"
commit_candidate_hash_before="$(ralph_candidate_hash "$worktree_dir" \
  --exclude "docs/slices/${slice_id}.md" \
  --exclude "docs/working/HANDOFF.md")"
printf '%s\n' "$commit_candidate_hash_before" \
  > "$run_dir/validated-commit-candidate.sha256"
{
  echo "# Candidate Hash Results"
  echo
  echo "Before validation: $candidate_hash_before"
  echo "Commit candidate before validation: $commit_candidate_hash_before"
} > "$run_dir/candidate-hash-results.md"

queue_only_reason=""
queue_only_label=""
if [[ -n "$split_slice_id" ]]; then
  queue_only_reason="oversized-slice queue rewrite contains no product changes"
  queue_only_label="queue-only oversized-slice split"
elif [[ "$mode" == "architecture_review" ]]; then
  architecture_scope_results="$run_dir/architecture-review-scope-results.md"
  {
    echo "# Architecture Review Scope Results"
    echo
    if ralph_validate_architecture_review_change_scope "$worktree_dir"; then
      echo "PASS: documentation-only architecture review contains no product changes."
    else
      echo "FAIL: architecture review changed a product path."
      exit 1
    fi
  } > "$architecture_scope_results" || {
    echo "Architecture review changed product code; refusing specialized validation." >&2
    exit 1
  }
  queue_only_reason="documentation-only architecture review contains no product changes"
  queue_only_label="documentation-only architecture review"
fi

if [[ -n "$queue_only_reason" ]]; then
  # The candidate is proven documentation/Ralph-metadata-only above. Product
  # gates cannot add signal to that change class, so record their deliberate
  # omission and finish with the same frozen-candidate hash used by commits.
  for queue_only_gate in build install typecheck lint test e2e backend-check backend-test backend-migrations backend-coverage; do
    write_skipped "$queue_only_gate" "$queue_only_reason"
  done
  candidate_hash_after="$(ralph_candidate_hash "$worktree_dir")"
  {
    echo "After validation: $candidate_hash_after"
    if [[ "$candidate_hash_after" == "$candidate_hash_before" ]]; then
      echo "PASS: candidate content remained frozen throughout queue validation."
    else
      echo "FAIL: candidate content changed while queue validation was running."
    fi
  } >> "$run_dir/candidate-hash-results.md"
  if [[ "$candidate_hash_after" != "$candidate_hash_before" ]]; then
    echo "Queue/documentation candidate changed during validation." >&2
    exit 1
  fi
  echo "Validation passed: $queue_only_label." >> "$artifact_file"
  echo "Ralph specialized validation passed ($queue_only_label): $run_dir"
  exit 0
fi

run_postgresql_acceptance_once() {
  local ordinal="$1"
  local log="$run_dir/evidence/terminal-logs/postgresql-acceptance-validation-${ordinal}.txt"
  local rc=0
  local cleanup_rc=0
  local started_ms
  local postgres_test_db
  started_ms="$(ralph_monotonic_ms)"
  postgres_test_db="$(postgresql_test_database_name "$run_id" "$ordinal")"
  mkdir -p "$(dirname "$log")"
  {
    echo "Command:"
    echo "SFPCL_POSTGRES_TEST_DB=$postgres_test_db $venv_python manage.py test sfpcl_credit.tests.test_credit_modules.LoanLimitConcurrencyTests sfpcl_credit.tests.test_appraisal_api.AppraisalConcurrencyTests sfpcl_credit.tests.test_sanction_submission_api.SanctionSubmissionConcurrencyTests --settings=sfpcl_credit.config.postgres_test_settings --noinput -v 2"
    echo
    echo "Working directory: $backend_dir/"
    echo
  } > "$log"
  if (
    cd "$worktree_dir/$backend_dir"
    SFPCL_POSTGRES_TEST_DB="$postgres_test_db" "$venv_python" manage.py test \
      sfpcl_credit.tests.test_credit_modules.LoanLimitConcurrencyTests \
      sfpcl_credit.tests.test_appraisal_api.AppraisalConcurrencyTests \
      sfpcl_credit.tests.test_sanction_submission_api.SanctionSubmissionConcurrencyTests \
      --settings=sfpcl_credit.config.postgres_test_settings --noinput -v 2
  ) >> "$log" 2>&1; then
    rc=0
  else
    rc=$?
  fi
  postgresql_drop_test_database "$venv_python" "$worktree_dir" "$postgres_test_db" >> "$log" 2>&1 \
    || cleanup_rc=$?
  if (( cleanup_rc != 0 )); then
    echo "FAIL: unable to remove isolated PostgreSQL test database $postgres_test_db." >> "$log"
  fi
  echo >> "$log"
  echo "Duration milliseconds: $(( $(ralph_monotonic_ms) - started_ms ))" >> "$log"
  echo "Exit code: $rc" >> "$log"
  echo "Cleanup exit code: $cleanup_rc" >> "$log"
  (( rc == 0 && cleanup_rc == 0 )) && postgresql_acceptance_log_passes "$log"
}

run_trusted_browser_acceptance_once() {
  local ordinal="$1"
  local log="$run_dir/evidence/terminal-logs/trusted-browser-acceptance-${ordinal}.log"
  local specs=()
  local spec=""
  local rc=0
  local started_ms
  started_ms="$(ralph_monotonic_ms)"
  while IFS= read -r spec; do
    [[ -n "$spec" ]] && specs+=("$spec")
  done < <(ralph_trusted_e2e_specs "$slice_file")

  mkdir -p "$(dirname "$log")" "$run_dir/evidence/screenshots"
  {
    echo "Command:"
    printf 'RALPH_EVIDENCE_DIR=%q E2E_DJANGO_PYTHON=%q npm run e2e --' \
      "$run_dir/evidence/screenshots" "$venv_python"
    printf ' %q' "${specs[@]}"
    echo
    echo
    echo "Working directory: $project_dir/"
    echo
  } > "$log"

  if (
    cd "$project_path"
    [[ -z "$node_bin_dir" ]] || export PATH="$node_bin_dir:$PATH"
    RALPH_EVIDENCE_DIR="$run_dir/evidence/screenshots" \
      E2E_DJANGO_PYTHON="$venv_python" \
      npm run e2e -- "${specs[@]}"
  ) >> "$log" 2>&1; then
    rc=0
  else
    rc=$?
  fi
  echo >> "$log"
  echo "Duration milliseconds: $(( $(ralph_monotonic_ms) - started_ms ))" >> "$log"
  echo "Exit code: $rc" >> "$log"
  (( rc == 0 ))
}

write_postgresql_environment() {
  local file="$run_dir/evidence/postgresql-environment-validation.md"
  if postgresql_environment_probe "$venv_python" "$worktree_dir" > "$file.tmp" 2>&1; then
    {
      echo "# PostgreSQL Validation Environment"
      echo
      cat "$file.tmp"
      echo "- Credentials: intentionally omitted"
    } > "$file"
    rm -f "$file.tmp"
    return 0
  fi
  {
    echo "# PostgreSQL Validation Environment"
    echo
    echo "FAIL: unable to query the configured PostgreSQL server without exposing credentials."
    cat "$file.tmp"
  } > "$file"
  rm -f "$file.tmp"
  return 1
}

# Any slice declaring the PostgreSQL five-race capability must execute those
# races independently through the orchestrator. The permission selector and
# acceptance gate consume the same declaration so future slice names cannot
# cause them to drift apart. Run both repetitions even when the first fails.
if [[ "$mode" =~ ^(normal_run|repair)$ && "$postgres_acceptance_required" == "1" ]]; then
  postgres_first=0
  postgres_second=0
  postgres_environment=0
  run_postgresql_acceptance_once 1 && postgres_first=1
  run_postgresql_acceptance_once 2 && postgres_second=1
  if (( postgres_first == 1 && postgres_second == 1 )); then
    write_postgresql_environment && postgres_environment=1
  fi
  {
    echo "# PostgreSQL Acceptance Results"
    echo
    (( postgres_first == 1 )) && echo "- PASS: first independent run executed all five tests successfully." || echo "- FAIL: first independent run did not satisfy all acceptance predicates."
    (( postgres_second == 1 )) && echo "- PASS: second independent run executed all five tests successfully." || echo "- FAIL: second independent run did not satisfy all acceptance predicates."
    (( postgres_environment == 1 )) && echo "- PASS: PostgreSQL server and non-secret connection facts were recorded." || echo "- FAIL: PostgreSQL environment evidence is missing."
  } > "$run_dir/postgresql-acceptance-results.md"
  if (( postgres_first == 1 && postgres_second == 1 && postgres_environment == 1 )); then
    postgres_acceptance_passed=1
  else
    failures=$((failures + 1))
    failed_gate_logs+=("postgresql-acceptance-results.md")
  fi
fi

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

# Browser processes need macOS services that are intentionally unavailable to
# the coding-agent sandbox. A slice declaring localhost E2E capability must
# therefore name its exact Playwright specs and expected screenshots in a
# strict Trusted Browser Acceptance section. The orchestrator executes that
# slice-specific contract twice outside the coding sandbox.
if [[ "$mode" =~ ^(normal_run|repair)$ && "$localhost_e2e_required" == "1" ]]; then
  browser_contract=0
  browser_readme=0
  browser_timezone=0
  browser_first=0
  browser_second=0
  browser_second_deferred=0
  browser_screenshots=1
  ralph_validate_trusted_browser_acceptance "$slice_file" "$project_path" && browser_contract=1
  rg -q "git rev-parse .*--git-common-dir" "$project_path/e2e/README.md" && browser_readme=1
  rg -q "timezoneId: 'Asia/Kolkata'" "$project_path/playwright.config.ts" && browser_timezone=1

  if (( browser_contract == 1 && browser_readme == 1 && browser_timezone == 1 )); then
    while IFS= read -r screenshot; do
      [[ -n "$screenshot" ]] && rm -f "$run_dir/evidence/screenshots/$screenshot"
    done < <(ralph_trusted_e2e_screenshots "$slice_file")
    if run_trusted_browser_acceptance_once 1; then
      browser_first=1
      run_trusted_browser_acceptance_once 2 && browser_second=1
    else
      browser_second_deferred=1
    fi
    while IFS= read -r screenshot; do
      [[ -z "$screenshot" ]] && continue
      [[ -s "$run_dir/evidence/screenshots/$screenshot" ]] || browser_screenshots=0
    done < <(ralph_trusted_e2e_screenshots "$slice_file")
  else
    browser_screenshots=0
  fi

  {
    echo "# e2e Results"
    echo
    (( browser_contract == 1 )) && echo "- PASS: slice-specific trusted browser contract is valid." || echo "- FAIL: slice-specific trusted browser contract is missing or invalid."
    (( browser_readme == 1 )) && echo "- PASS: README E2E command resolves the shared venv through Git's common directory." || echo "- FAIL: README E2E command does not resolve the shared venv through Git's common directory."
    (( browser_timezone == 1 )) && echo "- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata." || echo "- FAIL: Playwright does not pin the dashboard baseline timezone to Asia/Kolkata."
    (( browser_first == 1 )) && echo "- PASS: first trusted slice-specific browser run passed." || echo "- FAIL: first trusted slice-specific browser run did not pass."
    if (( browser_second == 1 )); then
      echo "- PASS: second trusted slice-specific browser run passed."
    elif (( browser_second_deferred == 1 )); then
      echo "- SKIP: second trusted slice-specific browser run deferred because the first run failed."
    else
      echo "- FAIL: second trusted slice-specific browser run did not pass."
    fi
    (( browser_screenshots == 1 )) && echo "- PASS: every declared browser screenshot exists and is non-empty." || echo "- FAIL: one or more declared browser screenshots are missing or empty."
    echo
    echo "Declared specs:"
    ralph_trusted_e2e_specs "$slice_file" | sed 's/^/- /'
    echo "Declared screenshots:"
    ralph_trusted_e2e_screenshots "$slice_file" | sed 's/^/- /'
  } > "$run_dir/e2e-results.md"

  if (( browser_contract == 1 && browser_readme == 1 && browser_timezone == 1 \
        && browser_first == 1 && browser_second == 1 && browser_screenshots == 1 )); then
    :
  else
    failures=$((failures + 1))
    required_browser_failed=1
    failed_gate_logs+=("e2e-results.md")
  fi
else
  write_skipped e2e "slice does not declare localhost-e2e-server"
fi

run_backend_gate() {
  local name="$1"
  local command="$2"
  local file="$run_dir/${name}-results.md"
  local started_ms rc=0
  started_ms="$(ralph_monotonic_ms)"
  {
    echo "# $name Results"
    echo
    echo "Command: $command"
    echo
  } > "$file"
  (cd "$worktree_dir" && bash -lc "$command") >> "$file" 2>&1 || rc=$?
  ralph_append_gate_timing "$file" "$started_ms" "$rc"
  if (( rc != 0 )); then
    failed_gate_logs+=("${name}-results.md")
    return "$rc"
  fi
}

if (( required_browser_failed == 1 )); then
  # A required browser failure already makes this candidate unmergeable. Keep
  # the cheap repository/evidence checks below, but defer the expensive backend
  # suite until the browser repair is green. The repair rerun executes every
  # backend gate normally, so no acceptance gate is removed from a passing run.
  write_skipped backend-check "required trusted browser acceptance failed; deferred until repair"
  write_skipped backend-test "required trusted browser acceptance failed; deferred until repair"
  write_skipped backend-migrations "required trusted browser acceptance failed; deferred until repair"
  write_skipped backend-coverage "required trusted browser acceptance failed; deferred until repair"
elif [[ -n "$backend_dir" && -f "$worktree_dir/$backend_dir/manage.py" ]]; then
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
    coverage_floor="$(awk -F': *' '/^[[:space:]]*coverage_fail_under:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
    coverage_floor="${coverage_floor:-85}"
    coverage_workers="$(awk -F': *' '/^[[:space:]]*backend_coverage_parallel_workers:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' "$config" | xargs || true)"
    coverage_workers="${coverage_workers:-1}"
    if "$venv_python" -c "import coverage" >/dev/null 2>&1; then
      if ! [[ "$coverage_workers" =~ ^[1-9][0-9]*$ ]]; then
        {
          echo "# backend-coverage Results"
          echo
          echo "FAIL: backend_coverage_parallel_workers must be a positive integer."
        } > "$run_dir/backend-coverage-results.md"
        failures=$((failures + 1))
      elif (( coverage_workers > 1 )); then
        run_backend_gate backend-coverage "\"$repo_root/scripts/ralph-parallel-backend-coverage.sh\" \"$venv_python\" \"$worktree_dir\" \"$backend_dir\" \"$coverage_workers\" \"$coverage_floor\"" || failures=$((failures + 1))
      else
        run_backend_gate backend-coverage "\"$venv_python\" -m coverage run --source=$backend_dir $backend_dir/manage.py test $backend_dir.tests && \"$venv_python\" -m coverage report --fail-under=$coverage_floor" || failures=$((failures + 1))
      fi
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

candidate_hash_after="$(ralph_candidate_hash "$worktree_dir")"
{
  echo "After validation: $candidate_hash_after"
  if [[ "$candidate_hash_after" == "$candidate_hash_before" ]]; then
    echo "PASS: candidate content remained frozen throughout validation."
  else
    echo "FAIL: candidate content changed while validation was running."
  fi
} >> "$run_dir/candidate-hash-results.md"
if [[ "$candidate_hash_after" != "$candidate_hash_before" ]]; then
  failures=$((failures + 1))
  failed_gate_logs+=("candidate-hash-results.md")
fi

if (( failures > 0 )); then
  # Compact failure summary: repair mode reads this file FIRST instead of
  # re-ingesting multi-MB gate logs (the historical cause of repair runs
  # peaking at 93-94% of the model context window).
  {
    echo "# Failure Summary"
    echo
    echo "- Run: $run_id"
    echo "- Mode: $mode"
    echo "- Slice: ${slice_id:-n/a}"
    echo "- Failed checks: $failures"
    echo
    echo "Repair mode: diagnose from this file first; open the full gate logs in this run"
    echo "folder only when a tail below is insufficient."
    echo
    echo "## All FAIL markers"
    echo
    echo '```'
    grep -H -iE '(^|- )FAIL' "$run_dir"/*.md 2>/dev/null | grep -v 'failure-summary.md' | sed "s|$run_dir/||" | head -40 || echo "(none in check files)"
    echo '```'
    echo
    if (( ${#failed_gate_logs[@]} > 0 )); then
      for gate_log in ${failed_gate_logs[@]+"${failed_gate_logs[@]}"}; do
        [[ -f "$run_dir/$gate_log" ]] || continue
        echo "## Last 50 lines: $gate_log"
        echo
        echo '```'
        tail -n 50 "$run_dir/$gate_log"
        echo '```'
        echo
      done
    fi
    echo "## Changed files (git status)"
    echo
    echo '```'
    printf '%s\n' "${changed_paths:-<unavailable>}"
    echo '```'
  } > "$run_dir/failure-summary.md"
  echo "Validation failed with $failures issue(s). See failure-summary.md." >> "$artifact_file"
  exit 1
fi

echo "Validation passed." >> "$artifact_file"
echo "Ralph validation passed: $run_dir"
