# Slice 006D: Loan Limit Snapshot Storage

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Harden the 006C loan-limit assessment persistence so every calculation stores an immutable,
reviewable source snapshot and can be read back without recalculating from mutable member, land,
crop, shareholding, or policy facts.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 006C

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
- Reuse the 006C loan-limit assessment calculate/read path; do not create a parallel calculator.
- Ensure the persisted `loan_limit_assessments` row stores the source-backed calculation snapshot
  named by `api-contracts.md` §23.1 and `data-model.md` §14.2:
  `member_id`, `shareholding_id`, `number_of_shares`, `valuation_per_share`,
  `share_limit_percentage`, `per_share_cap_amount`, `shareholding_based_limit_amount`,
  `land_area_acres`, `scale_of_finance_per_acre_amount`, `land_based_limit_amount`,
  `final_eligible_loan_amount`, `requested_amount`, `amount_within_limit_flag`,
  `exception_required_flag`, `calculation_rule_version`, `calculated_by_user_id`, and
  `calculated_at`.
- Snapshot the operative policy/rule facts used by 006C so later configuration changes do not
  alter old assessment responses.
- Snapshot the selected shareholding, landholding/crop-plan area, requested amount, and member
  identifiers used in the calculation response. Do not read mutable current values when serializing
  an existing assessment if snapshot fields are available.
- Keep new formulas, override behavior, appraisal-note create/edit/submit, Credit Manager review,
  sanction submission, and frontend wiring out of scope.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Update the loan-limit API contract to state which fields are immutable calculation snapshots and
which warnings/metadata come from the stored assessment.

## Permissions
Same as 006C: calculate requires `credit.loan_limit.calculate` and existing application
object-access; read follows the same application read/object-access boundary unless 006C already
introduced a narrower read permission. Do not implement `credit.loan_limit.override`.

## Audit Requirements
Successful first calculation and rerun/update write metadata-only loan-limit audit/workflow
evidence. Read-only access creates no success audit. Permission denial, object-scope denial,
invalid eligibility state, validation failure, and missing source facts create no successful
calculation evidence.

## Validation Rules
- Require 006C's normal eligibility/calculation preconditions.
- Rerun must update the one-to-one assessment for the application, preserving old-value audit
  metadata and replacing the snapshot only when the calculation succeeds.
- Later changes to shareholding, landholding, crop-plan, requested amount, or loan-policy config
  must not mutate an already stored assessment read response unless a new successful rerun occurs.
- If 006C blocks on unresolved share-policy ambiguity, 006D must not invent the missing policy.

## Test Cases
- TDD red/green proving an existing assessment read returns stored snapshot values after the
  underlying shareholding/land/crop/policy facts change.
- Successful rerun replaces the stored snapshot and writes metadata-only old/new audit evidence.
- Failed rerun because of invalid state, missing source facts, permission denial, or object-scope
  denial leaves the prior snapshot unchanged and creates no success workflow event.
- API response includes calculation rule version and warning metadata from the stored assessment.
- No frontend tests unless 006C introduced frontend wiring.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
High

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
