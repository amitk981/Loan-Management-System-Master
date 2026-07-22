# Review Packet: 2026-07-22_151342_normal_run

## Result
Ready for independent validation

## Slice
011E-recovery-decision-approval

## Recommended Next Action
Run Ralph's independent High-risk validation, including the complete backend coverage lane and the
declared PostgreSQL acceptance class twice. Commit/merge only if every independent gate passes.

## Delivered

- Added `POST /api/v1/default-cases/{id}/recovery-decision/` with the standard envelope and exact
  three-field request contract.
- Composed action-specific recovery routing into the existing versioned approval matrix,
  Sanction Committee snapshot, approval actions, maker-checker/conflict checks, and permission
  projection; no second voting engine was added.
- Added one immutable `RecoveryDecision` per default/note/approval case, with frozen reason, matrix,
  authority, approval-action, actor-role, time, audit, and workflow evidence.
- Exposed exactly one future execution action for approved SH-4/CDSL/blank-cheque decisions and no
  execution for rejection, follow-up/no-action, or configured other decisions.
- Preserved legacy 011D cases as readable but non-actionable unless they carry the new exact routed
  snapshot.

## Source Traceability

- The source says one recovery decision must follow a submitted Non-Payment Note and configured
  Sanction Committee/Board approval, must name the permitted action, and must block execution without
  approval (`product-requirements.md` §11.27; `api-contracts.md` §35.8). The code freezes an
  action-specific recovery matrix and requires a matching terminal approval before creating one
  decision. Verified by
  `RecoveryDecisionApiTests.test_matching_terminal_approval_creates_one_frozen_decision` and
  `test_pending_rejected_incomplete_stale_and_mismatched_approval_are_blocked`.
- The source says maker-checker, conflict exclusion, and distinct authority remain binding
  (`auth-permissions.md` §§16-18, 20.3, 25.8). The code reuses approval actions and fails submission
  when a note maker occupies an unsatisfiable configured authority. Verified by
  `test_existing_approval_owner_requires_every_distinct_recovery_authority` and
  `test_note_maker_in_configured_authority_fails_closed_before_submission`.
- The source says one decision per default and immutable approval/audit evidence (`data-model.md`
  §§15.2-15.4, 21.5; `security-privacy.md` §23.2). The schema uses protected one-to-one links and the
  writer retains exact evidence. Verified by
  `test_exact_replay_retains_truth_and_changed_or_second_decision_conflicts` and the declared
  PostgreSQL five-request acceptance.

## Verification

- TDD tracer RED then GREEN: retained in `evidence/terminal-logs/tdd-red-green.md`.
- Focused approval/matrix/recovery reverse pack: 145 passed.
- Declared PostgreSQL acceptance: 1 passed; five concurrent requests converged on one record/event
  chain.
- Django system check: passed.
- Migration sync (`makemigrations --check --dry-run`): passed, no changes detected.
- `git diff --check`: passed.
- Frontend tests/typecheck/lint/build: not applicable; no frontend file changed and the slice is
  explicitly backend/API-only.

## Independent Review Focus

- Confirm the independent migration graph and complete-suite coverage floor.
- Confirm the default-deny policy for Board-as-record and configured-other execution matches A-158.
- Confirm candidate file counting treats the required run packet consistently at the configured
  30-file boundary.
