You are running Ralph AFK mode.

Run ID:
2026-07-24_000933_architecture_review

Mode:
architecture_review

Prompt role:
queue_rewrite

Selected slice:
architecture-review

Working directory:
/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_000933_architecture_review

You must follow the Ralph workflow exactly.

Core requirements:
- Do not rely on chat history.
- Work only inside the active worktree.
- Read only the required context files first.
- Do not modify docs/source.
- Never modify protected files: scripts/, .ralph/config.yaml, .ralph/permissions.json, .codex/config.toml, AGENTS.md, CLAUDE.md, .gitignore, docs/working/HIGH_RISK_APPROVALS.md, docs/working/DECISION_POLICY.md. Validation fails the run if you do.
- Perform only the declared queue rewrite. Do not implement product code, discover architecture findings, or inspect unrelated slices.
- Save evidence.
- Save risk-assessment.md.
- Save review-packet.md.
- Before finishing successfully, set the review-packet.md Result section to exactly 'Ready for independent validation'. Missing, partial, or any other result fails closed.
- The orchestrator owns changed-files.txt, .ralph/state.json, .ralph/progress.md, the selected slice Status transition, and mechanical handoff/progress bookkeeping. Do not edit those mechanical facts. Put substantive next-run risks or decisions in review-packet.md; edit HANDOFF only when it needs non-mechanical context the orchestrator cannot derive.
- Never run git commit, git add, or git push: your sandbox cannot write the worktree's git metadata and the attempt will fail your run. The orchestrator independently validates and commits passing work after you finish.
- Stop only for the never-do list in DECISION_POLICY.md, forbidden/protected file edits, repeated gate failure, or diff limit violations.
- In repair mode: first diagnose the most recent failure — read failure-summary.md in the newest failed .ralph/runs/*/ folder (failed checks, last log lines, changed files); open the full gate logs only if that summary is insufficient, and inspect any leftover .ralph/worktrees/ from the failed attempt before starting fresh.

- This is an oversized-slice queue rewrite, not a general architecture review. Do not modify production code or review unrelated slices. Read docs/slices/011P-default-closure-compliance-frontend-wiring.md and the retained evidence for failed run 2026-07-23_233022_normal_run. The failed candidate measured 4468 lines against a 2000-line limit. Mark 011P Superseded and create at least two dependency-ordered Not Started successor slices named 011PA, 011PB, and so on. Each successor must contain an Origin section with the exact marker Oversized slice: `011P`. The first successor inherits every original prerequisite; each later successor depends on the previous one; every existing downstream dependency on 011P must point to the terminal successor. Preserve every original requirement, test, evidence, and risk across the successors. Each successor must be independently implementable and independently green, with a predicted diff comfortably below the configured limit. Update queue handoff or digest documents only when needed. Do not sharpen or change unrelated slices.

- In this queue-rewrite architecture mode, perform only the oversized-slice split described above.

- If you are Claude Code, use skills at the stages defined in docs/working/SKILL_REGISTRY.md (tdd during implementation, diagnosing-bugs in repair, code-review with the slice file as spec during architecture review). If a skill is unavailable, follow the baked-in rules; never stall on a missing skill.

Read in this order:
1. docs/working/CONTEXT.md
2. AGENTS.md or CLAUDE.md
3. docs/working/TOKEN_RULES.md
4. docs/working/HANDOFF.md
5. docs/slices/011P-default-closure-compliance-frontend-wiring.md and its linked parent Epic
6. The retained failure-summary and oversized-slice validation named above
7. Only the queue-contract section of docs/working/AFK_RUNBOOK.md

Do not load all docs/source during a normal run unless the selected slice explicitly requires it.
