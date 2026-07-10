# Slice 005I5: Application Ownership and Nominee Authority Hardening

## Status
Complete

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Close architecture-review findings from `2026-07-10_154638_architecture_review`: stop presenting
the intake receiver/creator as an assigned owner, complete the portal nominee-detail contract, and
remove duplicated adult/minor business decisions from React while strengthening the blocked-path
and production-component tests left by 005I3/005I4.

## User Value
Staff see no invented internal owner, and staff/member nominee screens consistently defer legal-age
validation to one backend authority while still showing the safe selected-nominee facts.

## Depends On
- 005I4

## Source / Review References
- `docs/source/api-contracts.md` §19.1-§19.5 and §44
- `docs/source/codebase-design.md` §§6.2-6.3, §§23.3-23.4, §26.3, and §§42.2-42.3
- `docs/source/functional-spec.md` M03-FR-003, M03-FR-009, and BR-009
- `docs/source/screen-spec-member-portal.md` MP06 and MP10
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_154638_architecture_review`
- `docs/working/digests/epic-005-application-intake.md`

## Backend / API Scope
- `assigned_owner` means a persisted assignment/task owner only. `received_by_user` and
  `created_by_user` are intake/audit facts and must never be relabelled as assignment facts.
- No assignment/task model exists yet, so staff list/detail responses return
  `assigned_owner = null` until the owning assignment/task slice supplies a real persisted value.
  Do not invent a role, infer from status/stage, or implement the future task engine here.
- Preserve `received_by_user`/`created_by_user` internally and preserve existing object access and
  `available_actions`; this correction changes only the misleading owner projection.
- Establish one public backend nominee-validation seam used by staff/portal draft validation,
  submit/completeness/reference gates, and eligibility. It must preserve the current same-member,
  non-minor, age/DOB-evidence behavior and error contract; do not add a new age threshold or date
  formula.
- Invalid staff PATCH and portal create/PATCH attempts for unknown, cross-member, minor, and
  missing-age-evidence nominees must leave the application payload, nominee selection,
  audit/workflow counts, and status unchanged.

## Frontend Scope
- Remove both React `hasAdultNomineeEvidence` implementations. The forms may require that a nominee
  ID is selected as simple input shape, but must not calculate age, decide minority, or override the
  backend validation result.
- Surface the existing backend `nominee_id` field error through the current validation/error
  pattern. Do not add styling, helper copy, or a parallel client rule.
- Portal application detail must render every safe 005I3 fact already returned by the API:
  nominee ID, name, age snapshot, minor/adult status, KYC status, relationship, and signature
  required status. PAN/Aadhaar values, hashes, tokens, and reveal controls remain absent.
- Preserve all approved prototype components/classes and existing loading/empty/error patterns.

## Test Quality Correction
- Add backend mutation-preservation tests for invalid staff PATCH and invalid portal create/PATCH,
  including success-evidence counts and the previously stored serialized detail.
- Add portal-detail render coverage for nominee ID and minor/adult status plus sensitive-field
  absence; selector-only rendering is insufficient.
- Exercise `ApplicationDetail` loading, success, error, and submit refresh through the actual
  production component/controller with mocked HTTP, not by injecting `status`/`data` directly into
  `ApplicationDetailView`. Use the existing E2E harness or one minimal pinned dev-only DOM test
  dependency if the current Node renderer cannot run effects; do not add a production dependency.
- Prove staff-created and portal-created applications return neutral owner state in list/detail;
  specifically, a borrower portal user must never appear as the staff-side assigned owner.

## Evidence Required
Backend and frontend red/green logs, staff/portal API examples, portal detail visual evidence, the
production-component regression, and all standard quality gates.

## Risk Level
High

## Acceptance Criteria
- No API path synthesizes `assigned_owner` from receiver, creator, role, status, or stage.
- Nominee age/minor authority is backend-owned and shared by intake/completeness/eligibility.
- Portal detail exposes all safe selected-nominee facts and no sensitive values.
- Required invalid mutation and real production-component paths have substantive regressions.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated
- [x] Permissions and audit tested
- [x] Visual evidence saved
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
