# Slice 007E: Conflict of Interest Blocking

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Detect conflicted approvers, exclude them from the required-approver set, block any conflicted approval attempt with the exact source error contract, and support abstention.

## User Value
A Director, committee member, or preparer can never approve their own or a relative's loan; the exclusion and reason are recorded and auditable (M05-FR-011).

## Depends On
- 007D

## Source References
- docs/source/auth-permissions.md §17.1 (conflicted cases: committee member/Director/relative as borrower, material interest, own application, maker-checker), §17.2 (COI-001..006), §17.3 (`CONFLICTED_APPROVER_NOT_ALLOWED` error body)
- docs/source/data-model.md §15.3 `excluded_approvers_json`
- docs/source/functional-spec.md M05-FR-011/012
- docs/source/security-privacy.md §12/§12.2 (segregation of duties, conflict controls)
- docs/source/codebase-design.md §13.2 Conflict of Interest Module

## Prototype Reference
- sfpcl-lms/src/pages/sanction/SanctionWorkbench.tsx (conflict/abstention display; wiring is 007I)

## Concrete Requirements
1. Conflict determination service (codebase-design §13.2 module seam) evaluating the §17.1 cases against a case's borrower and snapshot: borrower-is-approver, recorded Director/relative relationship, material interest, own application, and maker-checker (actor created/materially prepared the application or appraisal).
2. At enrichment (007B hook): conflicted users move from `required_approvers_json` to `excluded_approvers_json` with the conflict reason (COI-002/003); the remaining members form the required set per §16.2. If exclusions leave the case without the rule's required authority, the case is blocked with a contract error naming the gap — do not silently reduce authority.
3. At action time (007D hook): a conflicted or excluded user's approve/reject/return returns the exact §17.3 error (`CONFLICTED_APPROVER_NOT_ALLOWED` with case id and conflict reason) and writes an audit event for the denied attempt (COI-006).
4. Abstention: an assigned approver may record a conflict-abstention on their own decision slot with a reason; the case then requires the authority rule to still be satisfiable or blocks per requirement 2 (M05-FR-011).
5. Director/relative cases set the general-meeting-evidence requirement flag consumed by 007G (COI-004, M05-FR-012).
6. Conflicted users retain at most limited read where legally required (COI-005) — default to no assignment-scoped visibility; record the choice as an assumption.

## Run-Ahead Sharpening Review (007C, 2026-07-13)

- Store every exclusion as an object containing at least `user_id` and the source conflict reason;
  preserve the 007B ordered required snapshot for historical truth, but make 007C's assignment
  predicate and 007D's execution predicate consume the exclusion identically.
- Extend the 007C public parity matrix: an excluded actor must not enter `assigned_to_me`, must see
  no enabled action even if globally readable, and must receive the exact source denial from every
  007D write without creating an `ApprovalAction`. Keep current committee membership irrelevant.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_100911, 2026-07-13)

- Extend 007C2's coherent-snapshot validator rather than adding a separate exclusion parser.
  Excluded ids must be unique objects with a non-blank source reason, must refer to users in the
  immutable committee/required authority context, and cannot silently reduce the stored matrix's
  required CFO/Director count.
- Apply conflict access after the base 007C2 case object boundary. An unassigned reader remains
  nondisclosed; an assigned user newly excluded by the conflict service receives only the limited
  read explicitly chosen under requirement 6 and never inherits a global case read from permission
  possession.

## Run-Ahead Sharpening Review (007C2, 2026-07-13)

- Requirement 2's “move” is an eligibility overlay, not destructive history: keep the complete
  ordered `required_approvers_json` authority snapshot byte-for-byte unchanged and write unique
  `{user_id, reason}` objects to `excluded_approvers_json`. Extend the public 007C2 coherence and
  pending-actor predicates so exclusions can disable assignment/actions without making the frozen
  matrix/committee snapshot contradictory.
- Recompute satisfiability from the frozen committee candidates and stored matrix role/count facts,
  never live users or configuration. If a required CFO/Director slot has no non-conflicted stored
  candidate, persist the source-defined blocked outcome atomically or return a no-write contract
  error if the source still leaves that state unnamed; record that choice in ASSUMPTIONS.md.
- Decide and document the §17.1/COI-005 limited-read rule explicitly: base permission never grants
  global scope, unassigned users remain nondisclosed, and an excluded snapshotted actor receives
  only the fields source law requires. Denied conflict actions remain audited as the explicit
  COI-006 exception to 007C2's zero-write ordinary object denial.

## Test Cases
- Each §17.1 conflict class excludes at enrichment with recorded reason; attempted approval by each returns the exact §17.3 body and an audit row.
- Exclusion that breaks required authority blocks the case rather than completing with fewer approvers.
- Abstention flow keeps or blocks the case correctly; director/relative case flags the 007G requirement.
- Maker-checker: appraisal author cannot approve the same application's case.

## Run-Ahead Sharpening Review (007D, 2026-07-13)

- Extend `approval_actions.record_action` before its immutable insert; preserve its application ->
  appraisal -> case lock order, stale-version check, and canonical response composition.
- Ordinary unassigned/contradictory/acted denials remain exact zero-write outcomes. Only the
  source-required conflict denial may add COI-006 audit evidence, and that row must not change case,
  action, sanction, workflow, or notification ledgers.
- Conflict-abstention must use the existing immutable action ledger and case version increment; do
  not add a parallel action serializer or mutate the frozen required-approver snapshot.

## Out of Scope
General-meeting evidence recording (007G), exception register (007F), relationship data capture UI (member master owns relationships).

## Risk Level
High

## Acceptance Criteria
- No conflicted approval can be recorded by any path; exclusions, reasons, and denied attempts are all evidenced.
- All gates pass; error-contract examples saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
