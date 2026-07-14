# Review Packet: 2026-07-14_183058_normal_run

## Outcome

008G implements the narrow §26.6 tri-party verification path. Only a distinct Company Secretary can
verify a current-renderer tri-party document after the approval-owned frozen subsidiary route is
true and exact canonical borrower/nominee execution signatures pass. The action preserves all
checklist, package, security, repayment, file, and readiness truth.

## Traceability

- The source says `POST /api/v1/loan-documents/{id}/verify/` accepts verification status and remarks
  (`api-contracts.md` §26.6). The code exposes that exact route and strict two-field typed request;
  verified by `test_strict_request_and_company_secretary_checker_authority_precede_lookup`.
- The SOP says the Declaration/Tri-party Agreement applies when produce moves through a subsidiary
  and is signed by borrower and nominee (V10 p.15 §4.4; Epic 008 digest). The code consumes the
  approval owner's frozen subsidiary boolean and the legal owner's exact-document signature selector;
  verified by the public success tracer plus false-applicability and mismatch tests.
- Auth says Compliance prepares and Company Secretary checks with maker-checker separation
  (`auth-permissions.md` §§15.4-15.5/18). The module enforces action permission, Company Secretary
  role, non-null signature makers, and distinct checker identity; verified by the role-order test and
  success tracer.
- Data model §16.3 retains verification status/verifier/time; A-111 records why current API remarks
  use one nullable loan-document column. Every real change writes audit, VersionHistory, and workflow
  evidence; verified by the tracer and replay/change-history test.
- Slice 008G forbids checklist completion, repayment, security, or readiness effects. The read test
  proves checklist completion/status and the 008F package flags/status remain unchanged while list
  and checklist reads project verification metadata.

## Files and architecture

`legal_documents.modules.loan_document_verification` is the deep module interface. It reuses
`document_authority`, `document_checklist_facts`, and
`execution_signature_facts_for_document`; no parallel application-wide signature query or subsidiary
aggregate was added. HTTP parsing/view code is an adapter. One migration adds only current remarks.

## Tests and evidence

- RED: `evidence/terminal-logs/tri-party-tracer-red.txt` (expected route 404).
- GREEN: `evidence/terminal-logs/tri-party-tracer-green.txt`.
- Focused matrix: 7 tests, 6 pass plus the expected PostgreSQL-only skip.
- Legal regressions: 83 pass, 8 expected PostgreSQL-only skips.
- Full backend: 803 pass, 29 expected skips, 93% coverage (floor 85%).
- Django check and migration sync: pass.
- Frontend build/typecheck/lint: pass; full Vitest 293/293 passes on isolated retry. The initial
  parallel run had one unrelated AppraisalWorkbench async timeout and made no code change.
- API example: `evidence/tri-party-api-example.md`.

## Review findings

No protected paths, frontend files, source documents, dependencies, repayment models, security
instruments, or download paths changed. The tracked plus new-file diff remains below 30 files,
2,000 lines, one migration, and zero dependencies. Architecture review is now due after four
completed slices and is the next queue action.
