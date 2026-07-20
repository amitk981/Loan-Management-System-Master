You are running Ralph AFK mode.

Run ID:
2026-07-21_030327_repair

Mode:
repair

Selected slice:
010J2-reminder-eligibility-and-delivery-integrity-closure

Working directory:
/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_020140_normal_run

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
- In same-worktree repair: diagnose /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_020140_normal_run/.ralph/runs/2026-07-21_020140_normal_run/failure-summary.md first and preserve the current candidate. Fix only the demonstrated validation domain; within that domain, rerun the exact named validator until it passes and correct every error it reports or subsequently reveals. In architecture-review mode, retain documentation-only scope and do not repeat the product critique from scratch. Newly exposed errors from the same validator are part of the same bounded repair, not permission to change unrelated product scope. Rely on full independent revalidation before any commit.
- This corrective slice has a machine-readable closure contract. Before returning, run exactly: ./scripts/ralph-validate-review-closure.sh --slice docs/slices/010J2-reminder-eligibility-and-delivery-integrity-closure.md --run-dir .ralph/runs/2026-07-21_030327_repair . Keep rerunning that fast check until it prints PASS. Markdown prose may follow a table only after a blank line; Python tests may use an exact path::selector or exact Django dotted test label. Do not defer a failure from this command to the orchestrator.


- In architecture-review mode: do NOT modify production code. Review the diffs of slices merged since the last review as an independent critic: test quality (real assertions, edge cases), doc fidelity against source references, duplication, architecture drift. Append findings to docs/working/REVIEW_FINDINGS.md. Only Critical/High correctness, security, financial/data-integrity, or binding source-contract findings create immediate corrective work. Bundle Medium findings into the owning slice or epic closure and record Low findings unless they naturally combine with higher-severity work. Group related symptoms by root owner instead of creating one slice per symptom. Report findings closed, new findings by severity, and corrective slices added in review-packet.md under '## Convergence Metrics' using the exact lines '- Findings closed: N', '- New Critical: N', '- New High: N', '- New Medium: N', '- New Low: N', and '- Corrective slices added: N'. A normal new corrective must be a numeric Not Started slice with a valid Depends On contract. Exception: when the scope instruction says a carried root is already at the configured generation cap and it genuinely needs a different successor, create exactly one next-numbered CR-NNN terminal finalizer instead of another numeric leaf. Its filename may add a descriptive slug, but every Finding Closure Manifest row must use the CR-NNN identity. It must be Not Started, High risk, owned by the same Parent Epic, group every related Critical/High root into its Review Finding Closure contract, and contain exactly '## Architecture Review Finalizer' followed by '- Epic: NNN', '- Root ID: ROOT-NNN-*', and '- Exhausted corrective generation: N'. The standing owner policy admits only one such terminal CR per root; a second terminal recurrence still fails closed. When an actionable existing root-owner slice already covers a new Critical/High finding, do not duplicate it; add one exact '- Existing corrective slice: ID' line per mapped slice under the convergence metrics. Validation requires every mapped ID to resolve to one tracked Not Started or Blocked slice. If corrective additions exceed closures across two reviews, recommend one root-cause boundary correction instead of further leaf patches. - Every generated corrective slice must declare exactly one `## Runtime Capabilities` section. Declare `postgresql-five-race-acceptance` when its text or Trusted PostgreSQL Acceptance requires PostgreSQL, concurrency, locking, or race evidence; declare `localhost-e2e-server` when it requires browser, screenshot, Playwright, or trusted-browser evidence; otherwise declare `none`. Before returning, source `scripts/lib/ralph-runtime-capabilities.sh` and `scripts/lib/ralph-postgresql-acceptance.sh`, run `ralph_validate_slice_runtime_requirements` against every untracked `docs/slices/*.md` candidate, and run `ralph_validate_trusted_postgresql_acceptance` for every candidate declaring the PostgreSQL capability. A failure is part of this review candidate and must be corrected here, not deferred to the next product run. - Trusted per-root corrective history: ROOT-010-DPD-SNAPSHOT-OWNER=generation 1 via 010I2, ROOT-010-INTEREST-CALCULATION-OWNER=generation 2 via 010H3, ROOT-010-REMINDER-DELIVERY-OWNER=generation 1 via 010J2. Review the new product diff and these active roots only. Preserve every stable Finding ID/Root ID, never charge a new root for another root's history, and never relabel a carried symptom as New. A root may receive at most one grouped corrective plus one successor; unrelated roots retain independent budgets.
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
11. docs/slices/010J2-reminder-eligibility-and-delivery-integrity-closure.md
12. The matching docs/working/digests/ shared invariants and selected-slice section, if it exists

Do not load all docs/source during a normal run unless the selected slice explicitly requires it.
