# Risk Assessment

Selected slice: 006A-active-member-eligibility-service

Risk level: Medium

## Why
- Adds a new backend persistence table and public API endpoints in the credit/appraisal path.
- Enforces a high-risk permission, object access, state guard, and audit/workflow side effects.
- Does not move money, approve credit, override eligibility, send communications, or change frontend
  behavior.

## Controls
- TDD red/green evidence captured for the missing endpoint and green eligibility behavior.
- Run endpoint requires `credit.eligibility.run`.
- Read endpoint reuses application read/object access.
- Run requires formal `LO...` reference, `reference_generated`, `complete`, and
  `credit_assessment`.
- Denied and invalid-state paths are tested to create no assessment, no `eligibility.assessed`
  audit row, and no eligibility workflow event.
- Active-member history gaps are recorded in `ASSUMPTIONS.md` A-046 rather than converted into an
  invented supply-history calculation.

## Residual Risk
- Produce/service history persistence is not implemented yet, so BR-004 through BR-007 often return
  `manual_evidence_required`.
- 006B must complete the remaining eligibility checks before the assessment can produce final
  normal eligibility.

Manual review required: normal Ralph review packet only.
