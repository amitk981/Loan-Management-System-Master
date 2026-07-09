# Epic 006 Digest: Eligibility, Loan Limit, Appraisal, and Credit Review

Sources distilled during slice `005I-application-intake-frontend-wiring` while sharpening 006A/006B:
- `docs/source/api-contracts.md` §22.1-§22.3
- `docs/source/data-model.md` §14.1
- `docs/source/screen-spec.md` S15 and §9.2
- `docs/source/functional-spec.md` BR-004 through BR-018 and M04-FR-001 through M04-FR-011
- `docs/source/auth-permissions.md` action and endpoint maps for eligibility/loan-limit actions

## Eligibility Assessment Contract
- Source endpoint:
  `POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/run/`.
- Source read endpoint:
  `GET /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/`.
- Source override endpoint:
  `POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/override/`;
  override is not part of 006A/006B unless that slice explicitly says so.
- Response fields from §22.1 and `eligibility_assessments` §14.1:
  `eligibility_assessment_id`, `loan_application_id`, `member_active_check`, `default_check`,
  `document_check`, `terms_acceptance_check`, `purpose_check`, `nominee_check`,
  `overall_result`, `assessment_notes`, `assessed_by_user_id`, and `assessed_at`.
- Permission for run is `credit.eligibility.run`; override requires `credit.eligibility.override`.
- Endpoint map says eligibility can run only after the application is complete.

## 006A Active Member Slice Boundary
- Implement only the active-member portion of the eligibility assessment mechanism.
- Source active-member rules:
  - BR-004: individual active member must have availed services and supplied primary produce for
    four continuous financial years unless relaxation applies.
  - BR-005: recent individual member relaxation may apply after at least one year of supply to
    SFPCL/subsidiary/step-down subsidiary or through a producer institution.
  - BR-006: producer member service-based relaxation may apply after three continuous years of
    service in employment or other capacity to SFPCL/subsidiaries/step-down subsidiaries.
  - BR-007: producer institution must be a member, avail services, and supply primary produce for
    four continuous financial years unless one-year relaxation applies.
- Current persistence does not yet include enough historical produce/service rows for all variants.
  006A should implement the assessment storage/API and source-backed checks from existing member
  facts where available, and mark unavailable history as `relaxation`/manual-evidence-required only
  if the source-backed evidence is missing. Do not invent supply-history calculations.
- Active-member run must preserve 005C2 application object access and require formal `LO...`
  reference/completeness before appraisal eligibility starts.

## 006B Default, Document, Purpose, And Terms Checks
- Extend the 006A eligibility assessment to include:
  - BR-008: borrower must not be in default for any FPC loan of SFPCL, subsidiary, or associate.
  - BR-009: nominee must not be a minor.
  - BR-013/BR-014 and S15: land documents, borrower/nominee KYC, recent bank statement, and crop
    plan are mandatory checklist evidence.
  - BR-018 and S15: loan purpose must be crop production/agriculture activity only.
  - S15: borrower must agree to terms.
- Use existing 005D/005E checklist facts for document evidence where possible. Do not duplicate
  document-file storage or recalculate completeness from raw files.
- Normal ineligible results must not move the application into appraisal/sanction states. Rejection
  note generation remains the source-backed rejection-note mechanism from 005H or later appraisal
  rejection slices.

## 006C Loan Limit Configuration And Calculator
- Source endpoint:
  `POST /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/calculate/`.
- Request fields from `api-contracts.md` §23.1:
  `shareholding_id`, `land_holding_ids`, `crop_plan_id`, `requested_amount`, and
  `calculation_date`.
- Response/persistence fields from §23.1 and `loan_limit_assessments` §14.2:
  `loan_limit_assessment_id`, `member_id`, `shareholding_id`, `number_of_shares`,
  `valuation_per_share`, `share_limit_percentage`, `per_share_cap_amount`,
  `shareholding_based_limit_amount`, `land_area_acres`,
  `scale_of_finance_per_acre_amount`, `land_based_limit_amount`,
  `final_eligible_loan_amount`, `requested_amount`, `amount_within_limit_flag`,
  `exception_required_flag`, `calculation_rule_version`, `calculated_by_user_id`, and
  `calculated_at`.
- Formula contract from `api-contracts.md` §23.2:
  `shareholding_based_limit = number_of_shares × configured percentage or per-share cap`;
  `land_based_limit = scale_of_finance_per_acre × land_area_acres`;
  `final_eligible_loan_amount = min(shareholding_based_limit, land_based_limit)`.
- Functional-spec BR-020 requires agricultural land-based limit from scale of finance and land area
  under cultivation. BR-021 requires final eligible amount to be lower of shareholding and
  land-based limits.
- If requested amount exceeds final eligible amount, set exception required and return a
  `REQUESTED_AMOUNT_EXCEEDS_LIMIT` warning.
- Source docs still list an open question for the operative shareholding rule: 30%, 10%, or
  Rs 200/share. 006C must use source-backed loan-policy configuration if present; otherwise block
  calculation or record the ambiguity instead of inventing the rule.
- Permission for calculation is `credit.loan_limit.calculate`; override requires
  `credit.loan_limit.override` and is out of scope for 006C.
