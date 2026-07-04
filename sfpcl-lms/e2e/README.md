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

Login uses the real backend — no token injection or request mocking — so the
suite fails if the auth call is ever bypassed.

## Backend E2E users
The web server seeds two deterministic users via the backend command
`seed_e2e_users` (never frontend fixtures):
- `e2e.tracer@sfpcl.example` — active role `e2e_tracer` with exactly one
  `RolePermission` for `tracer.lifecycle.run`; `/auth/me/` returns exactly that
  permission.
- `e2e.zero@sfpcl.example` — active role `it_head` (neutral `backend_staff`) with
  no permissions.

Password for both (local only): `E2eTracer123!`.

## One-time setup
`@playwright/test` is a pinned dev dependency. Install it and the Chromium
browser (both need network the AFK sandbox lacks — run this on the operator
machine):

```bash
cd sfpcl-lms
npm install
npx playwright install chromium
```

## Running
```bash
# From sfpcl-lms/. Point E2E_DJANGO_PYTHON at the project venv interpreter.
E2E_DJANGO_PYTHON="../.ralph/venv/bin/python" npm run e2e
```

The config's `webServer` block starts both the Django dev server (on
`127.0.0.1:8000`, against an isolated `sfpcl_credit/e2e.sqlite3` via
`SFPCL_DB_PATH`) and the Vite dev server (on `localhost:5173`) automatically.

## Visual baselines
Baselines are committed under `e2e/*-snapshots/`. Subsequent runs fail on
unexpected pixel drift beyond Playwright's default threshold.

Generate or refresh a baseline (e.g. after an approved design change, or to
create the first set on a machine with browsers):

```bash
E2E_DJANGO_PYTHON="../.ralph/venv/bin/python" npm run e2e -- --update-snapshots
```

Deleting a baseline PNG and re-running with `--update-snapshots` regenerates just
that screenshot; commit the regenerated file.

## Promoting to a required gate
`quality_gates.e2e_tests` is `optional` in `.ralph/config.yaml` (a protected
file). Once this suite proves stable with committed baselines, the owner-side
operator may flip it so drift fails the run. See `docs/working/HANDOFF.md`.
