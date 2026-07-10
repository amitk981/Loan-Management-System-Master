# Slice 006C: Loan Limit Configuration and Calculator

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Implement the backend loan-limit calculation service and API using source-backed shareholding,
land, crop-plan, and configurable policy facts.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 006B

## Prior Slice Handoff
- 006B completed `POST/GET /eligibility-assessment/` source-backed checks for default,
  document checklist metadata, terms acceptance, purpose, and application-specific nominee facts.
- Loan-limit calculation must require a stored 006B assessment with `overall_result = eligible`.
  Treat `pending_manual_evidence` from active-member or missing application-specific nominee
  evidence as not eligible for normal calculation unless a future override slice implements a
  source-backed exception path.
- A 006B `ineligible` result does not advance the application into appraisal/sanction states and
  must not be bypassed by 006C.

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
- Implement `POST /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/calculate/`.
- Persist one `loan_limit_assessments` row per loan application, matching `data-model.md` §14.2:
  `loan_limit_assessment_id`, `loan_application_id`, `member_id`, `shareholding_id`,
  `number_of_shares`, `valuation_per_share`, `share_limit_percentage`, `per_share_cap_amount`,
  `shareholding_based_limit_amount`, `land_area_acres`, `scale_of_finance_per_acre_amount`,
  `land_based_limit_amount`, `final_eligible_loan_amount`, `requested_amount`,
  `amount_within_limit_flag`, `exception_required_flag`, `calculation_rule_version`,
  `calculated_by_user_id`, and `calculated_at`.
- Use existing member shareholding, landholding, and crop-plan models where possible. Do not
  duplicate member/share/land/crop persistence.
- Reuse existing versioned loan-policy configuration if it can express share percentage,
  per-share cap, and scale-of-finance values; otherwise add the smallest source-backed config
  fields needed in this slice and record any policy ambiguity in `ASSUMPTIONS.md`.
- Require the 006B `eligibility_assessments.overall_result = eligible` path before calculation.
  If 006B leaves any check pending for missing source-backed evidence, calculation should return a
  validation/invalid-state response and create no loan-limit assessment, audit, or workflow event.
- Keep override, appraisal-note create/edit/submit, Credit Manager review, sanction submission,
  and frontend wiring out of scope.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Create or update the API contract for this capability. Response must include the §23.1 fields:
shareholding-based limit, land-based limit, final eligible amount, requested amount,
`amount_within_limit_flag`, `exception_required_flag`, `calculation_rule_version`, and `warnings`.

## Permissions
Run requires `credit.loan_limit.calculate` plus the existing application object-access boundary.
Do not implement `credit.loan_limit.override`.

## Audit Requirements
Successful calculation writes metadata-only audit/workflow evidence. Permission denial,
object-scope denial, invalid state, validation failure, and missing source facts create no
successful calculation evidence.

## Validation Rules
- Require a 006B eligibility assessment to exist and be normal-eligible before calculation, unless
  the source explicitly says a pending-manual-evidence path may proceed; do not invent override
  behavior.
- Formula contract from `api-contracts.md` §23.2:
  `shareholding_based_limit = number_of_shares × configured percentage or per-share cap`;
  `land_based_limit = scale_of_finance_per_acre × land_area_acres`;
  `final_eligible_loan_amount = min(shareholding_based_limit, land_based_limit)`.
- Request must not broaden object authority: `shareholding_id`, `land_holding_ids`, and
  `crop_plan_id` must belong to the same member as the loan application. Cross-member facts return
  validation errors without persisted assessment/audit/workflow evidence.
- `functional-spec.md` BR-020 requires agricultural land-based limit from scale of finance and
  land area under cultivation.
- `functional-spec.md` BR-021 requires final eligible amount to be the lower of shareholding and
  land-based limits.
- If `requested_amount > final_eligible_loan_amount`, set `amount_within_limit_flag = false`,
  `exception_required_flag = true`, and return a `REQUESTED_AMOUNT_EXCEEDS_LIMIT` warning.
- Do not decide the unresolved 30% vs 10% vs Rs 200/share policy silently. Use source-backed
  configuration if available; otherwise record the ambiguity and block calculation with a
  validation result rather than inventing the operative rule.

## Test Cases
- TDD red/green for missing calculate endpoint, then green stored calculation response.
- Shareholding-based formula, land-based formula, and lower-of-two final amount.
- Requested amount below/equal/above final eligible amount, including exception warning when above.
- Missing/ambiguous loan-limit policy config blocks calculation without a persisted assessment.
- Missing shareholding/land/crop facts return validation errors without audit/workflow evidence.
- Permission denial and object-scope denial create no loan-limit assessment or success evidence.
- Re-run updates the existing one-to-one assessment instead of creating duplicates.

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
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [x] Visual evidence saved, if frontend (not applicable; backend-only slice)
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit created only after passing gates (delegated to Ralph orchestrator)
