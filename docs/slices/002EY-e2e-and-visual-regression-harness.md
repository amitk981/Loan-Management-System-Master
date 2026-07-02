# Slice 002EY: E2E and Visual Regression Harness (Playwright)

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell (quality infrastructure)
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Give the project a machine check for its two highest-value promises: user flows actually work end to end in a real browser, and screens stay visually identical to the approved prototype design.

## User Value
Design fidelity and working flows are verified automatically on every run that touches them — the owner no longer has to eyeball screenshots to catch visual drift.

## Depends On
- 002EX (the tracer bullet provides the first real end-to-end path)

## Concrete Requirements
1. Add `@playwright/test` (pinned) to `sfpcl-lms` dev dependencies; install the Chromium browser only.
2. `playwright.config.ts` with a `webServer` section that starts the Vite dev server and the Django dev server (persistent dev DB from 002D2).
3. One E2E test: login → walk the tracer-bullet happy path → assert the final closed state is visible in the UI.
4. Visual regression baselines (`toHaveScreenshot`) for: Login screen, Dashboard, and the tracer screen. Baselines are committed; subsequent runs fail on unexpected pixel drift beyond Playwright's default threshold.
5. Add script `"e2e": "playwright test"` to `sfpcl-lms/package.json`. Record in HANDOFF.md that the owner-side operator may flip `quality_gates.e2e_tests` from `optional` once the suite proves stable (config is protected).
6. Follow `docs/working/FRONTEND_DESIGN_RULES.md` — this slice adds tests only; zero product UI changes.

## Test Cases
- `npm run e2e` passes locally from a clean state.
- Deleting a baseline and re-running regenerates it (documented in the run summary).

## Out of Scope
Cross-browser matrices, mobile-device emulation (member portal E2E arrives with 005G), CI wiring for E2E (local gate first; CI later when stable).

## Risk Level
Medium

## Acceptance Criteria
- One command runs a real-browser end-to-end proof of the core loan path.
- Visual baselines exist for the three named screens and drift fails the run.
- All existing gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Harness configured
- [ ] E2E + visual tests green
- [ ] Tests/typecheck/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated (e2e gate flip suggested when stable)
- [ ] State updated
- [ ] Commit created only after passing gates
