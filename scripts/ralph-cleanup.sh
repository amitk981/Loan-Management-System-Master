#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

stale_locks=0
remove_idle_worktrees=0
confirm=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stale-locks) stale_locks=1; shift ;;
    --remove-idle-worktrees) remove_idle_worktrees=1; shift ;;
    --confirm) confirm=1; shift ;;
    --help|-h)
      echo "Usage: ./scripts/ralph-cleanup.sh --stale-locks [--remove-idle-worktrees --confirm]"
      exit 0
      ;;
    *) echo "Unknown cleanup argument: $1" >&2; exit 2 ;;
  esac
done

if (( stale_locks == 1 )); then
  find .ralph/locks -maxdepth 1 -type f -name '*.lock' -print -delete
fi

if (( remove_idle_worktrees == 1 )); then
  if (( confirm != 1 )); then
    echo "--remove-idle-worktrees requires --confirm" >&2
    exit 2
  fi
  find .ralph/worktrees -mindepth 1 -maxdepth 1 -type d -print
  echo "Use git worktree remove <path> manually for any worktree you want to remove."
fi
