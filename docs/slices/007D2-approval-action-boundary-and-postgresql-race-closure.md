# Slice 007D2: Approval Action Boundary and PostgreSQL Race Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007C3
- 007D

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make 007D's public action boundary earn its concurrency, serializer-parity, guarded-transition, and
Credit Assessment notification claims through the same production seams used by callers.

## Source / Review References

- `docs/source/api-contracts.md` §§25.3-25.8 and §44
- `docs/source/data-model.md` §§15.3-15.5, §24.2, §30, and §34
- `docs/source/functional-spec.md` M05-FR-007, M05-FR-008, and M05-FR-010
- `docs/source/codebase-design.md` §§13.1, 22.3, 26.1-26.3, and 42.1-42.2
- `docs/slices/003I-notification-adapter-shell.md`
- `docs/slices/007D-approval-action-api-approve-reject-return.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_131622_architecture_review`

## Concrete Requirements

1. Collection, detail, and action responses must compose one history-aware approval-case
   projection. Immediately after an action they agree on case version/status, every required
   approver's `decision`/`acted_at`, immutable route provenance, and enabled/disabled actions;
   collection must not return the raw required-approver snapshot as if no action occurred.
2. Retain the application -> appraisal -> case lock order and execute two authoritative PostgreSQL
   races twice: different remaining approvers submit the same case version concurrently, and the
   final remaining approver submits the final action twice concurrently. Prove one serial winner,
   stable stale/duplicate loser, no deadlock, one immutable action per actor, one sanction decision,
   one completion notification, and exact before/after case/action/sanction/audit/workflow/
   communication/notification ledgers.
3. Add independently named public POST rows for stale, acted, excluded, closed, unroutable/
   contradictory, unassigned, and each action-specific missing-permission state. The matching
   §44 detail action is disabled, the write returns the same reason class, and every ordinary loser
   is zero-write. Conflict-specific audited denial remains 007E.
4. Prove both reject and return reject missing/blank comments with `400 VALIDATION_ERROR`; approve
   still permits an omitted comment. Keep the documented positive integer case `version` input and
   exact stale contract in `API_CONTRACTS.md`.
5. Evaluate application, appraisal, and approval-case source states through the shared transition
   boundary before mutation. A mismatched application/appraisal state returns a stable conflict
   with no writes; direct status assignment must not bypass 002H's guard semantics.
6. Notify the Credit Assessment Team through a communication-owned internal adapter, not a direct
   `Notification.objects.create` from approvals. The same action transaction persists the source
   §24.2 pending `Communication` snapshot, linked team notification, and metadata-only communication
   audit; rollback of any adapter write rolls back the action and sanction outcome.

## Test Cases

- History-aware collection/detail/action parity after partial and final approval.
- Two twice-run PostgreSQL races with exact winner and zero-write loser evidence.
- Independently runnable action-denial/parity rows for all requirement 3 states and three action
  permissions.
- Reject/return blank-comment rows and invalid application/appraisal transition rows.
- Communication-adapter success and forced-failure rollback with one team notification only.

## Evidence Required

Failing parity/race/adapter/transition rows, two green exact PostgreSQL race runs, complete ledgers,
focused API output, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- 007D's completion and loser invariants are proved under PostgreSQL serialization.
- Every approval read/write projection agrees, and M05-FR-010 crosses the communication boundary.

## Run-Ahead Sharpening Review (007C3, 2026-07-13)

- Execute the action-denial matrix through the attributable `can_read_approval_case` decision.
  Company Secretary and Internal Auditor persisted read-only grants must reach detail but every
  approve/reject/return POST remains `403 FORBIDDEN`, absent from `assigned_to_me`, and zero-write
  across case/action/sanction/audit/workflow/communication/notification ledgers.
- Every successful or losing action must preserve/recompute the case's database coherence
  projection so ordinary SQL-scoped list counts and detail's live coherence decision still agree
  immediately after the race. Do not reintroduce Python-wide collection pagination.
