# Slice 003E: Versioned Configuration Shell

## Status
Complete

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Deliver the first versioned configuration foundation: a loan-policy config model/API shell plus
version-history read support, without implementing loan-limit, approval-matrix, interest, or scale
of finance business calculations.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 003D

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/api-contracts.md sections 26, 39, 41, 42-43
- docs/source/data-model.md document/config/audit tables
- docs/source/functional-spec.md M01-FR-001, M01-FR-002, M01-FR-015
- docs/source/component-spec.md
- docs/source/design-system.md

## Prototype Reference
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/pages/tasks/TaskInbox.tsx
- sfpcl-lms/src/components/loan/AuditTimeline.tsx
- sfpcl-lms/src/components/loan/DocumentPackModal.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
1. Add a `configurations` backend app (or established local equivalent) with
   `LoanPolicyConfig` matching `docs/source/data-model.md` §25.1 fields:
   `loan_policy_config_id`, `policy_name`, `policy_version`, `effective_from`, nullable
   `effective_to`, duration/month/year fields, threshold/default scale/share/per-share/interest
   fields, `rekyc_frequency_months`, `record_retention_years`, `grace_period_months`,
   `non_intentional_extension_months`, nullable `board_approval_reference`, and indexed `status`.
2. Add `VersionHistory` matching `docs/source/data-model.md` §26.3 with indexes on
   `versioned_entity_type` and `versioned_entity_id`.
3. Implement the loan-policy shell from `api-contracts.md` §41.1:
   - `GET /api/v1/config/loan-policy/` lists policy configs newest/effective-first with standard
     pagination.
   - `POST /api/v1/config/loan-policy/` creates a draft config.
   - `PATCH /api/v1/config/loan-policy/{loan_policy_config_id}/` updates draft configs only.
   - `POST /api/v1/config/loan-policy/{loan_policy_config_id}/activate/` marks a config active,
     captures version history, and retires/ends any previous active config if source-compatible;
     if exact retirement semantics are ambiguous, record the assumption.
4. Implement `GET /api/v1/version-histories/?versioned_entity_type=loan_policy_config&versioned_entity_id=uuid`
   from `api-contracts.md` §42.3.
5. Do not implement share valuation, scale of finance, interest-rate config, approval matrix,
   document template config, or calculations in this slice.
6. Trace the functional-spec policy requirements explicitly:
   - M01-FR-001: support one or more persisted loan product policy configurations.
   - M01-FR-002: store version, effective dates, approval authority/role, and Board approval
     reference/evidence fields available in the source model.
   - M01-FR-015: block activation unless required approval evidence is present; at minimum require
     `board_approval_reference` or record a source-backed assumption if the implementation uses a
     different evidence field.
   - M01-FR-003 through M01-FR-014 are not calculation/config-completeness scope for this shell;
     explicitly defer them in the review packet or `ASSUMPTIONS.md` instead of partially inventing
     eligibility, share valuation, scale-of-finance, interest, charge, document-template, re-KYC,
     or compliance-frequency rules.

## Database/Model Impact
One non-destructive migration is expected for `loan_policy_configs` and `version_histories`.
Do not modify existing audit/workflow/document/tracer migrations.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with request/response shapes, status transitions,
validation errors, version-history serialization, and any activation assumptions.

## Permissions
Use source permissions:
- Read/list/version history: `config.loan_policy.read` for loan-policy data and
  `audit.version_history.read` for version history.
- Create/update/activate: `config.loan_policy.manage`.
Do not invent CFO/Board grants; use the existing seeded permission catalogue and record any role
grant gaps in `ASSUMPTIONS.md`.

## Audit Requirements
Config create/update/activation must write `AuditLog` rows. Activation must also write a
`VersionHistory` row and capture `board_approval_reference` where supplied. Do not update/delete
existing audit/version-history rows.

## Validation Rules
- Required create fields mirror §41.1 request and §25.1 non-null columns.
- `effective_from` must be a valid ISO date; `effective_to`, if supplied, must be a valid ISO date
  on or after `effective_from`.
- Numeric money/percentage fields must parse as decimal strings and be non-negative.
- Integer month/year fields must be positive where source columns are required.
- Status is limited to `draft`, `active`, `retired`; create should default to `draft` unless
  explicitly documented otherwise.
- Updating non-draft configs should return `409 INVALID_STATE_TRANSITION` or standard validation
  error; choose one consistently and document it.
- Activation must fail when approval evidence required by M01-FR-015 is missing, with a standard
  `400 VALIDATION_ERROR` or `409 INVALID_STATE_TRANSITION` chosen consistently and documented.

## Test Cases
- Backend TDD red/green: loan-policy config API fails before model/service exists.
- API: authenticated read/list returns standard pagination and §41.1 fields.
- API: create draft succeeds and writes audit.
- API: patch draft succeeds, rejects invalid dates/decimals/status, and writes audit.
- API: activate succeeds, writes version history + audit, and blocks activation without manage
  permission.
- Version-history API: filters by `versioned_entity_type`/`versioned_entity_id`, rejects invalid
  UUID, and requires `audit.version_history.read`.
- Permission regressions: unauthenticated requests return `401`; no-permission actors return `403`
  without config/audit/version writes.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

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
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [x] Visual evidence saved, if frontend
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
