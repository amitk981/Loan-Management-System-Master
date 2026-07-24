# Slice 012D: Audit Explorer

## Status
Complete

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Expose immutable audit logs, workflow events, and version history through scoped, sanitised,
filterable read APIs suitable for the S74 Audit Log Explorer, without adding any mutation path.

## User Value
Authorised auditors can trace who changed what and why across a record lifecycle while restricted
business and identity data remains protected.

## Depends On
- 012C

## Runtime Capabilities

- `none`

## Source References
- `docs/source/api-contracts.md` sections 8 and 42
- `docs/source/product-requirements.md` section 11.32
- `docs/source/screen-spec.md` S74
- `docs/source/information-architecture.md` sections 18.1-18.3
- `docs/source/security-privacy.md` sections 24 and 32.3
- `docs/source/auth-permissions.md` sections 12.13 and 19.1
- `docs/source/test-plan.md` sections 18.5 and 24.2 (`PERF-010`)
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` section 012D

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx
- sfpcl-lms/src/pages/Dashboard.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
- Implement/read-harden `GET /api/v1/audit-logs/`, `/api/v1/workflow-events/`, and
  `/api/v1/version-histories/` using the existing immutable audit/workflow/version stores.
- Support S74 filters where the corresponding canonical fields exist: date range, actor/user,
  role, entity type/ID or application/loan reference, action type, module, exception, and
  approval. Do not invent denormalised truth; translate references through bounded selectors.
- Return the standard envelope, pagination, and deterministic newest-first ordering with a stable
  tie-breaker. Project actor role/team snapshot, action, entity, sanitised before/after, reason,
  outcome, request ID, and IP/device only as permitted.
- Apply endpoint permission plus entity/object/team scope. Internal Auditor is read-only; broad
  management/report access does not imply audit-log access.
- Provide an explicit read-only audit-export handoff to the 012B/012C export policy rather than a
  bypassing download route.

## Database/Model Impact
None expected. Add indexes only when query-plan evidence for contracted filters justifies a
non-destructive migration; never introduce editable mirror rows.

## API Contracts
Implement section 42 response fields and document supported filter names, pagination, sanitised
value projection, and links to related records without changing the immutable write contract.

## Permissions
Require `audit.audit_log.read`, `audit.workflow_event.read`, or
`audit.version_history.read` respectively plus object scope. Export additionally requires the
restricted 012C export decision. Mutation is unavailable to every UI role.

## Audit Requirements
Do not create recursive audit events for routine paginated reads unless policy already requires
access logs. Restricted audit export/download is audited by 012C. Preserve all existing critical
event creation and append-only protection.

## Validation Rules
- Audit values are sanitised before serialisation and never expose raw PAN/Aadhaar/bank/cheque,
  secrets, tokens, or unrestricted request bodies.
- POST/PUT/PATCH/DELETE have no route or return 405/403; sorting/filtering cannot mutate records.
- Large-table queries are indexed/bounded, paginated, and free of per-row actor/entity queries.

## Test Cases
- API tests for every supported filter, combined filters, pagination/order stability, linked
  record, empty results, invalid dates/values, 401, 403, and cross-scope access.
- `AUD-016` plus method tests prove no UI/API mutation; database-level append-only protections and
  existing audit recorder tests remain green.
- Fixtures containing raw sensitive old/new values prove response sanitisation and audit export
  cannot bypass 012C.
- Reverse-consumer tests cover critical action audit creation, sensitive reveal, restricted file
  download, auditor read-only views, workflow timelines, and version history.
- Representative large fixture/query-count or query-plan evidence covers `PERF-010` risk.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN; focused API/permission/sanitisation/mutation tests; example filtered pages; query-count
or plan evidence; restricted export handoff test; unchanged audit-recorder regression; full gate.

## Non-Goals
S74 frontend wiring, new/editable audit storage, changing event producers, non-audit reporting,
or bypassing 012C with a direct export/download route.

## Risk Level
Medium

## Acceptance Criteria
- All three section-42 resources are filterable, paginated, scoped, sanitised, deterministic,
  and strictly read-only through their distinct permissions.
- Existing critical event creation and immutable storage remain unchanged and regression-tested.
- Restricted audit export uses 012C policy; no raw-sensitive or cross-scope data is exposed.
- S74 frontend wiring, new audit storage, and non-audit reporting remain out of scope.

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
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
