#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

[[ -f scripts/lib/ralph-exit-protocol.sh ]] || fail "missing structured Ralph exit protocol"
# shellcheck source=../lib/ralph-exit-protocol.sh
source scripts/lib/ralph-exit-protocol.sh

[[ -f scripts/lib/ralph-runtime-capabilities.sh ]] || fail "missing Ralph runtime capability parser"
# shellcheck source=../lib/ralph-runtime-capabilities.sh
source scripts/lib/ralph-runtime-capabilities.sh

[[ -f scripts/lib/ralph-browser-acceptance.sh ]] || fail "missing trusted browser acceptance helper"
# shellcheck source=../lib/ralph-browser-acceptance.sh
source scripts/lib/ralph-browser-acceptance.sh
[[ -f scripts/lib/ralph-browser-runtime.sh ]] || fail "missing browser infrastructure recovery helper"
# shellcheck source=../lib/ralph-browser-runtime.sh
source scripts/lib/ralph-browser-runtime.sh

[[ -f scripts/lib/ralph-retry-policy.sh ]] || fail "missing bounded Ralph retry policy helper"
# shellcheck source=../lib/ralph-retry-policy.sh
source scripts/lib/ralph-retry-policy.sh

[[ -f scripts/lib/ralph-merge-guard.sh ]] || fail "missing safe Ralph merge collision guard"
# shellcheck source=../lib/ralph-merge-guard.sh
source scripts/lib/ralph-merge-guard.sh

[[ "$(ralph_outcome_for_status "$RALPH_EXIT_SUCCESS")" == "success" ]] || fail "success status misclassified"
[[ "$(ralph_outcome_for_status "$RALPH_EXIT_QUEUE_EMPTY")" == "queue_empty" ]] || fail "queue-empty status misclassified"
[[ "$(ralph_outcome_for_status "$RALPH_EXIT_OWNER_VETO")" == "owner_veto" ]] || fail "owner-veto status misclassified"
[[ "$(ralph_outcome_for_status "$RALPH_EXIT_MERGE_FAILED")" == "merge_failed" ]] || fail "merge-failed status misclassified"
[[ "$(ralph_outcome_for_status "$RALPH_EXIT_AGENT_LIMIT")" == "agent_limit" ]] || fail "agent-limit status misclassified"
[[ "$(ralph_outcome_for_status "$RALPH_EXIT_BROWSER_INFRASTRUCTURE")" == "browser_infrastructure" ]] \
  || fail "browser-infrastructure status misclassified"
[[ "$(ralph_outcome_for_status "$RALPH_EXIT_ITERATION_LIMIT")" == "iteration_limit" ]] \
  || fail "iteration-limit status misclassified"
[[ "$(ralph_outcome_for_status "$RALPH_EXIT_REVIEW_CONVERGENCE")" == "review_convergence" ]] \
  || fail "review-convergence status misclassified"
[[ "$(ralph_outcome_for_status "$RALPH_EXIT_REVIEW_TERMINAL_RECURRENCE")" == \
    "review_terminal_recurrence" ]] \
  || fail "terminal-review recurrence status misclassified"
[[ "$(ralph_outcome_for_status 1)" == "failed" ]] || fail "generic failure misclassified"

[[ -f scripts/lib/ralph-postgresql-acceptance.sh ]] || fail "missing PostgreSQL acceptance predicate"
# shellcheck source=../lib/ralph-postgresql-acceptance.sh
source scripts/lib/ralph-postgresql-acceptance.sh
fixture_dir="$(mktemp -d)"
trap 'rm -rf "$fixture_dir"' EXIT
cat > "$fixture_dir/retries.yaml" <<'EOF'
run:
  max_retries: 2
  max_progressive_repairs: 5
EOF
cat > "$fixture_dir/invalid-retries.yaml" <<'EOF'
run:
  max_retries: forever
EOF
[[ "$(ralph_max_repair_attempts "$fixture_dir/retries.yaml")" == "2" ]] \
  || fail "configured repair-attempt budget was not honored"
[[ "$(ralph_max_repair_attempts "$fixture_dir/invalid-retries.yaml")" == "1" ]] \
  || fail "invalid repair-attempt budget did not fail safely to one"
[[ "$(ralph_max_progressive_repair_attempts "$fixture_dir/retries.yaml")" == "5" ]] \
  || fail "configured progressive repair ceiling was not honored"
[[ "$(ralph_max_progressive_repair_attempts "$fixture_dir/invalid-retries.yaml")" == "3" ]] \
  || fail "missing progressive repair ceiling did not fail safely to three"

loop_limit_repo="$fixture_dir/loop-limit-repo"
mkdir -p "$loop_limit_repo/scripts/lib" "$loop_limit_repo/.ralph" \
  "$loop_limit_repo/docs/slices"
cp scripts/ralph-loop.sh "$loop_limit_repo/scripts/ralph-loop.sh"
for loop_lib in ralph-exit-protocol.sh ralph-retry-policy.sh ralph-repair-context.sh \
    ralph-oversized-slice.sh ralph-slice-selection.sh ralph-architecture-review.sh; do
  cp "scripts/lib/$loop_lib" "$loop_limit_repo/scripts/lib/$loop_lib"
done
cat > "$loop_limit_repo/scripts/ralph-recover.sh" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
cat > "$loop_limit_repo/scripts/afk-dev.sh" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
chmod +x "$loop_limit_repo/scripts/ralph-loop.sh" \
  "$loop_limit_repo/scripts/ralph-recover.sh" "$loop_limit_repo/scripts/afk-dev.sh"
cat > "$loop_limit_repo/.ralph/config.yaml" <<'EOF'
agent:
  default_tool: codex
  limit_fallback: false
run:
  max_retries: 2
  max_progressive_repairs: 5
EOF
printf '%s\n' '{"architecture_review_due": false}' > "$loop_limit_repo/.ralph/state.json"
cat > "$loop_limit_repo/docs/slices/001A-pending.md" <<'EOF'
## Status
Not Started

## Runtime Capabilities
- `none`

## Depends On
- None
EOF
git init -q "$loop_limit_repo"
git -C "$loop_limit_repo" add .
git -C "$loop_limit_repo" -c user.name='Ralph Regression' \
  -c user.email='ralph-regression@example.invalid' commit -qm fixture
set +e
(
  cd "$loop_limit_repo"
  ./scripts/ralph-loop.sh 1 > loop.stdout 2>&1
)
loop_limit_rc=$?
set -e
[[ "$loop_limit_rc" == "$RALPH_EXIT_ITERATION_LIMIT" ]] \
  || fail "unfinished loop limit returned $loop_limit_rc instead of $RALPH_EXIT_ITERATION_LIMIT"
grep -qF 'Stopped incomplete after reaching max iterations (1).' \
  "$loop_limit_repo/loop.stdout" \
  || fail "unfinished loop limit did not report its exact outcome"

# A failure before Ralph creates a quarantined candidate (for example, a
# preflight cleanliness failure) is not product-repairable. The loop must stop
# after the original attempt instead of spending the repair budget on empty
# failure signatures and claiming that independent validation reproduced one.
cat > "$loop_limit_repo/scripts/afk-dev.sh" <<'EOF'
#!/usr/bin/env bash
counter=".ralph/afk-call-count"
count=0
[[ -f "$counter" ]] && count="$(cat "$counter")"
printf '%s\n' "$((count + 1))" > "$counter"
exit 1
EOF
chmod +x "$loop_limit_repo/scripts/afk-dev.sh"
set +e
(
  cd "$loop_limit_repo"
  ./scripts/ralph-loop.sh 1 > no-context.stdout 2>&1
)
no_context_rc=$?
set -e
[[ "$no_context_rc" == 1 ]] \
  || fail "pre-candidate failure returned $no_context_rc instead of stopping with its original status"
[[ "$(cat "$loop_limit_repo/.ralph/afk-call-count")" == 1 ]] \
  || fail "pre-candidate failure incorrectly launched product repair attempts"
grep -qF 'Run failed before a quarantined candidate existed; product repair cannot apply.' \
  "$loop_limit_repo/no-context.stdout" \
  || fail "pre-candidate failure did not explain why repair was skipped"
if grep -qF 'Independent validation reproduced the current failure signature' \
    "$loop_limit_repo/no-context.stdout"; then
  fail "pre-candidate failure fabricated an independent-validation signature"
fi
if grep -qF 'All bounded repair attempts failed' "$loop_limit_repo/no-context.stdout"; then
  fail "pre-candidate failure claimed that nonexistent repair attempts ran"
fi

merge_repo="$fixture_dir/merge-repo"
git init -q -b integration "$merge_repo"
git -C "$merge_repo" config user.name "Ralph Regression"
git -C "$merge_repo" config user.email "ralph-regression@example.invalid"
printf 'base\n' > "$merge_repo/base.txt"
git -C "$merge_repo" add base.txt
git -C "$merge_repo" commit -qm base
git -C "$merge_repo" switch -qc completed-slice
mkdir -p "$merge_repo/.ralph/runs/failed-run"
printf 'identical evidence\n' > "$merge_repo/.ralph/runs/failed-run/evidence.md"
printf 'validated branch plan\n' > "$merge_repo/.ralph/runs/failed-run/execution-plan.md"
printf 'branch version\n' > "$merge_repo/conflict.txt"
git -C "$merge_repo" add .ralph/runs/failed-run/evidence.md \
  .ralph/runs/failed-run/execution-plan.md conflict.txt
git -C "$merge_repo" commit -qm completed
git -C "$merge_repo" switch -q integration
ralph_quarantined_commit_exists "$merge_repo" completed-slice \
  || fail "post-commit quarantined branch was misclassified as product-repairable"
if ralph_quarantined_commit_exists "$merge_repo" integration; then
  fail "integration HEAD was misclassified as a post-commit quarantine"
fi
mkdir -p "$merge_repo/.ralph/runs/failed-run"
printf 'identical evidence\n' > "$merge_repo/.ralph/runs/failed-run/evidence.md"
printf 'earlier diagnostic plan\n' > "$merge_repo/.ralph/runs/failed-run/execution-plan.md"
printf 'owner version\n' > "$merge_repo/conflict.txt"
if ralph_prepare_worktree_for_ff_merge "$merge_repo" completed-slice >/dev/null 2>&1; then
  fail "merge guard accepted a differing untracked collision"
fi
[[ -e "$merge_repo/.ralph/runs/failed-run/evidence.md" ]] \
  || fail "merge guard partially cleaned files after finding a differing collision"
[[ "$(cat "$merge_repo/.ralph/runs/failed-run/execution-plan.md")" == "earlier diagnostic plan" ]] \
  || fail "merge guard changed generated evidence while a non-generated collision was present"
[[ "$(cat "$merge_repo/conflict.txt")" == "owner version" ]] \
  || fail "merge guard changed a differing untracked file"
rm "$merge_repo/conflict.txt"
RALPH_MERGE_BACKUP_ID=regression-backup \
  ralph_prepare_worktree_for_ff_merge "$merge_repo" completed-slice \
  || fail "merge guard did not archive a differing generated artifact"
merge_git_dir="$(git -C "$merge_repo" rev-parse --absolute-git-dir)"
archived_plan="$merge_git_dir/ralph-merge-collision-backups/regression-backup/.ralph/runs/failed-run/execution-plan.md"
[[ "$(cat "$archived_plan")" == "earlier diagnostic plan" ]] \
  || fail "merge guard did not preserve the earlier generated artifact outside the worktree"
git -C "$merge_repo" merge --ff-only -q completed-slice \
  || fail "merge still failed after safe collision cleanup"
[[ "$(cat "$merge_repo/.ralph/runs/failed-run/execution-plan.md")" == "validated branch plan" ]] \
  || fail "validated branch artifact did not become canonical after merge"

[[ -f scripts/lib/ralph-repair-context.sh ]] || fail "missing same-worktree repair context helper"
# shellcheck source=../lib/ralph-repair-context.sh
source scripts/lib/ralph-repair-context.sh
[[ -f scripts/lib/ralph-oversized-slice.sh ]] || fail "missing oversized-slice split request helper"
# shellcheck source=../lib/ralph-oversized-slice.sh
source scripts/lib/ralph-oversized-slice.sh
repair_repo="$fixture_dir/repair-repo"
repair_worktree="$repair_repo/.ralph/worktrees/failed-run"
repair_run_dir="$repair_worktree/.ralph/runs/failed-run"
repair_context="$repair_repo/.ralph/repair-context.json"
mkdir -p "$repair_run_dir/evidence/terminal-logs" "$repair_repo/.git"
repair_worktree="$(cd "$repair_worktree" && pwd -P)"
repair_run_dir="$repair_worktree/.ralph/runs/failed-run"
cat > "$repair_run_dir/failure-summary.md" <<'EOF'
# Failure Summary

- Run: failed-run
- Slice: 999X-browser-fixture
- Failed checks: 1

e2e-results.md:- FAIL: trusted browser run did not pass.
EOF
cat > "$repair_run_dir/evidence/terminal-logs/trusted-browser-acceptance-1.log" <<EOF
Error: locator.click: Test timeout of 30000ms exceeded.
- waiting for getByRole('button', { name: 'Profile' })
at $repair_worktree/e2e/example.e2e.spec.ts:19:52
Exit code: 1
EOF
ralph_write_repair_context \
  "$repair_context" failed-run "$repair_worktree" \
  999X-browser-fixture ralph/failed-run_999X-browser-fixture \
  "$repair_run_dir/failure-summary.md"
[[ "$(ralph_repair_context_value "$repair_context" run_id)" == "failed-run" ]] \
  || fail "repair context lost the failed run id"
[[ "$(ralph_repair_context_value "$repair_context" worktree)" == "$repair_worktree" ]] \
  || fail "repair context lost the quarantined worktree"
[[ "$(ralph_repair_context_value "$repair_context" slice_id)" == "999X-browser-fixture" ]] \
  || fail "repair context lost the selected slice"
first_failure_signature="$(ralph_repair_context_value "$repair_context" failure_signature)"
[[ -n "$first_failure_signature" ]] || fail "repair context omitted the normalized failure signature"

second_worktree="$repair_repo/.ralph/worktrees/repair-run"
second_run_dir="$second_worktree/.ralph/runs/repair-run"
mkdir -p "$second_run_dir/evidence/terminal-logs"
sed 's/failed-run/repair-run/g' "$repair_run_dir/failure-summary.md" > "$second_run_dir/failure-summary.md"
sed "s#${repair_worktree//\#/\\#}#${second_worktree//\#/\\#}#g" \
  "$repair_run_dir/evidence/terminal-logs/trusted-browser-acceptance-1.log" \
  > "$second_run_dir/evidence/terminal-logs/trusted-browser-acceptance-1.log"
second_failure_signature="$(ralph_failure_signature "$second_run_dir/failure-summary.md")"
[[ "$first_failure_signature" == "$second_failure_signature" ]] \
  || fail "same browser failure received a different normalized signature"
printf '%s\n' 'Error: locator.click: strict mode violation.' \
  > "$second_run_dir/evidence/terminal-logs/trusted-browser-acceptance-1.log"
[[ "$first_failure_signature" != "$(ralph_failure_signature "$second_run_dir/failure-summary.md")" ]] \
  || fail "different browser failures received the same normalized signature"

registered_repo="$fixture_dir/registered-repair-repo"
registered_worktree="$registered_repo/.ralph/worktrees/registered-failure"
git init -q "$registered_repo"
git -C "$registered_repo" config user.name "Ralph Regression"
git -C "$registered_repo" config user.email "ralph-regression@example.invalid"
printf '%s\n' seed > "$registered_repo/seed.txt"
git -C "$registered_repo" add seed.txt
git -C "$registered_repo" commit -qm seed
mkdir -p "$registered_repo/.ralph/worktrees"
git -C "$registered_repo" worktree add -q -b ralph/registered-failure_fixture "$registered_worktree" HEAD
registered_run_dir="$registered_worktree/.ralph/runs/registered-failure"
mkdir -p "$registered_run_dir/evidence/terminal-logs"
cp "$repair_run_dir/failure-summary.md" "$registered_run_dir/failure-summary.md"
cp "$repair_run_dir/evidence/terminal-logs/trusted-browser-acceptance-1.log" \
  "$registered_run_dir/evidence/terminal-logs/trusted-browser-acceptance-1.log"
registered_context="$registered_repo/.ralph/repair-context.json"
ralph_write_repair_context \
  "$registered_context" registered-failure "$registered_worktree" \
  999X-browser-fixture ralph/registered-failure_fixture \
  "$registered_run_dir/failure-summary.md"
ralph_repair_context_is_resumable "$registered_repo" "$registered_context" \
  || fail "registered quarantined Ralph worktree was rejected for repair"

cat > "$registered_run_dir/oversized-slice-request.json" <<'EOF'
{
  "version": 1,
  "reason": "diff_limit_exceeded",
  "run_id": "registered-failure",
  "slice_id": "999X-browser-fixture",
  "total_lines": 2885,
  "max_lines": 2000
}
EOF
split_request="$(ralph_oversized_slice_request "$registered_repo" "$registered_context")" \
  || fail "valid oversized candidate did not produce a split request"
[[ "$split_request" == $'999X\tregistered-failure\t2885\t2000' ]] \
  || fail "oversized split request returned the wrong trusted facts: $split_request"

if ralph_oversized_split_retry_context \
    "$registered_repo" "$registered_context" 999X >/dev/null 2>&1; then
  fail "ordinary product failure was misclassified as a failed split planning gate"
fi
cat > "$registered_run_dir/oversized-slice-split-results.md" <<'EOF'
# Oversized Slice Split Results

PASS: 999X was replaced by a dependency-ordered, drainable successor chain.
Oversized-slice planning may not rewrite unrelated slice docs/slices/999-parent.md.
FAIL: the planning run changed files outside the queue-metadata allowlist.
EOF
cat > "$registered_run_dir/failure-summary.md" <<'EOF'
# Validation Failure Summary

## oversized-slice-split-results.md

FAIL: the planning run changed files outside the queue-metadata allowlist.
EOF
ralph_write_repair_context \
  "$registered_context" registered-failure "$registered_worktree" \
  999X-browser-fixture ralph/registered-failure_fixture \
  "$registered_run_dir/failure-summary.md"
split_failure_signature="$(ralph_repair_context_value \
  "$registered_context" failure_signature)"
split_retry_context="$(ralph_oversized_split_retry_context \
  "$registered_repo" "$registered_context" 999X)" \
  || fail "valid failed split planning context was not eligible for bounded correction"
[[ "$split_retry_context" == $'registered-failure\t'"$split_failure_signature" ]] \
  || fail "split retry context returned the wrong trusted facts: $split_retry_context"
if ralph_oversized_split_retry_context \
    "$registered_repo" "$registered_context" 999Y >/dev/null 2>&1; then
  fail "split retry context accepted a failure for a different oversized slice"
fi
ralph_oversized_split_retry_allowed "$RALPH_EXIT_FAILED" 1 2 \
  || fail "first independently failed split was not eligible for bounded correction"
if ralph_oversized_split_retry_allowed "$RALPH_EXIT_FAILED" 2 2; then
  fail "second independently failed split was allowed to retry indefinitely"
fi
if ralph_oversized_split_retry_allowed "$RALPH_EXIT_MERGE_FAILED" 1 2; then
  fail "validated split merge failure was misclassified as a planning repair"
fi

ralph_write_repair_context \
  "$registered_context" registered-failure "$registered_worktree" \
  999X-browser-fixture ralph/registered-failure_fixture \
  "$repair_run_dir/failure-summary.md"
if ralph_repair_context_is_resumable "$registered_repo" "$registered_context"; then
  fail "failure summary outside the quarantined worktree was accepted for repair"
fi

outside_worktree="$fixture_dir/outside-worktree"
git -C "$registered_repo" worktree add -q -b ralph/outside_fixture "$outside_worktree" HEAD
outside_run_dir="$outside_worktree/.ralph/runs/outside-failure"
mkdir -p "$outside_run_dir"
cp "$repair_run_dir/failure-summary.md" "$outside_run_dir/failure-summary.md"
ralph_write_repair_context \
  "$registered_context" outside-failure "$outside_worktree" \
  999X-browser-fixture ralph/outside_fixture "$outside_run_dir/failure-summary.md"
if ralph_repair_context_is_resumable "$registered_repo" "$registered_context"; then
  fail "registered worktree outside .ralph/worktrees was accepted for repair"
fi

cat > "$fixture_dir/pass.log" <<'EOF'
Found 5 test(s).
Ran 5 tests in 1.234s
OK
EOF
cat > "$fixture_dir/fail.log" <<'EOF'
Found 5 test(s).
Ran 5 tests in 1.234s
FAILED (errors=5)
EOF
postgresql_acceptance_log_passes "$fixture_dir/pass.log" || fail "valid PostgreSQL evidence was rejected"
if postgresql_acceptance_log_passes "$fixture_dir/fail.log"; then
  fail "failed PostgreSQL evidence was accepted"
fi

declare -F postgresql_environment_probe >/dev/null \
  || fail "missing reusable PostgreSQL environment probe"
declare -F postgresql_test_database_name >/dev/null \
  || fail "missing isolated PostgreSQL test database naming helper"
declare -F postgresql_drop_test_database >/dev/null \
  || fail "missing forced PostgreSQL test database cleanup helper"
probe_worktree="$fixture_dir/probe-worktree"
probe_python="$fixture_dir/probe-python"
mkdir -p "$probe_worktree"
cat > "$probe_python" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ "$PWD" == "$EXPECTED_PROBE_WORKTREE" ]]
[[ "$DJANGO_SETTINGS_MODULE" == "sfpcl_credit.config.postgres_test_settings" ]]
probe_source="$(cat)"
grep -qF 'connection._nodb_cursor()' <<< "$probe_source"
cat <<'OUTPUT'
- Engine: django.db.backends.postgresql
- Database: sfpcl_credit
- Test database: test_sfpcl_credit
- Host: (local Unix socket)
- Port: 5432
- PostgreSQL maintenance database: postgres
- PostgreSQL server version: 14.20
OUTPUT
EOF
chmod +x "$probe_python"
export EXPECTED_PROBE_WORKTREE="$probe_worktree"
probe_output="$(postgresql_environment_probe "$probe_python" "$probe_worktree")" \
  || fail "PostgreSQL environment probe did not execute from the repository import root"
grep -qF -- '- PostgreSQL maintenance database: postgres' <<< "$probe_output" \
  || fail "PostgreSQL environment probe did not use the maintenance connection"
grep -qF -- '- PostgreSQL server version: 14.20' <<< "$probe_output" \
  || fail "PostgreSQL environment probe did not record the live server version"

first_test_database="$(postgresql_test_database_name '2026-07-11_082409_normal_run' 1)"
second_test_database="$(postgresql_test_database_name '2026-07-11_082409_normal_run' 2)"
[[ "$first_test_database" != "$second_test_database" ]] \
  || fail "PostgreSQL validation repetitions do not receive distinct databases"
[[ ${#first_test_database} -le 63 && "$first_test_database" == test_sfpcl_credit_* ]] \
  || fail "PostgreSQL test database name is unsafe or exceeds PostgreSQL's identifier limit"

cleanup_python="$fixture_dir/cleanup-python"
cat > "$cleanup_python" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ "$PWD" == "$EXPECTED_PROBE_WORKTREE" ]]
[[ "$DJANGO_SETTINGS_MODULE" == "sfpcl_credit.config.postgres_test_settings" ]]
[[ "$1" == "-" ]]
[[ "$2" == test_sfpcl_credit_* ]]
cleanup_source="$(cat)"
grep -qF 'DROP DATABASE IF EXISTS' <<< "$cleanup_source"
grep -qF 'WITH (FORCE)' <<< "$cleanup_source"
EOF
chmod +x "$cleanup_python"
postgresql_drop_test_database "$cleanup_python" "$probe_worktree" "$first_test_database" \
  || fail "PostgreSQL test database cleanup did not use the maintenance connection"

cat > "$fixture_dir/future-postgres-slice.md" <<'EOF'
## Status
Not Started

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Goal
Exercise a future PostgreSQL-sensitive slice name.
EOF
cat > "$fixture_dir/ordinary-slice.md" <<'EOF'
## Status
Not Started

## Runtime Capabilities
- `none`
EOF
cat > "$fixture_dir/future-localhost-slice.md" <<'EOF'
## Status
Not Started

## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/future-browser.e2e.spec.ts`
- Screenshot: `future-validation.png`
- Screenshot: `future-success.png`
EOF
cat > "$fixture_dir/future-combined-slice.md" <<'EOF'
## Status
Not Started

## Runtime Capabilities
- `postgresql-five-race-acceptance`
- `localhost-e2e-server`
EOF
cat > "$fixture_dir/unknown-capability.md" <<'EOF'
## Runtime Capabilities
- `unrestricted-network`
EOF
mkdir -p "$fixture_dir/browser-project/e2e"
touch "$fixture_dir/browser-project/e2e/future-browser.e2e.spec.ts"
cat > "$fixture_dir/unsafe-browser-slice.md" <<'EOF'
## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/../../scripts/escape.e2e.spec.ts`
EOF
cat > "$fixture_dir/missing-browser-contract-slice.md" <<'EOF'
## Runtime Capabilities
- `localhost-e2e-server`
EOF

[[ "$(ralph_codex_permission_profile_for_slice "$fixture_dir/future-postgres-slice.md")" == "ralph-postgres" ]] \
  || fail "future PostgreSQL slice did not select the scoped socket profile"
[[ "$(ralph_codex_permission_profile_for_slice "$fixture_dir/ordinary-slice.md")" == ":workspace" ]] \
  || fail "ordinary slice did not retain workspace permissions"
[[ "$(ralph_codex_permission_profile_for_slice "$fixture_dir/future-localhost-slice.md")" == "ralph-localhost" ]] \
  || fail "future localhost E2E slice did not select the scoped localhost profile"
[[ "$(ralph_codex_permission_profile_for_slice "$fixture_dir/future-combined-slice.md")" == "ralph-postgres-localhost" ]] \
  || fail "combined local runtime capabilities did not select the composed profile"
if ralph_validate_slice_capabilities "$fixture_dir/unknown-capability.md" >/dev/null 2>&1; then
  fail "unknown runtime capability did not fail closed"
fi
ralph_validate_trusted_browser_acceptance \
  "$fixture_dir/future-localhost-slice.md" "$fixture_dir/browser-project" \
  || fail "valid trusted browser acceptance contract was rejected"
[[ "$(ralph_trusted_e2e_specs "$fixture_dir/future-localhost-slice.md")" == "e2e/future-browser.e2e.spec.ts" ]] \
  || fail "trusted browser spec parser returned the wrong path"
[[ "$(ralph_trusted_e2e_screenshots "$fixture_dir/future-localhost-slice.md" | paste -sd ',' -)" == "future-validation.png,future-success.png" ]] \
  || fail "trusted browser screenshot parser returned the wrong filenames"
if ralph_validate_trusted_browser_acceptance "$fixture_dir/unsafe-browser-slice.md" "$fixture_dir/browser-project" >/dev/null 2>&1; then
  fail "unsafe trusted browser spec path did not fail closed"
fi
if ralph_validate_trusted_browser_acceptance "$fixture_dir/missing-browser-contract-slice.md" "$fixture_dir/browser-project" >/dev/null 2>&1; then
  fail "localhost E2E slice without a trusted browser contract did not fail closed"
fi

browser_runtime_project="$fixture_dir/browser-runtime-project"
browser_runtime_bin="$fixture_dir/browser-runtime-bin"
browser_runtime_log="$fixture_dir/browser-runtime.log"
browser_runtime_state="$fixture_dir/browser-runtime.state"
mkdir -p "$browser_runtime_project" "$browser_runtime_bin"
cat > "$browser_runtime_bin/npm" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ "$*" == "run e2e:probe" ]]
echo probe >> "$BROWSER_RUNTIME_INVOCATIONS"
[[ -f "$BROWSER_RUNTIME_STATE" ]]
EOF
cat > "$browser_runtime_bin/npx" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
[[ "$*" == "playwright install chromium" ]]
echo install >> "$BROWSER_RUNTIME_INVOCATIONS"
touch "$BROWSER_RUNTIME_STATE"
EOF
chmod +x "$browser_runtime_bin/npm" "$browser_runtime_bin/npx"
PATH="$browser_runtime_bin:$PATH" \
  BROWSER_RUNTIME_INVOCATIONS="$browser_runtime_log" \
  BROWSER_RUNTIME_STATE="$browser_runtime_state" \
  ralph_ensure_browser_runtime \
    "$browser_runtime_project" \
    "$fixture_dir/browser-runtime-evidence.log" \
    "$repo_root/scripts/lib/ralph-run-with-timeout.py" \
    30 \
  || fail "browser infrastructure recovery did not retry a failed launch probe"
[[ "$(paste -sd ',' "$browser_runtime_log")" == "probe,install,probe" ]] \
  || fail "browser recovery did not run probe-install-probe exactly once"

# A failed required browser run must reach repair evidence quickly. It must not
# spend another full backend-test/coverage cycle on a candidate that is already
# unmergeable; the repair rerun restores every backend gate after browser green.
browser_failfast_repo="$fixture_dir/browser-failfast-repo"
browser_failfast_run="browser-failfast-run"
browser_failfast_run_dir="$browser_failfast_repo/.ralph/runs/$browser_failfast_run"
browser_failfast_bin="$fixture_dir/browser-failfast-bin"
browser_invocations="$fixture_dir/browser-invocations.log"
backend_invocation="$fixture_dir/backend-invocation.log"
mkdir -p \
  "$browser_failfast_repo/.ralph" \
  "$browser_failfast_repo/docs/slices" \
  "$browser_failfast_repo/frontend/e2e" \
  "$browser_failfast_repo/backend" \
  "$browser_failfast_run_dir" \
  "$browser_failfast_bin"
cat > "$browser_failfast_repo/.ralph/config.yaml" <<'EOF'
project_dir: frontend
backend_dir: backend
build: false
install: false
typecheck: false
lint: false
unit_tests: false
backend_check: true
backend_tests: true
backend_migrations: true
backend_coverage: true
max_changed_files: 30
max_lines_changed: 2000
EOF
printf '%s\n' '{"completed_slices": []}' > "$browser_failfast_repo/.ralph/state.json"
printf '%s\n' '{}' > "$browser_failfast_repo/.ralph/permissions.json"
cat > "$browser_failfast_repo/docs/slices/999Y-browser-failfast.md" <<'EOF'
# Slice 999Y: Browser fail-fast fixture

## Status
Not Started

## Depends On
- None

## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/failfast.e2e.spec.ts`
- Screenshot: `failfast.png`
EOF
touch "$browser_failfast_repo/frontend/e2e/failfast.e2e.spec.ts"
cat > "$browser_failfast_repo/frontend/e2e/README.md" <<'EOF'
Resolve the shared environment with `git rev-parse --git-common-dir`.
EOF
cat > "$browser_failfast_repo/frontend/playwright.config.ts" <<'EOF'
export default { use: { timezoneId: 'Asia/Kolkata' } }
EOF
cat > "$browser_failfast_bin/npm" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo browser >> "$BROWSER_INVOCATIONS"
exit 1
EOF
chmod +x "$browser_failfast_bin/npm"
cat > "$browser_failfast_repo/backend/manage.py" <<'EOF'
from pathlib import Path
import os

Path(os.environ["BACKEND_INVOCATION"]).write_text("backend gate ran\n")
EOF
for artifact in prompt.md changed-files.txt final-summary.md; do
  printf 'fixture\n' > "$browser_failfast_run_dir/$artifact"
done
printf '1. Exercise browser fail-fast.\n' > "$browser_failfast_run_dir/execution-plan.md"
printf 'Low risk fixture.\n' > "$browser_failfast_run_dir/risk-assessment.md"
cat > "$browser_failfast_run_dir/review-packet.md" <<'EOF'
## Result
Ready for independent validation
EOF
git init -q "$browser_failfast_repo"
git -C "$browser_failfast_repo" config user.name "Ralph Regression"
git -C "$browser_failfast_repo" config user.email "ralph-regression@example.invalid"
git -C "$browser_failfast_repo" add .
git -C "$browser_failfast_repo" commit -qm fixture
# Simulate a real agent candidate so the pre-coverage no-op blocker passes and
# this fixture reaches the trusted-browser fail-fast lane it is testing.
printf '// candidate change\n' >> "$browser_failfast_repo/frontend/e2e/failfast.e2e.spec.ts"
set +e
PATH="$browser_failfast_bin:$PATH" \
  BROWSER_INVOCATIONS="$browser_invocations" \
  BACKEND_INVOCATION="$backend_invocation" \
  scripts/ralph-validate.sh \
    --run-id "$browser_failfast_run" \
    --worktree "$browser_failfast_repo" \
    --mode normal_run \
    --slice 999Y-browser-failfast \
    > "$fixture_dir/browser-failfast.stdout" \
    2> "$fixture_dir/browser-failfast.stderr"
browser_failfast_rc=$?
set -e
[[ "$browser_failfast_rc" == "1" ]] \
  || fail "failed trusted browser fixture returned $browser_failfast_rc instead of validation failure"
[[ "$(wc -l < "$browser_invocations" | xargs)" == "1" ]] \
  || fail "validator did not stop trusted browser repetitions after the first failure"
[[ ! -e "$backend_invocation" ]] \
  || fail "backend gates ran after required trusted browser acceptance failed"
for backend_result in backend-check backend-test backend-migrations backend-coverage; do
  grep -qF 'Skipped: required trusted browser acceptance failed; deferred until repair' \
    "$browser_failfast_run_dir/${backend_result}-results.md" \
    || fail "$backend_result did not record browser fail-fast deferral"
done
grep -qF 'e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.' \
  "$browser_failfast_run_dir/failure-summary.md" \
  || fail "browser fail-fast did not leave repair-readable failure evidence"

# A cheap all-gates-disabled fixture must still reach a clean validator exit;
# this catches moved evidence variables becoming unbound after consolidation.
validator_success_repo="$fixture_dir/validator-success-repo"
validator_success_run="validator-success-run"
validator_success_run_dir="$validator_success_repo/.ralph/runs/$validator_success_run"
mkdir -p "$validator_success_repo/.ralph" "$validator_success_repo/docs/slices" \
  "$validator_success_repo/frontend" "$validator_success_run_dir"
cat > "$validator_success_repo/.ralph/config.yaml" <<'EOF'
project_dir: frontend
backend_dir: backend
build: false
install: false
typecheck: false
lint: false
unit_tests: false
backend_check: false
backend_tests: false
backend_migrations: false
backend_coverage: false
max_changed_files: 30
max_lines_changed: 2000
EOF
printf '%s\n' '{"completed_slices": []}' > "$validator_success_repo/.ralph/state.json"
printf '%s\n' '{}' > "$validator_success_repo/.ralph/permissions.json"
cat > "$validator_success_repo/docs/slices/999Z-validator-success.md" <<'EOF'
# Slice 999Z: Validator success fixture

## Status
Not Started

## Runtime Capabilities
- `none`

## Depends On
- None
EOF
for artifact in prompt.md changed-files.txt final-summary.md; do
  printf 'fixture\n' > "$validator_success_run_dir/$artifact"
done
printf '1. Exercise validator success.\n' > "$validator_success_run_dir/execution-plan.md"
printf 'Low risk fixture.\n' > "$validator_success_run_dir/risk-assessment.md"
cat > "$validator_success_run_dir/review-packet.md" <<'EOF'
## Result
Ready for independent validation
EOF
git init -q "$validator_success_repo"
git -C "$validator_success_repo" config user.name "Ralph Regression"
git -C "$validator_success_repo" config user.email "ralph-regression@example.invalid"
git -C "$validator_success_repo" add .
git -C "$validator_success_repo" commit -qm fixture
printf 'candidate\n' > "$validator_success_repo/frontend/change.txt"
scripts/ralph-validate.sh \
  --run-id "$validator_success_run" \
  --worktree "$validator_success_repo" \
  --mode normal_run \
  --slice 999Z-validator-success \
  > "$fixture_dir/validator-success.stdout" \
  2> "$fixture_dir/validator-success.stderr" \
  || fail "all-green validator fixture did not complete"
grep -qF 'Validation passed.' "$validator_success_run_dir/ralph-artifact-validation.md" \
  || fail "all-green validator did not finalize artifact evidence"
grep -qF 'PASS: candidate content remained frozen throughout validation.' \
  "$validator_success_run_dir/candidate-hash-results.md" \
  || fail "all-green validator did not verify the frozen candidate"

state_guard_run="orchestrator-state-guard-run"
state_guard_run_dir="$validator_success_repo/.ralph/runs/$state_guard_run"
mkdir -p "$state_guard_run_dir"
for artifact in prompt.md changed-files.txt final-summary.md; do
  printf 'fixture\n' > "$state_guard_run_dir/$artifact"
done
printf '1. Reject agent-owned state changes.\n' > "$state_guard_run_dir/execution-plan.md"
printf 'Low risk fixture.\n' > "$state_guard_run_dir/risk-assessment.md"
printf '## Result\nReady for independent validation\n' > "$state_guard_run_dir/review-packet.md"
printf '%s\n' '{"completed_slices": ["agent-forged-completion"]}' \
  > "$validator_success_repo/.ralph/state.json"
set +e
scripts/ralph-validate.sh \
  --run-id "$state_guard_run" \
  --worktree "$validator_success_repo" \
  --mode normal_run \
  --slice 999Z-validator-success \
  > "$fixture_dir/state-guard.stdout" \
  2> "$fixture_dir/state-guard.stderr"
state_guard_rc=$?
set -e
[[ "$state_guard_rc" == "1" ]] \
  || fail "agent-authored state returned $state_guard_rc instead of validation failure"
grep -qF 'FAIL: agent modified orchestrator-owned .ralph/state.json.' \
  "$state_guard_run_dir/orchestrator-ownership-check.md" \
  || fail "agent-authored state did not leave ownership evidence"
git -C "$validator_success_repo" show HEAD:.ralph/state.json \
  > "$validator_success_repo/.ralph/state.json"

# A configured backend gate with no manage.py is an unsafe repository/config
# condition. It must fail instead of being mislabeled as a no-backend skip.
missing_backend_repo="$fixture_dir/missing-backend-repo"
missing_backend_run="missing-backend-run"
missing_backend_run_dir="$missing_backend_repo/.ralph/runs/$missing_backend_run"
mkdir -p "$missing_backend_repo/.ralph" "$missing_backend_repo/docs/slices" \
  "$missing_backend_repo/frontend" "$missing_backend_run_dir"
cat > "$missing_backend_repo/.ralph/config.yaml" <<'EOF'
project_dir: frontend
backend_dir: missing-backend
build: false
install: false
typecheck: false
lint: false
unit_tests: false
backend_check: true
backend_tests: false
backend_migrations: false
backend_coverage: false
max_changed_files: 30
max_lines_changed: 2000
EOF
printf '%s\n' '{"completed_slices": []}' > "$missing_backend_repo/.ralph/state.json"
printf '%s\n' '{}' > "$missing_backend_repo/.ralph/permissions.json"
cat > "$missing_backend_repo/docs/slices/999X-missing-backend.md" <<'EOF'
# Slice 999X: Missing backend fixture

## Status
Not Started

## Runtime Capabilities
- `none`

## Depends On
- None

## Risk Level
Medium
EOF
for artifact in prompt.md changed-files.txt final-summary.md; do
  printf 'fixture\n' > "$missing_backend_run_dir/$artifact"
done
printf '1. Exercise missing backend failure.\n' \
  > "$missing_backend_run_dir/execution-plan.md"
printf 'Medium risk fixture.\n' > "$missing_backend_run_dir/risk-assessment.md"
cat > "$missing_backend_run_dir/review-packet.md" <<'EOF'
## Result
Ready for independent validation
EOF
git init -q "$missing_backend_repo"
git -C "$missing_backend_repo" config user.name "Ralph Regression"
git -C "$missing_backend_repo" config user.email "ralph-regression@example.invalid"
git -C "$missing_backend_repo" add .
git -C "$missing_backend_repo" commit -qm fixture
printf 'candidate\n' > "$missing_backend_repo/frontend/change.txt"
set +e
scripts/ralph-validate.sh \
  --run-id "$missing_backend_run" \
  --worktree "$missing_backend_repo" \
  --mode normal_run \
  --slice 999X-missing-backend \
  > "$fixture_dir/missing-backend.stdout" \
  2> "$fixture_dir/missing-backend.stderr"
missing_backend_rc=$?
set -e
[[ "$missing_backend_rc" == "1" ]] \
  || fail "configured missing backend returned $missing_backend_rc instead of failure"
grep -qF 'FAIL: configured backend is missing at missing-backend/manage.py' \
  "$missing_backend_run_dir/backend-validation-lane-results.md" \
  || fail "missing backend did not leave fail-closed lane evidence"

oversized_run="oversized-candidate-run"
oversized_run_dir="$validator_success_repo/.ralph/runs/$oversized_run"
mkdir -p "$oversized_run_dir"
for artifact in prompt.md changed-files.txt final-summary.md; do
  printf 'fixture\n' > "$oversized_run_dir/$artifact"
done
printf '1. Exercise oversized candidate classification.\n' > "$oversized_run_dir/execution-plan.md"
printf 'Low risk fixture.\n' > "$oversized_run_dir/risk-assessment.md"
cat > "$oversized_run_dir/review-packet.md" <<'EOF'
## Result
Ready for independent validation
EOF
awk 'BEGIN { for (i = 1; i <= 2001; i++) print "oversized candidate line " i }' \
  > "$validator_success_repo/frontend/oversized.txt"
set +e
scripts/ralph-validate.sh \
  --run-id "$oversized_run" \
  --worktree "$validator_success_repo" \
  --mode normal_run \
  --slice 999Z-validator-success \
  > "$fixture_dir/oversized-candidate.stdout" \
  2> "$fixture_dir/oversized-candidate.stderr"
oversized_rc=$?
set -e
[[ "$oversized_rc" == "1" ]] \
  || fail "oversized candidate returned $oversized_rc instead of validation failure"
python3 - "$oversized_run_dir/oversized-slice-request.json" <<'PY'
import json
import sys
from pathlib import Path

request = json.loads(Path(sys.argv[1]).read_text())
expected = {
    "version": 1,
    "reason": "diff_limit_exceeded",
    "run_id": "oversized-candidate-run",
    "slice_id": "999Z-validator-success",
    "max_lines": 2000,
}
for key, value in expected.items():
    if request.get(key) != value:
        raise SystemExit(f"FAIL: oversized marker {key}={request.get(key)!r}, expected {value!r}")
if request.get("total_lines", 0) <= request["max_lines"]:
    raise SystemExit("FAIL: oversized marker did not record a genuine limit breach")
PY

# Owner-maintenance performance and reliability contracts. These checks keep
# the exact quality gates while ensuring doomed candidates fail before costly
# suites, candidate contents remain frozen during validation, and the agent's
# complete log is stored once rather than copied into every loop transcript.
if rg -q "find docs/slices .*grep -q" scripts/ralph-preflight.sh; then
  fail "preflight slice discovery still uses the pipefail/SIGPIPE-prone find-to-grep pipeline"
fi
rg -q 'ralph_run_fast_candidate_checks' scripts/ralph-validate.sh \
  || fail "validator does not run cheap candidate blockers before expensive gates"
python3 - <<'PY'
from pathlib import Path

source = Path("scripts/ralph-validate.sh").read_text()
cheap = source.index("ralph_run_fast_candidate_checks")
frontend = source.index('run_gate build "npm run build"')
postgres = source.index("run_postgresql_acceptance_once 1")
backend = source.index("run_backend_gate backend-coverage")
if not cheap < min(frontend, postgres, backend):
    raise SystemExit("FAIL: cheap candidate checks do not precede every expensive validation lane")
PY
for cheap_contract in 'Slice Status Transition Check' 'No-Op Check Results' 'state.json is valid' 'config.yaml is parseable'; do
  rg -q "$cheap_contract" scripts/lib/ralph-fast-candidate-checks.sh \
    || fail "pre-coverage validation omits cheap contract: $cheap_contract"
done
if rg -q '^# Protected paths:|^# No-op check:|^# Artifact quality:' scripts/ralph-validate.sh; then
  fail "validator duplicates authoritative cheap-check implementations after expensive gates"
fi
rg -q 'Duration milliseconds:' scripts/ralph-validate.sh \
  || fail "validation gate results do not record monotonic duration"
rg -q 'ralph_candidate_hash' scripts/ralph-validate.sh \
  || fail "validator does not verify a frozen candidate hash"

candidate_hash_helper="scripts/lib/ralph-candidate-hash.py"
[[ -x "$candidate_hash_helper" ]] || fail "missing executable candidate hash helper"
candidate_repo="$fixture_dir/candidate-hash-repo"
git init -q "$candidate_repo"
git -C "$candidate_repo" config user.name "Ralph Regression"
git -C "$candidate_repo" config user.email "ralph-regression@example.invalid"
printf 'tracked\n' > "$candidate_repo/tracked.txt"
git -C "$candidate_repo" add tracked.txt
git -C "$candidate_repo" commit -qm fixture
first_candidate_hash="$(python3 "$candidate_hash_helper" "$candidate_repo")"
mkdir -p "$candidate_repo/.ralph/runs/example"
printf 'validation evidence\n' > "$candidate_repo/.ralph/runs/example/result.md"
[[ "$(python3 "$candidate_hash_helper" "$candidate_repo")" == "$first_candidate_hash" ]] \
  || fail "candidate hash changed for Ralph evidence only"
printf 'changed\n' >> "$candidate_repo/tracked.txt"
second_candidate_hash="$(python3 "$candidate_hash_helper" "$candidate_repo")"
[[ "$second_candidate_hash" != "$first_candidate_hash" ]] \
  || fail "candidate hash ignored a tracked product change"
printf 'new product file\n' > "$candidate_repo/new.txt"
third_candidate_hash="$(python3 "$candidate_hash_helper" "$candidate_repo")"
[[ "$third_candidate_hash" != "$second_candidate_hash" ]] \
  || fail "candidate hash ignored an untracked product change"
git -C "$candidate_repo" add tracked.txt new.txt
git -C "$candidate_repo" commit -qm candidate
committed_candidate_hash="$(python3 "$candidate_hash_helper" "$candidate_repo" --target HEAD)"
[[ "$committed_candidate_hash" == "$third_candidate_hash" ]] \
  || fail "committed candidate hash does not match the validated working-tree candidate"
rg -q 'PASS: committed product candidate exactly matches the validated candidate' scripts/ralph-run.sh \
  || fail "orchestrator does not verify the actual committed candidate before merge"

if rg -q 'tail -n \+1 -f "\$log"' scripts/agent-adapters/codex.sh scripts/agent-adapters/claude.sh; then
  fail "agent adapters still duplicate the complete agent log into the outer loop log"
fi
rg -q 'Full agent log:' scripts/agent-adapters/codex.sh \
  || fail "Codex adapter does not identify the retained authoritative full log"

# Full agent transcripts are operator-local, bounded-retention diagnostics.
# Only compact excerpts and cryptographic hashes belong in committed run evidence.
agent_log_helper="scripts/lib/ralph-agent-log.sh"
[[ -f "$agent_log_helper" ]] || fail "missing bounded external agent-log helper"
# shellcheck source=../lib/ralph-agent-log.sh
source "$agent_log_helper"
agent_log_repo="$fixture_dir/agent-log-repo"
git init -q "$agent_log_repo"
git -C "$agent_log_repo" config user.name "Ralph Regression"
git -C "$agent_log_repo" config user.email "ralph-regression@example.invalid"
printf 'fixture\n' > "$agent_log_repo/tracked.txt"
git -C "$agent_log_repo" add tracked.txt
git -C "$agent_log_repo" commit -qm fixture
if RALPH_RAW_AGENT_LOG_ROOT="$fixture_dir/untrusted-agent-log-root" \
    ralph_prepare_agent_log "$agent_log_repo" unsafe-run codex >/dev/null 2>&1; then
  fail "agent-log retention accepted an external deletion root without explicit test/operator opt-in"
fi
if RALPH_RAW_AGENT_LOG_ROOT="$fixture_dir/raw-agent-logs" \
    RALPH_ALLOW_EXTERNAL_AGENT_LOG_ROOT=true \
    ralph_prepare_agent_log "$agent_log_repo" ../unsafe-run codex >/dev/null 2>&1; then
  fail "agent-log retention accepted a path-traversing run id"
fi
RALPH_RAW_AGENT_LOG_ROOT="$fixture_dir/raw-agent-logs" \
  RALPH_ALLOW_EXTERNAL_AGENT_LOG_ROOT=true \
  ralph_prepare_agent_log "$agent_log_repo" fixture-run codex
printf 'session id: 11111111-1111-1111-1111-111111111111\nfirst line\nsecond line\n' > "$RALPH_AGENT_RAW_LOG"
agent_summary="$agent_log_repo/codex-log-summary.md"
ralph_write_agent_log_summary "$RALPH_AGENT_RAW_LOG" "$agent_summary" codex 0
grep -q '^SHA-256: [0-9a-f]\{64\}$' "$agent_summary" \
  || fail "compact agent-log summary omitted its SHA-256 digest"
grep -qF 'second line' "$agent_summary" \
  || fail "compact agent-log summary omitted the bounded final excerpt"
grep -qF 'Session ID: 11111111-1111-1111-1111-111111111111' "$agent_summary" \
  || fail "compact agent-log summary omitted context-tripwire session identity"
[[ "$RALPH_AGENT_RAW_LOG" != "$agent_log_repo"/* ]] \
  || fail "full agent transcript is still stored inside the commit candidate"
rm -rf "$fixture_dir/raw-agent-logs/fixture-run"
summary_run_dir="$agent_log_repo/.ralph/runs/fixture-run"
mkdir -p "$summary_run_dir/evidence/terminal-logs"
cp "$agent_summary" "$summary_run_dir/evidence/terminal-logs/codex-summary.md"
python3 - "$summary_run_dir" "$fixture_dir/raw-agent-logs" <<'PY'
import importlib.util
import sys
from pathlib import Path

script = Path("scripts/ralph-context-tripwire.py")
spec = importlib.util.spec_from_file_location("ralph_context_tripwire", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
actual = module.session_id_of(sys.argv[1], sys.argv[2])
expected = "11111111-1111-1111-1111-111111111111"
if actual != expected:
    raise SystemExit(f"compact-summary session lookup returned {actual!r}")
PY
mkdir -p "$fixture_dir/raw-agent-logs/older-run" "$fixture_dir/raw-agent-logs/newer-run"
python3 - "$fixture_dir/raw-agent-logs/older-run" "$fixture_dir/raw-agent-logs/newer-run" <<'PY'
import os
import sys
import time

now = time.time()
os.utime(sys.argv[1], (now - 200, now - 200))
os.utime(sys.argv[2], (now - 100, now - 100))
PY
RALPH_RAW_AGENT_LOG_ROOT="$fixture_dir/raw-agent-logs" \
RALPH_ALLOW_EXTERNAL_AGENT_LOG_ROOT=true \
RALPH_RAW_AGENT_LOG_RETENTION_DAYS=365 \
RALPH_RAW_AGENT_LOG_RETENTION_COUNT=2 \
  ralph_prepare_agent_log "$agent_log_repo" current-run codex
[[ ! -d "$fixture_dir/raw-agent-logs/older-run" ]] \
  || fail "bounded agent-log retention did not prune the oldest run"
[[ -d "$fixture_dir/raw-agent-logs/current-run" && -d "$fixture_dir/raw-agent-logs/newer-run" ]] \
  || fail "bounded agent-log retention removed one of the newest runs"
for adapter in scripts/agent-adapters/codex.sh scripts/agent-adapters/claude.sh; do
  rg -q 'ralph_prepare_agent_log' "$adapter" \
    || fail "$(basename "$adapter") does not route full logs outside the commit candidate"
  if rg -q 'RUN_DIR/evidence/terminal-logs/(codex|claude)\.log' "$adapter"; then
    fail "$(basename "$adapter") still stores a full transcript in committed run evidence"
  fi
done
rg -q 'codex-summary.md' scripts/ralph-context-tripwire.py \
  || fail "context trip-wire cannot read compact agent-log summaries"
rg -q 'ralph-agent-logs' scripts/ralph-context-tripwire.py \
  || fail "context trip-wire cannot read retained external raw logs"

# Ordinary architecture reviews are documentation/queue inspections. They
# may use the queue-only validation lane only when every candidate path is
# documentation or Ralph bookkeeping; any product path must fail closed.
architecture_scope_helper="scripts/lib/ralph-architecture-review.sh"
[[ -f "$architecture_scope_helper" ]] \
  || fail "missing architecture-review change-scope helper"
closure_preflight="scripts/ralph-validate-review-closure.sh"
[[ -x "$closure_preflight" ]] \
  || fail "missing executable agent-side semantic-closure preflight"
# shellcheck source=../lib/ralph-slice-selection.sh
source scripts/lib/ralph-slice-selection.sh
# shellcheck source=../lib/ralph-architecture-review.sh
source "$architecture_scope_helper"
declare -F ralph_validate_architecture_review_manifest >/dev/null \
  || fail "missing structured architecture-review finding manifest validator"
declare -F ralph_validate_review_finding_closure >/dev/null \
  || fail "missing corrective-slice closure evidence validator"
metrics_packet="$fixture_dir/architecture-review-packet.md"
cat > "$metrics_packet" <<'EOF'
# Review Packet

## Standards
- New High: a retained finding mentioned in narrative text is not a metric.

## Convergence Metrics
- Findings closed: 3
- New Critical: 0
- New High: 0
- New Medium: 2
- New Low: 1
- Corrective slices added: 1
EOF
[[ "$(ralph_architecture_review_metrics "$metrics_packet")" == $'3\t0\t0\t2\t1\t1' ]] \
  || fail "architecture-review convergence metrics did not parse deterministically"
sed 's/- New High: 0/- New High: unknown/' "$metrics_packet" > "$metrics_packet.invalid"
if ralph_architecture_review_metrics "$metrics_packet.invalid" >/dev/null 2>&1; then
  fail "architecture-review convergence metrics accepted a non-numeric severity count"
fi

semantic_review_repo="$fixture_dir/semantic-review-repo"
mkdir -p "$semantic_review_repo/docs/slices" \
  "$semantic_review_repo/docs/working" \
  "$semantic_review_repo/.ralph/runs/review-run/evidence/review-probes"
git init -q "$semantic_review_repo"
git -C "$semantic_review_repo" config user.name "Ralph Regression"
git -C "$semantic_review_repo" config user.email "ralph-regression@example.invalid"
printf '# Review findings\n\n' > "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md"
git -C "$semantic_review_repo" add .
git -C "$semantic_review_repo" commit -qm fixture
printf 'Finding ID: AR-010-OWNER-001\nRoot ID: ROOT-010-OWNER-DECISION\nFAIL: public assertion expected 0 rows, observed 1\n' \
  > "$semantic_review_repo/.ralph/runs/review-run/evidence/review-probes/owner-boundary.txt"
cat >> "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md" <<'EOF'
## AR-010-OWNER-001 — collection owner disagreement

Root: ROOT-010-OWNER-DECISION
EOF
cat > "$semantic_review_repo/docs/slices/010A1-owner-correction.md" <<'EOF'
# Slice 010A1

## Status
Not Started

## Depends On
- 010A

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-OWNER-001 | ROOT-010-OWNER-DECISION | .ralph/runs/review-run/evidence/review-probes/owner-boundary.txt | AC-1, AC-2 |

## Acceptance Criteria
- [AC-1] Canonical owner rejection removes the account from collection truth.
- [AC-2] The permanent public regression proves count, row, and detail parity.
EOF
semantic_packet="$semantic_review_repo/.ralph/runs/review-run/review-packet.md"
cat > "$semantic_packet" <<'EOF'
# Review Packet

## Convergence Metrics
- Findings closed: 0
- New Critical: 0
- New High: 1
- New Medium: 0
- New Low: 0
- Corrective slices added: 1

## Finding Closure Manifest
| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-OWNER-001 | ROOT-010-OWNER-DECISION | High | New | .ralph/runs/review-run/evidence/review-probes/owner-boundary.txt | 010A1 | - |
EOF
ralph_validate_architecture_review_manifest \
  "$semantic_packet" "$semantic_review_repo" 0 0 1 0 0 \
  || fail "valid structured architecture-review finding manifest was rejected"
cp "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md" \
  "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md.without-hidden"
cat >> "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md" <<'EOF'

## AR-010-HIDDEN-001 — unreported high finding

Root: ROOT-010-HIDDEN-OWNER
EOF
if ralph_validate_architecture_review_manifest \
    "$semantic_packet" "$semantic_review_repo" 0 0 1 0 0 \
    >/dev/null 2>&1; then
  fail "architecture review hid a changed findings-ledger entry outside its manifest"
fi
mv "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md.without-hidden" \
  "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md"
sed 's/- New High: 1/- New High: 0/' "$semantic_packet" \
  > "$semantic_packet.metrics-mismatch"
if ralph_validate_architecture_review_manifest \
    "$semantic_packet.metrics-mismatch" "$semantic_review_repo" 0 0 0 0 0 \
    >/dev/null 2>&1; then
  fail "finding manifest escaped convergence-metric reconciliation"
fi
sed 's#review-probes/owner-boundary.txt#review-probes/missing.txt#' "$semantic_packet" \
  > "$semantic_packet.missing-reproducer"
if ralph_validate_architecture_review_manifest \
    "$semantic_packet.missing-reproducer" "$semantic_review_repo" 0 0 1 0 0 \
    >/dev/null 2>&1; then
  fail "finding manifest accepted a missing public reproducer"
fi
mkdir -p "$semantic_review_repo/.ralph/runs/older-review/evidence/review-probes"
cp "$semantic_review_repo/.ralph/runs/review-run/evidence/review-probes/owner-boundary.txt" \
  "$semantic_review_repo/.ralph/runs/older-review/evidence/review-probes/owner-boundary.txt"
sed 's#\.ralph/runs/review-run/evidence/#.ralph/runs/older-review/evidence/#g' \
  "$semantic_packet" > "$semantic_packet.stale-evidence"
if ralph_validate_architecture_review_manifest \
    "$semantic_packet.stale-evidence" "$semantic_review_repo" 0 0 1 0 0 \
    >/dev/null 2>&1; then
  fail "finding manifest accepted evidence from a different architecture-review run"
fi
cp "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md.with-contract"
python3 - "$semantic_review_repo/docs/slices/010A1-owner-correction.md" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.write_text(path.read_text().split("## Review Finding Closure", 1)[0])
PY
if ralph_validate_architecture_review_manifest \
    "$semantic_packet" "$semantic_review_repo" 0 0 1 0 0 \
    >/dev/null 2>&1; then
  fail "finding manifest accepted a corrective slice without an exact closure contract"
fi
mv "$semantic_review_repo/docs/slices/010A1-owner-correction.md.with-contract" \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md"
cp "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md.with-criteria"
sed 's/\[AC-2\]/[AC-3]/' \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md.with-criteria" \
  > "$semantic_review_repo/docs/slices/010A1-owner-correction.md"
if ralph_validate_architecture_review_manifest \
    "$semantic_packet" "$semantic_review_repo" 0 0 1 0 0 \
    >/dev/null 2>&1; then
  fail "finding manifest accepted closure ids that omit a labelled acceptance criterion"
fi
mv "$semantic_review_repo/docs/slices/010A1-owner-correction.md.with-criteria" \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md"
git -C "$semantic_review_repo" add \
  docs/working/REVIEW_FINDINGS.md \
  docs/slices/010A1-owner-correction.md \
  .ralph/runs/review-run/evidence/review-probes/owner-boundary.txt
git -C "$semantic_review_repo" commit -qm "admit semantic corrective fixture"

cp "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md" \
  "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md.before-relabel"
cat >> "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md" <<'EOF'

## AR-010-OWNER-002 — relabelled collection owner disagreement

Root: ROOT-010-OWNER-DECISION
EOF
sed 's/AR-010-OWNER-001/AR-010-OWNER-002/g; s/Slice 010A1/Slice 010A2/' \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
  > "$semantic_review_repo/docs/slices/010A2-owner-correction.md"
printf 'Finding ID: AR-010-OWNER-002\nRoot ID: ROOT-010-OWNER-DECISION\nFAIL: recurring public owner mismatch\n' \
  > "$semantic_review_repo/.ralph/runs/review-run/evidence/review-probes/root-relabel.txt"
sed 's/AR-010-OWNER-001/AR-010-OWNER-002/g; s/010A1/010A2/g; s#owner-boundary.txt#root-relabel.txt#g' \
  "$semantic_packet" > "$semantic_packet.root-relabel"
if ralph_validate_architecture_review_manifest \
    "$semantic_packet.root-relabel" "$semantic_review_repo" 0 0 1 0 0 \
    >/dev/null 2>&1; then
  fail "architecture review relabelled an existing root as a New finding"
fi
mv "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md.before-relabel" \
  "$semantic_review_repo/docs/working/REVIEW_FINDINGS.md"
rm "$semantic_review_repo/docs/slices/010A2-owner-correction.md" \
  "$semantic_review_repo/.ralph/runs/review-run/evidence/review-probes/root-relabel.txt"

closure_run="$semantic_review_repo/.ralph/runs/corrective-run"
mkdir -p "$closure_run/evidence/terminal-logs" \
  "$semantic_review_repo/backend/tests"
test_spec='backend/tests/test_owner_boundary.py::test_failed_owner_boundary_is_hidden'
printf 'def test_failed_owner_boundary_is_hidden():\n    canonical_owner = None\n    response = {"total_count": 0, "rows": [], "detail_status": 404}\n    assert canonical_owner is None\n    assert response == {"total_count": 0, "rows": [], "detail_status": 404}\n' \
  > "$semantic_review_repo/backend/tests/test_owner_boundary.py"
printf 'Test: %s\nFAILED: expected zero rows\nExit code: 1\n' "$test_spec" \
  > "$closure_run/evidence/terminal-logs/owner-red.log"
printf 'Test: %s\n1 passed\nExit code: 0\n' "$test_spec" \
  > "$closure_run/evidence/terminal-logs/owner-green.log"
printf 'Test: %s\n2 passed\nExit code: 0\n' "$test_spec" \
  > "$closure_run/evidence/terminal-logs/owner-acceptance.log"
cat > "$closure_run/review-closure-evidence.md" <<'EOF'
# Review Closure Evidence

## Finding Evidence
| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-OWNER-001 | ROOT-010-OWNER-DECISION | backend/tests/test_owner_boundary.py::test_failed_owner_boundary_is_hidden | evidence/terminal-logs/owner-red.log | evidence/terminal-logs/owner-green.log |

## Acceptance Evidence
| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-1 | backend/tests/test_owner_boundary.py::test_failed_owner_boundary_is_hidden | evidence/terminal-logs/owner-acceptance.log |
| AC-2 | backend/tests/test_owner_boundary.py::test_failed_owner_boundary_is_hidden | evidence/terminal-logs/owner-acceptance.log |
EOF
ralph_validate_review_finding_closure \
  "$semantic_review_repo" \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
  "$closure_run" \
  || fail "valid corrective-slice semantic closure evidence was rejected"
"$repo_root/$closure_preflight" \
  --worktree "$semantic_review_repo" \
  --slice "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
  --run-dir "$closure_run" \
  || fail "agent-side semantic-closure preflight rejected valid evidence"

# Human commentary after a blank line is outside the Markdown table, and an
# exact Django test label is as executable as a path::selector. Both patterns
# occurred in real corrective runs and must pass the cheap agent-side validator
# instead of consuming one or more full Ralph repair turns.
cp "$closure_run/review-closure-evidence.md" \
  "$closure_run/review-closure-evidence.md.canonical"
django_test_spec='backend.tests.test_owner_boundary.test_failed_owner_boundary_is_hidden'
sed "s#${test_spec}#${django_test_spec}#g" \
  "$closure_run/review-closure-evidence.md.canonical" \
  > "$closure_run/review-closure-evidence.md"
cat >> "$closure_run/review-closure-evidence.md" <<'EOF'

Additional human-readable acceptance context is retained above the raw logs.
EOF
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed "s#${test_spec}#${django_test_spec}#g" \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.django"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.django" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
ralph_validate_review_finding_closure \
  "$semantic_review_repo" \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
  "$closure_run" \
  || fail "valid prose-separated Django closure evidence triggered a repair"
cp "$closure_run/review-closure-evidence.md" \
  "$closure_run/review-closure-evidence.md.exact-django"
dotted_module_only='backend.tests.test_owner_boundary'
sed "s#${django_test_spec}#${dotted_module_only}#g" \
  "$closure_run/review-closure-evidence.md.exact-django" \
  > "$closure_run/review-closure-evidence.md"
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed "s#${django_test_spec}#${dotted_module_only}#g" \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.module-only"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.module-only" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
if ralph_validate_review_finding_closure \
    "$semantic_review_repo" \
    "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
    "$closure_run" >/dev/null 2>&1; then
  fail "semantic closure accepted a Django module without an exact test selector"
fi
mv "$closure_run/review-closure-evidence.md.exact-django" \
  "$closure_run/review-closure-evidence.md"
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed "s#${dotted_module_only}#${django_test_spec}#g" \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.exact-django"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.exact-django" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
mv "$closure_run/review-closure-evidence.md.canonical" \
  "$closure_run/review-closure-evidence.md"
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed "s#${django_test_spec}#${test_spec}#g" \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.canonical"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.canonical" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
cp "$closure_run/review-closure-evidence.md" \
  "$closure_run/review-closure-evidence.md.valid-selector"
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed 's/::test_failed_owner_boundary_is_hidden/::MissingClass.test_failed_owner_boundary_is_hidden/g' \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.invalid-selector"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.invalid-selector" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
sed 's/::test_failed_owner_boundary_is_hidden/::MissingClass.test_failed_owner_boundary_is_hidden/g' \
  "$closure_run/review-closure-evidence.md.valid-selector" \
  > "$closure_run/review-closure-evidence.md"
if ralph_validate_review_finding_closure \
    "$semantic_review_repo" \
    "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
    "$closure_run" >/dev/null 2>&1; then
  fail "corrective closure accepted a nonexistent Python test container selector"
fi
mv "$closure_run/review-closure-evidence.md.valid-selector" \
  "$closure_run/review-closure-evidence.md"
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed 's/::MissingClass.test_failed_owner_boundary_is_hidden/::test_failed_owner_boundary_is_hidden/g' \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.valid-selector"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.valid-selector" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
cp "$closure_run/evidence/terminal-logs/owner-green.log" \
  "$closure_run/evidence/terminal-logs/owner-green.log.clean"
printf 'Test: %s\n0 passed, 1 failed\nExit code: 1\n' "$test_spec" \
  > "$closure_run/evidence/terminal-logs/owner-green.log"
if ralph_validate_review_finding_closure \
    "$semantic_review_repo" \
    "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
    "$closure_run" >/dev/null 2>&1; then
  fail "corrective closure accepted a failing result containing the word passed"
fi
mv "$closure_run/evidence/terminal-logs/owner-green.log.clean" \
  "$closure_run/evidence/terminal-logs/owner-green.log"
typescript_runtime="$repo_root/sfpcl-lms/node_modules/typescript"
[[ -d "$typescript_runtime" ]] \
  || fail "frontend TypeScript parser runtime is unavailable for semantic-closure regression"
mkdir -p "$semantic_review_repo/frontend/src" \
  "$semantic_review_repo/frontend/node_modules"
ln -s "$typescript_runtime" \
  "$semantic_review_repo/frontend/node_modules/typescript"
cat > "$semantic_review_repo/frontend/src/semantic-closure.test.ts" <<'EOF'
// test("commented selector", () => undefined)
const fixture = 'test("string fixture selector", () => undefined)'
test.describe("suite only", () => undefined)
test("actual selector", () => {
  expect(fixture).toContain("string fixture selector")
})
EOF
cp "$closure_run/review-closure-evidence.md" \
  "$closure_run/review-closure-evidence.md.python-test"
frontend_test_spec='frontend/src/semantic-closure.test.ts::actual selector'
sed "s#${test_spec}#${frontend_test_spec}#g" \
  "$closure_run/review-closure-evidence.md.python-test" \
  > "$closure_run/review-closure-evidence.md"
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed "s#${test_spec}#${frontend_test_spec}#g" \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.frontend"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.frontend" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
ralph_validate_review_finding_closure \
  "$semantic_review_repo" \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
  "$closure_run" \
  || fail "parser-backed frontend test declaration was not resolved"
sed 's/actual selector/commented selector/g' \
  "$closure_run/review-closure-evidence.md" \
  > "$closure_run/review-closure-evidence.md.commented"
mv "$closure_run/review-closure-evidence.md.commented" \
  "$closure_run/review-closure-evidence.md"
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed 's/actual selector/commented selector/g' \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.commented"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.commented" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
if ralph_validate_review_finding_closure \
    "$semantic_review_repo" \
    "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
    "$closure_run" >/dev/null 2>&1; then
  fail "corrective closure treated a commented frontend test as a declaration"
fi
sed 's/commented selector/suite only/g' \
  "$closure_run/review-closure-evidence.md" \
  > "$closure_run/review-closure-evidence.md.describe"
mv "$closure_run/review-closure-evidence.md.describe" \
  "$closure_run/review-closure-evidence.md"
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed 's/commented selector/suite only/g' \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.describe"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.describe" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
if ralph_validate_review_finding_closure \
    "$semantic_review_repo" \
    "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
    "$closure_run" >/dev/null 2>&1; then
  fail "corrective closure treated test.describe as an executable frontend test"
fi
mv "$closure_run/review-closure-evidence.md.python-test" \
  "$closure_run/review-closure-evidence.md"
for evidence_log in owner-red.log owner-green.log owner-acceptance.log; do
  sed "s#frontend/src/semantic-closure.test.ts::suite only#${test_spec}#g" \
    "$closure_run/evidence/terminal-logs/$evidence_log" \
    > "$closure_run/evidence/terminal-logs/$evidence_log.python"
  mv "$closure_run/evidence/terminal-logs/$evidence_log.python" \
    "$closure_run/evidence/terminal-logs/$evidence_log"
done
rm -rf "$semantic_review_repo/frontend"
cp "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md.before-bypass"
python3 - "$semantic_review_repo/docs/slices/010A1-owner-correction.md" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.write_text(path.read_text().split("## Review Finding Closure", 1)[0])
PY
if ralph_validate_review_finding_closure \
    "$semantic_review_repo" \
    "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
    "$closure_run" >/dev/null 2>&1; then
  fail "corrective candidate deleted its fixed-point closure contract"
fi
mv "$semantic_review_repo/docs/slices/010A1-owner-correction.md.before-bypass" \
  "$semantic_review_repo/docs/slices/010A1-owner-correction.md"
cp "$closure_run/evidence/terminal-logs/owner-green.log" \
  "$closure_run/evidence/terminal-logs/owner-green.log.bound"
sed '/^Test: /d' "$closure_run/evidence/terminal-logs/owner-green.log.bound" \
  > "$closure_run/evidence/terminal-logs/owner-green.log"
if ralph_validate_review_finding_closure \
    "$semantic_review_repo" \
    "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
    "$closure_run" >/dev/null 2>&1; then
  fail "corrective closure accepted GREEN evidence unrelated to its permanent test selector"
fi
mv "$closure_run/evidence/terminal-logs/owner-green.log.bound" \
  "$closure_run/evidence/terminal-logs/owner-green.log"
rm "$closure_run/evidence/terminal-logs/owner-red.log"
if ralph_validate_review_finding_closure \
    "$semantic_review_repo" \
    "$semantic_review_repo/docs/slices/010A1-owner-correction.md" \
    "$closure_run" >/dev/null 2>&1; then
  fail "corrective closure accepted missing RED evidence"
fi
adaptive_config="$fixture_dir/adaptive-review-config.yaml"
cat > "$adaptive_config" <<'EOF'
run:
  architecture_review_every_completed_slices: 4
  architecture_review_clean_every_completed_slices: 8
  architecture_review_clean_streak_required: 2
EOF
adaptive_state="$fixture_dir/adaptive-review-state.json"
printf '{"architecture_review_clean_streak": 0}\n' > "$adaptive_state"
[[ "$(ralph_architecture_review_interval "$adaptive_config" "$adaptive_state")" == 4 ]] \
  || fail "adaptive review interval did not retain four-slice scrutiny before clean proof"
printf '{"architecture_review_clean_streak": 2}\n' > "$adaptive_state"
[[ "$(ralph_architecture_review_interval "$adaptive_config" "$adaptive_state")" == 8 ]] \
  || fail "adaptive review interval did not expand after the configured clean streak"
printf '{"architecture_review_due": true}\n' > "$adaptive_state"
[[ "$(ralph_architecture_review_due "$adaptive_state")" == True ]] \
  || fail "valid due-review state was not read"
[[ "$(ralph_architecture_review_due_after_product True 2 8)" == True ]] \
  || fail "failed mandatory boundary review was cleared below cadence"
[[ "$(ralph_architecture_review_due_after_product False 8 8)" == True ]] \
  || fail "cadence threshold did not schedule a review"
[[ "$(ralph_architecture_review_due_after_product False 2 8)" == False ]] \
  || fail "clean sub-threshold product progress scheduled an early review"
printf '{"architecture_review_due": "unknown"}\n' > "$adaptive_state"
if ralph_architecture_review_due "$adaptive_state" >/dev/null 2>&1; then
  fail "non-boolean architecture-review state failed open"
fi
[[ "$(ralph_architecture_review_boundary_reason 009K-close 010A-start \
      '010A-start (Not Started)')" == "epic_boundary:009->010" ]] \
  || fail "cross-epic completion did not require an architecture review"

parent_epic_repo="$fixture_dir/parent-epic-review-repo"
mkdir -p "$parent_epic_repo"
cat > "$parent_epic_repo/009L6-close.md" <<'EOF'
# Slice 009L6
## Status
Complete
## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
EOF
cat > "$parent_epic_repo/CR-012-proof.md" <<'EOF'
# Slice CR-012
## Status
Not Started
## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
EOF
cat > "$parent_epic_repo/010A-start.md" <<'EOF'
# Slice 010A
## Status
Not Started
## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
EOF
[[ -z "$(ralph_architecture_review_boundary_reason 009L6-close CR-012-proof \
      $'CR-012-proof (Not Started)\n010A-start (Not Started)' "$parent_epic_repo")" ]] \
  || fail "same-parent change request was skipped by epic-boundary detection"
[[ "$(ralph_architecture_review_boundary_reason CR-012-proof 010A-start \
      '010A-start (Not Started)' "$parent_epic_repo")" == "epic_boundary:009->010" ]] \
  || fail "final same-parent change request did not trigger the real epic boundary"

false_boundary_state="$fixture_dir/false-boundary-state.json"
cat > "$false_boundary_state" <<'EOF'
{
  "architecture_review_due": true,
  "architecture_review_due_reason": "epic_boundary:009->010",
  "architecture_review_root_generations": {
    "ROOT-009-OWNER-BOUNDARY": {
      "epic": "009",
      "generation": 1,
      "corrective_slice": "009L6",
      "finding_id": "AR-009-OWNER-001",
      "severity": "High"
    }
  },
  "last_architecture_review_metrics": {"corrective_slices_added": 1}
}
EOF
cp "$false_boundary_state" "$false_boundary_state.before"
ralph_reconcile_architecture_review_due "$false_boundary_state" "$parent_epic_repo"
cmp -s "$false_boundary_state.before" "$false_boundary_state" \
  || fail "architecture-review reconciliation dirtied tracked orchestrator state before preflight"
declare -F ralph_architecture_review_effective_due >/dev/null \
  || fail "missing read-only effective architecture-review due predicate"
[[ "$(ralph_architecture_review_effective_due \
      "$false_boundary_state" "$parent_epic_repo")" == False ]] \
  || fail "same-parent terminal corrective did not defer the premature boundary review"
python3 - "$false_boundary_state" <<'PY'
import json
import sys

state = json.load(open(sys.argv[1]))
if state.get("architecture_review_due") is not True:
    raise SystemExit("read-only deferral rewrote the durable due flag")
root = state.get("architecture_review_root_generations", {}).get("ROOT-009-OWNER-BOUNDARY", {})
if root.get("epic") != "009" or root.get("generation") != 1:
    raise SystemExit("deferred corrective cycle lost its per-root Epic/generation")
PY
scope_instruction="$(ralph_architecture_review_scope_instruction "$false_boundary_state")"
[[ "$scope_instruction" == *"ROOT-009-OWNER-BOUNDARY=generation 1 via 009L6"* ]] \
  || fail "corrective cycle did not select the targeted closure-review lane"

convergence_config="$fixture_dir/convergence-config.yaml"
cat > "$convergence_config" <<'EOF'
run:
  architecture_review_max_corrective_generations: 2
EOF
root_convergence_packet="$fixture_dir/root-convergence-packet.md"
cat > "$root_convergence_packet" <<'EOF'
## Finding Closure Manifest
| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | High | Carried | rate.log | 010H2 | - |
| AR-010-INTEREST-001 | ROOT-010-INTEREST-OWNER-TRUTH | High | New | interest.log | 010H2 | - |
| AR-010-ALLOCATION-001 | ROOT-010-ALLOCATION-ADMISSION | High | Closed | allocation.log | - | allocation-green.log |
EOF
cat > "$adaptive_state" <<'EOF'
{
  "architecture_review_root_generations": {
    "ROOT-010-RATE-VERSION-OWNER": {
      "epic": "010",
      "generation": 1,
      "corrective_slice": "010E3",
      "finding_id": "AR-010-RATE-001",
      "severity": "High"
    }
  }
}
EOF
ralph_validate_architecture_review_convergence \
  "$convergence_config" "$adaptive_state" "$root_convergence_packet" \
  || fail "independent new/carried roots were incorrectly charged to one global generation"
declare -F ralph_apply_architecture_review_root_transitions >/dev/null \
  || fail "missing trusted per-root architecture-review state transition"
ralph_apply_architecture_review_root_transitions \
  "$adaptive_state" "$root_convergence_packet"
python3 - "$adaptive_state" <<'PY'
import json, sys
roots = json.load(open(sys.argv[1])).get("architecture_review_root_generations", {})
if roots["ROOT-010-RATE-VERSION-OWNER"]["generation"] != 2:
    raise SystemExit("carried rate root did not advance to generation 2")
if roots["ROOT-010-INTEREST-OWNER-TRUTH"]["generation"] != 1:
    raise SystemExit("new interest root did not start at generation 1")
if "ROOT-010-ALLOCATION-ADMISSION" in roots:
    raise SystemExit("closed allocation root remained in convergence state")
PY
ralph_validate_architecture_review_convergence \
  "$convergence_config" "$adaptive_state" "$root_convergence_packet" \
  || fail "mapping the same corrective twice incorrectly consumed another generation"
sed 's/"corrective_slice": "010H2"/"corrective_slice": "010H3"/g' \
  "$adaptive_state" > "$adaptive_state.exhausted"
if ralph_validate_architecture_review_convergence \
    "$convergence_config" "$adaptive_state.exhausted" "$root_convergence_packet" \
    >/dev/null 2>&1; then
  fail "third correction for the same root escaped the convergence cap"
fi

# Architecture reviews must not merge a corrective that the normal runner
# will reject before it can create a repairable worktree. This candidate has a
# PostgreSQL acceptance contract but deliberately omits Runtime Capabilities.
runtime_contract_repo="$fixture_dir/runtime-contract-review-repo"
mkdir -p "$runtime_contract_repo/docs/slices"
cat > "$runtime_contract_repo/docs/slices/010Z-runtime-contract-gap.md" <<'EOF'
# Slice 010Z: Runtime contract gap
## Status
Not Started
## Depends On
- None
## Trusted PostgreSQL Acceptance
- Test: example.tests.RuntimeContractTests
- Expected tests: 1
## Risk Level
High
EOF
git init -q "$runtime_contract_repo"
printf '%s\n' seed > "$runtime_contract_repo/seed.txt"
git -C "$runtime_contract_repo" add seed.txt
git -C "$runtime_contract_repo" -c user.name='Ralph Regression' \
  -c user.email='ralph-regression@example.invalid' commit -qm fixture
if ralph_architecture_review_new_corrective_count "$runtime_contract_repo" \
    >/dev/null 2>&1; then
  fail "architecture review admitted a generated slice with no runtime contract"
fi
cat > "$runtime_contract_repo/docs/slices/010Z-runtime-contract-gap.md" <<'EOF'
# Slice 010Z: Malformed PostgreSQL contract
## Status
Not Started
## Depends On
- None
## Runtime Capabilities
- `postgresql-five-race-acceptance`
## Trusted PostgreSQL Acceptance
- Expected tests: 1
## Risk Level
High
EOF
if ralph_architecture_review_new_corrective_count "$runtime_contract_repo" \
    >/dev/null 2>&1; then
  fail "architecture review admitted malformed generated PostgreSQL acceptance"
fi
cat > "$runtime_contract_repo/docs/slices/010Z-runtime-contract-gap.md" <<'EOF'
# Slice 010Z: Valid PostgreSQL contract
## Status
Not Started
## Depends On
- None
## Runtime Capabilities
- `postgresql-five-race-acceptance`
## Trusted PostgreSQL Acceptance
- Test: example.tests.RuntimeContractTests
- Expected tests: 1
## Risk Level
High
EOF
[[ "$(ralph_architecture_review_new_corrective_count "$runtime_contract_repo")" == 1 ]] \
  || fail "architecture review rejected a valid generated PostgreSQL contract"

# A standing owner policy may admit exactly one terminal CR for an exhausted
# root. The review transition keeps the exhausted generation stable, maps all
# grouped roots to the terminal CR, and lets the fully gated CR clear every root
# that it actually closes without another review/task cycle.
auto_finalizer_repo="$fixture_dir/auto-finalizer-repo"
auto_finalizer_dir="$auto_finalizer_repo/docs/slices"
mkdir -p "$auto_finalizer_repo/.ralph" "$auto_finalizer_dir" \
  "$auto_finalizer_repo/docs/working"
auto_finalizer_config="$auto_finalizer_repo/.ralph/config.yaml"
cp "$convergence_config" "$auto_finalizer_config"
auto_finalizer_slice="$auto_finalizer_dir/CR-014-servicing-terminal-finalizer.md"
cat > "$auto_finalizer_slice" <<'EOF'
# Slice CR-014: Servicing terminal finalizer
## Status
Not Started
## Parent Epic
Epic 010: Servicing
## Depends On
- 010J
## Runtime Capabilities
- none
## Architecture Review Finalizer
- Epic: 010
- Root ID: ROOT-010-RATE-VERSION-OWNER
- Exhausted corrective generation: 2
## Risk Level
High
EOF
cat > "$auto_finalizer_dir/010J-reminder.md" <<'EOF'
## Status
Complete
## Depends On
- None
EOF
auto_finalizer_approvals="$auto_finalizer_repo/docs/working/HIGH_RISK_APPROVALS.md"
cat > "$auto_finalizer_approvals" <<'EOF'
# Finalizer approvals
- [approved-finalizer-policy] generation 2 | one terminal finalizer per Root ID | owner regression approval
EOF
auto_finalizer_packet="$fixture_dir/auto-finalizer-packet.md"
cat > "$auto_finalizer_packet" <<'EOF'
## Finding Closure Manifest
| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | High | Carried | rate.log | CR-014 | - |
| AR-010-INTEREST-001 | ROOT-010-INTEREST-OWNER-TRUTH | High | Carried | interest.log | CR-014 | - |
EOF
auto_finalizer_state="$auto_finalizer_repo/.ralph/state.json"
cat > "$auto_finalizer_state" <<'EOF'
{
  "architecture_review_due": true,
  "architecture_review_due_reason": "cadence:4",
  "architecture_review_root_generations": {
    "ROOT-010-RATE-VERSION-OWNER": {
      "epic": "010",
      "generation": 2,
      "corrective_slice": "010E4",
      "finding_id": "AR-010-RATE-001",
      "severity": "High"
    },
    "ROOT-010-INTEREST-OWNER-TRUTH": {
      "epic": "010",
      "generation": 1,
      "corrective_slice": "010H2",
      "finding_id": "AR-010-INTEREST-001",
      "severity": "High"
    }
  },
  "architecture_review_terminal_roots": [],
  "slices_completed_since_architecture_review": 4
}
EOF
git init -q "$auto_finalizer_repo"
git -C "$auto_finalizer_repo" add .ralph docs/working docs/slices/010J-reminder.md
git -C "$auto_finalizer_repo" -c user.name='Ralph Regression' \
  -c user.email='ralph-regression@example.invalid' commit -qm fixture
[[ "$(ralph_architecture_review_new_corrective_count "$auto_finalizer_repo")" == 1 ]] \
  || fail "terminal CR was not counted as one validated corrective"
ralph_validate_architecture_review_convergence \
  "$auto_finalizer_config" "$auto_finalizer_state" "$auto_finalizer_packet" \
  "$auto_finalizer_dir" "$auto_finalizer_approvals" \
  || fail "standing owner policy did not admit one bounded terminal finalizer"

# The standing generation-2 policy must not legitimize corrupt/legacy state
# already beyond that exact cap; such a CR would be rejected at product time.
overcap_state="$auto_finalizer_repo/.ralph/overcap-state.json"
python3 - "$auto_finalizer_state" "$overcap_state" <<'PY'
import json, sys
state = json.load(open(sys.argv[1]))
state["architecture_review_root_generations"]["ROOT-010-RATE-VERSION-OWNER"]["generation"] = 3
open(sys.argv[2], "w").write(json.dumps(state) + "\n")
PY
cat > "$auto_finalizer_dir/CR-015-overcap-finalizer.md" <<'EOF'
# Slice CR-015: Invalid over-cap finalizer
## Status
Not Started
## Parent Epic
Epic 010: Servicing
## Depends On
- 010J
## Architecture Review Finalizer
- Epic: 010
- Root ID: ROOT-010-RATE-VERSION-OWNER
- Exhausted corrective generation: 3
## Risk Level
High
EOF
overcap_packet="$fixture_dir/overcap-finalizer-packet.md"
cat > "$overcap_packet" <<'EOF'
## Finding Closure Manifest
| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | High | Carried | rate.log | CR-015 | - |
EOF
if ralph_validate_architecture_review_convergence \
    "$auto_finalizer_config" "$overcap_state" "$overcap_packet" \
    "$auto_finalizer_dir" "$auto_finalizer_approvals" >/dev/null 2>&1; then
  fail "standing generation-2 policy admitted a corrupt generation-3 root"
fi
ralph_apply_architecture_review_root_transitions \
  "$auto_finalizer_config" "$auto_finalizer_state" "$auto_finalizer_packet" \
  "$auto_finalizer_dir" "$auto_finalizer_approvals"
python3 - "$auto_finalizer_state" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
state = json.loads(path.read_text())
state["architecture_review_due"] = False
state.pop("architecture_review_due_reason", None)
path.write_text(json.dumps(state) + "\n")
PY
ralph_mark_architecture_review_terminal_finalizer_due \
  "$auto_finalizer_config" "$auto_finalizer_state" "$auto_finalizer_dir" \
  "$auto_finalizer_approvals"
python3 - "$auto_finalizer_state" <<'PY'
import json, sys
state = json.load(open(sys.argv[1]))
roots = state["architecture_review_root_generations"]
if roots["ROOT-010-RATE-VERSION-OWNER"]["generation"] != 2:
    raise SystemExit("terminal finalizer incorrectly created a third ordinary generation")
if roots["ROOT-010-RATE-VERSION-OWNER"]["corrective_slice"] != "CR-014":
    raise SystemExit("exhausted root was not mapped to its terminal finalizer")
if roots["ROOT-010-INTEREST-OWNER-TRUTH"]["generation"] != 2:
    raise SystemExit("grouped non-exhausted root did not advance normally")
if state.get("architecture_review_due_reason") != "terminal_finalizer:ROOT-010-RATE-VERSION-OWNER":
    raise SystemExit("review did not retain the narrow terminal-finalizer barrier")
PY
[[ "$(ralph_architecture_review_effective_due \
      "$auto_finalizer_state" "$auto_finalizer_dir")" == False ]] \
  || fail "terminal finalizer did not pass the retained review barrier"
[[ "$(ralph_architecture_review_finalizer_contract \
      "$auto_finalizer_config" "$auto_finalizer_state" "$auto_finalizer_slice" \
      "$auto_finalizer_approvals")" == $'010\tROOT-010-RATE-VERSION-OWNER' ]] \
  || fail "standing finalizer policy did not authorize the exact terminal CR"
ralph_finalize_architecture_review_cycle \
  "$auto_finalizer_state" 010 ROOT-010-RATE-VERSION-OWNER \
  CR-014-servicing-terminal-finalizer auto-finalizer-run
python3 - "$auto_finalizer_state" <<'PY'
import json, sys
state = json.load(open(sys.argv[1]))
roots = state.get("architecture_review_root_generations", {})
if "ROOT-010-RATE-VERSION-OWNER" in roots or "ROOT-010-INTEREST-OWNER-TRUTH" in roots:
    raise SystemExit("terminal finalizer retained a grouped root it closed")
if state.get("architecture_review_terminal_roots") != ["ROOT-010-RATE-VERSION-OWNER"]:
    raise SystemExit("terminal root history was not retained")
record = state.get("last_architecture_review_finalizer", {})
if record.get("root_ids") != [
    "ROOT-010-INTEREST-OWNER-TRUTH", "ROOT-010-RATE-VERSION-OWNER"
]:
    raise SystemExit("terminal finalizer audit omitted grouped roots")
PY
terminal_recurrence_packet="$fixture_dir/terminal-recurrence-packet.md"
cat > "$terminal_recurrence_packet" <<'EOF'
## Finding Closure Manifest
| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-RATE-001 | ROOT-010-RATE-VERSION-OWNER | High | Carried | rate.log | 010Z9 | - |
EOF
terminal_recurrence_rc=0
ralph_validate_architecture_review_convergence \
  "$auto_finalizer_config" "$auto_finalizer_state" "$terminal_recurrence_packet" \
  "$auto_finalizer_dir" "$auto_finalizer_approvals" >/dev/null 2>&1 \
  || terminal_recurrence_rc=$?
[[ "$terminal_recurrence_rc" == "$RALPH_EXIT_REVIEW_TERMINAL_RECURRENCE" ]] \
  || fail "terminally finalized root restarted an ordinary corrective cycle"

# After the corrective-generation budget is exhausted, only a protected,
# owner-approved CR may finalize the epic boundary. Its successful full gates
# replace another immediate review/task generation; ordinary slices cannot
# claim this terminal transition.
finalizer_slice="$parent_epic_repo/CR-013-finalizer.md"
cat > "$finalizer_slice" <<'EOF'
# Slice CR-013: Finalizer fixture
## Status
Not Started
## Parent Epic
Epic 009: Fixture
## Depends On
- CR-012
## Architecture Review Finalizer
- Epic: 009
- Root ID: ROOT-009-OWNER-BOUNDARY
- Exhausted corrective generation: 2
## Risk Level
High
EOF
finalizer_state="$fixture_dir/finalizer-state.json"
cat > "$finalizer_state" <<'EOF'
{
  "architecture_review_due": true,
  "architecture_review_due_reason": "cadence:4",
  "architecture_review_root_generations": {
    "ROOT-009-OWNER-BOUNDARY": {
      "epic": "009",
      "generation": 2,
      "corrective_slice": "009L7",
      "finding_id": "AR-009-OWNER-001",
      "severity": "High"
    }
  },
  "slices_completed_since_architecture_review": 1
}
EOF
finalizer_approvals="$fixture_dir/finalizer-approvals.md"
printf '# Finalizer approvals\n' > "$finalizer_approvals"
declare -F ralph_architecture_review_finalizer_epic >/dev/null \
  || fail "missing architecture-review finalizer validation interface"
if ralph_architecture_review_finalizer_epic \
    "$convergence_config" "$finalizer_state" "$finalizer_slice" \
    "$finalizer_approvals" >/dev/null 2>&1; then
  fail "unapproved slice claimed the exhausted architecture-review finalizer"
fi
printf '%s\n' \
  '- [approved-finalizer] CR-013 | Epic 009 | Root ROOT-009-OWNER-BOUNDARY | generation 2 | owner regression approval' \
  >> "$finalizer_approvals"
[[ "$(ralph_architecture_review_finalizer_contract \
      "$convergence_config" "$finalizer_state" "$finalizer_slice" \
      "$finalizer_approvals")" == $'009\tROOT-009-OWNER-BOUNDARY' ]] \
  || fail "protected owner-approved exhausted-cycle finalizer was rejected"
finalizer_queue="$fixture_dir/finalizer-queue"
mkdir -p "$finalizer_queue/.ralph" "$finalizer_queue/docs/slices" \
  "$finalizer_queue/docs/working"
cp "$convergence_config" "$finalizer_queue/.ralph/config.yaml"
cp "$finalizer_state" "$finalizer_queue/.ralph/state.json"
cp "$finalizer_slice" "$finalizer_queue/docs/slices/CR-013-finalizer.md"
cp "$finalizer_approvals" "$finalizer_queue/docs/working/HIGH_RISK_APPROVALS.md"
cat > "$finalizer_queue/docs/slices/CR-012-prerequisite.md" <<'EOF'
## Status
Complete
## Depends On
- None
EOF
[[ "$(ralph_architecture_review_effective_due \
      "$finalizer_queue/.ralph/state.json" "$finalizer_queue/docs/slices")" == False ]] \
  || fail "approved first-grabbable exhausted-root finalizer did not defer the review barrier"
cat > "$finalizer_queue/docs/slices/CR-001-ordinary.md" <<'EOF'
## Status
Not Started
## Depends On
- None
EOF
[[ "$(ralph_architecture_review_effective_due \
      "$finalizer_queue/.ralph/state.json" "$finalizer_queue/docs/slices")" == True ]] \
  || fail "ordinary product work bypassed a due review ahead of the approved finalizer"
python3 - "$finalizer_state" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
state = json.loads(path.read_text())
state["architecture_review_root_generations"]["ROOT-009-OWNER-BOUNDARY"]["generation"] = 1
path.write_text(json.dumps(state) + "\n")
PY
if ralph_architecture_review_finalizer_contract \
    "$convergence_config" "$finalizer_state" "$finalizer_slice" \
    "$finalizer_approvals" >/dev/null 2>&1; then
  fail "finalizer bypassed a corrective generation that was not exhausted"
fi
python3 - "$finalizer_state" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
state = json.loads(path.read_text())
state["architecture_review_root_generations"]["ROOT-009-OWNER-BOUNDARY"]["generation"] = 2
path.write_text(json.dumps(state) + "\n")
PY
declare -F ralph_finalize_architecture_review_cycle >/dev/null \
  || fail "missing trusted architecture-review cycle finalization interface"
ralph_finalize_architecture_review_cycle \
  "$finalizer_state" 009 ROOT-009-OWNER-BOUNDARY CR-013-finalizer finalizer-run
python3 - "$finalizer_state" <<'PY'
import json, sys
state = json.load(open(sys.argv[1]))
if state.get("architecture_review_due") is not False:
    raise SystemExit("validated finalizer did not clear the exhausted boundary")
if "architecture_review_due_reason" in state:
    raise SystemExit("validated finalizer retained a stale boundary reason")
if "ROOT-009-OWNER-BOUNDARY" in state.get("architecture_review_root_generations", {}):
    raise SystemExit("validated finalizer retained the exhausted corrective root")
if state.get("slices_completed_since_architecture_review") != 0:
    raise SystemExit("validated finalizer did not reset the review cadence")
if state.get("last_architecture_review_finalizer") != {
    "epic": "009", "root_id": "ROOT-009-OWNER-BOUNDARY",
    "root_ids": ["ROOT-009-OWNER-BOUNDARY"],
    "slice_id": "CR-013-finalizer", "run_id": "finalizer-run"
}:
    raise SystemExit("validated finalizer audit record is incomplete")
PY
[[ "$(ralph_architecture_review_boundary_reason 009K-close '' \
      '010A-parked (Blocked)')" == "epic_boundary:009->010" ]] \
  || fail "a blocked next epic hid its mandatory boundary review"
[[ "$(ralph_architecture_review_boundary_reason 012I-close '' '')" == "epic_completion:012" ]] \
  || fail "final project completion did not require an architecture review"
[[ "$(ralph_architecture_review_boundary_reason CR-012-final-fix '' '')" == \
    "project_completion:CR-012-final-fix" ]] \
  || fail "a final change-request slice drained the queue without a completion review"
[[ -z "$(ralph_architecture_review_boundary_reason 012I-close '' \
      '012J-parked (Blocked)')" ]] \
  || fail "blocked remaining work was misclassified as final project completion"
ralph_validate_architecture_review_admission 0 0 0 \
  || fail "clean architecture review failed severity admission"
ralph_validate_architecture_review_admission 0 2 1 0 \
  || fail "grouped High findings with corrective work failed severity admission"
ralph_validate_architecture_review_admission 1 0 0 1 \
  || fail "High/Critical finding mapped to existing corrective work failed admission"
if ralph_validate_architecture_review_admission 1 0 0 0 >/dev/null 2>&1; then
  fail "Critical architecture finding passed without corrective work"
fi
corrective_repo="$fixture_dir/architecture-corrective-repo"
mkdir -p "$corrective_repo/docs/slices"
git init -q "$corrective_repo"
git -C "$corrective_repo" config user.name "Ralph Regression"
git -C "$corrective_repo" config user.email "ralph-regression@example.invalid"
cat > "$corrective_repo/docs/slices/010A-existing.md" <<'EOF'
## Status
Not Started

## Depends On
- None
EOF
cat > "$corrective_repo/docs/slices/010Z-complete.md" <<'EOF'
## Status
Complete

## Depends On
- None
EOF
cat > "$corrective_repo/docs/slices/CR-012-existing.md" <<'EOF'
## Status
Not Started

## Depends On
- 010A
EOF
git -C "$corrective_repo" add .
git -C "$corrective_repo" commit -qm fixture
corrective_mapping_packet="$corrective_repo/review-packet.md"
printf '%s\n' '- Existing corrective slice: 010A' > "$corrective_mapping_packet"
[[ "$(ralph_architecture_review_existing_corrective_count \
      "$corrective_mapping_packet" "$corrective_repo")" == 1 ]] \
  || fail "valid existing corrective mapping was not admitted"
printf '%s\n' '- Existing corrective slice: CR-012' > "$corrective_mapping_packet"
[[ "$(ralph_architecture_review_existing_corrective_count \
      "$corrective_mapping_packet" "$corrective_repo")" == 1 ]] \
  || fail "valid existing change-request corrective mapping was not admitted"
printf '%s\n' '- Existing corrective slice: CR-invalid' > "$corrective_mapping_packet"
if ralph_architecture_review_existing_corrective_count \
    "$corrective_mapping_packet" "$corrective_repo" >/dev/null 2>&1; then
  fail "malformed change-request corrective mapping was admitted"
fi
printf '%s\n' '- Existing corrective slice: CR-999' > "$corrective_mapping_packet"
if ralph_architecture_review_existing_corrective_count \
    "$corrective_mapping_packet" "$corrective_repo" >/dev/null 2>&1; then
  fail "missing change-request corrective mapping was admitted"
fi
printf '%s\n' '- Existing corrective slice: 010Z' > "$corrective_mapping_packet"
cat > "$corrective_repo/docs/slices/010Z-complete.md" <<'EOF'
## Status
Blocked

## Depends On
- None
EOF
if ralph_architecture_review_existing_corrective_count \
    "$corrective_mapping_packet" "$corrective_repo" >/dev/null 2>&1; then
  fail "slice made actionable only by the review was admitted as existing corrective work"
fi
cat > "$corrective_repo/docs/slices/010B-new.md" <<'EOF'
## Status
Not Started

## Depends On
- 010A

## Runtime Capabilities
- none
EOF
[[ "$(ralph_architecture_review_new_corrective_count "$corrective_repo")" == 1 ]] \
  || fail "valid new numeric corrective slice was not counted"
cat > "$corrective_repo/docs/slices/CR-001-invalid.md" <<'EOF'
## Status
Not Started

## Depends On
- None
EOF
if ralph_architecture_review_new_corrective_count "$corrective_repo" >/dev/null 2>&1; then
  fail "non-numeric untracked slice was counted as architecture corrective work"
fi
architecture_repo="$fixture_dir/architecture-review-repo"
mkdir -p "$architecture_repo/docs/working" "$architecture_repo/src" \
  "$architecture_repo/.ralph/runs/prior-review"
git init -q "$architecture_repo"
git -C "$architecture_repo" config user.name "Ralph Regression"
git -C "$architecture_repo" config user.email "ralph-regression@example.invalid"
printf 'baseline\n' > "$architecture_repo/docs/working/REVIEW_FINDINGS.md"
printf 'product\n' > "$architecture_repo/src/product.py"
printf '{}\n' > "$architecture_repo/.ralph/state.json"
printf 'retained historical evidence\n' \
  > "$architecture_repo/.ralph/runs/prior-review/evidence.md"
git -C "$architecture_repo" add .
git -C "$architecture_repo" commit -qm fixture
printf 'review finding\n' >> "$architecture_repo/docs/working/REVIEW_FINDINGS.md"
ralph_validate_architecture_review_change_scope "$architecture_repo" current-review \
  || fail "documentation-only architecture review was rejected"
printf '{"architecture_review_due": false}\n' > "$architecture_repo/.ralph/state.json"
if ralph_validate_architecture_review_change_scope \
    "$architecture_repo" current-review >/dev/null 2>&1; then
  fail "architecture-review lane accepted agent-authored state"
fi
git -C "$architecture_repo" show HEAD:.ralph/state.json \
  > "$architecture_repo/.ralph/state.json"
printf 'rewritten historical evidence\n' \
  > "$architecture_repo/.ralph/runs/prior-review/evidence.md"
if ralph_validate_architecture_review_change_scope \
    "$architecture_repo" current-review >/dev/null 2>&1; then
  fail "architecture-review lane accepted an edit to a prior run's evidence"
fi
printf 'retained historical evidence\n' \
  > "$architecture_repo/.ralph/runs/prior-review/evidence.md"
printf 'unsafe product edit\n' >> "$architecture_repo/src/product.py"
if ralph_validate_architecture_review_change_scope \
    "$architecture_repo" current-review >/dev/null 2>&1; then
  fail "architecture-review queue-only lane accepted a product change"
fi
rg -q 'ralph_validate_architecture_review_change_scope' scripts/ralph-validate.sh \
  || fail "validator does not classify documentation-only architecture reviews"
rg -q 'documentation-only architecture review contains no product changes' scripts/ralph-validate.sh \
  || fail "validator does not record the specialized architecture-review lane"
architecture_validator_repo="$fixture_dir/architecture-validator-repo"
architecture_validator_run="architecture-validator-run"
architecture_validator_run_dir="$architecture_validator_repo/.ralph/runs/$architecture_validator_run"
mkdir -p "$architecture_validator_repo/.ralph" \
  "$architecture_validator_repo/docs/slices" \
  "$architecture_validator_repo/docs/working" \
  "$architecture_validator_repo/frontend" \
  "$architecture_validator_run_dir"
cat > "$architecture_validator_repo/.ralph/config.yaml" <<'EOF'
project_dir: frontend
backend_dir: backend
build: true
install: true
typecheck: true
lint: true
unit_tests: true
backend_check: true
backend_tests: true
backend_migrations: true
backend_coverage: true
max_changed_files: 30
max_lines_changed: 2000
EOF
printf '%s\n' '{"completed_slices": []}' > "$architecture_validator_repo/.ralph/state.json"
printf '%s\n' '{}' > "$architecture_validator_repo/.ralph/permissions.json"
cat > "$architecture_validator_repo/docs/slices/001A-fixture.md" <<'EOF'
## Status
Complete

## Depends On
- None
EOF
printf 'baseline finding\n' > "$architecture_validator_repo/docs/working/REVIEW_FINDINGS.md"
printf 'baseline context\n' > "$architecture_validator_repo/docs/working/CONTEXT.md"
for artifact in prompt.md changed-files.txt final-summary.md; do
  printf 'fixture\n' > "$architecture_validator_run_dir/$artifact"
done
printf '1. Exercise documentation-only review validation.\n' \
  > "$architecture_validator_run_dir/execution-plan.md"
printf 'Low risk fixture.\n' > "$architecture_validator_run_dir/risk-assessment.md"
cat > "$architecture_validator_run_dir/review-packet.md" <<'EOF'
## Result
Ready for independent validation

## Convergence Metrics
- Findings closed: 0
- New Critical: 0
- New High: 0
- New Medium: 0
- New Low: 0
- Corrective slices added: 0

## Finding Closure Manifest
- None
EOF
git init -q "$architecture_validator_repo"
git -C "$architecture_validator_repo" config user.name "Ralph Regression"
git -C "$architecture_validator_repo" config user.email "ralph-regression@example.invalid"
git -C "$architecture_validator_repo" add .
git -C "$architecture_validator_repo" commit -qm fixture
printf 'review-confirmed context\n' >> "$architecture_validator_repo/docs/working/CONTEXT.md"
scripts/ralph-validate.sh \
  --run-id "$architecture_validator_run" \
  --worktree "$architecture_validator_repo" \
  --mode architecture_review \
  --slice architecture-review \
  > "$fixture_dir/architecture-validator.stdout" \
  2> "$fixture_dir/architecture-validator.stderr" \
  || fail "documentation-only architecture-review validator lane did not complete"
for skipped_gate in build install typecheck lint test e2e backend-check backend-test backend-migrations backend-coverage; do
  grep -qF 'Skipped: documentation-only architecture review contains no product changes' \
    "$architecture_validator_run_dir/${skipped_gate}-results.md" \
    || fail "architecture-review lane did not skip $skipped_gate with an explicit reason"
done
grep -qF 'PASS: architecture review reported machine-readable convergence metrics.' \
  "$architecture_validator_run_dir/architecture-review-metrics-results.md" \
  || fail "architecture-review lane did not preserve validated convergence metrics"
grep -qF 'PASS: stable finding identities, reproducers, metrics, and corrective contracts agree.' \
  "$architecture_validator_run_dir/architecture-review-metrics-results.md" \
  || fail "architecture-review lane did not enforce semantic finding closure"
cp "$architecture_validator_run_dir/review-packet.md" \
  "$architecture_validator_run_dir/review-packet.md.valid"
python3 - "$architecture_validator_run_dir/review-packet.md" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.write_text(path.read_text().split("## Finding Closure Manifest", 1)[0])
PY
if scripts/ralph-validate.sh \
    --run-id "$architecture_validator_run" \
    --worktree "$architecture_validator_repo" \
    --mode architecture_review \
    --slice architecture-review \
    > "$fixture_dir/architecture-validator-missing-manifest.stdout" \
    2> "$fixture_dir/architecture-validator-missing-manifest.stderr"; then
  fail "architecture-review lane accepted missing semantic finding manifest"
fi
mv "$architecture_validator_run_dir/review-packet.md.valid" \
  "$architecture_validator_run_dir/review-packet.md"
python3 - "$architecture_validator_run_dir/review-packet.md" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.write_text(
    path.read_text().replace(
        "Ready for independent validation",
        "Convergence failure — stop before product work",
        1,
    )
)
PY
if scripts/ralph-validate.sh \
    --run-id "$architecture_validator_run" \
    --worktree "$architecture_validator_repo" \
    --mode architecture_review \
    --slice architecture-review \
    > "$fixture_dir/architecture-validator-veto.stdout" \
    2> "$fixture_dir/architecture-validator-veto.stderr"; then
  fail "architecture-review lane accepted a non-ready Result and advanced product work"
fi

# A shadow selector records potential future backend lanes without changing the
# authoritative full gate. Its recommendations fail closed for high-risk,
# shared-schema, ambiguous, and periodic-checkpoint candidates.
backend_policy_helper="scripts/lib/ralph-backend-validation.sh"
[[ -f "$backend_policy_helper" ]] || fail "missing backend validation policy helper"
# shellcheck source=../lib/ralph-backend-validation.sh
source "$backend_policy_helper"
backend_policy_repo="$fixture_dir/backend-policy-repo"
mkdir -p "$backend_policy_repo/.ralph" \
  "$backend_policy_repo/docs/slices" \
  "$backend_policy_repo/frontend" \
  "$backend_policy_repo/backend/payments" \
  "$backend_policy_repo/backend/shared" \
  "$backend_policy_repo/backend/tests" \
  "$backend_policy_repo/backend/loans/migrations"
cat > "$backend_policy_repo/.ralph/config.yaml" <<'EOF'
backend_validation_policy: shadow
backend_full_suite_every_completed_slices: 4
backend_impacted_parallel_workers: 3
EOF
printf '%s\n' '{"completed_slices": []}' > "$backend_policy_repo/.ralph/state.json"
cat > "$backend_policy_repo/docs/slices/100A-medium.md" <<'EOF'
## Risk Level
Medium
EOF
cat > "$backend_policy_repo/docs/slices/100B-high.md" <<'EOF'
## Risk Level
High
EOF
printf 'baseline\n' > "$backend_policy_repo/frontend/app.ts"
printf 'baseline\n' > "$backend_policy_repo/backend/loans/service.py"
printf 'from backend.loans import service\n' > "$backend_policy_repo/backend/tests/test_loans.py"
printf 'baseline\n' > "$backend_policy_repo/backend/payments/service.py"
printf 'baseline\n' > "$backend_policy_repo/backend/shared/encryption.py"
printf 'from backend.payments import service\n' \
  > "$backend_policy_repo/backend/tests/test_unrelated.py"
printf 'baseline\n' > "$backend_policy_repo/backend/loans/migrations/0001_initial.py"
git init -q "$backend_policy_repo"
git -C "$backend_policy_repo" config user.name "Ralph Regression"
git -C "$backend_policy_repo" config user.email "ralph-regression@example.invalid"
git -C "$backend_policy_repo" add .
git -C "$backend_policy_repo" commit -qm fixture

printf 'frontend candidate\n' >> "$backend_policy_repo/frontend/app.ts"
ralph_select_backend_validation_lane \
  "$backend_policy_repo" backend \
  "$backend_policy_repo/docs/slices/100A-medium.md" 100A-medium \
  "$backend_policy_repo/.ralph/config.yaml" "$backend_policy_repo/.ralph/state.json"
[[ "$RALPH_BACKEND_VALIDATION_LANE" == "skip" ]] \
  || fail "frontend-only candidate did not receive the shadow skip recommendation"
git -C "$backend_policy_repo" add .
git -C "$backend_policy_repo" commit -qm frontend-candidate

printf 'localized backend candidate\n' >> "$backend_policy_repo/backend/loans/service.py"
printf 'localized test candidate\n' >> "$backend_policy_repo/backend/tests/test_loans.py"
ralph_select_backend_validation_lane \
  "$backend_policy_repo" backend \
  "$backend_policy_repo/docs/slices/100A-medium.md" 100A-medium \
  "$backend_policy_repo/.ralph/config.yaml" "$backend_policy_repo/.ralph/state.json"
[[ "$RALPH_BACKEND_VALIDATION_LANE" == "impacted" ]] \
  || fail "localized medium-risk backend candidate did not receive the impacted recommendation"
[[ " ${RALPH_BACKEND_TEST_LABELS[*]} " == *" backend.tests.test_loans "* ]] \
  || fail "impacted backend lane omitted its changed test module"
[[ "$RALPH_BACKEND_IMPACTED_WORKERS" == "3" ]] \
  || fail "impacted backend lane ignored its bounded worker count"

ralph_select_backend_validation_lane \
  "$backend_policy_repo" backend \
  "$backend_policy_repo/docs/slices/100B-high.md" 100B-high \
  "$backend_policy_repo/.ralph/config.yaml" "$backend_policy_repo/.ralph/state.json"
[[ "$RALPH_BACKEND_VALIDATION_LANE" == "full" ]] \
  || fail "high-risk backend candidate did not retain full coverage"
git -C "$backend_policy_repo" add .
git -C "$backend_policy_repo" commit -qm localized-candidate

printf 'schema candidate\n' >> "$backend_policy_repo/backend/loans/migrations/0001_initial.py"
ralph_select_backend_validation_lane \
  "$backend_policy_repo" backend \
  "$backend_policy_repo/docs/slices/100A-medium.md" 100A-medium \
  "$backend_policy_repo/.ralph/config.yaml" "$backend_policy_repo/.ralph/state.json"
[[ "$RALPH_BACKEND_VALIDATION_LANE" == "full" ]] \
  || fail "migration candidate did not retain full coverage"
git -C "$backend_policy_repo" add .
git -C "$backend_policy_repo" commit -qm schema-candidate

printf 'shared candidate\n' >> "$backend_policy_repo/backend/shared/encryption.py"
printf 'unrelated test candidate\n' >> "$backend_policy_repo/backend/tests/test_unrelated.py"
ralph_select_backend_validation_lane \
  "$backend_policy_repo" backend \
  "$backend_policy_repo/docs/slices/100A-medium.md" 100A-medium \
  "$backend_policy_repo/.ralph/config.yaml" "$backend_policy_repo/.ralph/state.json"
[[ "$RALPH_BACKEND_VALIDATION_LANE" == "full" ]] \
  || fail "shared backend candidate received a selective shadow recommendation"
git -C "$backend_policy_repo" add .
git -C "$backend_policy_repo" commit -qm shared-candidate

printf 'second module candidate\n' >> "$backend_policy_repo/backend/payments/service.py"
printf 'first module candidate\n' >> "$backend_policy_repo/backend/loans/service.py"
printf 'multi-module test candidate\n' >> "$backend_policy_repo/backend/tests/test_loans.py"
ralph_select_backend_validation_lane \
  "$backend_policy_repo" backend \
  "$backend_policy_repo/docs/slices/100A-medium.md" 100A-medium \
  "$backend_policy_repo/.ralph/config.yaml" "$backend_policy_repo/.ralph/state.json"
[[ "$RALPH_BACKEND_VALIDATION_LANE" == "full" ]] \
  || fail "multi-module backend candidate received a selective shadow recommendation"
git -C "$backend_policy_repo" add .
git -C "$backend_policy_repo" commit -qm multi-module-candidate

rm "$backend_policy_repo/backend/payments/service.py"
ralph_select_backend_validation_lane \
  "$backend_policy_repo" backend \
  "$backend_policy_repo/docs/slices/100A-medium.md" 100A-medium \
  "$backend_policy_repo/.ralph/config.yaml" "$backend_policy_repo/.ralph/state.json"
[[ "$RALPH_BACKEND_VALIDATION_LANE" == "full" ]] \
  || fail "deleted backend path received a selective shadow recommendation"
printf 'baseline\nsecond module candidate\n' \
  > "$backend_policy_repo/backend/payments/service.py"

printf '%s\n' '{"completed_slices": ["097A", "098A", "099A"]}' \
  > "$backend_policy_repo/.ralph/state.json"
printf 'checkpoint backend candidate\n' >> "$backend_policy_repo/backend/loans/service.py"
printf 'checkpoint test candidate\n' >> "$backend_policy_repo/backend/tests/test_loans.py"
ralph_select_backend_validation_lane \
  "$backend_policy_repo" backend \
  "$backend_policy_repo/docs/slices/100A-medium.md" 100A-medium \
  "$backend_policy_repo/.ralph/config.yaml" "$backend_policy_repo/.ralph/state.json"
[[ "$RALPH_BACKEND_VALIDATION_LANE" == "full" ]] \
  || fail "fourth completed-slice checkpoint did not retain full coverage"

# The shadow audit compares serial coverage against the shared bounded parallel
# module and proves exact outcome and line-coverage equivalence.
shadow_coverage="scripts/ralph-shadow-parallel-coverage.sh"
[[ -x "$shadow_coverage" ]] || fail "missing executable parallel-coverage shadow pilot"
rg -q 'manage.py.*test.*backend_dir.tests' "$shadow_coverage" \
  || fail "shadow pilot does not run the same complete backend test label"
rg -q 'ralph-parallel-backend-coverage.sh' "$shadow_coverage" \
  || fail "shadow pilot does not exercise Django's bounded parallel runner"
rg -q 'executed_lines' "$shadow_coverage" \
  || fail "shadow pilot does not compare exact executed coverage lines"
rg -q 'discovered_tests' "$shadow_coverage" \
  || fail "shadow pilot does not compare discovered test counts"
rg -q 'parallel_workers.*coverage_floor' "$shadow_coverage" \
  || fail "shadow pilot does not enforce the configured coverage floor in both lanes"
if rg -q 'ralph-shadow-parallel-coverage' scripts/ralph-validate.sh; then
  fail "unproven parallel coverage was added to the authoritative validation gate"
fi

# Once the shadow proof passes, the authoritative lane uses the same bounded
# multiprocessing implementation; it never drops the full-suite label or floor.
parallel_coverage_gate="scripts/ralph-parallel-backend-coverage.sh"
[[ -x "$parallel_coverage_gate" ]] \
  || fail "missing executable authoritative parallel-coverage module"
rg -q 'concurrency = multiprocessing' "$parallel_coverage_gate" \
  || fail "authoritative parallel coverage does not collect worker subprocesses"
rg -q -- '--parallel "\$workers"' "$parallel_coverage_gate" \
  || fail "authoritative parallel coverage does not use its bounded worker count"
rg -q 'coverage combine' "$parallel_coverage_gate" \
  || fail "authoritative parallel coverage does not combine subprocess data"
rg -q -- '--fail-under="\$coverage_floor"' "$parallel_coverage_gate" \
  || fail "authoritative parallel coverage does not retain the configured floor"
rg -q 'ralph-parallel-backend-coverage.sh' scripts/ralph-validate.sh \
  || fail "validator does not invoke the proven parallel-coverage module"
rg -q 'backend_coverage_parallel_workers: 6' .ralph/config.yaml \
  || fail "authoritative coverage worker count is not explicitly bounded at the proven six"
rg -q 'backend_validation_policy: shadow' .ralph/config.yaml \
  || fail "shadow backend validation classification is not enabled explicitly"
rg -q 'backend_full_suite_every_completed_slices: 4' .ralph/config.yaml \
  || fail "periodic full backend checkpoint is not explicitly bounded at four slices"
rg -q 'ralph_select_backend_validation_lane' scripts/ralph-validate.sh \
  || fail "validator does not classify backend work before selecting its suite"
rg -q 'backend-validation-lane-results.md' scripts/ralph-validate.sh \
  || fail "backend validation selection does not leave reviewable evidence"
if rg -q 'backend_validation_lane.*==.*(skip|impacted)' scripts/ralph-validate.sh; then
  fail "shadow backend recommendation can bypass an authoritative full gate"
fi

# GitHub keeps a complete-suite backstop even when a local slice selects its
# impacted modules. Public Linux runners receive four workers; serial execution
# remains a separate scheduled/manual canary instead of taxing every push.
rg -q 'cancel-in-progress: true' .github/workflows/ci.yml \
  || fail "CI does not cancel superseded runs on the same ref"
rg -q 'cache: pip' .github/workflows/ci.yml \
  || fail "backend CI does not cache pinned pip dependencies"
rg -q 'ralph-parallel-backend-coverage.sh.*sfpcl_credit 4 85' \
  .github/workflows/ci.yml \
  || fail "backend CI does not run complete coverage with four workers and the floor"
rg -q 'timeout-minutes: 30' .github/workflows/ci.yml \
  || fail "backend CI does not enforce its runtime cap"
serial_canary='.github/workflows/backend-serial-canary.yml'
[[ -f "$serial_canary" ]] || fail "missing serial backend canary workflow"
rg -q "cron: '30 18 \* \* \*'" "$serial_canary" \
  || fail "serial backend canary is not scheduled nightly"
rg -q 'workflow_dispatch:' "$serial_canary" \
  || fail "serial backend canary cannot be run at epic/release checkpoints"
rg -q 'coverage run --source=sfpcl_credit.*test sfpcl_credit.tests --timing' \
  "$serial_canary" \
  || fail "serial backend canary does not retain the complete serial test label"

# The PostgreSQL TransactionTestCase cannot share Django's class-level fixture.
# It must retain an explicit per-test builder instead of inheriting the no-op
# unittest setUp method after the primary class moves to setUpTestData.
python3 - <<'PY'
import ast
from pathlib import Path

tree = ast.parse(Path("sfpcl_credit/tests/test_approval_case_routing_api.py").read_text())
classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
concurrency = classes["ApprovalActionConcurrencyTests"]
setup = next(
    (node for node in concurrency.body if isinstance(node, ast.FunctionDef) and node.name == "setUp"),
    None,
)
if setup is None:
    raise SystemExit("PostgreSQL concurrency tests inherited a no-op setUp")
if not any(
    isinstance(node, ast.Attribute) and node.attr == "_build_fixture"
    for node in ast.walk(setup)
):
    raise SystemExit("PostgreSQL concurrency setUp does not build its fixture")
PY

[[ "$(tr -d '[:space:]' < .nvmrc)" == "20.19.6" ]] \
  || fail "repository Node version is not pinned to 20.19.6"
python3 - <<'PY'
import json
from pathlib import Path

package = json.loads(Path("sfpcl-lms/package.json").read_text())
if package.get("engines", {}).get("node") != "20.19.6":
    raise SystemExit("FAIL: frontend package metadata does not pin Node 20.19.6")
lock = json.loads(Path("sfpcl-lms/package-lock.json").read_text())
if lock["packages"][""].get("engines", {}).get("node") != "20.19.6":
    raise SystemExit("FAIL: frontend lock metadata does not pin Node 20.19.6")
PY
rg -q 'node-version: 20\.19\.6' .github/workflows/ci.yml \
  || fail "GitHub CI does not use the exact supported Node version"
rg -q 'ralph_activate_pinned_node' scripts/ralph-run.sh \
  || fail "Ralph does not activate the repository-pinned Node runtime"
rg -q 'Do not run the complete backend suite or full coverage yourself' scripts/ralph-run.sh \
  || fail "agent prompt still permits duplicate complete backend coverage runs"
if rg -q "grep -qiE 'fail\|blocked'" scripts/ralph-validate.sh; then
  fail "agent-declared result still treats explanatory uses of 'failure' as a failed verdict"
fi

# Agent output is untrusted text. It must never drive loop control flow.
if rg -n 'grep -q .*No eligible slice found|grep -q .*has been vetoed by the owner|grep -q .*MERGE_FAILED|grep -q .*AGENT_LIMIT_EXHAUSTED' scripts/ralph-loop.sh; then
  fail "ralph-loop.sh still derives control flow from agent transcript text"
fi
rg -q 'ralph_max_repair_attempts' scripts/ralph-loop.sh \
  || fail "Ralph loop ignores run.max_retries"
rg -q '^[[:space:]]*max_retries: 1' .ralph/config.yaml \
  || fail "unchanged failures still receive more than the one owner-approved repair"
rg -q 'ralph_max_progressive_repair_attempts' scripts/ralph-loop.sh \
  || fail "Ralph loop ignores the overall progressive repair ceiling"
rg -q 'repairs_for_signature=0' scripts/ralph-loop.sh \
  || fail "Ralph loop does not reset the per-signature budget after validation progresses"
rg -q 'repairs_for_signature >= max_repair_attempts' scripts/ralph-loop.sh \
  || fail "Ralph loop does not stop an unchanged failure at its bounded budget"
rg -q 'total_repair_attempts < max_progressive_repair_attempts' scripts/ralph-loop.sh \
  || fail "Ralph loop does not continue through distinct failures up to the safety ceiling"
rg -q -- '--resume-failed' scripts/ralph-loop.sh \
  || fail "Ralph loop does not reuse the failed worktree during bounded repairs"
rg -qF 'Architecture review validation failed; repairing its quarantined candidate' \
  scripts/ralph-loop.sh \
  || fail "architecture-review validation failures still repeat the full critique"
rg -qF 'converting the validated grouped corrective into the one owner-preauthorized terminal finalizer' \
  scripts/ralph-loop.sh \
  || fail "convergence exhaustion has no bounded same-worktree terminal rewrite"
if sed -n '/review_status == RALPH_EXIT_REVIEW_CONVERGENCE/,/Architecture-review convergence is exhausted/p' \
    scripts/ralph-loop.sh | rg -q 'review_failures_this_loop=.*\+ 1'; then
  fail "terminal-finalizer admission still consumes the generic review repair budget"
fi
rg -qF 'RALPH_TERMINAL_FINALIZER_REWRITE' scripts/ralph-run.sh \
  || fail "terminal rewrite does not receive a narrow corrective prompt"
rg -qF 'one next-numbered CR-NNN terminal finalizer' scripts/ralph-run.sh \
  || fail "architecture reviewer is not instructed to use the standing terminal transition"
rg -qF 'Every generated corrective slice must declare exactly one `## Runtime Capabilities` section' \
  scripts/ralph-run.sh \
  || fail "architecture reviewer is not instructed to emit executable runtime contracts"
rg -qF 'run `ralph_validate_trusted_postgresql_acceptance` for every candidate' \
  scripts/ralph-run.sh \
  || fail "architecture reviewer is not instructed to preflight generated PostgreSQL contracts"
[[ -x scripts/ralph-supervise.sh ]] \
  || fail "unattended Ralph supervisor is missing or not executable"
rg -q 'ralph_repair_context_value' scripts/afk-dev.sh \
  || fail "AFK repair entrypoint does not load structured repair context"
rg -q -- '--resume-worktree' scripts/ralph-run.sh \
  || fail "Ralph run interface cannot resume a quarantined failed worktree"
rg -q 'ralph_write_repair_context' scripts/ralph-run.sh \
  || fail "failed validation does not publish structured same-worktree repair context"
rg -q 'COMMIT_FAILED: validated work' scripts/ralph-run.sh \
  || fail "post-validation commit failure is not fatal and repair-readable"
rg -q 'ralph_prepare_worktree_for_ff_merge' scripts/ralph-run.sh \
  || fail "Ralph does not clear safe generated-artifact collisions before merging"
rg -q 'repair_status == RALPH_EXIT_MERGE_FAILED' scripts/ralph-loop.sh \
  || fail "a post-validation merge failure can consume another product repair attempt"
rg -q "declaring 'localhost-e2e-server'.*'## Trusted Browser Acceptance'" scripts/ralph-run.sh \
  || fail "trusted browser prompt text is vulnerable to heredoc command substitution"
python3 - <<'PY'
from pathlib import Path
source = Path("scripts/ralph-run.sh").read_text()
commit = source.index('git commit -m "chore(${slice_id})')
clear = source.rindex('ralph_clear_repair_context')
if clear < commit:
    raise SystemExit("FAIL: repair context is cleared before validated work is committed")
PY
if rg -q 'total_failures' scripts/ralph-loop.sh; then
  fail "Ralph loop still accumulates repaired failures across unrelated slices"
fi
if rg -q 'Attempting one repair run|Repair run also failed' scripts/ralph-loop.sh; then
  fail "Ralph loop still hard-stops after one repair attempt"
fi

rg -q 'ralph_codex_permission_profile_for_slice' scripts/agent-adapters/codex.sh \
  || fail "Codex adapter does not select permissions from slice capabilities"
rg -q 'default_permissions=":workspace"' scripts/agent-adapters/codex.sh \
  || fail "ordinary Ralph runs do not explicitly retain workspace permissions"
rg -q 'permissions\.ralph-postgres\.network\.unix_sockets=\{"/tmp/\.s\.PGSQL\.5432"="allow"\}' scripts/agent-adapters/codex.sh \
  || fail "nested Ralph worktrees do not receive the explicit PostgreSQL socket override"
rg -q 'permissions\.ralph-localhost\.network\.domains=\{"localhost"="allow","127\.0\.0\.1"="allow"\}' scripts/agent-adapters/codex.sh \
  || fail "nested Ralph worktrees do not receive the explicit localhost override"
rg -q '"/tmp/\.s\.PGSQL\.5432"[[:space:]]*=[[:space:]]*"allow"' .codex/config.toml \
  || fail "PostgreSQL Unix socket is not narrowly allowlisted"
rg -q '"localhost"[[:space:]]*=[[:space:]]*"allow"' .codex/config.toml \
  || fail "localhost E2E traffic is not narrowly allowlisted"
rg -q 'localhost_e2e_required' scripts/ralph-validate.sh \
  || fail "independent validation does not select localhost E2E from the shared capability"
rg -q 'ralph_validate_trusted_browser_acceptance' scripts/ralph-validate.sh \
  || fail "independent validation does not validate the slice-specific browser contract"
rg -q 'run_trusted_browser_acceptance_once 1' scripts/ralph-validate.sh \
  || fail "first trusted slice-specific browser run is missing"
rg -q 'run_trusted_browser_acceptance_once 2' scripts/ralph-validate.sh \
  || fail "second trusted slice-specific browser run is missing"
rg -q 'RALPH_EVIDENCE_DIR' scripts/ralph-validate.sh \
  || fail "trusted browser acceptance does not receive the current run evidence directory"
rg -q 'ralph_trusted_e2e_screenshots' scripts/ralph-validate.sh \
  || fail "trusted browser acceptance does not verify declared screenshots"
rg -q "README E2E command does not resolve the shared venv" scripts/ralph-validate.sh \
  || fail "independent localhost E2E validation does not enforce the worktree-safe README command"
rg -q "Playwright does not pin the dashboard baseline timezone" scripts/ralph-validate.sh \
  || fail "independent localhost E2E validation does not enforce the fixed browser timezone"
rg -q "grep -Eq '\^\[\[:space:\]\]\*\[0-9\]" scripts/lib/ralph-fast-candidate-checks.sh \
  || fail "artifact validation does not distinguish a filled numbered plan from an untouched template"
rg -q 'slice does not declare localhost-e2e-server' scripts/ralph-validate.sh \
  || fail "ordinary slices do not explicitly skip the capability-only E2E gate"
rg -q 'do not declare the run failed solely because Chromium cannot launch' scripts/ralph-run.sh \
  || fail "coding-agent prompt does not delegate sandbox-blocked browser execution to trusted validation"
rg -q 'ralph_ensure_browser_runtime' scripts/ralph-run.sh \
  || fail "Ralph does not probe and recover browser infrastructure before E2E implementation"
rg -q 'RALPH_EXIT_BROWSER_INFRASTRUCTURE' scripts/ralph-run.sh \
  || fail "persistent browser infrastructure failure is not returned as a structured outcome"
rg -qF 'browser_infrastructure)' scripts/ralph-loop.sh \
  || fail "outer loop does not stop browser infrastructure failure outside product repair"
rg -q 'RALPH_SPLIT_SLICE_ID' scripts/ralph-loop.sh \
  || fail "outer loop does not launch a trusted oversized-slice queue rewrite"
rg -q 'RALPH_SPLIT_SLICE_ID' scripts/ralph-run.sh \
  || fail "Ralph run prompt does not distinguish queue splitting from architecture review"
rg -q 'RALPH_SPLIT_CORRECTIVE_RUN_ID' scripts/ralph-loop.sh \
  || fail "outer loop does not pass prior split diagnostics to a corrective planning attempt"
rg -q 'RALPH_SPLIT_CORRECTIVE_RUN_ID' scripts/ralph-run.sh \
  || fail "corrective split prompt does not consume the trusted prior failure run"
rg -q 'ralph_validate_oversized_slice_split' scripts/ralph-validate.sh \
  || fail "independent validation does not verify oversized-slice queue rewrites"
python3 - <<'PY'
from pathlib import Path

source = Path('scripts/ralph-run.sh').read_text()
probe = source.index('ralph_ensure_browser_runtime')
agent = source.index('scripts/agent-adapters/$agent.sh')
if probe > agent:
    raise SystemExit('FAIL: browser launch probe runs after the coding agent starts')

loop = Path('scripts/ralph-loop.sh').read_text()
detect = loop.index('ralph_oversized_slice_request')
repair = loop.rindex('run_bounded_repair "$status"')
if detect > repair:
    raise SystemExit('FAIL: diff-limit split is detected only after product repair starts')
trusted_retry = loop.index('ralph_oversized_split_retry_context')
corrective_context = loop.index("read -r corrective_run_id failure_signature", trusted_retry)
if trusted_retry > corrective_context:
    raise SystemExit('FAIL: corrective split context is consumed before it is validated')

runner = Path('scripts/ralph-run.sh').read_text()
if 'oversized-slice-split-results.md' not in runner or 'failure-summary.md' not in runner:
    raise SystemExit('FAIL: corrective split prompt omits prior independent validation evidence')
if 'ralph_write_repair_context' not in runner or 'if (( no_worktree == 0 )); then' not in runner:
    raise SystemExit('FAIL: failed split validation does not publish a trusted retry context')
if loop.count('if (( split_status == RALPH_EXIT_AGENT_LIMIT )); then') < 2:
    raise SystemExit('FAIL: second split-planning agent exhaustion loses the clean limit stop')
PY
rg -q 'postgresql-acceptance-validation-\$\{ordinal\}\.txt' scripts/ralph-validate.sh \
  || fail "independent PostgreSQL acceptance log path is missing"
rg -q 'run_postgresql_acceptance_once 1' scripts/ralph-validate.sh \
  || fail "independent first PostgreSQL acceptance run is missing"
rg -q 'run_postgresql_acceptance_once 2' scripts/ralph-validate.sh \
  || fail "independent second PostgreSQL acceptance run is missing"
rg -q 'SFPCL_POSTGRES_TEST_DB' scripts/ralph-validate.sh \
  || fail "PostgreSQL acceptance does not isolate its test database per validation run"
rg -q -- '--settings=sfpcl_credit.config.postgres_test_settings --noinput -v 2' scripts/ralph-validate.sh \
  || fail "PostgreSQL acceptance can still stop for interactive input"
if rg -q -- '--settings=sfpcl_credit.config.postgres_test_settings --keepdb' scripts/ralph-validate.sh; then
  fail "independent PostgreSQL acceptance still reuses cross-run schema state"
fi
rg -q 'postgres_acceptance_required' scripts/ralph-validate.sh \
  || fail "PostgreSQL validation is not selected from the shared capability declaration"
rg -q 'acceptance-only slice is eligible' scripts/lib/ralph-fast-candidate-checks.sh \
  || fail "006F4 no-op exception is not tied to verified acceptance"
rg -q 'validation_timeout_seconds' scripts/ralph-run.sh \
  || fail "independent validation does not have a configured timeout"
rg -q 'environment_setup_timeout_seconds' scripts/ralph-run.sh \
  || fail "dependency preparation does not have a configured timeout"
rg -q 'run_environment_command' scripts/ralph-run.sh \
  || fail "dependency preparation does not use the unattended watchdog"
rg -q 'ralph-run-with-timeout.py' scripts/ralph-run.sh \
  || fail "independent validation does not use the process-group watchdog"
rg -q 'validation-timeout-results.md' scripts/ralph-run.sh \
  || fail "validation timeout does not leave repair-readable evidence"
rg -q 'postgresql_drop_test_database' scripts/ralph-run.sh \
  || fail "validation timeout does not clean isolated PostgreSQL databases"
rg -q 'run_postgresql_timeout_cleanup' scripts/ralph-run.sh \
  || fail "PostgreSQL timeout cleanup is not routed through a bounded helper"
rg -q -- '--timeout 60' scripts/ralph-run.sh \
  || fail "PostgreSQL timeout cleanup does not have a short hard deadline"

watchdog="scripts/lib/ralph-run-with-timeout.py"
[[ -x "$watchdog" ]] || fail "missing executable validation watchdog"

set +e
python3 "$watchdog" --timeout 2 --label "regression prompt" -- \
  python3 -c 'input("interactive prompt: ")' \
  > "$fixture_dir/prompt.stdout" 2> "$fixture_dir/prompt.stderr"
prompt_rc=$?
set -e
[[ "$prompt_rc" == "1" ]] || fail "closed-stdin prompt did not fail fast (exit $prompt_rc)"
grep -qF 'EOFError: EOF when reading a line' "$fixture_dir/prompt.stderr" \
  || fail "validation watchdog did not close command stdin"

started_at="$(date +%s)"
set +e
python3 "$watchdog" --timeout 1 --grace 1 --label "regression hang" -- \
  python3 -c 'import time; time.sleep(30)' \
  > "$fixture_dir/hang.stdout" 2> "$fixture_dir/hang.stderr"
hang_rc=$?
set -e
elapsed=$(( $(date +%s) - started_at ))
[[ "$hang_rc" == "124" ]] || fail "hung validation did not return timeout status 124 (exit $hang_rc)"
(( elapsed < 10 )) || fail "hung validation was not terminated promptly (${elapsed}s)"
grep -qF "timed out after 1 seconds" "$fixture_dir/hang.stderr" \
  || fail "validation timeout did not identify the bounded wait"

grandchild_pid_file="$fixture_dir/grandchild.pid"
set +e
python3 "$watchdog" --timeout 1 --grace 1 --label "regression process group" -- \
  python3 -c 'import pathlib, subprocess, sys, time; child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"]); pathlib.Path(sys.argv[1]).write_text(str(child.pid)); time.sleep(30)' \
  "$grandchild_pid_file" \
  > "$fixture_dir/process-group.stdout" 2> "$fixture_dir/process-group.stderr"
process_group_rc=$?
set -e
[[ "$process_group_rc" == "124" ]] \
  || fail "process-group timeout did not return status 124 (exit $process_group_rc)"
[[ -s "$grandchild_pid_file" ]] || fail "process-group fixture did not start its grandchild"
grandchild_pid="$(cat "$grandchild_pid_file")"
for _ in {1..20}; do
  kill -0 "$grandchild_pid" 2>/dev/null || break
  sleep 0.1
done
if kill -0 "$grandchild_pid" 2>/dev/null; then
  fail "validation watchdog left descendant process $grandchild_pid running"
fi

[[ "$(ralph_outcome_for_status "$RALPH_EXIT_QUEUE_BLOCKED")" == "queue_blocked" ]] \
  || fail "queue-blocked status misclassified"

[[ -f scripts/lib/ralph-slice-selection.sh ]] || fail "missing dependency-aware slice selection helpers"
# shellcheck source=../lib/ralph-slice-selection.sh
source scripts/lib/ralph-slice-selection.sh

slices_fixture="$fixture_dir/slices"
mkdir -p "$slices_fixture"
make_fixture_slice() {
  local id="$1" status="$2"
  shift 2
  {
    echo "# Slice $id: Fixture"
    echo
    echo "## Status"
    echo "$status"
    echo
    echo "## Depends On"
    if (( $# == 0 )); then
      echo "- None"
    else
      printf -- '- %s\n' "$@"
    fi
    echo "Prose commentary in this section must never be parsed as a dependency."
  } > "$slices_fixture/$id-fixture.md"
}
make_fixture_slice 001A Complete
make_fixture_slice 001B "Not Started" "001A (annotation text after the id)"
make_fixture_slice 001C "Not Started" 001D
make_fixture_slice 001D "Not Started"
make_fixture_slice 001E "Not Started" 009Z
make_fixture_slice 001F Superseded
make_fixture_slice 001G "Not Started" 001F

split_repo="$fixture_dir/oversized-split-repo"
mkdir -p "$split_repo/docs/slices" "$split_repo/src"
git init -q "$split_repo"
git -C "$split_repo" config user.name "Ralph Regression"
git -C "$split_repo" config user.email "ralph-regression@example.invalid"
cat > "$split_repo/docs/slices/020A-prerequisite.md" <<'EOF'
## Status
Complete

## Depends On
- None
EOF
cat > "$split_repo/docs/slices/020B-oversized.md" <<'EOF'
## Status
Not Started

## Depends On
- 020A
EOF
cat > "$split_repo/docs/slices/020C-downstream.md" <<'EOF'
## Status
Not Started

## Depends On
- 020B
EOF
printf 'baseline product\n' > "$split_repo/src/base.py"
git -C "$split_repo" add docs/slices src/base.py
git -C "$split_repo" commit -qm fixture
python3 - "$split_repo/docs/slices/020B-oversized.md" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
path.write_text(path.read_text().replace('Not Started', 'Superseded', 1))
PY
cat > "$split_repo/docs/slices/020BA-owner-migration.md" <<'EOF'
## Status
Not Started

## Origin
Oversized slice: `020B`

## Depends On
- 020A
EOF
cat > "$split_repo/docs/slices/020BB-policy-closure.md" <<'EOF'
## Status
Not Started

## Origin
Oversized slice: `020B`

## Depends On
- 020BA
EOF
python3 - "$split_repo/docs/slices/020C-downstream.md" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
path.write_text(path.read_text().replace('- 020B\n', '- 020BB\n'))
PY
ralph_validate_oversized_slice_split "$split_repo" 020B \
  || fail "valid dependency-ordered oversized-slice split was rejected"
ralph_validate_oversized_split_change_scope "$split_repo" 020B \
  || fail "queue-only oversized split was rejected as a product change"
printf '\nunrelated rewrite\n' >> "$split_repo/docs/slices/020A-prerequisite.md"
split_failure_run="split-corrective-failure"
set +e
RALPH_SPLIT_SLICE_ID=020B scripts/ralph-validate.sh \
  --run-id "$split_failure_run" \
  --worktree "$split_repo" \
  --mode architecture_review \
  > "$fixture_dir/split-corrective-failure.stdout" \
  2> "$fixture_dir/split-corrective-failure.stderr"
split_failure_rc=$?
set -e
[[ "$split_failure_rc" == "$RALPH_EXIT_FAILED" ]] \
  || fail "unsafe split rewrite returned $split_failure_rc instead of validation failure"
split_failure_summary="$split_repo/.ralph/runs/$split_failure_run/failure-summary.md"
grep -qF 'Oversized-slice planning may not rewrite unrelated slice docs/slices/020A-prerequisite.md.' \
  "$split_failure_summary" \
  || fail "split failure summary omitted the exact offending ancestor path"
grep -qF 'oversized-slice-split-results.md' "$split_failure_summary" \
  || fail "split failure summary omitted its machine-readable gate identity"
if ralph_validate_oversized_split_change_scope "$split_repo" 020B >/dev/null 2>&1; then
  fail "oversized-slice planning accepted an unrelated slice rewrite"
fi
python3 - "$split_repo/docs/slices/020A-prerequisite.md" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
path.write_text(path.read_text().replace('\nunrelated rewrite\n', ''))
PY
printf 'unsafe\n' > "$split_repo/src/unsafe.py"
if ralph_validate_oversized_split_change_scope "$split_repo" 020B >/dev/null 2>&1; then
  fail "oversized-slice planning accepted a product-code change"
fi
rm -f "$split_repo/src/unsafe.py"
git -C "$split_repo" mv src/base.py docs/slices/020BD-hidden-product.md
if ralph_validate_oversized_split_change_scope "$split_repo" 020B >/dev/null 2>&1; then
  fail "oversized-slice planning hid a product deletion inside an allowed queue rename"
fi
git -C "$split_repo" mv docs/slices/020BD-hidden-product.md src/base.py

priority_fixture="$fixture_dir/priority-slices"
mkdir -p "$priority_fixture"
cat > "$priority_fixture/008M-ordinary.md" <<'EOF'
## Status
Not Started

## Depends On
- None
EOF
cat > "$priority_fixture/CR-900-emergency.md" <<'EOF'
## Status
Not Started

## Depends On
- None
EOF
[[ "$(ralph_first_grabbable_slice "$priority_fixture")" == "CR-900-emergency.md" ]] \
  || fail "accepted emergency CR was not selected before ordinary backlog work"
cat > "$priority_fixture/CR-900-emergency.md" <<'EOF'
## Status
Not Started

## Depends On
- 999Z
EOF
[[ "$(ralph_first_grabbable_slice "$priority_fixture" 2>/dev/null)" == "008M-ordinary.md" ]] \
  || fail "dependency-blocked emergency CR froze unrelated ordinary work"

[[ "$(ralph_slice_status "$slices_fixture/001A-fixture.md")" == "Complete" ]] \
  || fail "slice status helper misread a Complete slice"
[[ "$(ralph_slice_dependencies "$slices_fixture/001B-fixture.md")" == "001A" ]] \
  || fail "annotated dependency entry did not parse to its bare id"
[[ -z "$(ralph_slice_dependencies "$slices_fixture/001D-fixture.md")" ]] \
  || fail "'- None' was parsed as a real dependency"

metrics_fixture="$fixture_dir/queue-metrics"
mkdir -p "$metrics_fixture"
make_fixture_slice_at() {
  local target="$1" id="$2" status="$3"
  cat > "$target/$id-fixture.md" <<EOF
## Status
$status

## Depends On
- None
EOF
}
make_fixture_slice_at "$metrics_fixture" 001A Complete
make_fixture_slice_at "$metrics_fixture" 001B "Not Started"
make_fixture_slice_at "$metrics_fixture" 001C Blocked
make_fixture_slice_at "$metrics_fixture" 001D Superseded
cat > "$metrics_fixture/architecture-review.md" <<'EOF'
## Status
Complete

## Depends On
- None
EOF
[[ "$(ralph_queue_status_counts "$metrics_fixture")" == $'1\t1\t1\t1\t3' ]] \
  || fail "queue metrics did not exclude the architecture-review pseudo-slice or count statuses exactly"
[[ "$(ralph_slice_epic 009H9A-queued-advice)" == "009" ]] \
  || fail "slice epic helper did not identify a numbered product epic"
[[ -z "$(ralph_slice_epic CR-011-fix)" ]] \
  || fail "slice epic helper misclassified a change request as an epic boundary"

ralph_slice_unmet_dependencies "$slices_fixture/001B-fixture.md" "$slices_fixture" >/dev/null \
  || fail "slice with a Complete dependency was reported blocked"
ralph_slice_unmet_dependencies "$slices_fixture/001G-fixture.md" "$slices_fixture" >/dev/null \
  || fail "slice with a Superseded dependency was reported blocked"
if unmet="$(ralph_slice_unmet_dependencies "$slices_fixture/001C-fixture.md" "$slices_fixture")"; then
  fail "slice with a Not Started dependency was reported grabbable"
fi
[[ "$unmet" == "001D" ]] || fail "unmet dependency id was not reported (got: $unmet)"
if unmet="$(ralph_slice_unmet_dependencies "$slices_fixture/001E-fixture.md" "$slices_fixture")"; then
  fail "slice with a dangling dependency reference was reported grabbable"
fi
[[ "$unmet" == 009Z* ]] || fail "dangling dependency was not surfaced (got: $unmet)"

[[ "$(ralph_pending_slices "$slices_fixture")" == "001B-fixture.md
001C-fixture.md
001D-fixture.md
001E-fixture.md
001G-fixture.md" ]] || fail "pending-slice listing did not return Not Started slices in queue order"

# Queue lint: a healthy queue passes; malformed or undrainable queues are
# rejected with one problem line per finding.
lint_fixture="$fixture_dir/lint-slices"
mkdir -p "$lint_fixture"
make_lint_slice() {
  local id="$1" status="$2"
  shift 2
  {
    echo "# Slice $id: Fixture"
    echo
    echo "## Status"
    echo "$status"
    echo
    echo "## Depends On"
    if (( $# == 0 )); then
      echo "- None"
    else
      printf -- '- %s\n' "$@"
    fi
  } > "$lint_fixture/$id-fixture.md"
}
make_lint_slice 010A Complete
make_lint_slice 010B "Not Started" 010A
make_lint_slice 010C "Not Started" 010B
ralph_slice_queue_lint "$lint_fixture" >/dev/null \
  || fail "healthy slice queue failed the lint"

make_lint_slice 010D "Not Started" 010Z
if lint_out="$(ralph_slice_queue_lint "$lint_fixture")"; then
  fail "dangling dependency reference passed the lint"
fi
[[ "$lint_out" == *"010D"*"010Z"* ]] || fail "dangling reference was not named (got: $lint_out)"
rm "$lint_fixture/010D-fixture.md"

make_lint_slice 010E "Not Started" 010F
make_lint_slice 010F "Not Started" 010E
if lint_out="$(ralph_slice_queue_lint "$lint_fixture")"; then
  fail "dependency cycle passed the lint"
fi
[[ "$lint_out" == *"can never become eligible"* ]] || fail "cycle was not reported as undrainable (got: $lint_out)"
rm "$lint_fixture/010E-fixture.md" "$lint_fixture/010F-fixture.md"

printf '# Slice 010G: Fixture\n\n## Status\nNot Started\n' > "$lint_fixture/010G-fixture.md"
if lint_out="$(ralph_slice_queue_lint "$lint_fixture")"; then
  fail "pending slice without a Depends On section passed the lint"
fi
[[ "$lint_out" == *"no '## Depends On' section"* ]] || fail "missing Depends On section was not reported (got: $lint_out)"
rm "$lint_fixture/010G-fixture.md"

make_lint_slice 010H "Not started" 010A
if lint_out="$(ralph_slice_queue_lint "$lint_fixture")"; then
  fail "unrecognized status value passed the lint"
fi
[[ "$lint_out" == *"unrecognized status"* ]] || fail "status typo was not reported (got: $lint_out)"
rm "$lint_fixture/010H-fixture.md"

make_lint_slice 010I Blocked 010C
ralph_slice_queue_lint "$lint_fixture" >/dev/null \
  || fail "Blocked slice on a drainable chain failed the lint"

# Ambiguous dependency references: two slice files matching one id must fail
# the lint — selection would silently resolve to whichever sorts first.
make_lint_slice 010J "Not Started" 010K
make_lint_slice 010K Complete
cp "$lint_fixture/010K-fixture.md" "$lint_fixture/010K-fixture-duplicate.md"
if lint_out="$(ralph_slice_queue_lint "$lint_fixture")"; then
  fail "ambiguous dependency reference passed the lint"
fi
[[ "$lint_out" == *"ambiguous"* ]] || fail "ambiguity was not reported (got: $lint_out)"
rm "$lint_fixture/010J-fixture.md" "$lint_fixture/010K-fixture.md" "$lint_fixture/010K-fixture-duplicate.md"

# Remaining-work listing: Blocked slices are unfinished work, so a queue
# holding only Blocked slices must never read as complete.
make_fixture_slice 001H Blocked
remaining="$(ralph_remaining_slices "$slices_fixture")"
[[ "$remaining" == *"001H-fixture (Blocked)"* ]] || fail "remaining-slice listing omits Blocked slices"
[[ "$remaining" == *"001B-fixture (Not Started)"* ]] || fail "remaining-slice listing omits Not Started slices"

# Status transition rules: agents cannot change even their selected status;
# the orchestrator applies that transition after independent validation.
if ralph_slice_transition_allowed normal_run 001X-f 001X-f "Not Started" "Complete"; then
  fail "implementation agent was allowed to complete its selected slice"
fi
ralph_slice_transition_allowed normal_run 001X-f 001Y-f "Not Started" "Not Started" \
  || fail "unchanged status was rejected"
if ralph_slice_transition_allowed normal_run 001X-f 001Y-f "Not Started" "Complete"; then
  fail "a normal run completing a non-selected slice was allowed"
fi
if ralph_slice_transition_allowed repair 001X-f 001Y-f "Not Started" "Blocked"; then
  fail "a repair run re-parking a non-selected slice was allowed"
fi
ralph_slice_transition_allowed architecture_review architecture-review 001Y-f "Blocked" "Not Started" \
  || fail "a review unblocking a stale slice was rejected"
ralph_slice_transition_allowed architecture_review architecture-review 001Y-f "Not Started" "Superseded" \
  || fail "a review superseding a slice was rejected"
if ralph_slice_transition_allowed architecture_review architecture-review 001Y-f "Not Started" "Complete"; then
  fail "a review completing a slice was allowed"
fi

status_restore_repo="$fixture_dir/status-restore-repo"
mkdir -p "$status_restore_repo/docs/slices"
git init -q "$status_restore_repo"
git -C "$status_restore_repo" config user.name "Ralph Regression"
git -C "$status_restore_repo" config user.email "ralph-regression@example.invalid"
cat > "$status_restore_repo/docs/slices/001R-repair.md" <<'EOF'
# Repair fixture

## Status
Not Started

## Depends On
- None
EOF
git -C "$status_restore_repo" add .
git -C "$status_restore_repo" commit -qm fixture
rm "$status_restore_repo/docs/slices/001R-repair.md"
ralph_restore_selected_slice_status \
  "$status_restore_repo" docs/slices/001R-repair.md \
  || fail "deleted selected slice was not restored for repair"
git -C "$status_restore_repo" diff --quiet -- docs/slices/001R-repair.md \
  || fail "deleted selected slice was not restored exactly from HEAD"
printf '# malformed repair slice\n' > "$status_restore_repo/docs/slices/001R-repair.md"
ralph_restore_selected_slice_status \
  "$status_restore_repo" docs/slices/001R-repair.md \
  || fail "status-less selected slice was not restored for repair"
git -C "$status_restore_repo" diff --quiet -- docs/slices/001R-repair.md \
  || fail "status-less selected slice was not restored exactly from HEAD"
cat >> "$status_restore_repo/docs/slices/001R-repair.md" <<'EOF'

Sharpened requirement retained.
EOF
python3 - "$status_restore_repo/docs/slices/001R-repair.md" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
path.write_text(path.read_text().replace("Not Started", "Complete", 1))
PY
ralph_restore_selected_slice_status \
  "$status_restore_repo" docs/slices/001R-repair.md \
  || fail "selected status was not restored while preserving repair content"
grep -qF 'Sharpened requirement retained.' "$status_restore_repo/docs/slices/001R-repair.md" \
  || fail "status restoration discarded valid slice sharpening"
[[ "$(ralph_slice_status "$status_restore_repo/docs/slices/001R-repair.md")" == "Not Started" ]] \
  || fail "selected status restoration did not restore the HEAD value"

bookkeeping_trusted="$fixture_dir/bookkeeping-trusted"
bookkeeping_worktree="$fixture_dir/bookkeeping-worktree"
mkdir -p "$bookkeeping_trusted/.ralph" "$bookkeeping_worktree/.ralph"
printf '{"architecture_review_due": false}\n' > "$bookkeeping_trusted/.ralph/state.json"
printf 'trusted progress\n' > "$bookkeeping_trusted/.ralph/progress.md"
printf 'outside sentinel\n' > "$fixture_dir/bookkeeping-sentinel"
ln -s "$fixture_dir/bookkeeping-sentinel" "$bookkeeping_worktree/.ralph/state.json"
ln "$fixture_dir/bookkeeping-sentinel" "$bookkeeping_worktree/.ralph/progress.md"
ralph_restore_worktree_bookkeeping "$bookkeeping_trusted" "$bookkeeping_worktree" \
  || fail "trusted bookkeeping could not replace rejected repair files"
[[ ! -L "$bookkeeping_worktree/.ralph/state.json" ]] \
  || fail "bookkeeping restoration retained a state symlink"
cmp -s "$bookkeeping_trusted/.ralph/state.json" "$bookkeeping_worktree/.ralph/state.json" \
  || fail "bookkeeping restoration did not materialize trusted state"
cmp -s "$bookkeeping_trusted/.ralph/progress.md" "$bookkeeping_worktree/.ralph/progress.md" \
  || fail "bookkeeping restoration did not materialize trusted progress"
[[ "$(cat "$fixture_dir/bookkeeping-sentinel")" == "outside sentinel" ]] \
  || fail "bookkeeping restoration followed a link outside the worktree"

rm "$status_restore_repo/docs/slices/001R-repair.md"
printf 'slice sentinel\n' > "$fixture_dir/slice-sentinel"
ln -s "$fixture_dir/slice-sentinel" "$status_restore_repo/docs/slices/001R-repair.md"
ralph_restore_selected_slice_status \
  "$status_restore_repo" docs/slices/001R-repair.md \
  || fail "selected-slice restoration could not replace a rejected symlink"
[[ ! -L "$status_restore_repo/docs/slices/001R-repair.md" ]] \
  || fail "selected-slice restoration retained a candidate symlink"
[[ "$(cat "$fixture_dir/slice-sentinel")" == "slice sentinel" ]] \
  || fail "selected-slice restoration followed a link outside the worktree"
git -C "$status_restore_repo" diff --quiet -- docs/slices/001R-repair.md \
  || fail "symlinked selected slice was not restored exactly from HEAD"

# Zero-padded CR identifiers are decimal identifiers, not shell octal values.
# Intake after CR-008 must deterministically produce CR-009 without an
# arithmetic diagnostic or a duplicate identifier.
intake_repo="$fixture_dir/intake-repo"
mkdir -p "$intake_repo/scripts" \
  "$intake_repo/docs/change-requests/inbox" \
  "$intake_repo/docs/change-requests/accepted" \
  "$intake_repo/docs/slices"
git init -q "$intake_repo"
cp scripts/ralph-intake.sh "$intake_repo/scripts/ralph-intake.sh"
cat > "$intake_repo/docs/slices/CR-008-existing.md" <<'EOF'
# Slice CR-008: Existing

## Status
Complete
EOF
cat > "$intake_repo/docs/change-requests/inbox/decimal-numbering.md" <<'EOF'
# Decimal numbering fixture

## Type
bug-backend

## Severity
Low

## What Is Happening
The fixture reproduces zero-padded CR numbering.

## Expected Behaviour
The next identifier is decimal CR-009.

## Steps To Reproduce
1. Run intake after CR-008.

## Where It Appears
Ralph intake.

## Source Document Reference
unknown

## Acceptance Criteria
CR-009 is created without an arithmetic warning.
EOF
(
  cd "$intake_repo"
  ./scripts/ralph-intake.sh --now > intake.stdout 2> intake.stderr
)
[[ -f "$intake_repo/docs/slices/CR-009-decimal-numbering.md" ]] \
  || fail "intake did not treat zero-padded CR-008 as decimal when allocating CR-009"
[[ ! -s "$intake_repo/intake.stderr" ]] \
  || fail "intake emitted a zero-padded CR arithmetic diagnostic"

# Codex mode profiles must be executable configuration, not settings-file
# decoration. Resolution fails closed when a profile is missing or disallows
# the requested Ralph mode, while explicit compatible profiles remain usable.
profile_helper="scripts/lib/ralph-agent-profile.sh"
[[ -f "$profile_helper" ]] || fail "missing Codex profile resolver"
# shellcheck source=../lib/ralph-agent-profile.sh
source "$profile_helper"
profile_fixture="$fixture_dir/profile-config.yaml"
cat > "$profile_fixture" <<'EOF'
agent:
  codex:
    default_profile: default
    allow_model_override: true
    allow_effort_override: true
    allow_verbosity_override: true
    allow_xhigh: false
    approval_modes_allowed: [never]
    profiles:
      default:
        model: gpt-default
        reasoning_effort: medium
        verbosity: medium
        allowed_modes: [normal_run]
      fast:
        model: gpt-fast
        reasoning_effort: low
        verbosity: low
        allowed_modes: [normal_run, docs_only]
      repair:
        model: gpt-repair
        reasoning_effort: high
        verbosity: medium
        allowed_modes: [repair]
      architecture:
        model: gpt-architecture
        reasoning_effort: high
        verbosity: medium
        allowed_modes: [architecture_review]
EOF
[[ "$(ralph_codex_profile_values "$profile_fixture" '' normal_run)" == $'default\tgpt-default\tmedium\tmedium\tnever' ]] \
  || fail "normal mode did not resolve the configured default Codex profile"
[[ "$(ralph_codex_profile_values "$profile_fixture" '' repair)" == $'repair\tgpt-repair\thigh\tmedium\tnever' ]] \
  || fail "repair mode did not resolve the repair Codex profile"
[[ "$(ralph_codex_profile_values "$profile_fixture" '' architecture_review)" == $'architecture\tgpt-architecture\thigh\tmedium\tnever' ]] \
  || fail "architecture mode did not resolve the architecture Codex profile"
[[ "$(ralph_codex_profile_values "$profile_fixture" fast normal_run)" == $'fast\tgpt-fast\tlow\tlow\tnever' ]] \
  || fail "explicit compatible Codex profile was not honored"
[[ "$(ralph_codex_profile_values "$profile_fixture" '' normal_run \
      gpt-owner high low never)" == $'default\tgpt-owner\thigh\tlow\tnever' ]] \
  || fail "allowed Codex profile overrides were not validated and applied"
if ralph_codex_profile_values "$profile_fixture" '' normal_run \
    '' '' '' on-request >/dev/null 2>&1; then
  fail "Codex profile resolver admitted an interactive approval mode for an AFK run"
fi
if ralph_codex_profile_values "$profile_fixture" '' normal_run \
    '' xhigh '' '' >/dev/null 2>&1; then
  fail "Codex profile resolver allowed xhigh while protected configuration disables it"
fi
profile_locked_fixture="$fixture_dir/profile-config-locked.yaml"
sed 's/allow_model_override: true/allow_model_override: false/' \
  "$profile_fixture" > "$profile_locked_fixture"
if ralph_codex_profile_values "$profile_locked_fixture" '' normal_run \
    gpt-owner '' '' '' >/dev/null 2>&1; then
  fail "Codex profile resolver bypassed a disabled model override"
fi
if ralph_codex_profile_values "$profile_fixture" fast repair >/dev/null 2>&1; then
  fail "Codex profile resolver accepted a profile that disallows repair mode"
fi
rg -qF 'ralph_codex_profile_values' scripts/agent-adapters/codex.sh \
  || fail "Codex adapter does not apply configured profile values"
rg -qF '$trusted_repo_root/.ralph/config.yaml' scripts/agent-adapters/codex.sh \
  || fail "Codex adapter resolves protected profiles from an agent-modifiable worktree"
if rg -qF '$WORKTREE_DIR/.ralph/config.yaml' scripts/agent-adapters/codex.sh; then
  fail "Codex adapter still trusts quarantined worktree profile configuration"
fi
rg -qF 'clean_streak = int("$pre_run_arch_clean_streak")' scripts/ralph-run.sh \
  || fail "adaptive review cadence trusts agent-edited worktree state"
if rg -qF 'CODEX_ADDITIONAL_ARGS' scripts/agent-adapters/codex.sh; then
  fail "Codex adapter accepts unrestricted arguments after protected settings"
fi
rg -qF 'codex "${args[@]}" exec' scripts/agent-adapters/codex.sh \
  || fail "Codex adapter does not use a fixed exec subcommand"

adapter_repo="$fixture_dir/codex-adapter-repo"
adapter_run_dir="$adapter_repo/run"
adapter_fake_bin="$adapter_repo/fake-bin"
adapter_args="$adapter_repo/codex-argv.txt"
mkdir -p "$adapter_run_dir" "$adapter_fake_bin"
git init -q "$adapter_repo"
printf 'prompt fixture\n' > "$adapter_repo/prompt.md"
cat > "$adapter_fake_bin/codex" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$FAKE_CODEX_ARGS"
EOF
chmod +x "$adapter_fake_bin/codex"
PATH="$adapter_fake_bin:$PATH" \
FAKE_CODEX_ARGS="$adapter_args" \
CODEX_MODEL=gpt-owner \
CODEX_REASONING_EFFORT=high \
CODEX_VERBOSITY=low \
CODEX_APPROVAL_MODE=never \
CODEX_ADDITIONAL_ARGS='--model injected --ask-for-approval on-request exec' \
RALPH_RAW_AGENT_LOG_ROOT="$adapter_repo/raw-agent-logs" \
RALPH_ALLOW_EXTERNAL_AGENT_LOG_ROOT=true \
RALPH_AGENT_HEARTBEAT_SECONDS=1 \
RUN_ID=adapter-argv-run \
RUN_DIR="$adapter_run_dir" \
WORKTREE_DIR="$adapter_repo" \
PROMPT_FILE="$adapter_repo/prompt.md" \
MODE=normal_run \
SELECTED_SLICE=010A-loan-account-schedule-and-ledger \
scripts/agent-adapters/codex.sh > "$adapter_repo/adapter.stdout" \
  || fail "Codex adapter argv-capture fixture failed"
python3 - "$adapter_args" <<'PY'
import sys
from pathlib import Path

args = Path(sys.argv[1]).read_text().splitlines()
if args[-1:] != ["exec"] or args.count("exec") != 1:
    raise SystemExit(f"FAIL: Codex adapter did not apply one final exec subcommand: {args}")
if "injected" in args or "on-request" in args or "--dangerously-bypass-approvals-and-sandbox" in args:
    raise SystemExit(f"FAIL: unrestricted Codex arguments reached the CLI: {args}")
if args[args.index("--model") + 1] != "gpt-owner":
    raise SystemExit(f"FAIL: validated model was not applied: {args}")
if args[args.index("--ask-for-approval") + 1] != "never":
    raise SystemExit(f"FAIL: headless approval mode was not applied: {args}")
PY

# Prompt ownership and context discipline: implementation agents own
# substantive code/evidence; the orchestrator owns mechanical queue state.
runner="scripts/ralph-run.sh"
rg -qF 'The orchestrator owns changed-files.txt, .ralph/state.json, .ralph/progress.md, the selected slice Status transition, and mechanical handoff/progress bookkeeping.' "$runner" \
  || fail "run prompt does not assign mechanical bookkeeping to the orchestrator"
rg -qF 'slice_file="architecture-review.md"' "$runner" \
  || fail "architecture-review runner has no concrete pseudo-slice before worktree restoration"
if rg -qF -- '- Save changed-files.txt.' "$runner"; then
  fail "run prompt still asks the implementation agent to regenerate changed-files.txt"
fi
if rg -qF -- '- Update state, progress, handoff, and slice status.' "$runner"; then
  fail "run prompt still asks the implementation agent to duplicate orchestrator state transitions"
fi
if rg -qF "Before finishing, sharpen the next 1-2 'Not Started' slice files" "$runner"; then
  fail "run prompt still expands implementation sessions into unrelated future-slice sharpening"
fi
rg -qF 'Read only the digest shared invariants and the selected slice section by default.' "$runner" \
  || fail "run prompt does not bound epic-digest reads to the selected slice"
rg -qF 'After roughly 500 changed lines, use diff stats and targeted hunks; never repeatedly print the complete cumulative diff.' "$runner" \
  || fail "run prompt does not prevent cumulative diff churn"
rg -qF 'Only Critical/High correctness, security, financial/data-integrity, or binding source-contract findings create immediate corrective work.' "$runner" \
  || fail "architecture-review prompt does not enforce severity-based queue admission"
rg -qF 'Report findings closed, new findings by severity, and corrective slices added' "$runner" \
  || fail "architecture-review prompt omits convergence metrics"
rg -qF "set the review-packet.md Result section to exactly 'Ready for independent validation'" "$runner" \
  || fail "run prompt does not safely state the exact agent-declared result"
if rg -qF 'review-packet.md `## Result`' "$runner"; then
  fail "unquoted prompt heredoc can execute review result backticks"
fi
rg -qF 'ralph_architecture_review_new_corrective_count' scripts/ralph-validate.sh \
  || fail "validator does not enforce the new corrective-slice queue contract"
rg -qF 'ralph_architecture_review_existing_corrective_count' scripts/ralph-validate.sh \
  || fail "validator cannot map findings to existing corrective work"
rg -qF 'Refusing to declare final completion.' scripts/ralph-loop.sh \
  || fail "loop can declare final completion while a mandatory review remains due"
rg -qF 'product work is empty but the mandatory final architecture review remains due.' scripts/ralph-loop.sh \
  || fail "iteration exhaustion can return success with a failed final review"
rg -qF 'max_iterations="${1:-250}"' scripts/ralph-loop.sh \
  || fail "default Ralph loop budget cannot drain the prepared remaining queue"
rg -qF 'exit "$RALPH_EXIT_ITERATION_LIMIT"' scripts/ralph-loop.sh \
  || fail "max-iteration exhaustion reports success for unfinished work"
rg -qF 'ralph_architecture_review_effective_due' scripts/ralph-loop.sh \
  || fail "loop does not use the read-only fail-closed architecture-review decision"
rg -qF 'Owner/architecture preparation maintains an 8-10 slice ready runway' AGENTS.md \
  || fail "repository rules do not assign future-slice preparation to a bounded planning lane"
if rg -qF 'Before finishing, sharpen the next 1-2 `Not Started` slice files' AGENTS.md; then
  fail "repository rules still expand every implementation session into future-slice preparation"
fi
if rg -qF 'Update state, progress, handoff, and slice status.' AGENTS.md; then
  fail "repository rules still assign mechanical bookkeeping to implementation agents"
fi
rg -qF 'state = json.loads(trusted_path.read_text())' scripts/ralph-run.sh \
  || fail "orchestrator rebuilds successful state from an agent-modifiable candidate"
rg -qF 'ralph_architecture_review_finalizer_contract' scripts/ralph-run.sh \
  || fail "runner does not validate the protected exhausted-cycle finalizer"
rg -qF 'ralph-validate-review-closure.sh' scripts/ralph-run.sh \
  || fail "corrective agent prompt omits the fast semantic-closure preflight"
rg -qF 'rerun the exact named validator until it passes' scripts/ralph-run.sh \
  || fail "repair prompt still stops after the first error from one validator"
rg -qF 'ralph_finalize_architecture_review_cycle' scripts/ralph-run.sh \
  || fail "runner does not close a validated finalizer without another immediate review"
rg -qF 'COMMIT_QUARANTINED: post-commit integrity failure' scripts/ralph-run.sh \
  || fail "post-commit failures can re-enter incompatible product repair"
rg -qF 'if (( no_worktree == 0 ))' scripts/ralph-run.sh \
  || fail "no-worktree commit failure can dereference an unset quarantine branch"
rg -qF 'if (( no_worktree == 0 )); then' scripts/ralph-run.sh \
  || fail "no-worktree validation failure can publish non-resumable repair context"
if rg -qF 'prior_due or cadence_due' scripts/ralph-run.sh; then
  fail "inline due logic bypasses the tested mandatory-review transition helper"
fi

echo "PASS: Ralph workflow regressions"
