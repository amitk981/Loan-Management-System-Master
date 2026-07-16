# Execution Plan

Selected slice: 009D2-readiness-evidence-and-loan-scope-closure

## Scope and interfaces

- Preserve the public read-only interface
  `disbursements.modules.disbursement_readiness.evaluate(actor, loan_account_id)` and the exact
  23-check HTTP response from API contracts §31.1.
- Deepen existing owner interfaces instead of copying legal, approval, security, SAP, or loan
  policy into the coordinator. The coordinator consumes immutable booleans only.
- Add one loan-account readiness scope decision owned by `loans`; it must use persisted Stage-5
  loan/disbursement facts, never application intake assignment.

## TDD sequence

1. Add a public loan-scope matrix proving persisted Senior Manager Finance/CFC access, wrong
   role/grant, inactive actor, unrelated assignment, cross-account/member/application, and absent-id
   nondisclosure. Save the initial focused failure.
2. Implement the canonical loan-owner scope resolver and make the scope matrix green.
3. Add public real-owner readiness fixtures that create terminal checklist, signature, security,
   bank, SAP, and approval evidence; prove all checks pass except A-126, then inject only the
   governed source-bank decision for genuine all-pass. Save red/green evidence.
4. Add focused owner-evidence mutation cases for checklist completion/action/audit/workflow/version/
   renderer, ordered approvals, all signature rows, PoA, SH-4, CDSL, blank cheque/bank linkage, and
   conditional inapplicability. Implement owner-side reconciliation by reusing the checklist
   terminal-evidence contract until each named check fails closed.
5. Add SAP public-decision cases for absent/inactive/cross-member/cross-application/incomplete and
   current coherent completion. Replace any copied status query with the post-009B3B public SAP
   decision and preserve the named secret-free failure.

## Verification and evidence

- Run only focused backend tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`; do not run
  the complete backend suite or coverage locally.
- Run Django check and migration-sync, plus relevant frontend gates only if frontend files change.
- Record red/green and gate output under `evidence/terminal-logs/`; retain sanitized ready and
  blocked JSON examples, mutation/scope/query/zero-write summaries, and dependency evidence.
- Review the final diff against the slice and source references, then update the slice status,
  state, progress, handoff, digest, changed-files, risk assessment, review packet, and final summary.
- Sharpen the next one or two Not Started slices using only already-opened Epic 009 sources.
