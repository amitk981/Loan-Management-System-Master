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
- Implemented in 006B:
  - `default_check`: `no_default` only for `Member.default_status = no_default`; existing or
    default-like statuses return `default_found` and make the assessment `ineligible`.
  - `document_check`: uses 005D/005E required checklist metadata; any blocking required item
    returns `incomplete` and makes the assessment `ineligible`.
  - `terms_acceptance_check`: `accepted` only for `LoanApplication.terms_acceptance_flag = true`;
    otherwise `pending` and `overall_result = ineligible`.
  - `purpose_check`: `agriculture_aligned` only for `crop_production` or `agriculture_activity`;
    other categories return `non_agriculture` and make the assessment `ineligible`.
  - `nominee_check`: uses `Nominee.loan_application_id` only when present. Adult nominees return
    `valid`; minor nominees return `minor` and make the assessment `ineligible`; missing
    application-specific nominee evidence remains `pending` with `overall_result =
    pending_manual_evidence`.
  - `overall_result = eligible` only when member-active, default, document, terms, purpose, and
    nominee checks all pass. Successful reruns update the existing one-to-one assessment.

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
- Implemented in 006C:
  - Calculation requires a stored 006B assessment with `overall_result = eligible`; absent,
    `pending_manual_evidence`, and `ineligible` paths return invalid state with no calculation
    evidence.
  - The request amount must match the persisted application request. Shareholding, every selected
    land holding, and crop plan must belong to that application member; application-mismatched or
    non-agriculture-aligned crop plans are rejected.
  - Exactly one active/effective Board-referenced `LoanPolicyConfig` is required. Missing,
    overlapping, non-positive, or percentage/cap-empty policies block calculation rather than
    selecting 30%, 10%, or Rs 200 in code.
  - Percentage produces a per-share amount from the stored valuation; configured per-share cap is
    a ceiling. Selected land acreage is summed and multiplied by configured scale of finance. The
    lower of share and land results is stored as the final amount.
  - Requested amount above the final limit returns `REQUESTED_AMOUNT_EXCEEDS_LIMIT` and sets both
    boundary flags. Equal/below amounts require no exception.
  - Successful calculation atomically snapshots all `data-model.md` §14.2 inputs/results, rule
    version, user, and time with `loan_limit.calculated` audit and `loan_limit_assessment` workflow
    evidence. Rerun updates the one-to-one row while denied/invalid/validation paths write none.

## 006D Immutable Loan-Limit Snapshot Readback
- Implemented `GET /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/` with
  `applications.loan_application.read` and the existing application object-access boundary.
  Missing applications/assessments return `404`; GET performs no calculation and writes no audit
  or workflow evidence.
- The persisted assessment includes policy config UUID, policy name, and Board approval reference
  snapshots. Calculate response, GET response, and audit old/new metadata serialize the policy
  source from those stored fields rather than the mutable `LoanPolicyConfig` row.
- All §14.2 numeric inputs/results, member/shareholding identifiers, requested amount, boundary
  flags/warnings, rule version, actor/time, and policy source remain unchanged on read when current
  application, shareholding, land/crop, or policy facts change.
- A successful rerun preserves the one-to-one assessment UUID, atomically replaces the stored
  snapshot, and records complete old/new snapshot audit metadata. Invalid-state, missing-source,
  permission-denied, and object-scope-denied reruns preserve the prior snapshot and create no
  success evidence.

## 006E-006F Appraisal And Credit Review Source Extract
- `api-contracts.md` §24 defines appraisal create/read, submit-for-review, Credit Manager review,
  and submit-to-sanction as separate actions. 006E owns create/read/edit/submit-for-review; 006F
  owns review only; 006G owns sanction submission.
- §24.4 review request fields are `decision` and `review_comments`. The example decision is
  `reviewed`; test-plan MOD-APPRAISAL-005 additionally requires a returned review with reason.
- `data-model.md` §14.4 stores one appraisal per application with prepared/reviewed users and times,
  immutable TAT due/status, summaries, recommendation terms, linked risk assessment,
  recommendation, and appraisal status.
- `auth-permissions.md` assigns `credit.appraisal.review` to Credit Manager and separately assigns
  `credit.appraisal.submit_sanction`; review must not imply sanction authority. Test-plan
  MOD-APPRAISAL-007 requires maker-checker, so the preparer cannot review their own appraisal.
- A review return uses the source `draft` state to permit maker revision/resubmission while storing
  the returned decision/reason and evidence; `reviewed` is the terminal 006F state consumed by 006G.

## Architecture Review 2026-07-10 04:18 - 006A Spot Check
- 006A implemented only the active-member portion of the eligibility assessment contract and left
  default, document, terms, purpose, and nominee checks pending for 006B as planned.
- The review verified 006A preserves the formal `LO...` reference, complete-documentation, and
  credit-assessment state guard; `credit.eligibility.run`; existing application object access; and
  no-success-evidence behavior on denied/invalid paths.
- Full review-run gates passed with 277 backend tests, 95% backend coverage, 95 frontend tests,
  frontend lint/typecheck/build, backend check, migration sync, and `git diff --check`.
