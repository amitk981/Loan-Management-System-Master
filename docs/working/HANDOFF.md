# Ralph Handoff

## Last Run

2026-07-16_100439_normal_run

## Current Status

Corrective slice 008M4 is complete. The staff documentation queue now applies approval-owned
post-sanction scope, counts and paginates before lightweight row projection, and does not lock or
serialize every checklist. Query regressions cover an exact one-row final page, growth by forty
inaccessible/off-page rows, and a bounded detail read.

The stable public workspace module is a shallow facade over queue and locked projection seams.
008M3 action behavior remains current-fact and opaque-ID bound; the old action-code dispatcher,
owner-URL id reconstruction, and arbitrary Company Secretary selection are gone. No governed PoA
attorney selector exists, so A-125 deliberately withholds that create action. Existing completion,
generation, verification, signature, stamp/notary, upload, correction, bank, security, mismatch,
approval, download, redaction, ordering, multipart, and one-refetch behaviors remain green.

The documentation frontend now uses the shared authenticated JSON, paginated, multipart, and blob
transports, including request-id and structured envelope errors. The 008M2-only four-column facts
grid is removed and required S26 facts remain in the existing queue-row composition. The trusted
browser spec declares all five required PNGs, including the narrow viewport.

## Validation

Run evidence is in `.ralph/runs/2026-07-16_100439_normal_run/evidence/`. Focused backend workspace,
query, dependency, frontend transport, and layout tests are green. Backend check and migration drift
are green; the full backend suite passed 951 tests with 51 expected skips at 91% coverage. Frontend
build, typecheck, lint, and all 322 tests passed. Playwright collects the real-Django spec. Local
Chromium was denied macOS Mach-port/bootstrap services before page creation, so no screenshots were
fabricated; the orchestrator's twice-run browser contract is authoritative for the five PNGs.

## Important Continuation Notes

- 009B2 is already sharpened: establish the public SAP owner/manual adapter before 009C consumes a
  code; exact retained workbook delivery, replay input, audit vocabulary, and PostgreSQL races are
  mandatory.
- 009C is already sharpened and depends on 009B2. It owns one replay-safe pre-disbursement account
  under `loans.modules.loan_account_lifecycle`; A-121 keeps its Critical permission ungranted and
  A-122 keeps all pre-disbursement balances zero.
- 009D remains read-only and must consume the 009B2/009C public owner seams. Finance initiation and
  CFC authorization are later actions, not readiness checks.

## Next Run

Run 009B2, then 009C. Continue to 009D only after both owner dependencies complete.
