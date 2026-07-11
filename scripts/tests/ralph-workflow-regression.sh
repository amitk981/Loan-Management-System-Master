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

# Agent output is untrusted text. It must never drive loop control flow.
if rg -n 'grep -q .*No eligible slice found|grep -q .*has been vetoed by the owner|grep -q .*MERGE_FAILED|grep -q .*AGENT_LIMIT_EXHAUSTED' scripts/ralph-loop.sh; then
  fail "ralph-loop.sh still derives control flow from agent transcript text"
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
[[ "$(rg -o 'npm run e2e -- e2e/tracer\.e2e\.spec\.ts e2e/auth-negative\.e2e\.spec\.ts' scripts/ralph-validate.sh | wc -l | xargs)" == "2" ]] \
  || fail "independent localhost E2E validation does not run both dashboard specs twice"
[[ "$(rg -o -- '--grep \\"zero-permission staff\|logs in, walks\\"' scripts/ralph-validate.sh | wc -l | xargs)" == "2" ]] \
  || fail "independent localhost E2E validation is not scoped to the two dashboard scenarios"
rg -q 'slice does not declare localhost-e2e-server' scripts/ralph-validate.sh \
  || fail "ordinary slices do not explicitly skip the capability-only E2E gate"
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

echo "PASS: Ralph workflow regressions"
