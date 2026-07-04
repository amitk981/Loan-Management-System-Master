# Risk Assessment — 002EY E2E and Visual Regression Harness

## Declared risk level
Medium (matches the slice file).

## Why Medium
- Adds test infrastructure and one small backend dev-seed command; touches no
  production business logic beyond a defect fix in `tracerApi.ts`.
- New dependency (`@playwright/test`) is dev-only and never imported by the app
  bundle; a build/CI concern, not a runtime/security one.
- The only production-code change is the Finding 2 fix, guarded by a new vitest.

## What could go wrong / mitigations
- **New dev dependency.** `@playwright/test@1.49.1` pinned exactly; lockfile
  reconciled so the committed state is `npm ci`-consistent. Browsers are not
  bundled; `npx playwright install chromium` is an explicit operator step.
- **Playwright specs breaking the hard gates.** e2e/ and `playwright.config.ts`
  sit outside tsconfig `include` (`src`), outside the Vite build graph, and are
  excluded from vitest (`test.include` confined to `src/**`). Verified: build,
  typecheck, and `vitest run` (17 tests) all green with the harness present.
- **Auth bypass in E2E.** The suite logs in only through the real
  `POST /auth/login/` + `GET /auth/me/` path via the form; no token injection or
  request mocking, so a bypass would fail the suite (req 7).
- **Backend seed correctness.** `seed_e2e_users` is idempotent (get_or_create)
  and covered by 5 tests asserting the single tracer permission, the zero-perm
  user, idempotency, and the exact `/auth/me/` permission set.
- **E2E DB isolation.** `SFPCL_DB_PATH` defaults unchanged; the harness points the
  dev server at a dedicated `sfpcl_credit/e2e.sqlite3` so it never touches the
  local dev DB.

## Sandbox limitation (honest disclosure)
- Unlike the 002EX run, this sandbox CAN bind `127.0.0.1` (verified), so the EPERM
  blocker (slice req 13) is resolved in principle.
- However this sandbox has no network, so `@playwright/test` and the Chromium
  binary cannot be installed here and the Playwright suite/baselines cannot be
  *run/generated* in this run. The full harness, specs, seed, and docs are
  authored and the dependency pinned; the committed baselines and green E2E run
  must be produced once on a networked machine with browsers
  (`npx playwright install chromium` + `npm run e2e -- --update-snapshots`), per
  `sfpcl-lms/e2e/README.md`. The hard gates never execute Playwright
  (`e2e_tests: optional`; no e2e gate in ralph-validate.sh), so this run's gates
  are unaffected.

## Protected / forbidden files
None modified. `playwright.config.ts` and `e2e/**` are new paths not present in
`.ralph/permissions.json` `allowed_without_approval`, but they are neither
protected nor forbidden and are exactly what the slice requires; created under the
owner's standing approval for autonomous runs.

## Gate evidence (this run)
- Frontend: typecheck ✓, build ✓, `vitest run` 17/17 ✓ (incl. new tracerApi test).
- Backend: `check` ✓, `makemigrations --check` clean ✓, 64 tests ✓, coverage 95%
  (floor 85) ✓.
- Playwright suite: authored; execution deferred to the networked operator env.
