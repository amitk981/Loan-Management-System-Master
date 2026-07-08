# Epic 012-reports-exports-hardening-uat: 012: Reports, Exports, Hardening, Regression, and UAT Readiness

This parent epic preserves the broad planning context from the earlier Ralph slice. Actual implementation work is broken into smaller child slices under `docs/slices/`.

## Source Broad Slice

# Slice 012: Reports, Exports, Hardening, Regression, and UAT Readiness

## Status
Not Started

## Goal
Complete report/export APIs, audit explorer, operational dashboards, security/privacy hardening, regression coverage, UAT evidence, and deployment readiness gaps.

## User Value
Stakeholders can review the system through reports, exports, audit evidence, and UAT-ready workflows before production launch.

## Depends On
- Slice 011

## Source References
- `docs/source/implementation-roadmap.md` sections 17, 24, 25, 27, 32, 33
- `docs/source/api-contracts.md` sections 40, 42, 43 (reporting, audit, dashboard)
- `docs/source/deployment-ops.md`
- `docs/source/security-privacy.md`
- `docs/source/test-plan.md`
- `docs/source/technical-architecture.md`

## Screens Involved
- Reports and MIS Center
- Audit Log Explorer
- Dashboard variants
- Settings/export controls
- Task Inbox (S03) — deferred from Epic 003, owned here by `012EA`/`012EB` (owner decision 2026-07-07) as a UAT-critical gap
- Any UAT-critical frontend gaps discovered in earlier slices

## Prototype Reference
- `ReportsMIS.tsx`
- `RegistersHub.tsx`
- `Dashboard.tsx`
- `SettingsHub.tsx`
- `TaskInbox.tsx`

## Frontend Scope
- Wire reports, exports, audit explorer, and operational dashboards to APIs.
- Add export masking, progress/status, error, and empty states.
- Close UAT-critical frontend gaps found during previous slices.
- Preserve operational reporting layout.

## Backend/API Scope
- Reporting service and report APIs.
- Export job/status APIs with masking and permissions.
- Audit explorer APIs.
- Operational dashboard APIs.
- Security/privacy hardening, dependency checks, deployment smoke checks.
- Regression and UAT evidence preparation.

## Database/Model Impact
- Reporting views/materialized views/export jobs where needed.
- No destructive migrations.

## API Contracts
- Reporting APIs
- Export APIs
- Audit and Workflow APIs
- Dashboard APIs

## Permissions
- Export and audit access must be masked and role-restricted.
- Auditor read-only access must not mutate records.

## Validation Rules
- Reports match source-defined filters and roles.
- Exports mask sensitive data unless authorized.
- Export jobs are idempotent/status-tracked.
- Audit explorer cannot leak restricted fields.

## Test Cases
- Report API filters.
- Export masking and unauthorized export.
- Audit explorer read-only.
- Dashboard summaries.
- Critical E2E/UAT smoke paths.
- Build/security/deployment smoke checks.

## Visual Acceptance Criteria
- Reports remain dense, sortable/filterable, and export-friendly.
- Long-running export states are clear.

## Evidence Required
- Report/export API tests.
- Screenshots of reports, export status, and audit explorer.
- Regression/UAT checklist output.

## Risk Level
Medium

## Acceptance Criteria
- Reports, exports, dashboards, and audit explorer are API-backed.
- Security/privacy and UAT readiness gaps are documented or resolved.
- Final regression evidence is saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates

