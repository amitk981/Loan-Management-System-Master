# Epic 006 Digest: Eligibility, Loan Limit, Appraisal, and Credit Review

## 006H2 Workbench Action Contract Hardening

- Returned appraisal responses now pass through one explicit writable projection before becoming
  editable state or PATCH bodies. The projection excludes IDs, frozen snapshots/provenance,
  statuses, reviewer/history/TAT/rejection facts, actor/time facts, and action summaries, including
  the corresponding response-only nested risk fields.
- The real workbench reload path reads the 006G2 sanction case alongside eligibility, loan limit,
  and appraisal facts. A `404 NOT_FOUND` means no case; success retains the server case UUID and
  canonical application/appraisal/submission facts. Sanction submission no longer invents either
  status in React.
- Ordinary action usability intersects `/auth/me.available_actions` with canonical permissions,
  role/state checks, while legacy remediation additionally requires the appraisal response's
  dedicated `revalidate_appraisal_prerequisites` action plus update and risk-management authority.
- Credit requests now reuse the shared authenticated envelope path. It preserves field errors,
  rejects malformed JSON as `MALFORMED_RESPONSE`, and performs no automatic stale-write retry.
- Frontend contract/behavior coverage verifies exact writable keys, nested risk keys, sanction-case
  URL/readback, role/action denial, legacy remediation authority, conditional rejection fields,
  standard `409` field errors, and the no-mock/no-formula boundary.

## 006F4 PostgreSQL Credit Concurrency Acceptance

- PostgreSQL 14.20 executed the two loan-limit, two appraisal/rejection, and one sanction-submission
  race twice through the public module interfaces. Both runs found and ran five tests, reported
  `OK`, and had zero skips; deterministic ordering showed the application row serializes each loser
  before payload/state mutation.
- Real PostgreSQL exposed acceptance-harness defects hidden by SQLite skips: inherited static
  fixture helpers were rebound as instance methods, appraisal assertions queried retired
  workflow-event fields instead of the canonical workflow projection, and eligibility attempted to
  lock nullable joined rows. The first two were corrected without weakening outcome assertions;
  eligibility now uses `select_for_update(of=("self",))` for its application lock.
- A run-packet verifier rejects missing markers, fewer/more than two logs, collection-only output,
  skips, non-PostgreSQL output, zero-test runs, connection/setup failures, and failed output.
- No formula, endpoint, state, permission, schema, migration, dependency, or frontend behavior
  changed. The earlier normal run failed only because the independent environment probe imported
  the package from the backend directory and then queried a non-existent application database;
  repair evidence records server facts through PostgreSQL's maintenance database instead.

## 006E4 Legacy Appraisal Remediation and History Backfill

- Corrective migration 0006 considers only `legacy_unverified` appraisals with a complete latest
  review projection. It derives `to_state` from `reviewed -> reviewed`, `returned -> draft`, or
  `rejected -> rejected`, adds at most one missing `legacy_latest_only` decision, preserves earlier
  native cycles, skips an exact existing latest decision and incomplete projections, preserves
  history on reverse, and is idempotent on a second forward run.
- `POST /api/v1/appraisal-notes/{id}/revalidate-prerequisites/` remains the single explicit repair
  seam with empty-object payload, appraisal-update plus risk-management permissions, and object
  scope. Draft stays draft; review-pending stays pending; reviewed returns to draft and clears only
  mutable latest-review authority. Immutable history and all caller-authored appraisal/risk/TAT
  facts remain unchanged.
- Rejected and sanction-submitted legacy rows return `409` with governed-manual-repair wording.
  Malformed JSON/unknown fields, permission/object denial, and forced audit/workflow failures write
  no remediation state or success evidence.
- Audit/workflow evidence names the remediation and prior/new state. Audit metadata includes source
  UUIDs and whether review authority was invalidated, but omits review comments, recommendation,
  financial values, and risk/free-text facts.

Sources distilled during slice `005I-application-intake-frontend-wiring` while sharpening 006A/006B:
- `docs/source/api-contracts.md` §22.1-§22.3
- `docs/source/data-model.md` §14.1
- `docs/source/screen-spec.md` S15 and §9.2
- `docs/source/functional-spec.md` BR-004 through BR-018 and M04-FR-001 through M04-FR-011
- `docs/source/auth-permissions.md` action and endpoint maps for eligibility/loan-limit actions

## 006D2C Concurrency And Boundary Regression
- Added PostgreSQL-only `TransactionTestCase` coverage around the public
  `LoanLimitCalculator.calculate_for_application(...)` seam. Deterministic barriers hold the first
  calculation after its application row lock while a second independent connection attempts the
  same lock.
- The valid/valid case requires one stable assessment UUID, complete non-mixed first/final source
  snapshots, two committed success audit/workflow pairs, and a final audit projection equal to the
  final row. The valid/invalid case requires one valid row/evidence pair and no invalid success
  evidence.
- SQLite explicitly reports these cases as non-proofs. `config.postgres_test_settings` is the
  repository integration configuration; run the two cases with that settings module after
  installing pinned `psycopg[binary]`.
- Static import inspection now resolves `ast.Import` and `ast.ImportFrom` package/alias references,
  rejects direct concrete credit-assessment/loan-policy/private calculator access, positively
  requires the calculator/appraisal public imports, and checks only the required subset of
  `AppraisalWorkflow` methods.
- No formula, endpoint, persistence, permission, rerun, audit payload, response, model, or migration
  behavior changed.

## Architecture Review 2026-07-10 17:33 - 005I5/006D2B/006D3/006E
- 006D2B's calculation module, locked mutable inputs, canonical public/audit projection, resolver
  direction, and rollback/failed-rerun assertions are substantive. 006D3's forward/reverse
  migration proof confirms state-only ownership without SQL or lost UUID/FK/evidence references.
- 006D2B's lock regression proves calls, not competing-transaction outcomes, and its AST check can
  miss package-level aliased concrete-model imports. Corrective 006D2C adds the codebase-design
  §26.3 concurrency proof and robust positive/negative import fixtures without changing behavior.
- 006E stores only eligibility/loan-limit UUIDs while explicit assessment reruns preserve those
  UUIDs and replace current facts. The appraisal therefore cannot prove which cultivated acreage,
  policy, financial limits, eligibility result, or exception flag supported its recommendation.
  ADR-0003 and corrective 006E2 require appraisal-owned immutable public projection snapshots.
- Functional §9.8/M04-FR-009 requires `repayment_capacity_notes`; 006E has risk fields but no such
  required field. API §24.3 remarks are validated and then discarded even though API §3 requires a
  reason for sensitive actions. 006E2 adds both before 006F.
- M04-FR-001/M04-FR-002 task creation and Deputy Manager – Finance assignment are not implemented
  by 006E. A-053 records the existing owner-planned 012EA task engine as their explicit owner; its
  slice now names the appraisal generation/closure/reopen rules and backfill test.
- M04-FR-011 Credit Manager rejection is not the same as 006F's returned-for-revision path. New
  corrective 006F2 owns terminal appraisal rejection plus one unsent 005H rejection-note draft;
  006G now follows that correction.
- M04-FR-003 remains implemented using application `created_at` as the available receipt proxy;
  A-054 records the unresolved receipt-versus-completeness-confirmation source ambiguity.

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

## 006C2 Cultivated Acreage Source Hardening
- Source ambiguity A-049 remains open: functional-spec BR-020 requires land area under cultivation,
  while the model exposes selected `LandHolding.area_acres`, application `CropPlan.planned_area_acres`,
  and nullable `IndividualMemberProfile.land_area_under_cultivation_acres` without a precedence rule.
- Implemented safe interim behavior: calculation proceeds only when the normalized Decimal acreage
  values agree across total selected verified land holdings, the selected verified crop plan linked
  to the current application, and profile cultivated acreage when that profile value exists. `5`,
  `5.0`, and `5.00` compare equal.
- The calculate endpoint now rejects pending/rejected selected land holdings, pending/rejected crop
  plans, crop plans with null `loan_application_id`, crop plans linked to another application, and
  mismatched acreage evidence before any `LoanLimitAssessment.save()`, `loan_limit.calculated`
  audit, or `loan_limit_assessment` workflow event.
- Mismatch contract for 006D2/module extraction: `400 VALIDATION_ERROR` with
  `error.field_errors.cultivated_acreage = "CULTIVATED_ACREAGE_UNRESOLVED"`. A failed rerun leaves
  the existing one-to-one assessment UUID, serialized GET response, policy snapshot, acreage
  snapshot, audit count, and workflow-event count unchanged.
- Successful calculation stores the agreed cultivated acreage in `loan_limit_assessments.land_area_acres`
  and keeps the existing source-backed scale-of-finance multiplication and lower-of-two formula.

## 006D2A Credit Eligibility And Configuration Seams
- Eligibility read/run behavior now lives behind
  `credit.modules.eligibility_assessment.EligibilityAssessmentModule`; application views only
  authenticate/parse, call `get` or `run`, and translate the module result/errors.
- The module owns permission/object access, application and assessment locking, state validation,
  active/default/document/terms/purpose/nominee evaluation, one-to-one rerun persistence,
  metadata-only audit, workflow evidence, and the public eligibility snapshot.
- Eligible, ineligible, and pending-manual-evidence paths retain the 006A/006B contracts. A forced
  audit failure rolls back the assessment and workflow evidence in the same transaction.
- Effective Board-approved loan-policy selection/validation now lives only in
  `configurations.modules.configuration_resolver.resolve_effective_loan_policy`. The still-legacy
  loan-limit implementation calls it with row locking and translates its shared validation error;
  006D2B will remove that compatibility translation when it extracts the calculator.
- Application services no longer expose eligibility lookup/run/serialization/rule/audit helpers or
  a private policy resolver. Models remain in `applications.models` and existing tables/UUIDs are
  unchanged under ADR-0002; there is no migration.
- HTTP endpoints, response/error envelopes, permissions, object scope, explicit rerun semantics,
  loan-limit formula/snapshot behavior, frontend behavior, and API contracts are unchanged.

## Architecture Review 2026-07-10 15:46 - 006D2B Boundary Hardening
- 006D2A's direct module tests substantively cover eligible/ineligible/pending paths and transaction
  rollback, but the import-boundary regression uses runtime identity/`hasattr` checks and cannot
  reject aliased private imports. 006D2B must replace it with static AST/import-graph coverage for
  application views/services and the future appraisal seam.
- `configurations.modules.configuration_resolver` currently imports a credit-specific validation
  error. 006D2B must remove the reverse `configurations -> credit` dependency, keep the resolver's
  result/error configuration-owned or neutral, and translate at the credit calculator boundary.
- During calculator extraction, lock the application, current assessment, shareholding, selected
  land rows, crop plan, applicable cultivated-area profile, and effective policy in one transaction.
  Tests must patch the public resolver, assert `for_update=True`, and reject direct policy queries.
- 006C2's mismatch, verification, Decimal normalization, nullable-profile, and failed-rerun
  preservation tests are substantive and must move behind the module interface unchanged.

## 006D2B Loan-Limit Calculator And Appraisal Seam
- `LoanLimitCalculator.get_assessment/calculate_for_application` now own access, locking,
  validation, formula, rerun persistence, canonical redacted projection, audit, and workflow.
- Application views are thin adapters; `applications.services` exposes no loan-limit helpers.
- The configuration resolver owns its error type; calculator translation preserves HTTP errors and
  always resolves the effective policy with `for_update=True`.
- Calculation locks application, eligibility/current assessment, shareholding, selected land,
  crop plan, applicable profile, and policy in one transaction. Failed reruns preserve evidence.
- `AppraisalWorkflow` is the projection-only 006E entry seam; no appraisal rule was added here.

## 006D3 Credit Assessment Model Ownership
- `EligibilityAssessment` and `LoanLimitAssessment` Django model state now belongs to
  `credit.models`; the legacy physical tables remain exactly `eligibility_assessments` and
  `loan_limit_assessments`.
- The single reversible migration performs state transfer only. It emits no SQL and does not
  rename, recreate, copy, backfill, truncate, or drop either table.
- Forward and reverse migration-executor proofs preserve both primary-key UUIDs, application/member/
  shareholding/user relationships, and audit/workflow entity UUID references.
- The public behavior seam remains `EligibilityAssessmentModule`, `LoanLimitCalculator`,
  `LoanLimitAssessmentResult`, `LoanLimitSnapshot`, and `AppraisalWorkflow`; future appraisal code
  must not import the concrete assessment models.

## 006E Appraisal Note Draft And Submit
- `AppraisalWorkflow` now owns create/read/draft-update/submit-for-review. Application views are
  thin envelope adapters and import no concrete credit assessment models.
- Create requires scoped `credit.appraisal.create` plus `credit.risk_assessment.manage`, consumes
  only `EligibilityAssessmentModule.get(...).snapshot` and
  `LoanLimitCalculator.get_assessment(...).snapshot`, and stores their IDs with one linked risk
  assessment. Missing/non-eligible prerequisites are invalid state and write no success evidence.
- Strict payload rules cover non-blank summaries, positive amount/optional tenure, floating
  interest type, recommendation/risk enums, nested risk shape, unknown fields, and the rule that a
  recommendation may exceed the stored final limit only when the stored snapshot already carries
  `exception_required_flag = true`.
- PATCH is draft-only and supplied-fields-only. Risk permission is additionally required only when
  nested risk fields change. Submit requires non-blank remarks and transitions exactly once to
  `review_pending`; post-submit edits and repeated submit are blocked.
- `tat_due_at = application.created_at + 2 days` is immutable. Exact due time is within TAT;
  preparation/submission after it is breached. Create/update/submit evidence is metadata-only and
  excludes summaries, mitigation notes, and submit remarks.

## 006E2 Appraisal Source Contract And Snapshot Hardening
- Create now stores exact canonical redacted eligibility and loan-limit public projections on the
  appraisal with their same-UUID provenance IDs and `prerequisite_provenance = verified`.
- GET, draft PATCH amount/exception checks, submit, and future review/sanction consumers use only
  those frozen JSON projections. Replacing current assessment facts under the same UUID does not
  alter the appraisal response or its recommendation boundary.
- `repayment_capacity_notes` is a required non-blank appraisal fact. Submit persists trimmed
  §24.3 remarks on the appraisal; audit JSON records only reason existence and owner ID.
- The additive migration copies current projections only where assessment timestamps and success
  audit chronology prove no later rerun. Ambiguous rows remain `legacy_unverified` and cannot
  submit/review until the draft-only revalidation action pins current public projections.
- `POST /api/v1/appraisal-notes/{id}/revalidate-prerequisites/` accepts `{}`, requires appraisal
  update plus risk-management scope and object access, and preserves all caller-authored
  recommendation, repayment, summary, risk, preparer, and TAT facts. All mutation/evidence paths
  are atomic and metadata-only.

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

## 006F Credit Manager Review
- `POST /api/v1/appraisal-notes/{id}/review/` accepts only `decision` and non-blank
  `review_comments`; 006F supports `reviewed` and `returned` while terminal rejection remains 006F2.
- `AppraisalWorkflow.review(...)` owns permission, Credit Manager object scope, row locking,
  maker-checker, state/provenance validation, review persistence, and atomic metadata-only evidence.
- `reviewed` moves `review_pending -> reviewed`; `returned` stores the reviewer/time/comments and
  decision while moving `review_pending -> draft` for maker revision and explicit resubmission.
- Review requires `credit.appraisal.review`, a different user from `prepared_by_user`, and verified
  frozen prerequisite provenance. Preparation/submit permissions do not imply review authority.
- Review never queries current eligibility/loan-limit rows or invokes prerequisite revalidation.
  Same-UUID current-assessment changes cannot alter the frozen appraisal projections,
  recommendation, repayment/submission facts, risk assessment, or TAT.
- Successful decisions write `appraisal.reviewed`/`appraisal.returned` audit and workflow evidence;
  free-text review comments and financial/risk projections remain only on the appraisal row.

## 006F2 Credit Manager Appraisal Rejection
- `AppraisalWorkflow.review(...)` accepts terminal `rejected` only from `review_pending` under the
  same review permission, Credit Manager object scope, maker-checker, verified-provenance, and row
  lock as 006F. Existing `reviewed` and `returned` behavior is unchanged.
- The rejected request adds the source 005H note fields `rejection_reason_category`,
  `detailed_reason`, `reapply_allowed_flag`, and `communication_mode`; the workflow-owned stage is
  fixed to `credit_assessment`. Missing/invalid/unknown facts write nothing.
- Rejection atomically stores reviewer/time/comments/decision, sets terminal appraisal state
  `rejected`, and calls the public applications rejection-note seam to create exactly one existing
  draft with derived `communication_status = not_sent`. It neither sends communication nor creates
  a sanction case.
- Appraisal evidence records only IDs/category/state/actor/time/request ID. Review comments and the
  detailed rejection reason are excluded; rejection-note validation/serialization/audit/workflow
  remain owned and reused from 005H. Any note or evidence failure rolls back the whole decision.
- Rejection consumes no current eligibility/loan-limit model. The frozen projections,
  recommendation/terms, repayment/submission facts, linked risk assessment, and TAT remain unchanged.

## Architecture Review 2026-07-10 19:15 - Appraisal Historical And Concurrency Corrections

- Migration 0003's legacy “safe copy” is not conservative enough: it requires no later success
  audit but does not require positive pre-appraisal success audits for both exact prerequisite IDs.
  006E3 must downgrade every unproven row to `legacy_unverified`; absence of evidence is not proof.
- Source auth §25.3 requires both `credit.appraisal.review` and actual Credit Manager role authority.
  Generic owner/receiver object access must not let another role exercise review merely because it
  was granted the permission.
- Latest `LoanAppraisalNote.review_comments` cannot serve as review history. A return reason is lost
  when a later review overwrites it, while metadata-only audit intentionally excludes the text.
  ADR-0004 and 006E3 require one immutable appraisal-owned decision record per review action.
- 006D2C merged without its mandatory PostgreSQL execution: committed evidence contains only a
  missing-driver failure and SQLite skips. 006F3 must execute those existing tests on PostgreSQL,
  normalize application → appraisal → rejection/history lock order, and add competing appraisal
  review/rejection outcomes before 006G.
- The top-level API-contract appraisal status and the older requirement-status paragraph in this
  digest are stale beside the later implemented 006F/006F2 sections. 006E3 owns reconciliation.

## 006E3 Appraisal History And Review Authority Hardening

- `AppraisalWorkflow.review(...)` now requires both `credit.appraisal.review` and active
  `credit_manager` primary-role membership before object scope. Another-role permission holders,
  including in-scope application owners/receivers, receive `PERMISSION_DENIED` with no writes. A
  real Credit Manager retains all-applications access inside the credit-assessment domain and the
  distinct `OBJECT_ACCESS_DENIED` result outside it.
- Every successful reviewed/returned/rejected action appends one appraisal-owned immutable review
  decision in the same transaction as latest appraisal projections, optional rejection note,
  audit, and workflow evidence. API `review_history` is chronological and retains decision,
  comments, reviewer/time, from/to states, and `native|legacy_latest_only` provenance. Generic
  evidence references the history UUID but excludes comments, detailed rejection reason, and
  frozen financial/risk free text.
- Migration 0005 keeps a legacy appraisal `verified` only when both exact same-application
  prerequisite UUIDs have their matching success audits at/before preparation, neither has a later
  success audit, and both source timestamps are at/before preparation. Every other formerly
  verified row is relabelled `legacy_unverified` without rewriting copied JSON or decision facts.
  Existing unverified rows stay unverified; explicit draft revalidation remains the repair path.
- The migration backfills at most one complete latest known legacy review decision and labels it
  `legacy_latest_only`; it never fabricates prior cycles. Reverse schema migration drops this
  derived table but deliberately does not relabel unproven prerequisites as verified.

## 006F3 Lock-Order Candidate And Unmet Acceptance (2026-07-10_195330)

- The implementation candidate centralizes appraisal mutation locking inside `AppraisalWorkflow`:
  application first, appraisal second, then existing immutable history and optional rejection-note
  work. PostgreSQL `FOR UPDATE OF self` limits locks to the intended rows when nullable related
  users are joined for authorization/serialization.
- PostgreSQL-only public-interface tests now describe rejected-review versus stale draft PATCH and
  duplicate terminal review races. They require deterministic serialization, one native terminal
  history row, one optional rejection note, matching audit/workflow history UUIDs, preserved
  pre-race history, and no loser success evidence.
- This run is not acceptance evidence: the live PostgreSQL 14 server socket was visible but the AFK
  sandbox denied connection with `Operation not permitted`; an in-sandbox cluster also could not
  allocate PostgreSQL's required SysV bootstrap segment. The combined loan-limit/appraisal command
  found four tests but executed none. 006F3 must remain incomplete and rerun in an environment that
  permits the PostgreSQL connection; SQLite skips and the otherwise-green standard gates do not
  satisfy the slice.

## Architecture Review 2026-07-10 04:18 - 006A Spot Check
- 006A implemented only the active-member portion of the eligibility assessment contract and left
  default, document, terms, purpose, and nominee checks pending for 006B as planned.
- The review verified 006A preserves the formal `LO...` reference, complete-documentation, and
  credit-assessment state guard; `credit.eligibility.run`; existing application object access; and
  no-success-evidence behavior on denied/invalid paths.
- Full review-run gates passed with 277 backend tests, 95% backend coverage, 95 frontend tests,
  frontend lint/typecheck/build, backend check, migration sync, and `git diff --check`.

## Architecture Review 2026-07-10 09:32 - 006B-006D Contract And Module Review
- 006B's default/document/terms/purpose paths and 006C/006D's permission, object-scope,
  lower-of-two, below/equal/above boundary, policy ambiguity, snapshot read, and failed-rerun tests
  contain substantive assertions and preserve no-success-evidence guarantees.
- Application nominee authority is not reachable through public APIs: source §19.2's `nominee_id`
  is absent from `LoanApplication`, while 006B reverse-queries nullable legacy rows and chooses the
  first. `005I3` must establish one stored selection, use it for 006B, and keep missing/ambiguous
  evidence pending rather than eligible.
- BR-020 names acreage under cultivation, but 006C uses the total of selected owned
  `LandHolding.area_acres` and only validates crop-plan ownership/alignment. `006C2` must block when
  selected-land, crop-plan, and applicable profile cultivation acreage disagree; A-049 records the
  source ambiguity so the corrective slice does not invent a selector formula.
- Eligibility, loan-limit calculation, configuration resolution, persistence, serialization, and
  audit projection now sit in `applications.services` (2,789 lines), contrary to the source-named
  `credit.modules.eligibility_assessment`, `credit.modules.loan_limit_calculator`, and
  `configurations.modules.configuration_resolver` seams. `006D2` must establish those deep module
  boundaries before 006E adds appraisal behavior.
- Explicit successful reruns currently replace the one-to-one loan-limit snapshot while preserving
  its UUID and complete old/new audit metadata. The source one-to-one data model and reviewed slice
  require that behavior; passive policy/source changes do not alter GET. Treat versioned recalculation
  as a watch item and prohibit future appraisal code from bypassing stored snapshots.
- Epic 006 remains incomplete. M04-FR-004 through M04-FR-011 are implemented through 006E3 except
  sanction submission itself, which remains 006G; M04-FR-001/M04-FR-002 remain explicitly owned by
  012EA under A-053, and M04-FR-003 keeps the A-054 receipt-time proxy pending source confirmation.

## 006G Submit To Sanction

- `POST /api/v1/loan-applications/{id}/submit-to-sanction-committee/` accepts exactly non-blank
  `remarks` and requires active Credit Manager authority, the independent
  `credit.appraisal.submit_sanction` permission, and credit-domain object scope.
- The application-first transaction locks application, appraisal, ordered immutable review rows,
  then the approval-case namespace. Submission requires reviewed state, verified complete frozen
  prerequisite projections, complete risk/appraisal facts, and a latest immutable review row that
  exactly matches every latest appraisal review projection.
- Success creates one unique pending approval-case shell, copies the frozen exception-required
  flag for later Epic 007 routing, and transitions application/appraisal status to
  `submitted_to_sanction_committee`. It preserves all recommendation, risk, TAT, prerequisite,
  reviewer/comment, history, and rejection-note facts.
- Approval-matrix selection, approver assignment/actions, exception decisions, meetings,
  documents, communication, and sanction decisions remain Epic 007. A-059 requires 007B to enrich
  the existing unique case instead of creating a duplicate.
- Metadata-only audit/workflow evidence contains application/appraisal/case/latest-review IDs,
  states, actor/time, request ID, and exception flag; it excludes request remarks, comments,
  summaries, detailed rejection text, and risk notes.
- The SQLite functional suite covers strict validation, permissions/scope, invalid/rejected/
  missing/repeated/inconsistent states, rollback, and preservation. A PostgreSQL-only competing
  submission test exists; AFK sandbox socket denial is environment evidence, not concurrency proof.

## 006G2 Sanction Handoff Module And Read Contract

- `approvals.modules.sanction_handoff.SanctionHandoffModule` is the sole pending-case create/get/
  serialization seam. Credit retains appraisal validation and the application -> appraisal ->
  immutable-history locks, then calls the approvals interface; it no longer imports the concrete
  approvals model.
- POST and authenticated object-scoped `GET /api/v1/loan-applications/{id}/sanction-case/` return
  the same case/application/appraisal/latest-review/workflow UUIDs, canonical statuses,
  exception flag, actor/time, and empty pre-007 action list. Remarks and frozen free text are absent.
- Malformed/non-object JSON is a standard `400 VALIDATION_ERROR`; missing cases are `404 NOT_FOUND`;
  denied scope retains `403 OBJECT_ACCESS_DENIED`. Case, audit, or workflow failure rolls back the
  full handoff transaction, and repeated submission remains `409 INVALID_STATE_TRANSITION`.
- The exact 006F4 five-race PostgreSQL command passed twice with five executed tests, zero skips,
  and the existing application-first serialization order after the module extraction.

## 006H Frontend Integration
- The workbench and Application Detail credit tab now read stored eligibility, limit, appraisal,
  immutable history, rejection summary, and pending sanction response through §22-§24 APIs.
- Canonical `/auth/me` permissions plus exact server states gate actions; standard errors surface.
- Decimal inputs remain strings, sanction sends exactly `{ remarks }`, and frontend formulas and
  appraisal `mockData` ownership are removed. Browser screenshots remain 006X host evidence.

## Architecture Review 2026-07-10 21:39 - 006E3 Through 006H Corrections

- Migration 0005 conservatively downgrades unproven prerequisite provenance in every appraisal
  state, but the repair action is draft-only. `review_pending` and `reviewed` rows can therefore be
  blocked forever. It also misses a known returned decision when a later submit has moved the row
  back to `review_pending`. 006E4 owns state-aware remediation and latest-known history backfill;
  A-061 records the conservative re-review rule.
- The authoritative loan-limit/appraisal PostgreSQL command found four tests and executed none,
  while 006G's sanction race found one and executed none. 006F4 must run all five tests twice with
  zero skips; connection or sandbox failure remains failed acceptance.
- 006G creates its concrete approval row from the credit module, reversing the documented
  `approvals -> credit` dependency. ADR-0005 and 006G2 put create/read/serialization behind the
  approval-case module interface, retain the same unique row for 007B, return canonical statuses,
  and make the pending case UUID recoverable after reload.
- 006H assigns the full appraisal response to the edit form, so PATCH sends response-only IDs,
  snapshots, review history, status, and TAT into a strict writable contract. Returned/existing
  drafts cannot save. Revalidation is gated by submit permission rather than update+risk authority,
  and local code synthesizes post-sanction statuses. 006H2 owns writable projection, server
  actions/state, reload, and real container interaction tests.
- 006H replaced the approved staged workbench/checklist/calculator composition with a new condensed
  layout without screenshots. 006H3 restores the pre-006H visual composition using real data and
  requires host visual regression; missing browser evidence is not deferrable there.
- Functional-ID spot check: M04-FR-004 through M04-FR-009 have substantive backend assertions;
  M04-FR-010/M04-FR-011 behavior exists but remains High-risk until 006E4/006F4/006G2 close repair,
  concurrency, and sanction-handoff defects. M04-FR-001/M04-FR-002 remain explicitly deferred to
  012EA by A-053. M04-FR-003 remains the explicit A-054 receipt-time proxy. Epic 006 is not complete.
