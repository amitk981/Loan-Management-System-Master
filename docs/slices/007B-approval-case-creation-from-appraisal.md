# Slice 007B: Approval Case Creation from Appraisal

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Enrich the approval case shell that 006G already creates: resolve the effective 007A matrix rule, snapshot the required approvers, and attach appraisal/application facts — without introducing a second create path.

## User Value
Every submitted appraisal becomes exactly one routed approval case whose required authority is a durable snapshot of the rule that applied on that day.

## Depends On
- 007A4

## Source References
- docs/working/digests/epic-007-sanction-approval-workflow.md (007B section: 006G owns the unique pending case shell; enrichment only; no duplicate create path)
- docs/source/api-contracts.md §25.2 (create/enrich adapter contract, `force_exception_route`), §24.5 (submit to sanction)
- docs/source/data-model.md §15.3 `approval_cases` (`required_approvers_json` snapshot, `excluded_approvers_json`, related-entity columns)
- docs/source/auth-permissions.md §12.6 (`approvals.case.create`)
- ADR-0005 and docs/slices/006G2-sanction-handoff-module-and-read-contract.md (approval-case module is the only create/read/enrichment seam)

## Prototype Reference
- sfpcl-lms/src/pages/sanction/SanctionWorkbench.tsx (consumer; wiring is 007I)

## Concrete Requirements
1. Extend the approval-case module (ADR-0005 seam) with an enrichment operation: resolve the active 007A rule by (decision_type=loan_sanction, recommended amount, condition, date); write `approval_matrix_rule_id`, `amount`, `required_approvers_json` snapshot (concrete committee users per role from the active §15.1 committee), related-entity facts, and exception condition/reason onto the existing 006G row.
2. Any §25.2 `POST /api/v1/loan-applications/{id}/approval-cases/` adapter must return/enrich the existing unique pending case idempotently or reject incompatible state; it must never create a duplicate case (digest rule). Credit code must not import or mutate the case model directly.
3. `required_approvers_json` is immutable once assigned; later matrix changes do not alter existing snapshots (digest rule; §15.3).
4. `force_exception_route` and the exceeds-permissible-limit condition select the exception rule (CFO + 2 Directors + register); the register entry itself is 007F.
5. Permission `approvals.case.create` (High) on the adapter; enrichment triggered by the 006G submit path keeps that path's permissions. Test 401/403.
6. Audit/workflow events for enrichment; the 006G3 `workflow_event_id` identity is preserved.

## Test Cases
- Amount ≤ 5,00,000 snapshots CFO + 1 Director; above snapshots CFO + 2 Directors; exceeds-limit condition snapshots the exception rule.
- Repeat create/enrich calls are idempotent — same case id, no duplicate rows; incompatible state (already decided case) is rejected.
- Matrix rule superseded after enrichment: snapshot unchanged.
- No effective rule found → contract error, case stays unrouted, no partial write.

## Out of Scope
Approver assignment filters/queues (007C), actions (007D), conflict exclusion (007E), registers (007F/007H).

## Risk Level
Medium

## Acceptance Criteria
- Exactly one enriched approval case exists per submitted application, with an immutable authority snapshot naming rule and users.
- All gates pass; API examples saved.

## Run-Ahead Sharpening Review (006Z2, 2026-07-13)

- Consume the stored authoritative loan-limit assessment's `exception_required_flag`, not the
  borrower portal projection or a fresh amount comparison, when selecting the exception rule.
  Snapshot the assessment/policy provenance with the matrix projection so later portal/configuration
  changes cannot reroute or reinterpret the existing case.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_004501, 2026-07-13)

- Reject enrichment when the stored loan-limit assessment is absent, stale against the reviewed
  appraisal/application, or lacks its effective policy provenance. Leave the existing 006G case
  shell unrouted and byte-for-byte unchanged; do not fall back to portal/current-policy calculation.
- Exercise the public enrichment seam with exact before/after case, rule, audit, and workflow
  snapshots for no-rule, stale-assessment, already-enriched, and decided-case paths. A repeat with
  the identical assessment/rule is idempotent; any conflicting snapshot is a stable `409`.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_025409, 2026-07-13)

- Add a mismatched-condition proof: identical amount and decision date with opposite canonical
  exception conditions must select different stored rule projections, so amount comparison cannot
  silently replace the condition supplied by the authoritative credit assessment.
- The enrichment adapter must surface 400/403/409 without retrying or re-resolving current policy;
  each loser leaves the existing case shell, rule snapshot, audit, and workflow evidence unchanged.

## Run-Ahead Sharpening Review (006Z10, 2026-07-13)

- After enrichment, repeat the public read across a later matrix activation and prove the stored
  decision date, rule id/version, required approvers, and exception flag remain byte-for-byte stable.
- Add an exact adapter interaction trace: one enrichment write and one canonical case read; 400/403/
  409 must preserve the case shell and perform no retry, current-rule re-resolution, or local merge.

## Run-Ahead Sharpening Review (007A, 2026-07-13)

- Call the public `resolve_approval_matrix` interface exactly once with the authoritative appraisal
  decision date, recommended amount, `loan_sanction`, and canonical assessment condition. Persist
  its returned rule id/version, decision date, roles/director count, joint flag, and register fact
  without querying `ApprovalMatrixRule` or repeating its inclusive-range logic.
- Resolve committee users from the committee effective on that same decision date and snapshot the
  committee id/version alongside them. Matrix/committee absence or ambiguity is one atomic loser:
  the pre-existing case shell, version history, workflow, and audit snapshots remain unchanged.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_044409, 2026-07-13)

- Consume both 007A2 public resolvers exactly once. Do not query rule/committee rows directly,
  filter only current `status`, or reconstruct retained historical intervals in the case engine.
- Prove enrichment on a historical decision date after newer rule and committee versions activate:
  the stored rule/committee ids, versions, authority users, and decision date must match the unique
  historical projections and remain stable across repeat/read.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_055322, 2026-07-13)

- Consume only configuration versions whose governed activation passed the post-007A3 concurrency
  boundary in 007A4; a still-pending or losing proposal is never a routable rule or committee.
- Reuse 007A4's real open-case snapshot fixture shape when proving later activation cannot rewrite
  the enriched case. Include the case version and complete required-approver snapshot in the exact
  before/after equality, not only the linked rule/committee ids.

## Run-Ahead Sharpening Review (CR-003, 2026-07-13)

- Resolve and snapshot only an approved proposal's effective rule/committee projections. Add an
  explicit pending-proposal and losing-proposal case proving neither is routable and the existing
  006G shell, version, workflow event, and audit ledger remain byte-for-byte unchanged.
- Treat the resolver projections as the complete configuration input: persist their inclusive
  amount/condition route, roles/director count, joint/register facts, effective decision date, and
  rule/committee ids and versions without reconstructing those facts in the case module.

## Run-Ahead Sharpening Review (007A4, 2026-07-13)

- Reuse the case snapshot columns introduced by 007A4 (`approval_matrix_rule`, rule version,
  `sanction_committee`, committee version, `required_approvers_json`, `decision_date`, and case
  `version`); do not introduce parallel configuration columns or a second snapshot representation.
- Populate all snapshot columns in one approval-owned atomic enrichment and increment the case
  version exactly once. A missing/ambiguous resolver projection or conflicting repeat leaves every
  column, the original workflow-event identity, audit rows, and case version unchanged.

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
