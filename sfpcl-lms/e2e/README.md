# End-to-end & visual-regression harness (Playwright)

This suite proves the two highest-value promises of the platform in a real
browser: the core loan flow works end to end, and the approved screens stay
visually identical to the prototype.

## What it covers
- `tracer.e2e.spec.ts` — logs in through the **production staff auth path**
  (`POST /api/v1/auth/login/` then `GET /api/v1/auth/me/`), opens the Tracer
  workspace from the shell nav, runs the tracer, and asserts the closed-state
  evidence rows (Member, Application, Sanction, Loan account, Repayment) with the
  loan account showing **Closed**. Visual baselines: `login`, `dashboard`,
  `tracer-closed`.
- `auth-negative.e2e.spec.ts` — a missing session and an invalid login both stay
  on the staff login with no tracer route exposed; a zero-permission staff user
  sees the neutral backend-staff dashboard with no Tracer nav and no Settings
  shortcut in the profile menu. Visual baselines: `login-missing-session`,
  `login-invalid`, `dashboard-zero-permission`.
- `epic-006-closure.e2e.spec.ts` — captures the eighteen-state Appraisal
  Workbench matrix, then uses real Deputy Manager Finance and Credit Manager
  logins to reach one pending sanction case through the real Django API.

Login uses the real backend — no token injection or request mocking — so the
suite fails if the auth call is ever bypassed.

## Backend E2E users
The web server seeds deterministic users via the backend command
`seed_e2e_users` (never frontend fixtures):
- `e2e.tracer@sfpcl.example` — active role `e2e_tracer` with exactly one
  `RolePermission` for `tracer.lifecycle.run`; `/auth/me/` returns exactly that
  permission.
- `e2e.zero@sfpcl.example` — active role `it_head` (neutral `backend_staff`) with
  no permissions.
- `e2e.credit.finance@sfpcl.example` and `e2e.credit.manager@sfpcl.example` —
  synthetic Epic 006 actors plus one resettable `LOE2E00601` credit fixture.
- `e2e.epic009.finance@sfpcl.example`, `e2e.epic009.credit@sfpcl.example`, and
  `e2e.epic009.cfc@sfpcl.example` — isolated Epic 009 actors for the exact staff-disbursement
  closure spec. That spec uses `ChecklistPass123!`, a guarded owner-evidence seed, and real Django
  Loan Account/workspace/action endpoints. It captures nine state-specific PNGs and writes
  `epic-009-screenshot-sha256.txt`, rejecting any pair of byte-identical screenshots.

The tracer, zero-permission, and Epic 006 users use `E2eTracer123!` (local only).

This is not production seed data. The command refuses to run unless both
`SFPCL_DEBUG=true` and `SFPCL_ALLOW_E2E_SEED=true` are present. The Playwright
config sets those flags only for the backend web server that uses the isolated
`SFPCL_DB_PATH` sqlite database.

## One-time setup
`@playwright/test` is a pinned dev dependency. Install it and the Chromium
browser (both need network the AFK sandbox lacks — run this on the operator
machine):

```bash
cd sfpcl-lms
npm install
npx playwright install chromium
```

All specs use the browser selected centrally by `playwright.browser.ts`: an
explicit `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`, then Playwright-managed
Chromium, then an installed system Chrome/Chromium. Verify that the selected
browser can create a page without starting Django or Vite:

```bash
npm run e2e:probe
```

Before a Ralph slice declaring `localhost-e2e-server` starts, the orchestrator
runs this probe. If it fails, Ralph makes one bounded Chromium installation
attempt and probes again. A second failure stops as browser infrastructure;
it does not spend a product repair attempt. The slice-specific browser
acceptance still runs twice after implementation.

## Running
```bash
# From sfpcl-lms/. Point E2E_DJANGO_PYTHON at the Ralph venv interpreter.
E2E_DJANGO_PYTHON="$(git rev-parse --path-format=absolute --git-common-dir)/../.ralph/venv/bin/python" npm run e2e
```

`E2E_DJANGO_PYTHON` is required. The config fails fast if it is unset rather
than falling back to `python` or `python3`.

The config's `webServer` block starts both the Django dev server (on
`127.0.0.1:8000`, against an isolated `sfpcl_credit/e2e.sqlite3` via
`SFPCL_DB_PATH`) and the Vite dev server (on `localhost:5173`) automatically.

## Visual baselines
Baselines are committed under `e2e/*-snapshots/`. Subsequent runs fail on
unexpected pixel drift beyond Playwright's default threshold.

The Epic 006 contract stores each PNG baseline as a one-line `.png.base64`
file, decodes it only for comparison, and removes the temporary PNG afterward.
This preserves the exact Chromium bytes while keeping Ralph's line-count gate
meaningful for binary files.

Generate or refresh a baseline (e.g. after an approved design change, or to
create the first set on a machine with browsers):

```bash
E2E_DJANGO_PYTHON="$(git rev-parse --path-format=absolute --git-common-dir)/../.ralph/venv/bin/python" npm run e2e -- --update-snapshots
```

Deleting a baseline PNG and re-running with `--update-snapshots` regenerates just
that screenshot; commit the regenerated file.

## Required slice acceptance

General E2E remains optional in `.ralph/config.yaml`, but any slice declaring
`localhost-e2e-server` must name its trusted specs and screenshots. Ralph runs
that exact contract twice and rejects the slice on either failure or missing
evidence.
