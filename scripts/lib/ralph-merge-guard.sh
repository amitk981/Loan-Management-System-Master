#!/usr/bin/env bash

# Remove only untracked files that are byte-identical to files introduced by a
# completed Ralph branch. Failed-run artifacts are copied to the integration
# worktree for diagnosis; a later repair can legitimately commit those same
# artifacts, which would otherwise make an ff-only merge fail.
ralph_remove_identical_untracked_merge_collisions() {
  local repo_root="${1:?repository root is required}"
  local branch_name="${2:?branch name is required}"
  local path branch_blob working_blob
  local blocked=0

  while IFS= read -r -d '' path; do
    [[ -e "$repo_root/$path" || -L "$repo_root/$path" ]] || continue
    git -C "$repo_root" ls-files --error-unmatch -- "$path" >/dev/null 2>&1 && continue

    branch_blob="$(git -C "$repo_root" rev-parse --verify "$branch_name:$path" 2>/dev/null || true)"
    [[ -n "$branch_blob" ]] || continue
    working_blob="$(git -C "$repo_root" hash-object -- "$path" 2>/dev/null || true)"

    if [[ -z "$working_blob" || "$working_blob" != "$branch_blob" ]]; then
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
    [[ -n "$working_blob" && "$working_blob" == "$branch_blob" ]] || continue
    rm -f -- "$repo_root/$path"
    echo "Removed identical untracked merge collision: $path"
  done < <(git -C "$repo_root" diff --name-only --diff-filter=A -z HEAD "$branch_name" --)
}
