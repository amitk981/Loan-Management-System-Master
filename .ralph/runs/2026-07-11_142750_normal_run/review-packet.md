# Review Packet: 2026-07-11_142750_normal_run

## Result
Ready for independent validation

## Slice
005FA3-portal-auth-interaction-and-demo-flag-proof

## Recommended Next Action
Run the configured validator, including the collected Playwright interaction spec in an environment
that permits local Django/Vite server sockets; capture `portal-login-validation.png` there.

## Scope and Review Notes

- Production: `MP00_Login` no longer uses native `required` on its two controlled fields, allowing
  its existing empty-submit error to render. No styling, credential payload, or callback changed.
- Tests: real browser interactions cover default pre-login denial, exact populated login request,
  backend portal identity, and failed-network logout clearing. Vitest covers module-isolated
  unset/false/true demo flags and the required single-callback prop contract.
- Dependency attempt: Testing Library/jsdom were unavailable from the offline cache, so package and
  lock files remain untouched; the repository's pinned Playwright harness supplies real DOM events.

## Traceability

- The Epic 005 digest says 005FA2 removed the demo fallback but lacked executed form, flag, and
  logout proof. `portal-auth-interaction.e2e.spec.ts` executes those public boundaries; the focused
  flag and RoleProvider tests verify default authority without copying production projections.
- Source security/session requirements require protected UI to fail closed. The logout interaction
  aborts `/auth/logout/`, then asserts the backend identity, protected content, demo affordance, and
  stored session are absent.

## Validation

- Frontend: lint, typecheck, build, and 144 Vitest tests passed.
- Backend: check and migration sync passed; 394 tests passed at 94% coverage (floor 85%).
- Browser: collection/spec is present; local server startup failed with sandbox `Operation not
  permitted`, saved in `evidence/terminal-logs/portal-auth-red.log`.
