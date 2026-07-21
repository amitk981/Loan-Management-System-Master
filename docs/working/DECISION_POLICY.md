# Decision Policy for Autonomous Runs

The project owner is not a developer and has granted standing approval for autonomous operation (see `docs/working/HIGH_RISK_APPROVALS.md`). Agents therefore do not ask for approval. Instead, every decision follows this policy, in order:

## 1. Decision ladder (ambiguity is not a reason to stop)
1. If `docs/source/` answers it → do what the source documents say. They are the product truth.
2. If the source docs are silent → choose the boring, industry-standard option (see §3), record one line in `docs/working/ASSUMPTIONS.md` (what was assumed, why, which slice must confirm it), and continue.
3. If the choice would invent a business rule (eligibility formulas, money amounts, approval authority, compliance behaviour) that the docs do not state → do NOT invent it. Implement the mechanism with the rule left explicitly configurable/stubbed, record it as an open question in ASSUMPTIONS.md, and continue the rest of the slice.
4. Only stop when continuing would require doing something on the never-do list (§4) or the same gate has failed after a repair attempt.

## 2. Quality bar (what "done" means)
- TDD is mandatory for backend and business logic: failing test first, then code, red/green evidence saved.
- All risk-selected quality gates green (see `.ralph/config.yaml`): frontend typecheck/tests/build; backend check/migrations-sync plus independently mapped impacted tests for localized Low/Medium candidates, or complete-suite coverage and its floor for every fail-closed class and periodic checkpoint.
- API contract changes are reflected in `docs/working/API_CONTRACTS.md` in the same run.
- The review packet includes a traceability note: "the source doc says X (file §n), the code does X, verified by test Y" — written for a non-developer.
- Frontend fidelity: `docs/working/FRONTEND_DESIGN_RULES.md` is binding — reuse the prototype's components and visual system; never introduce new styling or components. If the documents require functionality with no prototype screen, the slice must build that screen from existing patterns and stitch it to the backend; a backend with no reachable UI does not count as done.
- No dead code, no commented-out blocks, no TODOs without a slice or ASSUMPTIONS entry that owns them.

## 3. Technology standards (the "better tools" defaults)
Backend: Django + Django REST Framework, PostgreSQL in production (SQLite acceptable only for local tests), djangorestframework-simplejwt/PyJWT for tokens, pytest or Django test runner, coverage.py. Frontend: React + TypeScript + Vite, vitest + Testing Library, ESLint. Infrastructure: environment variables for secrets, pinned dependencies, migrations for every schema change. Prefer the standard, maintained, widely-documented tool over a clever or niche one; new dependencies follow `docs/working/DEPENDENCY_POLICY.md`.

## 4. Never do autonomously (hard-enforced; validation fails the run)
- Modify protected files: `scripts/`, `.github/`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, or anything in `docs/source/`.
- Weaken, skip, or reinterpret the risk-selected quality gates, checkpoint rules, coverage floor, risk rules, or this policy.
- Delete or rewrite committed history; force-push.
- Deploy anywhere, call paid external services, or send communications to real people.
- Store real personal or financial data in fixtures/tests.

## 5. Owner's brake
The owner can stop any slice without a conversation: add `- [revoked] <slice-id> | <date> | <reason>` to `docs/working/HIGH_RISK_APPROVALS.md`. Runs check this before starting.
