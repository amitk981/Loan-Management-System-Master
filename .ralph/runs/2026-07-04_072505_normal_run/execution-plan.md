# Execution Plan — 002EY E2E and Visual Regression Harness (Playwright)

## Slice intent
Add a Playwright end-to-end + visual-regression harness for the staff shell: one
real-browser E2E test that logs in through the production auth path and walks the
002EX tracer happy path to a closed state, plus visual baselines for Login,
Dashboard and Tracer screens. Also close the dead-ternary defect flagged by
architecture review 2026-07-04_071340 Finding 2 in `tracerApi.ts`. Tests-only for
the frontend product UI; no design changes (FRONTEND_DESIGN_RULES.md).

## Environment reality (why some artifacts are authored, not executed here)
- This sandbox CAN bind `127.0.0.1` (verified), unlike the 002EX run — so the
  EPERM limitation (slice req 13) is gone in principle.
- BUT the sandbox has no network and `@playwright/test` + the Chromium binary are
  not installed and cannot be installed offline. So the Playwright suite and its
  screenshot baselines cannot be *run/generated* inside this run.
- Per the run rules ("pin the dependency, write the code/tests, note the missing
  module, finish"), I author the full harness + specs + seed + docs, pin
  `@playwright/test`, and document the one operator command that generates the
  committed baselines and flips the gate. The hard gates never execute Playwright
  (no e2e gate in ralph-validate.sh; `e2e_tests: optional`), so this is safe.

## Changes
### Backend (TDD)
1. `identity/management/commands/seed_e2e_users.py` — idempotent command creating:
   - a tracer staff user (`e2e.tracer@sfpcl.example`) with an active role holding a
     single `RolePermission` for `tracer.lifecycle.run` (req 8, 14);
   - a zero-permission staff user (`e2e.zero@sfpcl.example`, role `it_head` → maps
     to neutral `backend_staff`, no RolePermissions) for the restricted-UI checks
     (req 9, 11, test case 5).
2. `config/settings.py` — allow `SFPCL_DB_PATH` env override for the sqlite NAME
   (default unchanged) so the E2E web server uses an isolated dev DB. Boring
   env-var default per DECISION_POLICY §3; logged in ASSUMPTIONS.md.
3. `tests/test_seed_e2e_users.py` — asserts the seeded users, roles, single tracer
   RolePermission, idempotency, and that `/auth/me/` returns exactly
   `['tracer.lifecycle.run']` for the tracer user and `[]` for the zero user.

### Frontend
4. `src/services/tracerApi.ts` — Finding 2 fix: capture the sanction response and
   derive the Sanction/Application row status from `sanction.new_status`; drop the
   unreachable `disbursement ? 'recorded' : 'pending'` ternary (disburse call kept
   for its state transition, no longer bound to an unused var).
5. `src/services/tracerApi.test.ts` — vitest: mocks fetch across the 7 calls and
   asserts the Sanction row is derived from the real sanction response ('sanctioned')
   and the loan-account row reflects closure ('closed') — locks in the fix.
6. `playwright.config.ts` — two `webServer`s (Django dev server on 127.0.0.1:8000
   with migrate+seed, Vite dev server on 127.0.0.1:5173), Chromium project, default
   screenshot threshold, testDir `./e2e`.
7. `e2e/helpers.ts` — shared credentials + a `staffLogin()` helper (UI form only).
8. `e2e/tracer.e2e.spec.ts` — login via production path → click Tracer nav → Run
   tracer → assert Member/Application/Sanction/Loan account/Repayment rows + the
   `Closed` badge; visual baselines for Login, Dashboard, Tracer (req 3,4,10,15).
9. `e2e/auth-negative.e2e.spec.ts` — no stored session lands on staff login and
   hides the tracer route; zero-permission staff sees neutral dashboard, no Tracer
   nav, no Settings shortcut (req 9,11, test case 5).
10. `e2e/README.md` — how to install the browser, run `npm run e2e`, (re)generate
    baselines with `--update-snapshots`, and the note that the operator may flip
    `quality_gates.e2e_tests` from `optional` once stable.
11. `package.json` — pin `@playwright/test`, add `"e2e": "playwright test"` (req 1,5).
12. `vite.config.ts` — confine vitest to `src/**` so it never tries to run the
    Playwright specs under `e2e/` (which import the not-yet-installed package).

## Gate strategy
- e2e/ and playwright.config.ts are outside tsconfig `include` (`src`) → typecheck
  untouched; outside vite build graph → build untouched; excluded from vitest via
  the confined include → unit tests untouched. Backend gates cover the new command
  and settings via new tests. Protected-paths, diff-limits, no-op all satisfied.

## Verification here
- Backend: red→green for `test_seed_e2e_users.py`, full suite + coverage.
- Frontend: red→green for `tracerApi.test.ts`, then `npm test`, `typecheck`, `build`.
- Playwright suite + baselines: authored; execution deferred to the networked
  operator/orchestrator environment (documented). Logs in evidence/terminal-logs/.
