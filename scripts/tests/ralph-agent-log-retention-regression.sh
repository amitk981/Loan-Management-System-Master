#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

fixture_dir="$(mktemp -d)"
trap 'rm -rf "$fixture_dir"' EXIT

# shellcheck source=../lib/ralph-agent-log.sh
source scripts/lib/ralph-agent-log.sh

repo="$fixture_dir/repo"
root="$fixture_dir/raw"
git init -q "$repo"
git -C "$repo" config user.name "Ralph Regression"
git -C "$repo" config user.email "ralph-regression@example.invalid"
printf 'fixture\n' > "$repo/tracked.txt"
git -C "$repo" add tracked.txt
git -C "$repo" commit -qm fixture

mkdir -p "$root/old-run" "$root/new-run"
printf '12345678' > "$root/old-run/codex.log"
printf 'abcdefgh' > "$root/new-run/codex.log"
python3 - "$root/old-run" "$root/new-run" <<'PY'
import os
import sys
import time

now = time.time()
os.utime(sys.argv[1], (now - 200, now - 200))
os.utime(sys.argv[2], (now - 100, now - 100))
PY

RALPH_RAW_AGENT_LOG_ROOT="$root" \
RALPH_ALLOW_EXTERNAL_AGENT_LOG_ROOT=true \
RALPH_RAW_AGENT_LOG_RETENTION_DAYS=365 \
RALPH_RAW_AGENT_LOG_RETENTION_COUNT=20 \
RALPH_RAW_AGENT_LOG_RETENTION_BYTES=10 \
  ralph_prepare_agent_log "$repo" current-run codex

[[ ! -d "$root/old-run" ]] \
  || fail "byte retention cap did not prune the oldest raw run"
[[ -d "$root/new-run" && -d "$root/current-run" ]] \
  || fail "byte retention cap removed the newest or current run"

if RALPH_RAW_AGENT_LOG_ROOT="$root" \
    RALPH_ALLOW_EXTERNAL_AGENT_LOG_ROOT=true \
    RALPH_RAW_AGENT_LOG_RETENTION_BYTES=invalid \
    ralph_prepare_agent_log "$repo" invalid-cap codex >/dev/null 2>&1; then
  fail "invalid byte retention value failed open"
fi

summary="$fixture_dir/summary.md"
printf 'bounded raw log\n' > "$RALPH_AGENT_RAW_LOG"
RALPH_RAW_AGENT_LOG_RETENTION_BYTES=10 \
  ralph_write_agent_log_summary "$RALPH_AGENT_RAW_LOG" "$summary" codex 0
grep -qF '10 bytes' "$summary" \
  || fail "compact summary does not disclose the raw-log byte cap"

echo "PASS: Ralph raw agent-log retention is bounded by total bytes."
