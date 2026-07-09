# Execution Plan

Selected slice: 006A-active-member-eligibility-service

## Scope
- Implement only the 006A backend eligibility-assessment foundation and active-member check.
- Do not implement override, default/document/purpose/terms/nominee rules, loan limits, appraisal notes, review, sanction submission, or frontend wiring.

## Source Trace
- `docs/source/api-contracts.md` §22.1-§22.2 defines run/read endpoints under loan applications.
- `docs/source/data-model.md` §14.1 defines `eligibility_assessments` as one row per loan application.
- `docs/source/auth-permissions.md` §12.4, §20.1, and endpoint map require `credit.eligibility.run` and application-complete workflow state.
- `docs/source/functional-spec.md` BR-004 through BR-007 define active-member evidence and relaxation paths.
- `docs/working/digests/epic-006-eligibility-loan-limit-appraisal.md` records that current persistence lacks supply/service history and 006A must not invent that calculation.

## TDD Plan
1. Add a focused failing API test for the missing run/read endpoints and expected assessment shape.
2. Implement the model, migration, URLs, view handlers, service functions, serializer, permissions, object access, state guard, and audit/workflow success event.
3. Add focused tests for invalid state, missing permission, same-permission object denial, and manual-evidence active-member result with no success side effects on denied/invalid paths.
4. Run focused tests after each meaningful change, then run full Ralph backend/frontend gates.

## Implementation Notes
- Use existing `applications` module patterns and `evaluate_application_object_access`.
- Run requires global `credit.eligibility.run` and object access using that same permission.
- Read uses the existing application read permission and object access boundary.
- Valid run state is formal `LO...` reference, `application_status=reference_generated`, `completeness_status=complete`, and `current_stage=credit_assessment`.
- Active-member result is `manual_evidence_required` until produce/service history exists; other checks are stored as `pending`.
- Successful runs write metadata-only `eligibility.assessed` audit and workflow evidence. Denied and invalid-state paths write no success evidence.

## Evidence To Save
- Red focused test output in `evidence/terminal-logs/`.
- Green focused test output in `evidence/terminal-logs/`.
- Full quality-gate outputs in `evidence/terminal-logs/`.
- API response examples in the run evidence folder.
