# CLAUDE.md

This repository is agent-agnostic. `AGENTS.md` is the single source of truth for the Ralph AFK workflow — follow it exactly (read order, core rules, protected files, decision policy). Codex reads `AGENTS.md` and ignores this file; this file only adds Claude-specific notes, so the two never conflict.

## Running the automation with Claude
- "run ralph loop" = `./scripts/ralph-loop.sh` from the repository root (codex drives by default).
- To drive runs with Claude instead: `AGENT_TOOL=claude ./scripts/ralph-loop.sh` (uses `scripts/agent-adapters/claude.sh`, headless).
- Skills are optional accelerators used only at the stages listed in `docs/working/SKILL_REGISTRY.md` (the short version: `tdd` while implementing, `diagnosing-bugs` in repair, `code-review` with the slice file as spec during review runs, `research`/`domain-modeling` when building digests). The registry also lists skills deliberately excluded and why. The workflow must never depend on a skill existing.

## Recovering from an interrupted session (usage-limit exhaustion, crash, closed terminal)
If any previous session — Claude or codex — stopped mid-run, recovery is automatic: the next `./scripts/ralph-loop.sh` (run by either agent) executes `scripts/ralph-recover.sh` at startup, which salvages the dead run's artifacts to `.ralph/runs/<run-id>/`, removes the orphaned worktree and lock, and the still-queued slice reruns cleanly. Nothing manual is needed — just run the loop again.

Manual fallback (single runs, or to inspect first): `./scripts/ralph-recover.sh`, then check the salvaged `.ralph/runs/<run-id>/` folder (`final-summary.md` saying "In Progress" confirms the interruption). Never salvage half-finished work — its gates never passed; rerun the slice.

Do not use skills randomly. Do not make broad refactors unless the runbook and risk rules allow it.
