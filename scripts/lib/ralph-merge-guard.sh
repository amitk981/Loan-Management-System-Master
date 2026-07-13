#!/usr/bin/env bash

# Prepare the integration worktree for a completed Ralph branch without losing
# diagnostics. Failed-run artifacts are copied to the integration worktree; a
# later repair can commit an expanded version of the same generated file.
# Identical copies are removed. Differing .ralph/runs/** copies are archived in
# Git's private metadata directory. Any other differing path still fails closed.
ralph_prepare_worktree_for_ff_merge() {
  local repo_root="${1:?repository root is required}"
  local branch_name="${2:?branch name is required}"
  local path branch_blob working_blob archive_root archive_path git_dir
  local blocked=0

  git_dir="$(git -C "$repo_root" rev-parse --absolute-git-dir)" || return 1
  archive_root="$git_dir/ralph-merge-collision-backups/${RALPH_MERGE_BACKUP_ID:-$(date '+%Y-%m-%d_%H%M%S')_$$}"

  while IFS= read -r -d '' path; do
    [[ -e "$repo_root/$path" || -L "$repo_root/$path" ]] || continue
    git -C "$repo_root" ls-files --error-unmatch -- "$path" >/dev/null 2>&1 && continue

    branch_blob="$(git -C "$repo_root" rev-parse --verify "$branch_name:$path" 2>/dev/null || true)"
    [[ -n "$branch_blob" ]] || continue
    working_blob="$(git -C "$repo_root" hash-object -- "$path" 2>/dev/null || true)"

    if [[ -z "$working_blob" || "$working_blob" != "$branch_blob" ]]; then
      if [[ "$path" == .ralph/runs/* ]]; then
        continue
      fi
      echo "Refusing merge: untracked file differs from completed branch: $path" >&2
      blocked=1
    fi
  done < <(git -C "$repo_root" diff --name-only --diff-filter=A -z HEAD "$branch_name" --)

  (( blocked == 0 )) || return 1

  while IFS= read -r -d '' path; do
    [[ -e "$repo_root/$path" || -L "$repo_root/$path" ]] || continue
    git -C "$repo_root" ls-files --error-unmatch -- "$path" >/dev/null 2>&1 && continue
    branch_blob="$(git -C "$repo_root" rev-parse --verify "$branch_name:$path" 2>/dev/null || true)"
    [[ -n "$branch_blob" ]] || continue
    working_blob="$(git -C "$repo_root" hash-object -- "$path" 2>/dev/null || true)"
    if [[ -n "$working_blob" && "$working_blob" == "$branch_blob" ]]; then
      if ! rm -f -- "$repo_root/$path"; then
        echo "Refusing merge: could not remove identical generated collision: $path" >&2
        return 1
      fi
      echo "Removed identical untracked merge collision: $path"
      continue
    fi

    [[ "$path" == .ralph/runs/* ]] || continue
    archive_path="$archive_root/$path"
    if ! mkdir -p "$(dirname "$archive_path")" \
        || ! mv -- "$repo_root/$path" "$archive_path"; then
      echo "Refusing merge: could not archive differing generated collision: $path" >&2
      return 1
    fi
    echo "Archived differing generated merge collision: $path -> $archive_path"
  done < <(git -C "$repo_root" diff --name-only --diff-filter=A -z HEAD "$branch_name" --)
}
