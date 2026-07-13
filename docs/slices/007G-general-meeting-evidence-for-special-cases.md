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

## Run-Ahead Sharpening Review (007E, 2026-07-13)

- Gate exclusively on the immutable case field `general_meeting_evidence_required`; do not
  re-evaluate live declarations, member relationships, committee membership, or a later appraisal
  when deciding a historical cycle.
- `blocked_by_conflict` is an authority failure, not missing general-meeting evidence. An approved
  meeting record cannot unblock absent CFO/Director authority, and recording evidence must not
  mutate exclusions, abstentions, required authority history, or case cycle facts.
- Extend 007D's final-action transaction after its conflict availability decision: a conflicted
  actor still receives exact `CONFLICTED_APPROVER_NOT_ALLOWED`; an otherwise eligible final actor
  receives the dedicated missing/rejected-meeting contract before action/sanction insertion.
- Prove cycle isolation: a returned cycle's meeting reference and conflict flag remain historical;
  a later cycle consumes only an applicable approved record under the §25.11 application-history
  rules and retains its own `cycle_number` in detail/action evidence.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_164911, 2026-07-13)

- Consume only 007E2's immutable per-cycle flag. The source §16.2 set includes Director, relative,
  and Sanction Committee member borrowers even when the related Director/member is not an assigned
  approver; material-interest and maker-checker conflicts alone do not trigger meeting evidence.
- The final sanction gate must run after distinct effective authority has been proved. Approved
  meeting evidence cannot make a duplicated/insufficient CFO-or-Director set satisfiable, and a
  missing meeting record cannot mask the more fundamental `blocked_by_conflict` outcome.
- Project the applicable meeting reference alongside the canonical replacement/action history so
  007H can evidence the actual distinct approvers. Unused committee candidates remain outside
  list/detail counts and cannot obtain meeting-document access through conflict declaration alone.

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
