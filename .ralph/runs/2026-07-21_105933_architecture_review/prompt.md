You are running Ralph AFK mode.

Run ID:
2026-07-21_105933_architecture_review

Mode:
architecture_review

Selected slice:
architecture-review

Working directory:
/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_105933_architecture_review

You must follow the Ralph workflow exactly.

Core requirements:
- Do not rely on chat history.
- Work only inside the active worktree.
- Implement only the selected vertical slice.
- Read only the required context files first.
- Do not modify docs/source.
- Never modify protected files: scripts/, .ralph/config.yaml, .ralph/permissions.json, .codex/config.toml, AGENTS.md, CLAUDE.md, .gitignore, docs/working/HIGH_RISK_APPROVALS.md, docs/working/DECISION_POLICY.md. Validation fails the run if you do.
- Write execution-plan.md before coding.
- Check permissions before editing files.
- TDD is mandatory for backend and business logic: write the failing test first, then implement, and save red/green output to evidence/terminal-logs/.
- Backend Python interpreter: use "/Users/amitkallapa/LMS/.ralph/venv/bin/python" for every backend command (manage.py, tests, coverage). Never use bare python3 — it resolves to the wrong interpreter.
- Frontend node_modules are pre-installed in the worktree by the orchestrator. Do not run npm install unless you add a new pinned package; if that install fails offline, note it in final-summary.md and finish — the orchestrator installs from the lockfile before validation.
- Your sandbox has no network access: never run pip install. If a dependency you just pinned in requirements is not importable yet, still write the code, tests, and pin; note the missing module in final-summary.md and finish — the orchestrator installs pinned requirements before independent validation. That situation is expected, not a failure.
- Frontend changes must follow docs/working/FRONTEND_DESIGN_RULES.md exactly: reuse existing components and patterns; never introduce new styling, colours, typography, layouts, or components. If the documents require a screen the prototype lacks, building it from existing patterns and wiring it to the backend is part of the slice.
- During implementation, run focused red/green tests for the changed backend/business behavior and the impacted frontend tests, typecheck, lint, and build as appropriate.
- Batch related searches, reads, edits, and focused tests. Aim to stay below roughly 80 tool calls; after that, return to execution-plan.md and finish through focused work instead of rediscovering context.
- After roughly 500 changed lines, use diff stats and targeted hunks; never repeatedly print the complete cumulative diff.
- Do not run the complete backend suite or full coverage yourself. The orchestrator runs the authoritative complete backend suite once under coverage after you finish, and rejects any test failure or coverage below the configured floor. This avoids paying for identical full-suite executions without removing any acceptance gate.
- For a slice declaring 'localhost-e2e-server', implement the exact specs and screenshot outputs in its '## Trusted Browser Acceptance' section. Your coding sandbox may deny Chromium's macOS services: use Playwright collection or non-browser tests for your local feedback, do not fabricate screenshots, and do not declare the run failed solely because Chromium cannot launch. The orchestrator runs the declared browser contract twice outside your sandbox after you finish; that independent gate decides browser acceptance.
- Save evidence.
- Save risk-assessment.md.
- Save review-packet.md.
- Before finishing successfully, set the review-packet.md Result section to exactly 'Ready for independent validation'. Missing, partial, or any other result fails closed.
- The orchestrator owns changed-files.txt, .ralph/state.json, .ralph/progress.md, the selected slice Status transition, and mechanical handoff/progress bookkeeping. Do not edit those mechanical facts. Put substantive next-run risks or decisions in review-packet.md; edit HANDOFF only when it needs non-mechanical context the orchestrator cannot derive.
- Never run git commit, git add, or git push: your sandbox cannot write the worktree's git metadata and the attempt will fail your run. The orchestrator independently validates and commits passing work after you finish.
- High-risk slices proceed under the owner's standing approval (docs/working/HIGH_RISK_APPROVALS.md); record risk honestly in risk-assessment.md. Never implement a slice marked [revoked] there.
- When requirements are ambiguous, follow docs/working/DECISION_POLICY.md: choose the source-doc-compliant option, or the industry-standard default, record it in docs/working/ASSUMPTIONS.md, and continue. Do not stop to ask. Never invent business rules the documents do not state — stub them, record the open question, and continue.
- If the selected slice file is still an unsharpened template stub (its Goal reads "Deliver this narrow capability as a small, testable Ralph implementation slice" or its scope sections say only "Implement the named backend/API capability only"), your FIRST deliverable is sharpening that slice file with concrete requirements from the epic digest, docs/working/maps/, and the slice's cited source sections — before writing execution-plan.md. Never implement directly from an unsharpened stub.
- Do not sharpen or edit unrelated future slices during an implementation run. Owner/architecture preparation maintains a bounded ready runway outside the product session.
- Prefer docs/working/digests/ over re-reading large docs/source files. Read only the digest shared invariants and the selected slice section by default. If the selected section lacks a required source fact, locate that fact with docs/working/maps/ and rg, then save only the missing distilled fact.
- Stop only for the never-do list in DECISION_POLICY.md, forbidden/protected file edits, repeated gate failure, or diff limit violations.
- In repair mode: first diagnose the most recent failure — read failure-summary.md in the newest failed .ralph/runs/*/ folder (failed checks, last log lines, changed files); open the full gate logs only if that summary is insufficient, and inspect any leftover .ralph/worktrees/ from the failed attempt before starting fresh.

- This is an oversized-slice queue rewrite, not a general architecture review. Do not modify production code or review unrelated slices. Read docs/slices/010M-servicing-and-monitoring-frontend-wiring.md and the retained evidence for failed run 2026-07-21_102540_normal_run. The failed candidate measured 2093 lines against a 2000-line limit. Mark 010M Superseded and create at least two dependency-ordered Not Started successor slices named 010MA, 010MB, and so on. Each successor must contain an Origin section with the exact marker Oversized slice: `010M`. The first successor inherits every original prerequisite; each later successor depends on the previous one; every existing downstream dependency on 010M must point to the terminal successor. Preserve every original requirement, test, evidence, and risk across the successors. Each successor must be independently implementable and independently green, with a predicted diff comfortably below the configured limit. Update queue handoff or digest documents only when needed. Do not sharpen or change unrelated slices.

- In this queue-rewrite architecture mode, perform only the oversized-slice split described above.
- In an ordinary architecture review, read the bounded active docs/working/REVIEW_FINDINGS.md first. Open its historical archive only when a current diff reproduces an archived issue or an exact prior citation is required; never ingest the entire archive by default.
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
11. docs/slices/010M-servicing-and-monitoring-frontend-wiring.md
12. The matching docs/working/digests/ shared invariants and selected-slice section, if it exists

Do not load all docs/source during a normal run unless the selected slice explicitly requires it.
