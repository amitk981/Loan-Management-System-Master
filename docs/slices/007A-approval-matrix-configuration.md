# Slice 007A: Approval Matrix Configuration

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Persist the approval matrix and sanction committee as effective-dated backend configuration with read/manage APIs, so routing (007C) resolves rules from data rather than hard-coded thresholds.

## User Value
Admins manage who must approve what amount as versioned configuration; every later approval decision can name the exact rule version it applied.

## Depends On
- 006X

## Source References
- docs/working/digests/epic-007-sanction-approval-workflow.md (007A section)
- docs/source/api-contracts.md §25.1 (`/api/v1/approval-matrix-rules/` GET/POST/PATCH and response item)
- docs/source/data-model.md §15.1 `sanction_committees`, §15.2 `approval_matrix_rules` (including the example-rules table)
- docs/source/auth-permissions.md §12.6 (`approvals.matrix.read`, `approvals.matrix.manage`), §16.2 Loan Sanction Authority
- docs/source/functional-spec.md M05-FR-003/004/005/006

## Prototype Reference
- sfpcl-lms/src/pages/settings/SettingsHub.tsx (approval matrix panel — wiring is 007J)

## Concrete Requirements
1. Implement `sanction_committees` (§15.1: CFO + two director user FKs, board meeting reference, effective range, active/superseded status) and `approval_matrix_rules` (§15.2: decision_type, amount_min/max, condition_code, required_approver_roles_json, joint_approval_required_flag, register_required, effective range, status). Non-destructive migrations.
2. `GET/POST/PATCH /api/v1/approval-matrix-rules/` per §25.1 with the standard envelope; expose `required_director_count` per the §25.1 response item. Committee read endpoint follows the same pattern; record its exact path in API_CONTRACTS.md.
3. Validation: for the same decision_type + condition_code, effective ranges and amount ranges must not overlap; amount_min ≤ amount_max; PATCH cannot rewrite history that an existing approval case snapshot references — supersede with a new effective-dated row instead (digest rule).
4. Seed the source rules as data, not code: sanction ≤ ₹5,00,000 → CFO + 1 Director; > ₹5,00,000 → CFO + 2 Directors; `exceeds_permissible_limit` condition → CFO + 2 Directors + exception register (§16.2, M05-FR-004/005/006). Seed one active sanction committee from seed users.
5. Permissions: reads require `approvals.matrix.read`; mutations require `approvals.matrix.manage` (Critical). Test 401/403.
6. Audit events for rule create/supersede and committee changes.

## Test Cases
- Effective-date and amount-range overlap rejection; boundary rule resolution at exactly 500000.00 (inclusive in the ≤ 5L rule per "up to" — record as assumption if the owner decision on the exact-₹5,00,000 treatment in the Open Decisions Index changes it).
- Seeded rules match §16.2 facts; resolution by (decision_type, amount, condition, date) returns the right rule.
- Permission negatives on read and manage; audit rows on mutation.

## Out of Scope
Case creation/enrichment (007B), routing/assignment (007C), settings UI (007J), disbursement/recovery decision types beyond seeding the vocabulary.

## Risk Level
Medium

## Acceptance Criteria
- Matrix facts live only in versioned configuration; no threshold constant in the case engine.
- All gates pass; API examples for list/create/supersede saved.

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
