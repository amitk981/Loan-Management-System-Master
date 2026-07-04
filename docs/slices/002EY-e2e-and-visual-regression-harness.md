# Slice 002EY: E2E and Visual Regression Harness (Playwright)

## Status
Complete

## Parent Epic
Epic 002: Platform Auth and Role Shell (quality infrastructure)
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Give the project a machine check for its two highest-value promises: user flows actually work end to end in a real browser, and screens stay visually identical to the approved prototype design.

## User Value
Design fidelity and working flows are verified automatically on every run that touches them — the owner no longer has to eyeball screenshots to catch visual drift.

## Depends On
- 002E2 (role bridge hardened before browser assertions rely on protected-shell role behavior)
- 002EX (the tracer bullet provides the first real end-to-end path)

## Concrete Requirements
1. Add `@playwright/test` (pinned) to `sfpcl-lms` dev dependencies; install the Chromium browser only.
2. `playwright.config.ts` with a `webServer` section that starts the Vite dev server and the Django dev server (persistent dev DB from 002D2).
3. One E2E test: login → walk the tracer-bullet happy path → assert the final closed state is visible in the UI.
4. Visual regression baselines (`toHaveScreenshot`) for: Login screen, Dashboard, and the tracer screen. Baselines are committed; subsequent runs fail on unexpected pixel drift beyond Playwright's default threshold.
5. Add script `"e2e": "playwright test"` to `sfpcl-lms/package.json`. Record in HANDOFF.md that the owner-side operator may flip `quality_gates.e2e_tests` from `optional` once the suite proves stable (config is protected).
6. Follow `docs/working/FRONTEND_DESIGN_RULES.md` — this slice adds tests only; zero product UI changes.
7. The login step must use the 002E production/default staff auth path (`POST /api/v1/auth/login/` followed by `GET /api/v1/auth/me/`). Do not enable `VITE_ENABLE_DEMO_AUTH` for the main E2E proof.
8. Seed or create the E2E staff user through backend test/dev setup, not through frontend fixtures. The user must have a backend role whose canonical permissions expose the tracer route/actions.
9. Add a negative browser check for revoked or missing auth: opening the app without a stored valid session shows the staff login and does not expose the tracer route.
10. Close the 002E visual-evidence gap from architecture review `2026-07-03_224536_architecture_review`: replace the prior HTML harness-only evidence with actual Playwright screenshots/baselines for login, authenticated dashboard, invalid login, missing/revoked auth, and tracer closed state.
11. Add a browser assertion for the 002E2 role hardening: an unmapped or zero-permission backend role must not see auditor/admin/borrower-specific shell affordances and must not expose tracer navigation/actions.
12. Close the additional 002E2 local visual-evidence limitation from run `2026-07-03_232853_normal_run`: the in-app Browser plugin reported `Browser is not available: iab`, so this slice must prove the neutral `backend_staff` dashboard/profile/header state with real Playwright screenshots instead of relying on plugin screenshots.
13. Close the 002EX local visual-evidence limitation from run `2026-07-03_234219_normal_run`: both Django `runserver` on `127.0.0.1:8000` and Vite on `127.0.0.1:5173` failed with `EPERM`, so this slice must run in an environment where Playwright can bind web servers and save the actual closed-state tracer screenshot.
14. E2E seed/setup must create a staff user with an explicitly active backend role and a `RolePermission` for `tracer.lifecycle.run`; `/auth/me/` must show `permissions` and `available_actions` containing exactly that tracer permission plus any other explicitly seeded test permissions.
15. The tracer browser test must click the staff-shell `Tracer` navigation item, click `Run tracer`, and assert visible closed evidence for Member, Application, Sanction, Loan account, and Repayment rows. It must not call tracer APIs directly from the test except through UI setup/verification helpers.
16. Clean up the dead ternary flagged by architecture review `2026-07-04_071340_architecture_review` Finding 2: in `sfpcl-lms/src/services/tracerApi.ts`, the Sanction row uses `status: disbursement ? 'recorded' : 'pending'`, but `disbursement` is always a truthy resolved object, so the `'pending'` branch is unreachable dead code. Derive the Sanction row status from the sanction response instead, and let the new tracer browser assertion cover the corrected value.

## Test Cases
- `npm run e2e` passes locally from a clean state.
- Deleting a baseline and re-running regenerates it (documented in the run summary).
- `npm run e2e` fails if the staff login call is mocked or bypassed instead of hitting the dev Django server.
- A missing/revoked session and a zero-permission role both land on the expected restricted UI without rendering protected tracer controls.
- A zero-permission `it_head` or `management_viewer` login renders the neutral backend-staff dashboard state and no Settings shortcut in the profile menu unless canonical settings permissions are present.
- The tracer closed-state screenshot is captured after the UI has completed all seven backend transitions and the visible loan-account row has status `Closed`.

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
