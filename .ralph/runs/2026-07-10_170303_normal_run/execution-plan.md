# Execution Plan

Selected slice: 006E-appraisal-note-create-edit-submit

## Scope and interface

- Implement only appraisal-note create/read/draft-update/submit-for-review through the existing
  `credit.modules.appraisal_workflow.AppraisalWorkflow` seam.
- Add the `RiskAssessment` and `LoanAppraisalNote` persistence required by source data-model
  sections 14.3-14.4, in one non-destructive migration.
- Expose the three application appraisal-note methods (`POST`, `GET`, `PATCH`) and the appraisal-ID
  submit action while preserving the standard API envelope and application object-access rules.
- Consume stored eligibility and loan-limit projections through their public credit modules only;
  never recalculate or import the concrete assessment models.
- Keep Credit Manager review, sanction submission, exception creation, rejection notes, and
  frontend work out of scope.

## TDD tracer bullets

1. Add a public-interface create test for a complete eligible application, run it red, implement
   the smallest model/module/view path, and run it green. Verify linked risk persistence, immutable
   two-day due time, projection-derived prerequisite checks, metadata-only evidence, and response.
2. Add GET and draft-only PATCH behavior one test at a time, preserving omitted fields and proving
   GET has no side effects.
3. Add validation/prerequisite tests incrementally: missing or non-eligible assessment, missing
   loan limit, unknown/blank/enum/positive/nested-risk errors, and above-limit recommendation
   without an existing exception flag.
4. Add TAT boundary and submit tests incrementally: within/breached timing, non-blank remarks,
   one `draft -> review_pending` transition, immutable due time, repeated-submit rejection, and
   post-submit edit rejection.
5. Add independent permission/object-scope denial tests and static import-seam regression tests;
   prove every failure path leaves appraisal/risk/audit/workflow success evidence untouched.

## Documentation and verification

- Update the internal API contract, epic digest, and any assumption record required by a
  source-silent implementation choice.
- Run focused red/green commands with the mandated Ralph Python interpreter and save their output
  under `evidence/terminal-logs/`, then run backend check, migration sync, full coverage, frontend
  lint/typecheck/tests/build, and diff checks.
- Save self-contained API response evidence, changed-files, risk assessment, review packet, and
  final summary; update progress, handoff, state, and slice status.
- Sharpen the next one or two Not Started slices using only source material already opened.
