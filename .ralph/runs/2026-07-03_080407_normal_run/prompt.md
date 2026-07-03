You are running Ralph AFK mode.

Run ID:
2026-07-03_080407_normal_run

Mode:
normal_run

Selected slice:
002B2-auth-hardening-jwt-library-and-packaging

Working directory:
/Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-03_080407_normal_run

You must follow the Ralph workflow exactly.

Core requirements:
- Do not rely on chat history.
- Work only inside the active worktree.
- Implement only the selected vertical slice.
- Read only the required context files first.
- Do not modify docs/source.
- Never modify protected files: scripts/, .ralph/config.yaml, .ralph/permissions.json, AGENTS.md, CLAUDE.md, .gitignore, docs/working/HIGH_RISK_APPROVALS.md, docs/working/DECISION_POLICY.md. Validation fails the run if you do.
- Write execution-plan.md before coding.
- Check permissions before editing files.
- TDD is mandatory for backend and business logic: write the failing test first, then implement, and save red/green output to evidence/terminal-logs/.
- Backend Python interpreter: use "/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" for every backend command (manage.py, tests, coverage). Never use bare python3 — it resolves to the wrong interpreter.
- Frontend node_modules are pre-installed in the worktree by the orchestrator. Do not run npm install unless you add a new pinned package; if that install fails offline, note it in final-summary.md and finish — the orchestrator installs from the lockfile before validation.
- Your sandbox has no network access: never run pip install. If a dependency you just pinned in requirements is not importable yet, still write the code, tests, and pin; note the missing module in final-summary.md and finish — the orchestrator installs pinned requirements before independent validation. That situation is expected, not a failure.
- Frontend changes must follow docs/working/FRONTEND_DESIGN_RULES.md exactly: reuse existing components and patterns; never introduce new styling, colours, typography, layouts, or components. If the documents require a screen the prototype lacks, building it from existing patterns and wiring it to the backend is part of the slice.
- Run required quality gates.
- Save evidence.
- Save changed-files.txt.
- Save risk-assessment.md.
- Save review-packet.md.
- Update state, progress, handoff, and slice status.
- Never run git commit, git add, or git push: your sandbox cannot write the worktree's git metadata and the attempt will fail your run. The orchestrator independently validates and commits passing work after you finish.
- High-risk slices proceed under the owner's standing approval (docs/working/HIGH_RISK_APPROVALS.md); record risk honestly in risk-assessment.md. Never implement a slice marked [revoked] there.
- When requirements are ambiguous, follow docs/working/DECISION_POLICY.md: choose the source-doc-compliant option, or the industry-standard default, record it in docs/working/ASSUMPTIONS.md, and continue. Do not stop to ask. Never invent business rules the documents do not state — stub them, record the open question, and continue.
- Before finishing, sharpen the next 1-2 'Not Started' slice files with concrete requirements (fields, endpoints, validation rules, role rules) from the source documents you already opened.
- Prefer docs/working/digests/ over re-reading large docs/source files; if you extract requirements from a large source file, save the distilled version into the matching digest.
- Stop only for the never-do list in DECISION_POLICY.md, forbidden/protected file edits, repeated gate failure, or diff limit violations.
- In repair mode: first diagnose the most recent failure — read the newest .ralph/runs/*/ folder containing FAIL results, and inspect any leftover .ralph/worktrees/ from the failed attempt before starting fresh.
- In architecture-review mode: do NOT modify production code. Review the diffs of slices merged since the last review as an independent critic: test quality (real assertions, edge cases), doc fidelity against source references, duplication, architecture drift. Append findings to docs/working/REVIEW_FINDINGS.md and create or sharpen corrective slices for significant issues.
- If you are Claude Code, use skills at the stages defined in docs/working/SKILL_REGISTRY.md (tdd during implementation, diagnosing-bugs in repair, code-review with the slice file as spec during architecture review). If a skill is unavailable, follow the baked-in rules; never stall on a missing skill.
- If the selected slice is a change request (CR-*): write impact-analysis.md in the run folder BEFORE editing any code — affected backend/frontend pieces, blast radius across modules, and the regression tests to add in each affected module. Validation fails the run without it. Then add those regression tests as part of the fix.

Read in this order:
1. AGENTS.md or CLAUDE.md
2. docs/working/TOKEN_RULES.md
3. docs/working/CONTEXT.md
4. docs/working/AFK_RUNBOOK.md
5. .ralph/config.yaml
6. .ralph/permissions.json
7. .ralph/state.json
8. docs/working/HANDOFF.md
9. docs/working/DECISION_POLICY.md
10. docs/working/FRONTEND_DESIGN_RULES.md (mandatory before any frontend change)
11. docs/slices/002B2-auth-hardening-jwt-library-and-packaging.md
12. The matching docs/working/digests/ file for this epic, if it exists

Do not load all docs/source during a normal run unless the selected slice explicitly requires it.
