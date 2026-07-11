# Review Packet: 2026-07-11_205723_normal_run

## Result
Ready for independent validation

## Slice
005FA4-portal-auth-real-boundary-flag-proof

## Recommended Next Action
Run the configured Ralph validation and trusted browser contract, then commit/merge only if green.

## Change Summary

- Replaced the manually projected `LoginScreen` demo-flag test with unset/false/true module-isolated
  renders of the real `App` and its real `RoleProvider`.
- The red true-flag test exposed `Borrower / Member` in the staff demo selector. Removed only that
  role and clarified the existing label; every staff role and the visual pattern remain unchanged.
- Removed the Playwright spec's old hard-coded run ID, required `RALPH_EVIDENCE_DIR`, created the
  relative screenshot folder, and added the declared post-logout screenshot.

## Traceability

- The slice/review says false and unset must fail closed and true may expose only staff demo
  controls with no portal bypass. `demoAuthFlag.test.tsx` renders the real boundary for all three;
  its red output proves the borrower leak, and the green matrix proves its removal.
- The auth/session references require credential-backed portal identity and fail-closed logout.
  `portal-auth-interaction.e2e.spec.ts` asserts empty-submit zero-call validation, one exact populated
  request, backend identity restore, and token/protected-content removal despite logout transport
  failure.
- The browser acceptance section declares `portal-login-validation.png` and
  `portal-post-logout.png`. Both paths are now beneath the supplied evidence directory; local
  Chromium launch was sandbox-denied and the trusted orchestrator gate must produce them.

## Verification

- Frontend: lint, typecheck, build, and 148 Vitest tests passed.
- Backend: Django check and migration sync passed; 397 tests passed (5 expected skips), 94% coverage.
- Browser: both cases reached launch after healthy Django/Vite servers; Chromium failed only at the
  documented macOS Mach-port restriction. Full log is in `evidence/terminal-logs/`.
- Review: `git diff --check` and state JSON parsing passed; no source/protected files changed.
