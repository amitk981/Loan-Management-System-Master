# Slice 005I3: Application Nominee Selection Contract

## Status
Complete

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Close architecture-review finding `2026-07-10_092630_architecture_review`: make the source §19.2
`nominee_id` a real loan-application fact so an application can reach 006B eligibility through
public staff/member APIs without direct database fixture writes or an invented “first nominee” rule.

## User Value
Staff and members select exactly one existing adult nominee for a draft application, and every
later completeness/eligibility read uses that stored selection.

## Depends On
- 005I2

## Source / Review References
- `docs/source/api-contracts.md` §19.2-§19.5
- `docs/source/data-model.md` §10.4 and §13.1
- `docs/source/functional-spec.md` M03-FR-003, M03-FR-005, M03-FR-006, and BR-009
- `docs/source/screen-spec-member-portal.md` MP06
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_092630_architecture_review`
- `docs/working/digests/epic-005-application-intake.md`

## Backend / API Scope
- Add nullable `LoanApplication.nominee` persistence as a protected FK to `Nominee`; keep existing
  drafts migration-safe, but require a selected nominee before submit/completeness/reference and
  before a normal eligible 006B result.
- Accept `nominee_id` on staff and portal draft create/update through their existing endpoints.
  Reject unknown fields as today; do not add a parallel nominee-link endpoint.
- The nominee must belong to the application member. Cross-member, missing, ambiguous, or deleted
  nominee IDs return validation errors and create no application/audit/workflow changes.
- Reject a selected nominee when `minor_flag = true`, age is below the A-031 majority threshold, or
  both date-of-birth and age snapshot evidence are absent. Do not infer adulthood from a default
  false boolean alone.
- Serialize the source §19.3 metadata-only `nominee` summary on staff and own-member portal detail:
  ID, name, age snapshot, `minor_flag`, `kyc_status`, relationship, and signature-required/status
  facts that already exist. Never expose PAN/Aadhaar tokens or hashes.
- Change 006B nominee evaluation to use only `LoanApplication.nominee`; remove reverse-query
  ordering/`.first()`. Legacy applications with no selected nominee remain
  `pending_manual_evidence`, not eligible.
- Preserve the member-level nominee API; it creates reusable member nominees and does not silently
  reassign them to an application.

## Frontend Scope
- Wire the existing staff and member-portal application forms to list the selected member's
  nominees and submit `nominee_id`, using existing select/form/validation patterns only.
- Show the selected nominee metadata on Application Detail and portal application detail using
  existing detail-card patterns; no sensitive reveal control is part of this slice.
- Missing nominees use the existing empty/validation state and cannot be replaced with mock people.

## Permissions And Audit
- Reuse existing application create/update/submit permissions and object access. Reading a nominee
  list still requires the existing nominee-read authority/own-member portal authority.
- Application create/update/submit audit metadata may include nominee UUID only, never nominee
  identity values. Denied/invalid paths write no success evidence.

## Test Cases
- Staff and portal create/update persist a same-member nominee and detail returns its safe summary.
- Cross-member nominee, unknown nominee, minor nominee, and missing age evidence are rejected with
  no application/audit/workflow mutation.
- Submit without `nominee_id` is blocked; an existing valid draft can select a nominee then submit.
- 006B returns pending for a legacy null selection and eligible for one explicitly selected valid
  adult nominee; multiple reverse-linked rows cannot affect the decision.
- Staff and portal render tests select a real API nominee and contain no hardcoded nominee values.

## Evidence Required
Backend and frontend red/green logs, API examples, visual evidence for selection/validation/detail,
and all standard quality gates.

## Risk Level
High

## Acceptance Criteria
- The source `nominee_id` works end to end through staff and portal draft flows.
- 006B has one deterministic application-owned nominee source and no `.first()` selection rule.
- Minor/missing-evidence/cross-member paths are blocked without success side effects.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated
- [x] Database rules followed
- [x] Permissions and audit tested
- [x] Visual evidence saved
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit delegated to the orchestrator only after passing gates
