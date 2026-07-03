# Risk Assessment

Risk level: Medium

- Selected slice: 002E2-frontend-role-bridge-hardening
- Mode: normal_run
- Manual review required: normal Ralph review only.

## Scope
- Frontend auth/session role mapping.
- Protected-shell role display branches in dashboard, profile, and header settings shortcut.
- Slice/status/handoff/progress/digest updates and next-slice sharpening.

## Controls
- No backend code, database schema, dependencies, package files, protected files, or source documents changed.
- No route permissions broadened. Backend canonical permissions still map only through the explicit `CANONICAL_TO_PROTOTYPE_PERMISSIONS` bridge.
- Unknown canonical permissions still grant no UI access.
- Backend roles with no prototype equivalent now map to neutral `backend_staff` with no prototype permissions unless canonical permissions map explicitly.
- Borrower portal demo auth and staff demo auth flag behavior were preserved.

## Residual Risk
- Browser screenshot capture could not be completed because the in-app Browser runtime was unavailable (`Browser is not available: iab`). This is recorded in `evidence/visual-evidence.md`, and `002EY` was sharpened to close the gap with Playwright screenshots.
- Some deeper pages still contain prototype role-specific branches, but zero-permission neutral users cannot reach permission-gated pages through sidebar/route access. This slice hardened the protected shell surfaces named by the slice: dashboard, profile, header/sidebar access, and shell display.

## Validation
- Focused frontend TDD red: `evidence/terminal-logs/frontend-auth-session-red.log`.
- Focused frontend green: `evidence/terminal-logs/frontend-auth-session-green.log`.
- Full frontend tests: `evidence/terminal-logs/frontend-tests.log`.
- Frontend typecheck: `evidence/terminal-logs/frontend-typecheck.log`.
- Frontend build: `evidence/terminal-logs/frontend-build.log`.
- Backend check/tests/migrations/coverage: `evidence/terminal-logs/backend-*.log`.
