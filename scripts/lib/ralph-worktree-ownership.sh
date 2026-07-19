#!/usr/bin/env bash

# Trusted, operator-local ownership metadata for Ralph worktrees. The record is
# stored under the common Git directory so an agent working in the candidate
# cannot alter the run-to-worktree association used by crash recovery.

ralph_worktree_owner_directory() {
  local repo_root="${1:?repository root is required}" common_dir
  common_dir="$(git -C "$repo_root" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" \
    || return 1
  printf '%s/ralph-worktree-owners\n' "$common_dir"
}

# Print the one trusted owner record for a worktree. No match returns 1;
# duplicate records are treated as corrupt metadata and return 2.
ralph_worktree_owner_file() {
  local repo_root="${1:?repository root is required}"
  local worktree="${2:?worktree path is required}" owner_dir
  owner_dir="$(ralph_worktree_owner_directory "$repo_root")" || return 1
  [[ -d "$owner_dir" ]] || return 1
  python3 - "$owner_dir" "$worktree" <<'PY'
import json
import re
import sys
from pathlib import Path

owner_dir = Path(sys.argv[1])
target = Path(sys.argv[2]).resolve()
matches = []
invalid_match = False
for candidate in sorted(owner_dir.glob("*.json")):
    if candidate.is_symlink() or not candidate.is_file():
        continue
    try:
        payload = json.loads(candidate.read_text())
        owned_value = payload.get("worktree")
        if not isinstance(owned_value, str):
            continue
        owned = Path(owned_value).resolve()
    except (OSError, TypeError, json.JSONDecodeError):
        continue
    if owned != target:
        continue
    run_ids = payload.get("run_ids")
    valid = (
        payload.get("version") == 1
        and isinstance(payload.get("owner_id"), str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", payload["owner_id"])
        and isinstance(payload.get("branch"), str)
        and payload["branch"].startswith("ralph/")
        and isinstance(payload.get("slice_id"), str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", payload["slice_id"])
        and isinstance(run_ids, list)
        and all(
            isinstance(value, str)
            and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value)
            for value in run_ids
        )
    )
    if valid:
        matches.append(candidate)
    else:
        invalid_match = True
if invalid_match or len(matches) > 1:
    raise SystemExit(2)
if not matches:
    raise SystemExit(1)
print(matches[0])
PY
}

ralph_worktree_owner_value() {
  local owner_file="${1:?owner file is required}" key="${2:?key is required}"
  python3 - "$owner_file" "$key" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
if path.is_symlink() or not path.is_file():
    raise SystemExit(1)
payload = json.loads(path.read_text())
if payload.get("version") != 1 or sys.argv[2] not in payload:
    raise SystemExit(1)
value = payload[sys.argv[2]]
if not isinstance(value, str):
    raise SystemExit(1)
print(value)
PY
}

ralph_worktree_owner_run_ids() {
  local owner_file="${1:?owner file is required}"
  python3 - "$owner_file" <<'PY'
import json
import re
import sys
from pathlib import Path

path = Path(sys.argv[1])
if path.is_symlink() or not path.is_file():
    raise SystemExit(1)
payload = json.loads(path.read_text())
values = payload.get("run_ids")
if payload.get("version") != 1 or not isinstance(values, list):
    raise SystemExit(1)
for value in values:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise SystemExit(1)
    print(value)
PY
}

# Create or update the stable owner record and make the current run the active
# owner. Reusing a worktree appends the repair run id without changing its
# stable owner id, path, or branch.
ralph_record_worktree_owner() {
  local repo_root="${1:?repository root is required}"
  local worktree="${2:?worktree path is required}"
  local branch="${3:?branch is required}" owner_id="${4:?owner id is required}"
  local run_id="${5:?run id is required}" slice_id="${6:?slice id is required}"
  local owner_dir owner_file
  local expected_root resolved_worktree
  [[ "$owner_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ \
      && "$run_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ \
      && "$slice_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ \
      && "$branch" == ralph/* ]] || {
    echo "Unsafe Ralph worktree ownership values." >&2
    return 1
  }
  expected_root="$(cd "$repo_root/.ralph/worktrees" 2>/dev/null && pwd -P)" || return 1
  resolved_worktree="$(cd "$worktree" 2>/dev/null && pwd -P)" || return 1
  [[ "$resolved_worktree" == "$expected_root/"* ]] || {
    echo "Ralph worktree owner path escapes .ralph/worktrees: $resolved_worktree" >&2
    return 1
  }
  git -C "$repo_root" worktree list --porcelain \
    | awk '$1 == "worktree" {print substr($0, 10)}' \
    | grep -Fxq "$resolved_worktree" || {
      echo "Cannot own an unregistered Ralph worktree: $resolved_worktree" >&2
      return 1
    }
  owner_dir="$(ralph_worktree_owner_directory "$repo_root")" || return 1
  mkdir -p "$owner_dir"
  owner_file="$owner_dir/$owner_id.json"
  python3 - "$owner_file" "$owner_id" "$resolved_worktree" \
      "$branch" "$run_id" "$slice_id" <<'PY'
import json
import os
import sys
from pathlib import Path

target = Path(sys.argv[1])
owner_id, worktree, branch, run_id, slice_id = sys.argv[2:]
if target.exists():
    if target.is_symlink() or not target.is_file():
        raise SystemExit("worktree owner record is not a trusted regular file")
    payload = json.loads(target.read_text())
    expected = (
        payload.get("version"), payload.get("owner_id"),
        payload.get("worktree"), payload.get("branch"), payload.get("slice_id"),
    )
    actual = (1, owner_id, worktree, branch, slice_id)
    if expected != actual:
        raise SystemExit("worktree owner record conflicts with stable ownership")
    run_ids = payload.get("run_ids")
    if not isinstance(run_ids, list) or not all(isinstance(value, str) for value in run_ids):
        raise SystemExit("worktree owner run history is invalid")
else:
    payload = {
        "version": 1,
        "owner_id": owner_id,
        "worktree": worktree,
        "branch": branch,
        "slice_id": slice_id,
        "run_ids": [],
    }
    run_ids = payload["run_ids"]
if run_id not in run_ids:
    run_ids.append(run_id)
payload["active_run_id"] = run_id
temporary = target.with_name(f"{target.name}.tmp.{os.getpid()}")
temporary.write_text(json.dumps(payload, indent=2) + "\n")
temporary.replace(target)
PY
  printf '%s\n' "$owner_file"
}

# Succeed when any run recorded for this worktree still owns a live lock.
ralph_worktree_owner_has_live_lock() {
  local repo_root="${1:?repository root is required}"
  local owner_file="${2:?owner file is required}" run_id lock pid
  while IFS= read -r run_id; do
    [[ -n "$run_id" ]] || continue
    lock="$repo_root/.ralph/locks/$run_id.lock"
    [[ -f "$lock" ]] || continue
    pid="$(sed -n '2p' "$lock" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      printf '%s\n' "$run_id"
      return 0
    fi
  done < <(ralph_worktree_owner_run_ids "$owner_file")
  return 1
}

# Release a run lock on ordinary exits, but preserve the lock when a registered
# worktree exists and durable ownership has not yet been recorded. That narrow
# state is the only trusted evidence recovery has if SIGTERM/SIGHUP lands after
# `git worktree add` and before ralph_record_worktree_owner completes.
ralph_release_run_lock() {
  local repo_root="${1:?repository root is required}"
  local lock_file="${2:?lock file is required}"
  local worktree_hint="${3:-}"
  local owner_recorded="${4:?owner-recorded flag is required}"
  local no_worktree="${5:?no-worktree flag is required}"
  local expected_lock_dir actual_lock_dir resolved_worktree expected_worktree_root

  [[ "$owner_recorded" =~ ^[01]$ && "$no_worktree" =~ ^[01]$ ]] || return 1
  expected_lock_dir="$(cd "$repo_root/.ralph/locks" 2>/dev/null && pwd -P)" || return 1
  actual_lock_dir="$(cd "$(dirname "$lock_file")" 2>/dev/null && pwd -P)" || return 1
  [[ "$actual_lock_dir" == "$expected_lock_dir" \
      && "$(basename "$lock_file")" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*\.lock$ ]] \
    || return 1

  if [[ "$owner_recorded" == "1" || "$no_worktree" == "1" ]]; then
    rm -f -- "$lock_file"
    return 0
  fi

  if [[ -n "$worktree_hint" && -d "$worktree_hint" ]]; then
    resolved_worktree="$(cd "$worktree_hint" 2>/dev/null && pwd -P)" || return 1
    expected_worktree_root="$(cd "$repo_root/.ralph/worktrees" 2>/dev/null && pwd -P)" \
      || return 1
    [[ "$resolved_worktree" == "$expected_worktree_root/"* ]] || return 1
    if git -C "$repo_root" worktree list --porcelain \
        | awk '$1 == "worktree" {print substr($0, 10)}' \
        | grep -Fxq "$resolved_worktree"; then
      echo "Preserving bootstrap lock until durable worktree ownership can be recovered: $lock_file" >&2
      return 0
    fi
  fi

  rm -f -- "$lock_file"
}

ralph_remove_worktree_owner() {
  local repo_root="${1:?repository root is required}"
  local worktree="${2:?worktree path is required}" owner_file
  owner_file="$(ralph_worktree_owner_file "$repo_root" "$worktree" 2>/dev/null)" \
    || return 0
  rm -f -- "$owner_file"
}
