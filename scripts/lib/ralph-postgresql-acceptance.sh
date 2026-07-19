#!/usr/bin/env bash

ralph_trusted_postgresql_acceptance_entries() {
  local slice_file="${1:?slice file is required}"

  awk '
    $0 == "## Trusted PostgreSQL Acceptance" { in_acceptance = 1; next }
    in_acceptance && /^## / { exit }
    in_acceptance {
      line = $0
      sub(/^[[:space:]]*-[[:space:]]*/, "", line)
      gsub(/`/, "", line)
      sub(/^[[:space:]]+/, "", line)
      sub(/[[:space:]]+$/, "", line)
      if (length(line) > 0) print line
    }
  ' "$slice_file"
}

ralph_trusted_postgresql_test_labels() {
  local slice_file="${1:?slice file is required}"
  local entry=""

  while IFS= read -r entry; do
    case "$entry" in
      "Test: "*) printf '%s\n' "${entry#Test: }" ;;
    esac
  done < <(ralph_trusted_postgresql_acceptance_entries "$slice_file")
}

ralph_trusted_postgresql_expected_count() {
  local slice_file="${1:?slice file is required}"
  local entry=""

  while IFS= read -r entry; do
    case "$entry" in
      "Expected tests: "*) printf '%s\n' "${entry#Expected tests: }" ;;
    esac
  done < <(ralph_trusted_postgresql_acceptance_entries "$slice_file")
}

ralph_validate_trusted_postgresql_acceptance() {
  local slice_file="${1:?slice file is required}"
  local entry=""
  local value=""
  local label_count=0
  local expected_count_entries=0
  local seen_labels=""
  local problem_count=0

  while IFS= read -r entry; do
    case "$entry" in
      "Test: "*)
        value="${entry#Test: }"
        if [[ ! "$value" =~ ^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$ ]]; then
          echo "Invalid trusted PostgreSQL test label '$value' in $slice_file; use an exact dotted Django test label." >&2
          problem_count=$((problem_count + 1))
        elif printf '%s\n' "$seen_labels" | grep -Fxq "$value"; then
          echo "Duplicate trusted PostgreSQL test label '$value' in $slice_file." >&2
          problem_count=$((problem_count + 1))
        else
          label_count=$((label_count + 1))
          seen_labels="${seen_labels}${seen_labels:+$'\n'}${value}"
        fi
        ;;
      "Expected tests: "*)
        value="${entry#Expected tests: }"
        expected_count_entries=$((expected_count_entries + 1))
        if [[ ! "$value" =~ ^[1-9][0-9]*$ ]]; then
          echo "Invalid trusted PostgreSQL expected test count '$value' in $slice_file; use a positive integer." >&2
          problem_count=$((problem_count + 1))
        fi
        ;;
      *)
        echo "Unknown trusted PostgreSQL acceptance entry '$entry' in $slice_file." >&2
        problem_count=$((problem_count + 1))
        ;;
    esac
  done < <(ralph_trusted_postgresql_acceptance_entries "$slice_file")

  if (( label_count == 0 )); then
    echo "Slice $slice_file declares PostgreSQL acceptance but no valid Test entry." >&2
    problem_count=$((problem_count + 1))
  fi
  if (( expected_count_entries != 1 )); then
    echo "Slice $slice_file must declare exactly one 'Expected tests: N' PostgreSQL acceptance entry." >&2
    problem_count=$((problem_count + 1))
  fi

  (( problem_count == 0 ))
}

postgresql_acceptance_log_passes() {
  local log="${1:?acceptance log is required}"
  local expected_count="${2:-5}"
  [[ "$expected_count" =~ ^[1-9][0-9]*$ ]] || return 1
  grep -qF "Found $expected_count test(s)." "$log" \
    && grep -qE "^Ran $expected_count tests? in " "$log" \
    && grep -qE '^OK$' "$log" \
    && ! grep -qiE 'skipped|Operation not permitted|OperationalError|connection .*failed|setup failure|FAILED \(' "$log"
}

postgresql_test_database_name() {
  local run_id="${1:?run id is required}"
  local ordinal="${2:?acceptance ordinal is required}"
  local database_name
  # Keep the ordinal before the variable-length run id so truncation can never
  # make the two independent repetitions share a database.
  database_name="$(printf 'test_sfpcl_credit_%s_%s' "$ordinal" "$run_id" | tr -c '[:alnum:]_' '_')"
  printf '%s\n' "${database_name:0:63}"
}

postgresql_drop_test_database() {
  local python_bin="${1:?python executable is required}"
  local worktree_dir="${2:?worktree directory is required}"
  local database_name="${3:?test database name is required}"

  (
    cd "$worktree_dir"
    DJANGO_SETTINGS_MODULE=sfpcl_credit.config.postgres_test_settings \
      "$python_bin" - "$database_name" <<'PY'
import re
import sys

import django

database_name = sys.argv[1]
if not re.fullmatch(r"test_sfpcl_credit_[a-zA-Z0-9_]+", database_name):
    raise SystemExit(f"Refusing to drop unsafe test database name: {database_name}")

django.setup()
from django.db import connection

with connection._nodb_cursor() as cursor:
    cursor.execute(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)')
PY
  )
}

postgresql_environment_probe() {
  local python_bin="${1:?python executable is required}"
  local worktree_dir="${2:?worktree directory is required}"

  (
    cd "$worktree_dir"
    DJANGO_SETTINGS_MODULE=sfpcl_credit.config.postgres_test_settings "$python_bin" - <<'PY'
import django

django.setup()
from django.db import connection

config = connection.settings_dict
print(f"- Engine: {config.get('ENGINE', '')}")
print(f"- Database: {config.get('NAME', '')}")
print(f"- Test database: {config.get('TEST', {}).get('NAME', '')}")
print(f"- Host: {config.get('HOST') or '(local Unix socket)'}")
print(f"- Port: {config.get('PORT') or '5432'}")
with connection._nodb_cursor() as cursor:
    cursor.execute("SELECT current_database(), current_setting('server_version')")
    maintenance_database, server_version = cursor.fetchone()
print(f"- PostgreSQL maintenance database: {maintenance_database}")
print(f"- PostgreSQL server version: {server_version}")
PY
  )
}
