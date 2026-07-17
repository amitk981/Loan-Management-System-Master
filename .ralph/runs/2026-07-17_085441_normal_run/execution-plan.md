# Execution Plan

Selected slice: `009D4-readiness-effective-role-and-signature-scope-closure`

## Scope and interfaces

- Preserve the existing public `GET /api/v1/loan-accounts/{id}/disbursement-readiness/`
  contract and the 23 ordered, secret-free, read-only checks.
- Change the loan owner resolver behind that endpoint to authorize against the central active
  effective-role boundary and the explicit readiness permission, unioning the canonical object
  scopes of every effective readiness role.
- Change the legal signature owner decision to reconcile only the latest current applicable Term
  Sheet, Loan Agreement, PoA, tri-party agreement, and SH-4 signature rows. Keep exact expected
  signer sets and current mismatch provenance for those documents.
- No frontend, schema, response-envelope, permission-catalogue, or route change is planned.

## TDD sequence

1. Add public readiness API probes for active governed CFO/CFC authority, inactive or unknown
   authority, missing permission, and multi-role Senior Finance/CFC union behavior. Run the focused
   test(s) and retain failing output in `evidence/terminal-logs/`.
2. Implement the minimal effective-role and union-of-scopes resolver change in
   `loans.modules.loan_account_lifecycle`; rerun the focused tests and retain green output.
3. Add legal-owner probes showing an unrelated current signature does not affect readiness and
   showing extra/wrong/duplicate signer identities on each applicable required document fail
   closed. Retain the failing output.
4. Implement the minimal current applicable-document signature filtering in
   `legal_documents.modules.signatures`; rerun the focused tests and retain green output.
5. Run the impacted readiness/signature tests, Django check and migration-sync check, then the
   configured frontend lint, typecheck, tests, and build. Do not run the complete backend suite or
   coverage locally; Ralph performs those authoritative gates independently.

## Completion evidence and bookkeeping

- Save the governed role/scope matrix, exact signer matrix, zero-write/query proof, terminal logs,
  changed-files list, risk assessment, review packet, and final summary in this run folder.
- Update the Epic 009 digest with the retained closure, mark this slice Complete, update Ralph
  progress/state/handoff, and sharpen the next one or two Not Started slices using only source
  material already opened during this run.
