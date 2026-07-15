# Final Summary

Result: Repair complete; independent browser acceptance pending

Repaired the demonstrated 008L4 trusted-browser failure while preserving the quarantined
implementation.

## Root cause and fix

Real portal login and `/auth/me` succeeded, but the canonical catalogue still marked
`borrower_portal_user` inactive. `/auth/me` consequently returned `roles: []`; the frontend mapped
the session to its neutral staff shell, called `/api/v1/dashboard/`, and never rendered the member
heading. The catalogue now treats `borrower_portal_user` as the one active external role. All future
external identities remain inactive, no staff permissions were granted, and portal sessions retain
only the existing own-data allowlist.

## Verification

- Failing-first evidence captured inactive catalogue status and the empty real `/auth/me` role list;
  the exact assertions pass after the repair.
- 25 affected identity/portal tests pass.
- Playwright collects the two declared real-boundary specs with no API route interception.
- Frontend lint, typecheck, all 304 tests, and production build pass.
- Django check and migration drift pass; all 897 backend tests pass with 46 expected capability skips
  and 91% coverage, above the configured 85% floor.
- Local Chromium still cannot launch because the coding sandbox denies its macOS Mach port. The
  in-app browser also has no available backend. No screenshot was fabricated; Ralph must run both
  specs twice externally and retain all four declared screenshots before acceptance.

## Scope

The repair changed only the canonical borrower-role seed contract and its regressions, plus required
Ralph documentation/evidence. Portal document authority, current-renderer selection, audit events,
deficiency lifecycle behavior, Playwright flows, UI design, schemas, and dependencies are unchanged.
