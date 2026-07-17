#!/usr/bin/env bash

# Ordinary architecture reviews may change documentation, queue metadata, and
# Ralph bookkeeping only. Product changes in review mode are a workflow error:
# fail closed instead of masking them behind the product gate suite.
ralph_validate_architecture_review_change_scope() {
  local worktree="${1:?worktree is required}"
  local run_id="${2:?current run id is required}"
  local changed invalid=0

  if ! [[ "$run_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
    echo "Architecture review run id is unsafe: $run_id" >&2
    return 1
  fi

  while IFS= read -r changed; do
    [[ -n "$changed" ]] || continue
    case "$changed" in
      docs/*|.ralph/state.json|.ralph/progress.md|.ralph/runs/"$run_id"/*)
        ;;
      *)
        echo "Architecture review may not modify product path $changed." >&2
        invalid=1
        ;;
    esac
  done < <(
    {
      git -C "$worktree" diff --name-only --no-renames HEAD --
      git -C "$worktree" ls-files --others --exclude-standard
    } | sort -u
  )

  (( invalid == 0 ))
}
