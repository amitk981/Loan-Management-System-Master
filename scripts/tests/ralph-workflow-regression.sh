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
printf 'branch version\n' > "$merge_repo/conflict.txt"
git -C "$merge_repo" add .ralph/runs/failed-run/evidence.md conflict.txt
git -C "$merge_repo" commit -qm completed
git -C "$merge_repo" switch -q integration
mkdir -p "$merge_repo/.ralph/runs/failed-run"
printf 'identical evidence\n' > "$merge_repo/.ralph/runs/failed-run/evidence.md"
printf 'owner version\n' > "$merge_repo/conflict.txt"
if ralph_remove_identical_untracked_merge_collisions "$merge_repo" completed-slice >/dev/null 2>&1; then
  fail "merge guard accepted a differing untracked collision"
fi
[[ -e "$merge_repo/.ralph/runs/failed-run/evidence.md" ]] \
  || fail "merge guard partially cleaned files after finding a differing collision"
[[ "$(cat "$merge_repo/conflict.txt")" == "owner version" ]] \
  || fail "merge guard changed a differing untracked file"
rm "$merge_repo/conflict.txt"
ralph_remove_identical_untracked_merge_collisions "$merge_repo" completed-slice \
  || fail "merge guard rejected a clean branch after identical collisions were removed"
git -C "$merge_repo" merge --ff-only -q completed-slice \
  || fail "merge still failed after safe collision cleanup"

[[ -f scripts/lib/ralph-repair-context.sh ]] || fail "missing same-worktree repair context helper"
# shellcheck source=../lib/ralph-repair-context.sh
source scripts/lib/ralph-repair-context.sh
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

# Agent output is untrusted text. It must never drive loop control flow.
if rg -n 'grep -q .*No eligible slice found|grep -q .*has been vetoed by the owner|grep -q .*MERGE_FAILED|grep -q .*AGENT_LIMIT_EXHAUSTED' scripts/ralph-loop.sh; then
  fail "ralph-loop.sh still derives control flow from agent transcript text"
fi
rg -q 'ralph_max_repair_attempts' scripts/ralph-loop.sh \
  || fail "Ralph loop ignores run.max_retries"
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
rg -q 'ralph_repair_context_value' scripts/afk-dev.sh \
  || fail "AFK repair entrypoint does not load structured repair context"
rg -q -- '--resume-worktree' scripts/ralph-run.sh \
  || fail "Ralph run interface cannot resume a quarantined failed worktree"
rg -q 'ralph_write_repair_context' scripts/ralph-run.sh \
  || fail "failed validation does not publish structured same-worktree repair context"
rg -q 'COMMIT_FAILED: validated work' scripts/ralph-run.sh \
  || fail "post-validation commit failure is not fatal and repair-readable"
rg -q 'ralph_remove_identical_untracked_merge_collisions' scripts/ralph-run.sh \
  || fail "Ralph does not clear safe generated-artifact collisions before merging"
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
rg -q "grep -Eq '\^\[\[:space:\]\]\*\[0-9\]" scripts/ralph-validate.sh \
  || fail "artifact validation does not distinguish a filled numbered plan from an untouched template"
rg -q 'slice does not declare localhost-e2e-server' scripts/ralph-validate.sh \
  || fail "ordinary slices do not explicitly skip the capability-only E2E gate"
rg -q 'do not declare the run failed solely because Chromium cannot launch' scripts/ralph-run.sh \
  || fail "coding-agent prompt does not delegate sandbox-blocked browser execution to trusted validation"
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
rg -q 'verified acceptance-only slice' scripts/ralph-validate.sh \
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

[[ "$(ralph_slice_status "$slices_fixture/001A-fixture.md")" == "Complete" ]] \
  || fail "slice status helper misread a Complete slice"
[[ "$(ralph_slice_dependencies "$slices_fixture/001B-fixture.md")" == "001A" ]] \
  || fail "annotated dependency entry did not parse to its bare id"
[[ -z "$(ralph_slice_dependencies "$slices_fixture/001D-fixture.md")" ]] \
  || fail "'- None' was parsed as a real dependency"

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

# Status transition rules: only the executed slice may change status, and no
# run may complete a slice it did not execute.
ralph_slice_transition_allowed normal_run 001X-f 001X-f "Not Started" "Complete" \
  || fail "selected slice completion was rejected"
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

echo "PASS: Ralph workflow regressions"
