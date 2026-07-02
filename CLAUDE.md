# CLAUDE.md

This repository is agent-agnostic. `AGENTS.md` is the single source of truth for the Ralph AFK workflow — follow it exactly (read order, core rules, protected files, decision policy). Codex reads `AGENTS.md` and ignores this file; this file only adds Claude-specific notes, so the two never conflict.

## Running the automation with Claude
- "run ralph loop" = `./scripts/ralph-loop.sh` from the repository root (codex drives by default).
- To drive runs with Claude instead: `AGENT_TOOL=claude ./scripts/ralph-loop.sh` (uses `scripts/agent-adapters/claude.sh`, headless).
- Skills (`/tdd`, `/diagnosing-bugs`, etc.) are optional accelerators used only at the stages listed in `docs/working/SKILL_REGISTRY.md`, and only if available in the session. The workflow must never depend on a skill existing.

## Recovering from an interrupted session (usage-limit exhaustion, crash, closed terminal)
If any previous session — Claude or codex — stopped mid-run, recovery is built in and safe:
1. Stale locks are removed automatically by preflight (it checks whether the owning process is still alive). Run `./scripts/afk-dev.sh --dry-run` to confirm a clean state.
2. Check `git worktree list`. A leftover `.ralph/worktrees/<run-id>` means that run never passed its gates. Default recovery: discard it — `git worktree remove --force <path>` then `git branch -D ralph/<run-id>_<slice-id>` — and simply rerun the slice. This is always safe: a slice's status only flips to Complete at the very end of a successful run, so an interrupted slice is still `Not Started` and will be picked up again automatically.
3. The newest `.ralph/runs/<run-id>/` folder shows how far the interrupted run got (`final-summary.md` still saying "In Progress" confirms interruption; gate result files show what passed).
4. Never salvage half-finished work from an interrupted run — its gates never passed. Rerun the slice.

Do not use skills randomly. Do not make broad refactors unless the runbook and risk rules allow it.
