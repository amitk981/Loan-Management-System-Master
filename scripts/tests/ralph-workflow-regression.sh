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
cat > "$fixture_dir/unknown-capability.md" <<'EOF'
## Runtime Capabilities
- `unrestricted-network`
EOF

[[ "$(ralph_codex_permission_profile_for_slice "$fixture_dir/future-postgres-slice.md")" == "ralph-postgres" ]] \
  || fail "future PostgreSQL slice did not select the scoped socket profile"
[[ "$(ralph_codex_permission_profile_for_slice "$fixture_dir/ordinary-slice.md")" == ":workspace" ]] \
  || fail "ordinary slice did not retain workspace permissions"
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
rg -q '"/tmp/\.s\.PGSQL\.5432"[[:space:]]*=[[:space:]]*"allow"' .codex/config.toml \
  || fail "PostgreSQL Unix socket is not narrowly allowlisted"
rg -q 'postgresql-acceptance-validation-\$\{ordinal\}\.txt' scripts/ralph-validate.sh \
  || fail "independent PostgreSQL acceptance log path is missing"
rg -q 'run_postgresql_acceptance_once 1' scripts/ralph-validate.sh \
  || fail "independent first PostgreSQL acceptance run is missing"
rg -q 'run_postgresql_acceptance_once 2' scripts/ralph-validate.sh \
  || fail "independent second PostgreSQL acceptance run is missing"
rg -q 'postgres_acceptance_required' scripts/ralph-validate.sh \
  || fail "PostgreSQL validation is not selected from the shared capability declaration"
rg -q 'verified acceptance-only slice' scripts/ralph-validate.sh \
  || fail "006F4 no-op exception is not tied to verified acceptance"

echo "PASS: Ralph workflow regressions"
