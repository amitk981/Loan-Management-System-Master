# Ralph Handoff

## Last Run
2026-07-02-workflow-repair (manual repair session, not an AFK run)

## Current Status
Workflow repaired and all completed work merged to `main`. Slices 002A (backend scaffold + health) and 002B (auth login/refresh/logout) are on `main`; stale worktrees and branches removed.

Repair changes now in effect:
- Ralph refuses to launch from inside a worktree (nesting bug fixed) and removes its lock on any exit (stale-lock bug fixed).
- High-risk slices require an `[approved]` entry in `docs/working/HIGH_RISK_APPROVALS.md`; the orchestrator enforces this before starting the agent.
- Successful runs auto-merge (fast-forward) into `main` and clean up their worktree.
- Quality gates are enforced and real: frontend `typecheck`/`test`/`build` (59 type errors fixed; vitest added), backend `manage.py check` + tests. A failing gate now fails the run (previously only build counted).
- Dependency policy allows pre-approved packages (see `docs/working/DEPENDENCY_POLICY.md`); backend has pinned `requirements.txt` and identity migrations.
- New slices: `002B2` (replace hand-rolled JWT with PyJWT — pre-approved) and `002EX` (early end-to-end tracer bullet after 002E — NOT yet approved, review it when the queue reaches it).
- Requirement digests live in `docs/working/digests/`; epic-002 digest is ready for 002C/002D.

## Current Slice
None selected. Next in queue: `002B2-auth-hardening-jwt-library-and-packaging` (High risk, pre-approved).

## Current Blocker
None.

## Next Recommended Action
Run `./scripts/afk-dev.sh 1 --mode normal` from the repository root. It will select 002B2, verify its approval, run gates, and auto-merge on success.
