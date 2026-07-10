#!/usr/bin/env bash

postgresql_acceptance_log_passes() {
  local log="${1:?acceptance log is required}"
  grep -qF "Found 5 test(s)." "$log" \
    && grep -qE '^Ran 5 tests in ' "$log" \
    && grep -qE '^OK$' "$log" \
    && ! grep -qiE 'skipped|Operation not permitted|OperationalError|connection .*failed|setup failure|FAILED \(' "$log"
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
