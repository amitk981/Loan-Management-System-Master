# AGENTS.md

You are operating inside the Ralph AFK workflow.

Core rules:
- Do not rely on chat history.
- Read repo files to understand current state.
- Implement only one vertical slice per run.
- Treat `docs/source/` as read-only source material.
- Work inside an isolated worktree when Ralph creates one.
- Run required tests, typecheck, lint, and build gates.
- Save evidence before marking work complete.
- Update state, progress, handoff, and slice status.
- Commit only passing work when config allows it.
- Continue autonomously through high-risk slices after the user's standing approval, while still recording risk and evidence.
- Stop safely on ambiguity, unsafe git state, repeated failures, forbidden file edits, or diff limit violations.

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
