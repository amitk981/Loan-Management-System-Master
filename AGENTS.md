# AGENTS.md

You are operating inside the Ralph AFK workflow.

## "run ralph loop"

When the owner says "run ralph loop" (or similar), execute from the repository root:

```
./scripts/ralph-loop.sh
```

It runs the slice queue autonomously: one slice per iteration with every risk-selected gate required by `.ralph/config.yaml`, auto-commit, auto-merge to the `staging` integration branch, and auto-push of `staging` to GitHub; one repair attempt per failure; stops when the queue is empty, after repeated failures, or on an owner veto. Localized Low/Medium backend candidates use the independently mapped impacted lane; fail-closed classes and every fourth completed product slice use complete-suite coverage. If the active agent's usage limit is exhausted mid-loop (`agent.limit_fallback` in `.ralph/config.yaml`), the loop switches between codex and claude and retries the slice; when both agents are exhausted it stops cleanly — completed slices are already committed, and the queued slice reruns on the next loop. Agents never commit to, merge into, or push `main` — the owner alone promotes `staging` to `main` via a GitHub pull request (see `docs/working/RELEASE_PROMOTION.md`). `ralph-run.sh` refuses to run unless `staging` is checked out. Do not improvise a different loop.

## Core rules
- Do not rely on chat history.
- Read repo files to understand current state.
- Implement only one vertical slice per run.
- Treat `docs/source/` as read-only source material.
- Work inside an isolated worktree when Ralph creates one.
- Run required tests, typecheck, lint, and build gates.
- Save evidence before marking work complete.
- Save substantive implementation and test evidence. The orchestrator owns changed-files, state, progress, the selected-slice status transition, and mechanical handoff text; edit HANDOFF only for exceptional context it cannot derive.
- During runs, never invoke git commit/add/push yourself — the orchestrator validates independently and commits passing work after the agent finishes (agent sandboxes cannot write worktree git metadata).
- TDD is mandatory for backend and business logic: failing test first, red/green evidence saved.
- The owner has granted standing approval for autonomous runs (`docs/working/HIGH_RISK_APPROVALS.md`). Do not ask for approval; follow `docs/working/DECISION_POLICY.md` for every judgment call and record assumptions in `docs/working/ASSUMPTIONS.md`.
- Never modify protected files (scripts/, .ralph/config.yaml, .ralph/permissions.json, .codex/config.toml, AGENTS.md, CLAUDE.md, .gitignore, HIGH_RISK_APPROVALS.md, DECISION_POLICY.md, docs/source/) — validation fails the run if you do. Never weaken risk rules or quality gates.
- Frontend changes follow `docs/working/FRONTEND_DESIGN_RULES.md` exactly: reuse existing components/patterns, never introduce new styling; build missing screens from existing patterns when the documents require them.
- Never change code directly from a chat request. All code changes flow through queued slices. When the owner reports a bug or requests a feature in chat, help them fill the template in `docs/change-requests/` (see its README), run `./scripts/ralph-intake.sh`, and implement only once a CR slice exists in `docs/slices/`. If the template is not satisfied, change nothing.
- Owner/architecture preparation maintains an 8-10 slice ready runway with concrete, source-cited requirements and bounded epic digests. At an explicit owner-stopped preparation checkpoint it may prepare complete bounded epics to retire known template debt before a long AFK run. A normal implementation run never sharpens a template stub or edits unrelated future slices: specification decisions belong to preparation, while implementation executes an already-ready slice. Store any genuinely missing source fact discovered during implementation in the selected epic digest section.
- Stop only for the never-do list in DECISION_POLICY.md, unsafe git state, repeated failures, protected/forbidden file edits, an owner veto, or diff limit violations.
- If a previous session was interrupted mid-run (limit exhaustion, crash — whichever agent was driving), recovery is automatic: `./scripts/ralph-loop.sh` runs `scripts/ralph-recover.sh` at startup, which salvages the dead run's artifacts, removes its worktree, and requeues the slice. For manual single runs, run `./scripts/ralph-recover.sh` yourself first. Never salvage ungated work.

The generated prompt contains a role-specific read manifest. Follow that manifest rather than loading every workflow document for every mode. A normal implementation reads the selected slice and its bounded digest before workflow mechanics; an architecture review reads only its fixed diff, active findings, and exact cited evidence. `docs/working/FRONTEND_DESIGN_RULES.md` remains mandatory before any frontend edit. Do not load all source documents or the architecture-review state machine during a normal implementation run.
