#!/usr/bin/env bash
# Recover from interrupted runs (usage-limit exhaustion, crash, closed terminal),
# regardless of which agent (codex or claude) was driving the run.
# Safe by design: a slice's status only flips to Complete at the end of a
# successful run, so an interrupted slice is still queued and reruns cleanly.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"
source "$repo_root/scripts/lib/ralph-repair-context.sh"
source "$repo_root/scripts/lib/ralph-worktree-ownership.sh"

if [[ "$repo_root" == *"/.ralph/worktrees/"* ]]; then
  echo "Refusing to run: current directory is inside a Ralph worktree ($repo_root)." >&2
  exit 1
fi

integration_branch="$(awk -F': *' '/^[[:space:]]*integration_branch:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' ".ralph/config.yaml" | xargs || true)"
integration_branch="${integration_branch:-staging}"

recovered=0
recovery_errors=0
repair_context="$repo_root/.ralph/repair-context.json"
context_worktree=""
context_run_id=""
context_branch=""
context_slice_id=""
if [[ -f "$repair_context" ]]; then
  if ! ralph_repair_context_is_resumable "$repo_root" "$repair_context"; then
    echo "Refusing recovery: repair context is malformed, stale, or unsafe; it was not cleared." >&2
    exit 1
  fi
  context_worktree="$(ralph_repair_context_value "$repair_context" worktree 2>/dev/null || true)"
  context_run_id="$(ralph_repair_context_value "$repair_context" run_id 2>/dev/null || true)"
  context_branch="$(ralph_repair_context_value "$repair_context" branch)"
  context_slice_id="$(ralph_repair_context_value "$repair_context" slice_id)"
  context_worktree="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$context_worktree")"
fi

append_run_id() {
  local value="${1:-}"
  [[ "$value" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || return 0
  case $'\n'"$run_ids"$'\n' in
    *$'\n'"$value"$'\n'*) ;;
    *) run_ids="${run_ids}${run_ids:+$'\n'}${value}" ;;
  esac
}

run_lock_is_live() {
  local value="${1:-}" lock pid
  [[ "$value" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || return 1
  lock="$repo_root/.ralph/locks/$value.lock"
  [[ -f "$lock" ]] || return 1
  pid="$(sed -n '2p' "$lock" 2>/dev/null || true)"
  [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

# `ralph-run.sh` writes the trusted root lock before `git worktree add`. A
# process can be killed in the few instructions between a successful add and
# the durable owner-record write. Authenticate only that exact bootstrap shape:
# worktree basename == lock/run id, lock points back to this worktree, the
# registered branch encodes the same run plus an existing exact slice stem.
authenticate_bootstrap_worktree() {
  local wt_abs="${1:?worktree path is required}"
  local owner_id="${2:?owner id is required}"
  local lock="$repo_root/.ralph/locks/$owner_id.lock"
  local lock_run lock_worktree branch branch_prefix slice_id
  [[ -f "$lock" && ! -L "$lock" ]] || return 1
  lock_run="$(sed -n '1p' "$lock" 2>/dev/null || true)"
  lock_worktree="$(sed -n '3p' "$lock" 2>/dev/null || true)"
  [[ "$lock_run" == "$owner_id" && -n "$lock_worktree" ]] || return 1
  lock_worktree="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$lock_worktree")"
  [[ "$lock_worktree" == "$wt_abs" ]] || return 1
  branch="$(git -C "$wt_abs" symbolic-ref --quiet --short HEAD 2>/dev/null)" || return 1
  branch_prefix="ralph/${owner_id}_"
  [[ "$branch" == "$branch_prefix"* ]] || return 1
  slice_id="${branch#"$branch_prefix"}"
  [[ "$slice_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ \
      && -f "$repo_root/docs/slices/$slice_id.md" \
      && ! -L "$repo_root/docs/slices/$slice_id.md" ]] || return 1
  ralph_record_worktree_owner \
    "$repo_root" "$wt_abs" "$branch" "$owner_id" "$owner_id" "$slice_id" \
    >/dev/null || return 1
  echo "  Authenticated interrupted bootstrap worktree from its trusted root lock."
}

shopt -s nullglob
for wt in .ralph/worktrees/*/; do
  wt="${wt%/}"
  wt_abs="$(cd "$wt" && pwd -P)"
  owner_id="$(basename "$wt")"
  owner_file=""
  owner_branch=""
  owner_slice_id=""
  run_ids=""
  owner_lookup_rc=0
  owner_file="$(ralph_worktree_owner_file "$repo_root" "$wt_abs" 2>/dev/null)" \
    || owner_lookup_rc=$?
  if [[ "$owner_lookup_rc" == "1" ]] \
      && authenticate_bootstrap_worktree "$wt_abs" "$owner_id"; then
    owner_file="$(ralph_worktree_owner_file "$repo_root" "$wt_abs")"
    owner_lookup_rc=0
  fi
  if [[ "$owner_lookup_rc" != "0" ]]; then
    if [[ "$owner_lookup_rc" == "2" ]]; then
      echo "Refusing to recover $owner_id: duplicate or corrupt trusted worktree-owner records." >&2
    else
      echo "Refusing to recover $owner_id: stable worktree-owner metadata is missing." >&2
    fi
    recovery_errors=$((recovery_errors + 1))
    continue
  fi
  owner_id="$(ralph_worktree_owner_value "$owner_file" owner_id)"
  owner_branch="$(ralph_worktree_owner_value "$owner_file" branch)"
  owner_slice_id="$(ralph_worktree_owner_value "$owner_file" slice_id)"
  run_ids="$(ralph_worktree_owner_run_ids "$owner_file")"
  append_run_id "$owner_id"
  context_matches=0
  if [[ -n "$context_worktree" && "$context_worktree" == "$wt_abs" ]]; then
    if [[ "$context_branch" != "$owner_branch" \
        || "$context_slice_id" != "$owner_slice_id" ]] \
        || ! printf '%s\n' "$run_ids" | grep -Fxq "$context_run_id"; then
      echo "Refusing to recover $owner_id: repair context disagrees with stable worktree ownership." >&2
      recovery_errors=$((recovery_errors + 1))
      continue
    fi
    context_matches=1
    append_run_id "$context_run_id"
  fi

  active_run=""
  for associated_lock in "$repo_root"/.ralph/locks/*.lock; do
    [[ -f "$associated_lock" ]] || continue
    lock_worktree="$(sed -n '3p' "$associated_lock" 2>/dev/null || true)"
    [[ -n "$lock_worktree" ]] || continue
    lock_worktree="$(python3 -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$lock_worktree")"
    [[ "$lock_worktree" == "$wt_abs" ]] || continue
    lock_run="$(sed -n '1p' "$associated_lock" 2>/dev/null || true)"
    append_run_id "$lock_run"
    if run_lock_is_live "$lock_run"; then
      active_run="$lock_run"
      break
    fi
  done
  while IFS= read -r candidate_run; do
    [[ -n "$active_run" ]] && break
    [[ -n "$candidate_run" ]] || continue
    if run_lock_is_live "$candidate_run"; then
      active_run="$candidate_run"
      break
    fi
  done <<< "$run_ids"
  if [[ -n "$active_run" ]]; then
    echo "Skipping $owner_id: associated run $active_run is still active."
    continue
  fi

  echo "Recovering interrupted worktree: $owner_id"

  while IFS= read -r artifact_run; do
    [[ -n "$artifact_run" ]] || continue
    if [[ -d "$wt/.ralph/runs/$artifact_run" ]]; then
      mkdir -p ".ralph/runs/$artifact_run"
      cp -R "$wt/.ralph/runs/$artifact_run/." ".ralph/runs/$artifact_run/"
      echo "  Salvaged run artifacts to .ralph/runs/$artifact_run/ for diagnosis."
    fi
  done <<< "$run_ids"

  git worktree remove --force "$wt" 2>/dev/null || rm -rf "$wt"
  echo "  Removed worktree $wt."

  branches="$owner_branch"
  while IFS= read -r branch; do
    [[ -z "$branch" ]] && continue
    case $'\n'"$branches"$'\n' in
      *$'\n'"$branch"$'\n'*) ;;
      *) branches="${branches}${branches:+$'\n'}${branch}" ;;
    esac
  done < <(git branch --list "ralph/${owner_id}_*" --format='%(refname:short)')
  while IFS= read -r branch; do
    [[ -z "$branch" || "$branch" != ralph/* ]] && continue
    ahead="$(git rev-list --count "${integration_branch}..$branch" 2>/dev/null || echo 1)"
    if [[ "$ahead" == "0" ]]; then
      git branch -D "$branch" >/dev/null 2>&1 && echo "  Deleted empty branch $branch."
    else
      echo "  KEPT branch $branch: it has $ahead unmerged commit(s) — review and merge or delete manually."
    fi
  done <<< "$branches"

  while IFS= read -r stale_run; do
    [[ -n "$stale_run" ]] && rm -f ".ralph/locks/$stale_run.lock"
  done <<< "$run_ids"
  [[ -n "$owner_file" ]] && rm -f -- "$owner_file"
  if (( context_matches == 1 )); then
    rm -f -- "$repair_context"
    context_worktree=""
    context_run_id=""
    context_branch=""
    context_slice_id=""
    echo "  Cleared the matching dead repair context."
  fi
  recovered=$((recovered + 1))
done

git worktree prune >/dev/null 2>&1 || true

if (( recovered > 0 )); then
  echo "Recovered $recovered interrupted worktree(s). Their slices are still queued and will rerun automatically."
else
  echo "No interrupted runs found."
fi
if (( recovery_errors > 0 )); then
  echo "Recovery stopped with $recovery_errors invalid worktree-owner record(s)." >&2
  exit 1
fi
