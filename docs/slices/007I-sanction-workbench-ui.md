# Slice 007I: Sanction Workbench UI

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Wire the Sanction Workbench (screen-spec S21 committee workbench, S22 case detail, S24 special-case approval) to the Epic 007 APIs, replacing the screen's mock data with the real approval queue, checklist, and decision actions.

## User Value
The Sanction Committee reviews and decides real cases — with the ten-point checklist, conflict/abstention visibility, exception flags, and mandatory reasons — in the approved prototype composition.

## Depends On
- 007H

## Source References
- docs/source/screen-spec.md S21, S22, S24
- docs/source/functional-spec.md M05-FR-002/007/008/011 and the ten-point Sanction Committee checklist
- docs/source/api-contracts.md §25.3-§25.7, §25.11, §44 (available_actions authority)
- docs/source/content-spec.md S14/S15 (committee and special-case content)
- docs/source/component-spec.md §12.1 (committee review component)
- docs/slices/006H4-workbench-authoritative-actions-and-container-tests.md (resource-action authority pattern to reuse)

## Prototype Reference
- sfpcl-lms/src/pages/sanction/SanctionWorkbench.tsx

## Concrete Requirements
1. Queue from `GET /api/v1/approval-cases/?assigned_to_me=true` plus permitted status filters; detail from §25.4 with required/excluded approvers, per-approver decisions, exception flag, and related-party/GM status.
2. Render the M05 ten-point checklist confirmations from the detail projection (eligibility, amount, purpose, compliance, history, risk, documentation, authority, exception flag, conflict flag) — display only; no client-side derivation of any checklist fact.
3. Actions approve / reject / return call §25.5-§25.7 with mandatory reason enforcement surfaced as field errors; action visibility follows resource `available_actions` intersected with `/auth/me` usability exactly per the 006H4 pattern (never union global permissions into resource actions).
4. Special-case panel (S24): related-party cases show GM evidence status and the record affordance for permitted roles via §25.11; sanction attempts blocked by the 007G gate render the contract error meaningfully.
5. Conflict/abstention: excluded approvers and reasons visible per content-spec; a conflicted viewer gets the restricted treatment (no enabled actions, §17.3 error surfaced if attempted).
6. Remove the screen's mock reads; App-shell mock seeding is already gone (006H5) — this slice wires the real data in. Keep the approved prototype composition; no new visual patterns (006H3 fidelity conventions apply).
7. Loading, empty, error, unauthorized, validation, stale, and denied states throughout.

## Owned Mock Removals
- `src/pages/sanction/SanctionWorkbench.tsx` — no `mockData` import or inline case fixtures remain.
- `src/components/loan/ApprovalPanel.tsx` — the hard-coded ₹5,00,000 authority matrix (line ~50), the client-side "my slot" role matching, and the `can('approve_sanction')` decision gating must all be replaced by the case snapshot and resource `available_actions` from the API; no authority fact may be computed in this component.

## Test Cases
- Container tests per the 006H4 pattern: mount the real workbench, click every action, assert exact URL/body, joint-approval pending/complete renders, mandatory-reason validation, conflict denial, GM-gate error rendering.
- Regression: no `mockData` import on the wired path.
- Role matrix: CFO/Director see enabled actions on assigned cases only; Credit Manager sees read-only; unauthorized role blocked.

## Run-Ahead Sharpening Review (007G delivered contract, 2026-07-13)

- Render only the case projection's nullable frozen `general_meeting_approval`; do not fetch or
  calculate the latest application outcome client-side. The record affordance requires the current
  case's object scope plus all three backend permissions named in API_CONTRACTS.md/A-085.
- Surface the exact missing/pending/rejected 409 codes distinctly while leaving the failed final
  action/version unchanged. `CONFLICTED_APPROVER_NOT_ALLOWED` remains the higher-priority conflict
  treatment and must not be replaced by a meeting-evidence message.
- Send all three distinct uploaded document ids and bounded related-party/status vocabulary to
  §25.11. Exact replay may return the same id; a changed submission returns a new superseding id.
  Keep document download actions behind the existing document permission rather than case/register
  visibility.

## Run-Ahead Sharpening Review (007H delivered contract, 2026-07-13)

- After a final approved action, render decision terms only from
  `GET /api/v1/loan-applications/{id}/sanction-decision/` under
  `approvals.sanction.read`; do not copy the action response's sanction id into a client-owned
  financial projection. Before final approval and after rejection the endpoint deliberately
  returns `404 NOT_FOUND`, so case status/reason remains the authoritative rejected/pending UI.
- The workbench does not gain register scope from case or sanction permission. Do not call the
  Credit Sanction Register to reconstruct a case, approver, exception, conflict, meeting, or
  decision view; it is a separate `approvals.sanction_register.read` compliance projection.
- A terminal action is atomic with the generated register row and its audit/workflow reference.
  The UI must treat action failure as no completion and re-fetch the canonical case/decision only
  after success; never optimistically fabricate a register or sanction outcome.

## Visual Acceptance Criteria
Queue, case detail (pending/partially approved/approved/rejected/returned), exception-flagged case, special-case panel, conflict/abstention display, empty, loading, denied, and error states; deterministic Playwright baselines per the 006H3 harness conventions.

## Risk Level
Medium

## Acceptance Criteria
- S21/S22/S24 run on backend truth with role-correct actions and the full checklist visible.
- All gates pass; screenshots/baselines saved via the pinned e2e harness.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
