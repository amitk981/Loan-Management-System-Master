# Epic 003-audit-documents-config-foundation: 003: Audit, Documents, Config, and Dashboard Foundation

This parent epic preserves the broad planning context from the earlier Ralph slice. Actual implementation work is broken into smaller child slices under `docs/slices/`.

## Source Broad Slice

# Slice 003: Audit, Documents, Config, and Dashboard Foundation

## Status
Not Started

## Goal
Build shared audit, document storage, configuration, communication-template, and dashboard/task foundations used by downstream lending flows.

## User Value
Future workflows can upload evidence, record immutable audit trails, use versioned policy settings, and display actionable dashboard tasks consistently.

## Depends On
- Slice 002

## Source References
- `docs/source/implementation-roadmap.md` sections 10, 20.1, 20.2, 21.1, 22.1
- `docs/source/data-model.md` document, configuration, communication, audit, and workflow event tables
- `docs/source/api-contracts.md` sections 10, 26, 37, 39, 42, 43
- `docs/source/component-spec.md`
- `docs/source/design-system.md`
- `docs/source/test-plan.md`

## Screens Involved
- Dashboard
- Task inbox
- Notifications
- Settings/config shell
- Audit timeline/explorer shell
- Generic document upload/viewer shell

## Prototype Reference
- `Dashboard.tsx`
- `TaskInbox.tsx`
- `NotificationsCenter.tsx`
- `SettingsHub.tsx`
- `AuditTimeline.tsx`
- `DocumentPackModal.tsx`
- `DocumentChecklist.tsx`

## Frontend Scope
- Replace dashboard/task mock summaries with API-backed shell data.
- Add shared document upload/progress/error patterns.
- Add audit timeline component integration from backend events.
- Add config screens for policy shells without implementing every policy rule yet.

## Backend/API Scope
- Implement append-only audit service and workflow event service.
- Implement document file metadata, storage adapter interface, checksum, sensitivity, signed download pattern.
- Implement versioned configuration shell for loan policy, approval matrix, share valuation, scale of finance, and interest settings.
- Implement communication template shell and dashboard/task summary APIs.

## Database/Model Impact
- Document files, audit logs, workflow events, configuration versions, communication templates, integration provider shell.

## API Contracts
- Document upload/download APIs
- Audit log/workflow event APIs
- Configuration APIs
- Dashboard APIs

## Permissions
- Restricted downloads require permission checks and audit events.
- Config updates require admin/CFO/CS permissions per source docs.

## Validation Rules
- Audit entries are append-only.
- Restricted document download is signed, permissioned, and audited.
- Config changes are versioned, not overwritten silently.

## Test Cases
- Upload/download happy path and unauthorized path.
- Audit append immutability.
- Config version creation.
- Dashboard/task empty and populated states.

## Visual Acceptance Criteria
- Dashboard/task shell should retain prototype information density.
- Upload and audit UI states should be usable on desktop/tablet.

## Evidence Required
- API test output.
- Screenshots of dashboard, upload state, and audit timeline.
- Validation outputs.

## Risk Level
Medium

## Acceptance Criteria
- Shared audit/document/config foundations are available for later slices.
- Frontend no longer depends on mock dashboard/task data for this foundation path.
- Evidence download and config changes are permissioned and audited.

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

