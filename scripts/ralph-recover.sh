#!/usr/bin/env bash
# Recover from interrupted runs (usage-limit exhaustion, crash, closed terminal),
# regardless of which agent (codex or claude) was driving the run.
# Safe by design: a slice's status only flips to Complete at the end of a
# successful run, so an interrupted slice is still queued and reruns cleanly.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

if [[ "$repo_root" == *"/.ralph/worktrees/"* ]]; then
  echo "Refusing to run: current directory is inside a Ralph worktree ($repo_root)." >&2
  exit 1
fi

integration_branch="$(awk -F': *' '/^[[:space:]]*integration_branch:/ {sub(/[[:space:]]*#.*$/, "", $2); print $2; exit}' ".ralph/config.yaml" | xargs || true)"
integration_branch="${integration_branch:-staging}"

recovered=0
shopt -s nullglob
for wt in .ralph/worktrees/*/; do
  wt="${wt%/}"
  run_id="$(basename "$wt")"
  lock=".ralph/locks/$run_id.lock"

  if [[ -f "$lock" ]]; then
    pid="$(sed -n '2p' "$lock" 2>/dev/null || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      echo "Skipping $run_id: its run is still active."
      continue
    fi
  fi

  echo "Recovering interrupted run: $run_id"

  if [[ -d "$wt/.ralph/runs/$run_id" && ! -d ".ralph/runs/$run_id" ]]; then
    mkdir -p ".ralph/runs/$run_id"
    cp -R "$wt/.ralph/runs/$run_id/." ".ralph/runs/$run_id/" 2>/dev/null || true
    echo "  Salvaged run artifacts to .ralph/runs/$run_id/ for diagnosis."
  fi

  git worktree remove --force "$wt" 2>/dev/null || rm -rf "$wt"
  echo "  Removed worktree $wt."

  while IFS= read -r branch; do
    [[ -z "$branch" ]] && continue
    ahead="$(git rev-list --count "${integration_branch}..$branch" 2>/dev/null || echo 1)"
    if [[ "$ahead" == "0" ]]; then
      git branch -D "$branch" >/dev/null 2>&1 && echo "  Deleted empty branch $branch."
    else
      echo "  KEPT branch $branch: it has $ahead unmerged commit(s) — review and merge or delete manually."
    fi
  done < <(git branch --list "ralph/${run_id}_*" --format='%(refname:short)')

  rm -f "$lock"
  recovered=$((recovered + 1))
done

git worktree prune >/dev/null 2>&1 || true
rm -f .ralph/repair-context.json

if (( recovered > 0 )); then
  echo "Recovered $recovered interrupted run(s). Their slices are still queued and will rerun automatically."
else
  echo "No interrupted runs found."
fi
