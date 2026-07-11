# Slice 005FA2: Portal Demo-Login Gating and Session Authority

## Status
Complete

Owner-fixed directly on 2026-07-11 (outside the Ralph loop, same commit as this file): `MP00_Login.tsx` demo fallback removed and `onSubmitLogin` made required; `App.tsx` unconditional demo wiring removed and `clearUser()` added to logout; `RoleContext` now defaults to an exported `UNAUTHENTICATED_USER` (no identity, no role codes, no permissions) instead of the deputy-manager fixture. Regression tests added in `MP00_Login.test.tsx` (3) and `RoleContext.test.tsx` (2). Gates run in the owner session: typecheck, ESLint, Vitest 137/137, production build — all pass. The staff LoginScreen demo selector and Header role switcher were verified already gated by `DEMO_AUTH_ENABLED`.

## Parent Epic
Epic 005: Application Intake and Completeness (portal authentication corrective)
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Close a latent client-side authentication bypass found in the 2026-07-11 prototype-logic audit: `MP00_Login.tsx` fell back to `onLogin()` when credentials were filled but `onSubmitLogin` was absent, and `App.tsx` wired that fallback to `handleDemoLogin('borrower')` unconditionally — NOT gated by `DEMO_AUTH_ENABLED`. Unreachable with the then-current App wiring (which always passed `onSubmitLogin`), but one refactor away from a credential-less demo borrower session.

## User Value
No one can enter the member portal shell without a real authenticated session; demo affordances exist only when the demo flag is explicitly enabled.

## Depends On
- 005FA

## Source References
- docs/source/auth-permissions.md portal authentication requirements
- docs/source/security-privacy.md session/authentication controls
- docs/slices/005FA-member-portal-authentication.md (the real portal session contract)
- docs/slices/005G2-member-portal-session-and-audit-contract-hardening.md
- sfpcl-lms/src/services/authSession.ts (`DEMO_AUTH_ENABLED = import.meta.env.VITE_ENABLE_DEMO_AUTH === 'true'`)

## Prototype Reference
- sfpcl-lms/src/pages/borrower/portal/auth/MP00_Login.tsx (lines ~27-30: empty-credential fallback)
- sfpcl-lms/src/App.tsx (unconditional `onLogin={() => handleDemoLogin('borrower')}` for MP00)
- sfpcl-lms/src/contexts/RoleContext.tsx (initial state is the `ROLE_USERS.deputy_manager_finance` fixture)

## Concrete Requirements
1. Remove the `onLogin()` demo fallback path from `MP00_Login.tsx`: empty/invalid credentials produce a validation error; the only success path is `onSubmitLogin` completing against the real 005FA session API.
2. In `App.tsx`, the demo borrower login (like the staff demo selector) must exist only behind `DEMO_AUTH_ENABLED`; when the flag is false there is no demo code path reachable from either login surface.
3. Harden `RoleContext`: the pre-login state must not be a plausible staff fixture user with permissions. Initialize to an unauthenticated/empty user (no permissions, no role label) so nothing can render role-gated content before `setBackendUser` runs; demo `setRole` remains available only under `DEMO_AUTH_ENABLED`.
4. Verify the staff `LoginScreen` demo selector remains correctly gated (it already checks the flag) and add the regression tests below so it stays that way.
5. No visual redesign; error states use existing patterns.

## Test Cases
- Submitting the portal login form with empty fields shows a validation error and does not set any logged-in state (regression on the exact bypass).
- With `VITE_ENABLE_DEMO_AUTH` unset/false: no demo affordance renders on staff or portal login, and `handleDemoLogin` is unreachable.
- With the flag true: demo flows still work for local development.
- Pre-login render exposes no permission-gated UI (RoleContext default-user regression).

## Out of Scope
Backend session/audit contract (005FA/005G2 delivered), tracer/demo production isolation inventory (012E2 — this slice closes the login-path subset early because it is an auth bypass), portal screens beyond the login surfaces.

## Risk Level
High

## Acceptance Criteria
- The empty-credential portal bypass is gone and covered by regression tests; all demo paths are flag-gated.
- All gates pass; screenshots of the corrected login validation state saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] Permissions tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
