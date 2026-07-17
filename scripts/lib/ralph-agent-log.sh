#!/usr/bin/env bash

# Full agent transcripts are useful for short-lived operator diagnosis but are
# too large to commit into every Ralph run. Keep them under the repository's
# common Git directory (outside every worktree candidate), prune them with a
# bounded retention policy, and commit only the compact summary written below.

ralph_prepare_agent_log() {
  local worktree="${1:?worktree is required}"
  local run_id="${2:?run id is required}"
  local agent="${3:?agent name is required}"
  local common_dir root resolved_root

  if ! [[ "$run_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ \
      && "$agent" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
    echo "Refusing unsafe agent-log run or agent name." >&2
    return 1
  fi

  common_dir="$(git -C "$worktree" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" \
    || return 1
  root="${RALPH_RAW_AGENT_LOG_ROOT:-$common_dir/ralph-agent-logs}"
  [[ -n "$root" && "$root" != "/" ]] || return 1
  mkdir -p "$root"
  resolved_root="$(cd "$root" && pwd -P)" || return 1
  case "$resolved_root/" in
    "$common_dir/"*) ;;
    *)
      if [[ "${RALPH_ALLOW_EXTERNAL_AGENT_LOG_ROOT:-false}" != "true" ]]; then
        echo "Refusing agent-log root outside the common Git directory: $resolved_root" >&2
        return 1
      fi
      ;;
  esac
  root="$resolved_root"
  mkdir -p "$root/$run_id"
  touch "$root/$run_id"

  RALPH_AGENT_LOG_ROOT="$root"
  RALPH_AGENT_RAW_LOG="$root/$run_id/${agent}.log"
  export RALPH_AGENT_LOG_ROOT RALPH_AGENT_RAW_LOG

  python3 - "$root" "$run_id" \
    "${RALPH_RAW_AGENT_LOG_RETENTION_DAYS:-14}" \
    "${RALPH_RAW_AGENT_LOG_RETENTION_COUNT:-20}" <<'PY'
import shutil
import sys
import time
from pathlib import Path

root = Path(sys.argv[1]).resolve()
current_run_id = sys.argv[2]
try:
    retention_days = max(0, int(sys.argv[3]))
    retention_count = max(1, int(sys.argv[4]))
except ValueError:
    raise SystemExit("invalid Ralph raw-agent-log retention value")

current = (root / current_run_id).resolve()
now = time.time()
directories = sorted(
    (path for path in root.iterdir() if path.is_dir()),
    key=lambda path: path.stat().st_mtime,
    reverse=True,
)
retained = 0
for directory in directories:
    resolved = directory.resolve()
    if resolved == current:
        retained += 1
        continue
    age_days = (now - directory.stat().st_mtime) / 86_400
    if age_days > retention_days or retained >= retention_count:
        shutil.rmtree(directory)
    else:
        retained += 1
PY
}

ralph_write_agent_log_summary() {
  local raw_log="${1:?raw log is required}"
  local summary="${2:?summary path is required}"
  local agent="${3:?agent name is required}"
  local status="${4:?agent status is required}"
  local bytes lines digest session_id

  [[ -f "$raw_log" ]] || : > "$raw_log"
  bytes="$(wc -c < "$raw_log" | xargs)"
  lines="$(wc -l < "$raw_log" | xargs)"
  digest="$(python3 - "$raw_log" <<'PY'
import hashlib
import sys
from pathlib import Path

digest = hashlib.sha256()
with Path(sys.argv[1]).open("rb") as stream:
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
print(digest.hexdigest())
PY
)"
  session_id="$(python3 - "$raw_log" <<'PY'
import re
import sys
from pathlib import Path

pattern = re.compile(
    r"session id:\s*([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.IGNORECASE,
)
match = None
with Path(sys.argv[1]).open(errors="ignore") as stream:
    for line in stream:
        match = pattern.search(line)
        if match:
            break
print(match.group(1) if match else "unavailable")
PY
)"

  mkdir -p "$(dirname "$summary")"
  {
    echo "# Agent Log Summary"
    echo
    echo "Agent: $agent"
    echo "Exit code: $status"
    echo "Bytes: $bytes"
    echo "Lines: $lines"
    echo "SHA-256: $digest"
    echo "Session ID: $session_id"
    echo "Raw retention: operator-local, at most ${RALPH_RAW_AGENT_LOG_RETENTION_COUNT:-20} runs or ${RALPH_RAW_AGENT_LOG_RETENTION_DAYS:-14} days."
    echo
    echo "## Final Excerpt"
    echo
    tail -n "${RALPH_AGENT_LOG_SUMMARY_LINES:-80}" "$raw_log" 2>/dev/null \
      | cut -c1-500 || true
  } > "$summary"
}
