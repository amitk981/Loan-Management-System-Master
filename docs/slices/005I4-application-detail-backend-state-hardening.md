# Slice 005I4: Application Detail Backend State Hardening

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Close architecture-review finding `2026-07-10_092630_architecture_review`: remove the remaining
synthetic stage, owner, readiness, and lifecycle facts from Application Detail after 005I2.

## User Value
Staff never see invented dates, owners, stage completions, or payment readiness on a real loan.

## Depends On
- 005I3

## Source / Review References
- `docs/slices/005I2-application-detail-api-state-hardening.md`
- `docs/source/api-contracts.md` §19.1/§19.3 and §44
- `docs/source/codebase-design.md` §§23.3-23.4 and §42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_092630_architecture_review`

## Frontend Scope
- Remove `emptyApplication` defaults that turn absent API facts into real-looking documentation,
  disbursement, owner-role, tenure, loan-type, or readiness values.
- Remove hardcoded stepper metadata such as fixed dates, `Credit reviewed`, `CS verified`, and
  inferred SAP/disbursement progress. Display only backend-supplied facts; otherwise use the
  existing neutral unavailable/not-started pattern.
- Always display `assigned_owner` from the backend or neutral unavailable. Do not replace it with
  Compliance, Company Secretary, Finance, CFC, or Accounts based on frontend status logic.
- Do not compute `isReadyForPayment` or any workflow availability from document/SAP/status fields.
  Actions must come from backend object-shaped `available_actions`; until the owning future API
  supplies an action, hide/disable it with the existing pattern.
- Keep checklist badge counts as a direct presentation of API checklist rows, but do not convert
  them into downstream documentation/disbursement decisions.
- Preserve all existing visual classes/components; no new styling or layout.

## Backend / API Scope
- Add only metadata fields needed to stop synthesis if the existing §19.3 response already owns
  them. Do not implement documentation, SAP, security, sanction, or disbursement workflows early.
- Return neutral absence for future facts and object-shaped `available_actions` for implemented
  application actions only.

## Test Quality Correction
- Remove the production `initialData`/`initialActiveTab` test bypass added by 005I2 unless those are
  genuine product interfaces. Tests must mock the HTTP service and exercise loading/success/error
  rendering through the same seam as production.
- Add a later-stage regression whose backend owner conflicts with the old inferred owner and prove
  the API owner wins; assert no fixed dates, synthetic completion claims, or payment-readiness CTA.
- Preserve the `LO00000035`, rejection-note, empty witness, and selected nominee regressions.
- The selected-nominee regression must assert the 005I3 metadata-only fields (ID, name, age,
  minor/KYC/relationship/signature facts) survive the HTTP rendering seam while PAN/Aadhaar labels,
  tokens, hashes, and reveal controls remain absent.
- The submitted-state regression must use a backend `assigned_owner.full_name` that differs from
  every old inferred department label; the later-stage regression must use another conflicting
  owner and assert both exact names, not only absence of the old labels.

## Evidence Required
Frontend red/green logs, screenshots for submitted and later-stage detail, API contract examples if
the detail DTO changes, and all standard quality gates.

## Risk Level
Medium

## Acceptance Criteria
- Application Detail contains no frontend-owned workflow/owner/readiness decisions.
- Real HTTP-mocked rendering tests cover submitted, later-stage, empty, and error states.
- Styling remains within the approved prototype system.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested, if needed
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
