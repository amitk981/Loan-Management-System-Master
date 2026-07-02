You are running Ralph AFK mode.

Run ID:
2026-07-02_154724_normal_run

Mode:
normal_run

Selected slice:
002B-user-model-and-jwt-login-refresh-logout

Working directory:
/Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-02_152504_normal_run/.ralph/worktrees/2026-07-02_154724_normal_run

You must follow the Ralph workflow exactly.

Core requirements:
- Do not rely on chat history.
- Work only inside the active worktree.
- Implement only the selected vertical slice.
- Read only the required context files first.
- Do not modify docs/source.
- Write execution-plan.md before coding.
- Check permissions before editing files.
- Use TDD where practical.
- Run required quality gates.
- Save evidence.
- Save changed-files.txt.
- Save risk-assessment.md.
- Save review-packet.md.
- Update state, progress, handoff, and slice status.
- Commit only if gates pass and config allows commits.
- Continue through high-risk slices under the user's standing approval, while recording risk and evidence.
- Stop safely on ambiguity, forbidden file edits, repeated failure, or diff limit violations.

Read in this order:
1. AGENTS.md or CLAUDE.md
2. docs/working/TOKEN_RULES.md
3. docs/working/CONTEXT.md
4. docs/working/AFK_RUNBOOK.md
5. .ralph/config.yaml
6. .ralph/permissions.json
7. .ralph/state.json
8. docs/working/HANDOFF.md
9. docs/slices/002B-user-model-and-jwt-login-refresh-logout.md

Do not load all docs/source during a normal run unless the selected slice explicitly requires it.
