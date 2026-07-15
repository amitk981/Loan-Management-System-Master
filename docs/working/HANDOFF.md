# Ralph Handoff

## Last Run

2026-07-15_204059_repair

## Current Status

008L4 is complete after manual recovery of the stopped repair run. The guarded E2E seed consumes
the canonical active `borrower_portal_user` role, real portal login and `/auth/me` select the
borrower shell, MP07/MP13 keep documentation status visible independently of allowed actions, and
the deficiency response exposes stable accessible browser boundaries. Django CORS explicitly
allows the canonical `X-Request-ID` header required by the real audit/download probe. Nominee, bank,
subsidiary, and external-auditor identities remain inactive; the borrower role receives no staff
permission links and portal sessions retain the existing own-data allowlist.

## Validation

Repair evidence is in `.ralph/runs/2026-07-15_204059_repair/evidence/`; the original implementation
evidence remains in the prior run. Machine-readable Playwright reports prove both real-boundary
specs passed twice, 2/2 on each fresh database, and all four declared screenshots are non-empty.
Frontend lint, typecheck, all 305 tests, and build pass; Django check and migration drift pass; all
898 backend tests pass with 46 expected capability skips at 92% coverage.

## Next Run

Run the sharpened `008M-documentation-hub-frontend-wiring`; it must reuse L4's latest-current selector/
signed capability and server snapshot without reading portal submission rows or duplicating document
audit events. After 008M, 009A remains concrete.
