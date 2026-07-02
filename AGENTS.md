# AGENTS.md

You are operating inside the Ralph AFK workflow.

## "run ralph loop"

When the owner says "run ralph loop" (or similar), execute from the repository root:

```
./scripts/ralph-loop.sh
```

It runs the slice queue autonomously: one slice per iteration with full gates, auto-commit, auto-merge to main, and auto-push to GitHub; one repair attempt per failure; stops when the queue is empty, after repeated failures, or on an owner veto. Do not improvise a different loop.

## Core rules
- Do not rely on chat history.
- Read repo files to understand current state.
- Implement only one vertical slice per run.
- Treat `docs/source/` as read-only source material.
- Work inside an isolated worktree when Ralph creates one.
- Run required tests, typecheck, lint, and build gates.
- Save evidence before marking work complete.
- Update state, progress, handoff, and slice status.
- Commit only passing work when config allows it.
- TDD is mandatory for backend and business logic: failing test first, red/green evidence saved.
- The owner has granted standing approval for autonomous runs (`docs/working/HIGH_RISK_APPROVALS.md`). Do not ask for approval; follow `docs/working/DECISION_POLICY.md` for every judgment call and record assumptions in `docs/working/ASSUMPTIONS.md`.
- Never modify protected files (scripts/, .ralph/config.yaml, .ralph/permissions.json, AGENTS.md, CLAUDE.md, .gitignore, HIGH_RISK_APPROVALS.md, DECISION_POLICY.md, docs/source/) — validation fails the run if you do. Never weaken risk rules or quality gates.
- Frontend changes follow `docs/working/FRONTEND_DESIGN_RULES.md` exactly: reuse existing components/patterns, never introduce new styling; build missing screens from existing patterns when the documents require them.
- Never change code directly from a chat request. All code changes flow through queued slices. When the owner reports a bug or requests a feature in chat, help them fill the template in `docs/change-requests/` (see its README), run `./scripts/ralph-intake.sh`, and implement only once a CR slice exists in `docs/slices/`. If the template is not satisfied, change nothing.
- Before finishing, sharpen the next 1-2 `Not Started` slice files with concrete requirements from source documents you already opened, and store distilled extracts in `docs/working/digests/`.
- Stop only for the never-do list in DECISION_POLICY.md, unsafe git state, repeated failures, protected/forbidden file edits, an owner veto, or diff limit violations.
- If a previous session was interrupted mid-run (limit exhaustion, crash — whichever agent was driving), recovery is automatic: `./scripts/ralph-loop.sh` runs `scripts/ralph-recover.sh` at startup, which salvages the dead run's artifacts, removes its worktree, and requeues the slice. For manual single runs, run `./scripts/ralph-recover.sh` yourself first. Never salvage ungated work.

Read in this order during normal runs:
1. `docs/working/TOKEN_RULES.md`
2. `docs/working/CONTEXT.md`
3. `docs/working/AFK_RUNBOOK.md`
4. `.ralph/config.yaml`
5. `.ralph/permissions.json`
6. `.ralph/state.json`
7. `docs/working/HANDOFF.md`
8. The selected `docs/slices/*.md` file only

Do not load all source documents during normal runs unless the selected slice explicitly requires it.
