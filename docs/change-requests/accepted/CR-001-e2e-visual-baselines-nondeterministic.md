# E2E visual baselines are nondeterministic (rendered date/greeting) and README run command is wrong

## Type
bug-frontend

## Severity
Medium

## What Is Happening
The Playwright visual-regression baselines rot on their own even when the UI has not changed:

1. The dashboard screenshots (`dashboard.png`, `dashboard-zero-permission.png`) capture the header line "SFPCL LMS · <role> · <current date>" and the time-of-day greeting ("Good morning/afternoon/evening, E2E"). Because the real current date and wall-clock time render into the screenshot, a baseline captured on one day fails on any other day (pixel drift on the date text), and a baseline captured in the afternoon fails in the morning (greeting text). Observed on 2026-07-10: baselines committed 2026-07-08 failed with drift on exactly the date region even though most drift was legitimate UI change.
2. `sfpcl-lms/e2e/README.md` documents the run command as `E2E_DJANGO_PYTHON="../.ralph/venv/bin/python" npm run e2e` (relative path), but `playwright.config.ts` runs the backend webServer with `cwd: repoRoot`, so the relative path resolves to `/Users/<user>/.ralph/venv/bin/python` and the webServer fails with exit 127 ("No such file or directory"). Only an absolute path works today.

## Expected Behaviour
Two e2e runs on different days and at different times of day must produce pixel-identical screenshots when the UI code is unchanged, so committed baselines only fail on real UI drift. The README's documented run command must work as written.

## Steps To Reproduce
1. On day N, as operator, run `E2E_DJANGO_PYTHON="<absolute path to>/.ralph/venv/bin/python" npm run e2e -- --update-snapshots` from `sfpcl-lms/` and commit the baselines.
2. On day N+1 (or at a different time of day), run `E2E_DJANGO_PYTHON=... npm run e2e` with no UI changes.
3. The dashboard screenshot assertions fail with pixel drift confined to the date text (and the greeting text across time-of-day boundaries).
4. Separately: run the README's documented command with the relative `../.ralph/venv/bin/python` path — the backend webServer exits 127 before any test runs.

## Where It Appears
`sfpcl-lms/e2e/tracer.e2e.spec.ts` (dashboard baseline), `sfpcl-lms/e2e/auth-negative.e2e.spec.ts` (dashboard-zero-permission baseline), `sfpcl-lms/playwright.config.ts` (webServer cwd vs README), `sfpcl-lms/e2e/README.md` (run command), and the dashboard header component that renders the current date and time-of-day greeting.

## Source Document Reference
docs/slices/002EY-e2e-and-visual-regression-harness.md — the harness requires deterministic screenshot baselines (the config already deletes the e2e DB before each run precisely so sequence numbers stay identical; rendered wall-clock date/time defeats the same determinism goal).

## Acceptance Criteria
- With no UI changes, `npm run e2e` passes against committed baselines regardless of the calendar date or time of day it is run (e.g. by freezing/mocking the browser clock in the Playwright fixtures, or masking the date/greeting regions in `toHaveScreenshot` — implementer chooses, but the mechanism must not weaken detection of real UI drift elsewhere on the page).
- Baselines regenerated once after the fix stay green on subsequent days without `--update-snapshots`.
- The run command documented in `sfpcl-lms/e2e/README.md` works exactly as written from `sfpcl-lms/` (fix the path or the documented command).
- The production dashboard behaviour (showing the real current date/greeting to real users) is unchanged — determinism is achieved in the test harness, not by removing the feature.
