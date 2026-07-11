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
- 007A

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
