# Execution Plan — 002EYA E2E Baseline Capture and Seed Safety

## Scope
- Preserve the committed Playwright snapshot baselines already present under `sfpcl-lms/e2e/*-snapshots/`.
- Make the Playwright backend server fail fast if `E2E_DJANGO_PYTHON` is missing instead of falling back to `python` or `python3`.
- Guard `seed_e2e_users` so deterministic local E2E users are created only when explicit local/E2E flags are present.
- Add/adjust backend tests test-first for the seed guard and keep existing seed behavior green under the guard.
- Save red/green and gate evidence under `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/`.

## Permission Check
- Allowed edit paths used: `sfpcl-lms/**`, `sfpcl_credit/**`, `.ralph/runs/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`.
- Protected paths will not be edited: `scripts/`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, `docs/source/**`.

## TDD Steps
1. Add a backend test proving `seed_e2e_users` refuses when the explicit E2E seed guard is absent; run it and save the failing red log.
2. Implement the command guard requiring local debug plus explicit `SFPCL_ALLOW_E2E_SEED=true`.
3. Update existing seed tests to set the guard for success cases; run targeted tests and save the green log.
4. Add/update frontend config test coverage if a suitable existing unit harness exists; otherwise validate the fail-fast behavior by running `npm run e2e` without `E2E_DJANGO_PYTHON` and saving the blocked/fail-fast log.

## Verification
- Backend targeted seed tests.
- Backend full tests, `manage.py check`, migrations check, and coverage using `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`.
- Frontend `npm run typecheck`, `npm run lint`, `npm test`, and `npm run build`.
- `npm run e2e` with the required interpreter if local browsers are available; if the sandbox cannot run browsers or bind servers, save the actual failure/blocking output.

## Finish
- Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Update `docs/working/HANDOFF.md`, `.ralph/progress.md`, `.ralph/state.json`, and the selected slice status/checklist.
- Sharpen the next 1-2 `Not Started` slice files using already-opened digest context only.
