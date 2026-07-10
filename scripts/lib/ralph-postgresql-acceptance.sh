#!/usr/bin/env bash

postgresql_acceptance_log_passes() {
  local log="${1:?acceptance log is required}"
  grep -qF "Found 5 test(s)." "$log" \
    && grep -qE '^Ran 5 tests in ' "$log" \
    && grep -qE '^OK$' "$log" \
    && ! grep -qiE 'skipped|Operation not permitted|OperationalError|connection .*failed|setup failure|FAILED \(' "$log"
}
