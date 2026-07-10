# Ralph Handoff

## Last Run
2026-07-10_125342_normal_run

## Current Status
Completed `006C2-cultivated-acreage-source-hardening`.

- Loan-limit calculation now requires selected land holdings to be verified and member-owned, and
  the selected crop plan to be verified, member-owned, agriculture aligned, and linked to the current
  loan application.
- BR-020 acreage is accepted only when normalized Decimal values agree across total selected land
  acreage, crop-plan planned acreage, and profile cultivated acreage when present. Decimal strings
  such as `5`, `5.0`, and `5.00` compare equal.
- Mismatch returns `400 VALIDATION_ERROR` with
  `error.field_errors.cultivated_acreage = "CULTIVATED_ACREAGE_UNRESOLVED"` before any
  `LoanLimitAssessment.save()`, `loan_limit.calculated` audit, or `loan_limit_assessment` workflow
  event.
- Successful calculation snapshots the agreed cultivated acreage in `land_area_acres`; failed reruns
  preserve the existing assessment UUID, GET payload, policy snapshot, acreage snapshot, audit count,
  and workflow-event count.

## Validation
Backend check/migration sync passed; 301 tests passed under coverage at 95% (floor 85%). Frontend
lint/typecheck passed; 106 tests and build passed. `git diff --check` passed. Evidence is in
`.ralph/runs/2026-07-10_125342_normal_run/`, including matched/mismatched API examples.

## Next Run
Run `006D2-credit-assessment-deep-module-boundary`, then
`006E-appraisal-note-create-edit-submit`; both are sharpened with the 006C2 acreage contract.
