# Execution Plan

Selected slice: 011H-noc-issuance

## Boundary

Implement only backend NOC issuance for an existing eligible full-repayment `LoanClosure` through
`LoanClosureModule.generate_noc` and `POST /api/v1/loan-closures/{id}/noc/`. Reuse the existing
document-generation/storage, communications, permission, and audit owners. No frontend, template
wording, provider infrastructure, security return, or archive work is in scope.

## Public Behaviours (TDD order)

1. An authorised Company Secretary or Compliance user can issue one NOC for an eligible retained
   full-repayment closure; borrower, loan, application, disbursed amount, repayment date, governed
   signatory, issuer, generated document, and delivery truth are server-owned and retained.
2. Ineligible/pre-close, recovery/write-off, wrong-role/scope/signatory, foreign or missing generated
   document/template, and caller-supplied certificate facts are rejected through the standard error
   contract with correlated denial audit evidence.
3. Exact replay returns the same NOC and document; changed replay is rejected. Delivery failure is
   retained honestly and retry reuses the certificate rather than generating another.
4. Borrower self-scope and authorised staff/auditor reads/downloads follow existing object-scope and
   audited-download interfaces; foreign borrowers receive no disclosure.
5. The declared PostgreSQL five-racer acceptance produces one NOC/document/outbox chain.

## Implementation Shape

- First inspect the existing closure, document, communications, permission, audit, and API-envelope
  interfaces and follow their established adapters and lock ordering.
- Add one failing public-behaviour test, save RED output, implement the minimum vertical path, save
  GREEN output, and repeat one behaviour at a time.
- Add the `NocRecord` schema and one migration, serializer/view/route, permission catalogue entry if
  absent, audit actions, and focused reverse-consumer regressions only where the established seams
  require them.
- Add the exact PostgreSQL acceptance class named by the slice.

## Verification and Evidence

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Run focused NOC tests during RED/GREEN, then impacted closure/document/communications/download and
  permission tests, Django check, and migration-drift check. Do not run the complete backend suite;
  Ralph performs the authoritative impacted/full lane independently.
- Save red/green and focused gate logs under `evidence/terminal-logs/`, plus a bounded NOC metadata
  example under `evidence/api-responses/`.
- Inspect diff stats and targeted hunks, confirm no protected file changed, and complete
  `risk-assessment.md`, `review-packet.md`, and `final-summary.md`. Set the review result exactly to
  `Ready for independent validation` only after focused verification is green.
