# Execution Plan

Selected slice: `010E-subsidiary-deduction-reconciliation`

## Delivery boundary

Extend the existing loans repayment-capture module with a subsidiary-deduction interface that
retains agreement, deduction, statement-match, Treasury-verification, allocation, and SAP evidence
as separate facts. Reuse the legal-document verification owner, the 010D statement-matching owner,
and the 010C allocation owner. Do not add frontend work, calculate subsidiary payments, create
agreements, or introduce a second matching/allocation policy.

## TDD sequence

1. Add one public API tracer test for capturing a positive subsidiary deduction with all mandatory
   facts and verified tri-party agreement; run it RED and save the log, then implement the minimal
   model/module/view/routing path and migration to make it GREEN.
2. Add focused public tests one behavior at a time for missing agreement, invalid/missing facts,
   duplicate deduction/transfer reference and exact idempotent replay, role/permission and object
   scope, statement auto-match versus explicit exception, ambiguous/excess cases, and audit truth;
   alternate each test addition with the smallest implementation needed.
3. Add public transition tests proving Treasury verification precedes allocation/SAP marking,
   allocation delegates to the canonical 010C interface, SAP replay is zero-write, and direct 010B
   plus generic 010D behavior remains unchanged.
4. Add the declared two-test PostgreSQL acceptance class for concurrent duplicate capture and
   concurrent reconcile/allocation replay. Preserve one receipt, one match, and at most one
   allocation.

## Implementation seams

- Keep the external HTTP interface in the existing loans routes/views and standard envelopes.
- Put subsidiary orchestration in one loans module interface; keep agreement verification behind a
  small legal-documents evidence reader rather than importing private policy into views.
- Extend canonical repayment persistence only with distinct subsidiary/Treasury/SAP evidence and
  database constraints/indexes required for duplicate and ordering integrity.
- Invoke 010D and 010C through their existing public module interfaces; no direct balance or ledger
  mutation from subsidiary code.

## Verification and evidence

- Save exact RED and GREEN focused backend commands under `evidence/terminal-logs/`, always using
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run focused subsidiary/API/permission/audit tests, the declared PostgreSQL label when the local
  database is available, and reverse-consumer tests for direct capture, allocation, and statement
  matching. Do not run the complete backend suite or full coverage.
- Run `manage.py check` and `makemigrations --check`; inspect migration/model sync and targeted diff
  hunks.
- Update `docs/working/API_CONTRACTS.md` for new mutation contracts and record any genuinely missing
  business fact in `docs/working/ASSUMPTIONS.md` without inventing policy.
- Complete `risk-assessment.md`, `review-packet.md` with traceability and exactly `Ready for
  independent validation`, and `final-summary.md`.
