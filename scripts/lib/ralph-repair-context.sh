#!/usr/bin/env bash

# Structured handoff between a failed independent validation and a bounded
# repair attempt. The context is written by the trusted orchestrator in the
# integration checkout; coding agents cannot alter it from their worktrees.

ralph_failure_signature() {
  local failure_summary="${1:?failure summary path is required}"
  python3 - "$failure_summary" <<'PY'
import hashlib
import re
import sys
from pathlib import Path

summary = Path(sys.argv[1]).resolve()
if not summary.is_file():
    raise SystemExit(f"missing failure summary: {summary}")

run_dir = summary.parent
interesting = []
for line in summary.read_text(errors="replace").splitlines():
    if "FAIL:" in line or line.startswith("# Validation Failure Summary"):
        interesting.append(line)

log_dir = run_dir / "evidence" / "terminal-logs"
patterns = (
    "Error:", "Test timeout", "timed out", "waiting for", "locator.",
    "getByRole", "getByText", "strict mode", "Exit code:", "FATAL:",
    "Traceback", "FAILED (",
)
for log in sorted(log_dir.glob("trusted-browser-acceptance-*.log")):
    for line in log.read_text(errors="replace").splitlines():
        if any(pattern in line for pattern in patterns):
            interesting.append(line)

if not interesting:
    interesting = summary.read_text(errors="replace").splitlines()

normalized = []
for line in interesting:
    line = re.sub(r"/\.ralph/worktrees/[^/]+", "/.ralph/worktrees/<run>", line)
    line = re.sub(r"/\.ralph/runs/[^/]+", "/.ralph/runs/<run>", line)
    line = re.sub(r"\b\d{4}-\d{2}-\d{2}_\d{6}_(?:normal_run|repair|architecture_review)\b", "<run>", line)
    line = re.sub(r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b", "<uuid>", line, flags=re.I)
    normalized.append(line.strip())

payload = "\n".join(sorted(set(filter(None, normalized))))
print(hashlib.sha256(payload.encode()).hexdigest())
PY
}

ralph_write_repair_context() {
  local context_file="${1:?context path is required}"
  local run_id="${2:?run id is required}"
  local worktree="${3:?worktree path is required}"
  local slice_id="${4:?slice id is required}"
  local branch="${5:?branch is required}"
  local failure_summary="${6:?failure summary path is required}"
  local signature
  signature="$(ralph_failure_signature "$failure_summary")" || return
  mkdir -p "$(dirname "$context_file")"
  python3 - "$context_file" "$run_id" "$worktree" "$slice_id" "$branch" "$failure_summary" "$signature" <<'PY'
import json
import os
import sys
from pathlib import Path

target = Path(sys.argv[1])
payload = {
    "version": 1,
    "run_id": sys.argv[2],
    "worktree": str(Path(sys.argv[3]).resolve()),
    "slice_id": sys.argv[4],
    "branch": sys.argv[5],
    "failure_summary": str(Path(sys.argv[6]).resolve()),
    "failure_signature": sys.argv[7],
}
temporary = target.with_name(f"{target.name}.tmp.{os.getpid()}")
temporary.write_text(json.dumps(payload, indent=2) + "\n")
temporary.replace(target)
PY
}

ralph_repair_context_value() {
  local context_file="${1:?context path is required}"
  local key="${2:?context key is required}"
  python3 - "$context_file" "$key" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
key = sys.argv[2]
payload = json.loads(path.read_text())
if payload.get("version") != 1 or key not in payload:
    raise SystemExit(1)
value = payload[key]
if not isinstance(value, (str, int, float, bool)):
    raise SystemExit(1)
print(str(value))
PY
}

ralph_repair_context_is_resumable() {
  local repo_root="${1:?repository root is required}"
  local context_file="${2:?context path is required}"
  local worktree branch failure_summary expected_root current_branch
  [[ -f "$context_file" ]] || return 1
  worktree="$(ralph_repair_context_value "$context_file" worktree)" || return 1
  branch="$(ralph_repair_context_value "$context_file" branch)" || return 1
  failure_summary="$(ralph_repair_context_value "$context_file" failure_summary)" || return 1
  expected_root="$(cd "$repo_root/.ralph/worktrees" 2>/dev/null && pwd -P)" || return 1
  worktree="$(cd "$worktree" 2>/dev/null && pwd -P)" || return 1
  failure_summary="$(cd "$(dirname "$failure_summary")" 2>/dev/null && pwd -P)/$(basename "$failure_summary")" || return 1
  [[ "$worktree" == "$expected_root/"* ]] || return 1
  [[ "$failure_summary" == "$worktree/.ralph/runs/"*"/failure-summary.md" ]] || return 1
  [[ -f "$failure_summary" ]] || return 1
  git -C "$worktree" rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 1
  current_branch="$(git -C "$worktree" symbolic-ref --short HEAD 2>/dev/null || true)"
  [[ "$current_branch" == "$branch" && "$branch" == ralph/* ]] || return 1
  git -C "$repo_root" worktree list --porcelain \
    | awk '$1 == "worktree" {print substr($0, 10)}' \
    | grep -Fxq "$worktree"
}

ralph_clear_repair_context() {
  local context_file="${1:?context path is required}"
  rm -f "$context_file"
}
