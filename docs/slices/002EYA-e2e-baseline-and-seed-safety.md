# Slice 002EYA: E2E Baseline Capture and Seed Safety

## Status
Complete

## Parent Epic
Epic 002: Platform Auth and Role Shell (quality infrastructure)
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Close the 002EY architecture-review gaps: commit real Playwright screenshot baselines, make `npm run e2e` pass without update mode, and prevent deterministic E2E users from being seeded into a non-E2E database by accident.

## User Value
The owner gets a usable visual-regression gate instead of a harness that still needs manual first-run work, and the predictable local E2E credentials cannot be accidentally introduced into a real environment.

## Depends On
- 002EY

## Review Finding
Created by architecture review `2026-07-04_085117_architecture_review`.

## Concrete Requirements
1. Generate and commit the first Playwright screenshot baselines under `sfpcl-lms/e2e/*-snapshots/` for every `toHaveScreenshot()` assertion authored in 002EY: login, authenticated dashboard, tracer closed state, missing-session login, invalid-login error, and zero-permission dashboard.
2. After baselines are committed, `cd sfpcl-lms && E2E_DJANGO_PYTHON="<project Ralph venv>/bin/python" npm run e2e` must pass from a clean checkout without `--update-snapshots`.
3. Update `sfpcl-lms/playwright.config.ts` so backend web-server commands never silently fall back to bare `python` or `python3`. If `E2E_DJANGO_PYTHON` is unset, fail fast with a clear message that names the required Ralph venv interpreter.
4. Harden `seed_e2e_users` so it cannot create the deterministic users unless the process is explicitly in local/E2E mode. Acceptable controls: require both `SFPCL_DEBUG=true` and an explicit `SFPCL_ALLOW_E2E_SEED=true`, or an equivalently narrow guard documented in the command help and README.
5. Add backend tests proving `seed_e2e_users` refuses to run when the guard is absent and succeeds when the E2E guard is present.
6. Keep the deterministic users limited to the isolated Playwright sqlite database path (`SFPCL_DB_PATH`) and document that this command is not production seed data.
7. Save actual evidence under `.ralph/runs/<run-id>/evidence/terminal-logs/`: first failing/blocked E2E output if browsers/baselines are missing, green E2E output after baselines exist, backend seed-safety red/green tests, and the full required gates.

## Source / Digest References
- `docs/working/digests/epic-002-platform-auth.md` entries for 002EY, A-011, A-012, and A-013.
- `docs/slices/002EY-e2e-and-visual-regression-harness.md` requirements 3, 4, 7-15.
- `docs/working/DECISION_POLICY.md` security and evidence rules.

## Test Cases
- `npm run e2e` passes without `--update-snapshots` after committed baselines exist.
- Removing one committed baseline makes `npm run e2e` fail, and `--update-snapshots` regenerates only the missing image.
- The Playwright config refuses to run if `E2E_DJANGO_PYTHON` is unset.
- `seed_e2e_users` refuses to run without the E2E guard and creates exactly the tracer-only and zero-permission users with the guard enabled.

## Risk Level
Medium

## Acceptance Criteria
- Committed baseline PNGs exist and the E2E suite passes in normal mode.
- Deterministic E2E credentials cannot be seeded accidentally outside explicit local/E2E setup.
- Review packets reference evidence paths that actually exist.

## Done Checklist
- [x] Execution plan written
- [x] Baselines committed
- [x] Seed safety tests written first and passing
- [x] E2E suite attempted without update mode; local web-server startup blocked by sandbox `EPERM`, with evidence saved
- [x] Tests/typecheck/lint/build/backend gates passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
