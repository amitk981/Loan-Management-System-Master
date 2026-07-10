# Execution Plan

Selected slice: `006F2-credit-manager-appraisal-rejection`

## Public interfaces and module seams

- Extend `POST /api/v1/appraisal-notes/{id}/review/` and the existing
  `AppraisalWorkflow.review(...)` interface with the terminal `rejected` decision.
- Keep permission, object-scope, maker-checker, row-locking, frozen-provenance, and transaction
  ownership inside the existing deep appraisal module.
- Add a public rejection-note draft creation seam in the applications domain and reuse the 005H
  payload validation, persistence, serialization, audit, and workflow implementation. The credit
  adapter will not create `RejectionNote` rows or evidence directly.

## TDD tracer bullets

1. RED -> GREEN: API rejection of a review-pending appraisal creates exactly one linked draft,
   unsent rejection note and transitions the appraisal to terminal `rejected`.
2. RED -> GREEN: rejected-decision payload validation rejects missing/blank/unknown rejection-note
   facts with no appraisal, note, audit, or workflow mutation.
3. RED -> GREEN: existing permission, object-scope, maker-checker, verified-provenance, state, and
   repeat guards apply to rejection and prevent duplicate notes/evidence.
4. RED -> GREEN: rejection preserves frozen appraisal/risk/TAT facts, redacts free text from
   appraisal evidence, and rolls back all appraisal/note/audit/workflow writes when either module's
   evidence creation fails.
5. Regression: `reviewed` and `returned` retain their exact existing contract, and a rejected
   appraisal is not eligible for later sanction submission.

Each failing focused test run will be saved under `evidence/terminal-logs/` before the corresponding
minimal implementation, followed by its green output.

## Documentation, gates, and handoff

- Update `docs/working/API_CONTRACTS.md`, the Epic 006 digest, and the assumption register for the
  source-silent rejected-review payload shape.
- Run backend focused tests after each cycle, then backend check, full coverage suite, migration
  sync, frontend lint/typecheck/tests/build, and diff checks with the mandated Ralph interpreter.
- Save API/redaction examples and all required run artifacts; sharpen the next Not Started slice
  from source material already opened; then update slice status, progress, state, and handoff.

No frontend or database migration is planned: `LoanAppraisalNote.appraisal_status` is an existing
string state field and the rejection-note table already exists.
