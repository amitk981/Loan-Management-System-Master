# Slice 006B: Default Document Purpose and Terms Eligibility Checks

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Extend the eligibility assessment from 006A with default, document, purpose, nominee, and terms
checks needed before loan-limit/appraisal work begins.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 006A
- 005I2

## Prior Slice Handoff
- Architecture review `2026-07-10_041851_architecture_review` created corrective slice `005I2`
  because Application Detail still contained hardcoded mock-loan state after 005I. Run 005I2 before
  this slice so the intake detail UI remains backend-owned before eligibility/appraisal state grows.
- 005I2 should be treated as complete only if staff application detail exposes nullable,
  metadata-only `rejection_note` on the staff detail response, borrower portal detail still omits
  staff rejection-note metadata, and `ApplicationDetail.tsx` no longer special-cases `LO00000035`
  or renders hardcoded witness/nominee sensitive data.
- 006A created one-to-one `eligibility_assessments` storage and the nested run/read endpoints.
- 006A currently persists `default_check`, `document_check`, `terms_acceptance_check`,
  `purpose_check`, and `nominee_check` as `pending`; 006B must replace those pending values with
  source-backed decisions.
- Preserve 006A's state guard, permission/object access, metadata-only `eligibility.assessed`
  audit, and no-success-evidence behavior on denied/invalid paths.

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 22-24
- docs/source/data-model.md eligibility/appraisal tables
- docs/source/functional-spec.md
- docs/source/test-plan.md
- docs/working/digests/epic-006-eligibility-loan-limit-appraisal.md

## Prototype Reference
- sfpcl-lms/src/pages/appraisal/AppraisalWorkbench.tsx
- sfpcl-lms/src/components/loan/EligibilityChecklist.tsx
- sfpcl-lms/src/components/loan/LoanLimitCalculator.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
- Reuse the 006A `POST /eligibility-assessment/run/` and `GET /eligibility-assessment/`
  endpoints; do not add a parallel endpoint.
- Populate `default_check`, `document_check`, `terms_acceptance_check`, `purpose_check`, and
  `nominee_check` according to source fields in `api-contracts.md` §22.1 and `data-model.md` §14.1.
- Combine 006A's active-member result with the new checks into `overall_result`: `eligible` only
  when every implemented check passes, `ineligible` when any blocker fails, and
  `pending_manual_evidence` when active-member manual evidence remains unresolved.
- Use 005D/005E checklist/application-document metadata for document evidence rather than reading
  raw files or duplicating document storage.
- Treat existing `Member.default_status = no_default` as the only automatic pass for
  `default_check`; any active default/default-like value should fail unless a future source-backed
  override slice implements exception handling.
- Treat `LoanApplication.terms_acceptance_flag = true` as the only automatic pass for
  `terms_acceptance_check`.
- Treat `purpose_category in {crop_production, agriculture_activity}` as pass for `purpose_check`;
  other values fail without changing application status/stage.
- For `nominee_check`, use existing nominee facts only where available. If the current application
  schema cannot identify the submitted nominee, leave the check as a documented pending/manual
  evidence result rather than inventing a nominee selection rule.
- Keep loan-limit calculation, appraisal-note create/edit/submit, Credit Manager review, and
  sanction submission out of scope.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Same as 006A: run requires `credit.eligibility.run`, read follows application read/object access
unless the codebase already has a narrower read permission. Do not implement
`credit.eligibility.override`.

## Audit Requirements
Successful rerun/update writes metadata-only eligibility audit/workflow evidence. Failed validation,
invalid state, permission denial, and object-scope denial create no success audit/workflow events.

## Validation Rules
- BR-008: active/defaulted borrower status blocks normal eligibility unless a source-backed
  exception/override exists; override is out of scope here.
- BR-009: nominee must not be a minor.
- BR-013/BR-014 and S15: borrower/nominee KYC, land document, crop plan, and six-month bank
  statement are required document evidence.
- BR-018/S15: purpose category must be crop production/agriculture activity.
- S15: terms must be accepted.
- Ineligible result must not advance application status/stage into appraisal or sanction states.

## Test Cases
- TDD red/green for a referenced application whose default/document/purpose/terms checks are not
  yet populated.
- Eligible path: all checks pass and `overall_result = eligible`.
- Ineligible paths for active default, missing required checklist evidence, non-agriculture
  purpose, missing terms acceptance, and invalid/minor nominee where existing nominee facts allow
  the check.
- Re-run updates the existing one-to-one assessment instead of creating duplicates.
- Permission/object-scope/invalid-state failures create no assessment changes and no success audit.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
Medium

## Acceptance Criteria
- The named capability works through the intended backend/API/frontend path, where applicable.
- Source-doc business rules are enforced or documented as assumptions.
- Permissions and audit expectations are tested when applicable.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
