# Slice 007G: General Meeting Evidence for Special Cases

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Record general-meeting approval evidence for director / relative / committee-member borrower cases and gate sanction completion on it (COI-004, M05-FR-012).

## User Value
Related-party loans cannot be sanctioned without the legally required general-meeting notice, minutes, and resolution being on file.

## Depends On
- 007F

## Source References
- docs/source/api-contracts.md §25.11 (`POST /api/v1/loan-applications/{id}/general-meeting-approval/` with related_party fields, meeting_date, notice/minutes/resolution document ids, approval_status)
- docs/source/data-model.md §15.8 `general_meeting_approvals`
- docs/source/auth-permissions.md §12.6 (`approvals.general_meeting.record` Critical), §16.2 (related-party row), §17.2 COI-004
- docs/source/functional-spec.md M05-FR-012
- docs/slices/003C-document-metadata-and-storage-adapter.md (document ids)

## Prototype Reference
- sfpcl-lms/src/pages/sanction/SanctionWorkbench.tsx (special-case panel per screen-spec S24; wiring is 007I)

## Concrete Requirements
1. Implement §15.8 `general_meeting_approvals` and the §25.11 endpoint: related_party_type (director / relative / committee member), optional related party user, relationship description, meeting_date, and notice/minutes/resolution document references validated against existing 003C document metadata the actor may access.
2. Permission `approvals.general_meeting.record` (Critical); recording is idempotent per application (a superseding record requires an explicit new row with audit trail, not an overwrite).
3. Gate: when 007E flagged a case as related-party, the 007D completion transaction must refuse final sanction until an `approved` general-meeting record exists for the application; the refusal uses a contract error naming the missing evidence.
4. approval_status lifecycle pending / approved / rejected; a rejected meeting outcome blocks sanction and is surfaced on the case detail (§25.4 projection notes in API_CONTRACTS.md).
5. Audit/workflow events on record/status change; register linkage (register GM reference field) is consumed by 007H.

## Test Cases
- Related-party case cannot complete sanction without an approved GM record; completes after; non-related-party case unaffected.
- Document-id validation negatives (missing/no-access document); permission negatives.
- Superseding record keeps history; rejected meeting blocks sanction with the contract error.

## Out of Scope
Conflict determination (007E), register generation (007H), document upload itself (003C/§26), UI (007I).

## Risk Level
Medium

## Acceptance Criteria
- The related-party sanction gate is enforced server-side with evidenced documents.
- All gates pass; API examples saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
