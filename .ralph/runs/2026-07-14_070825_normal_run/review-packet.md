# Review Packet: 2026-07-14_070825_normal_run

## Result
Success

## Slice
007R-legacy-approval-history-and-frozen-identity-closure

## Outcome

New approval review packages are honestly versioned v3. Exact pre-007O v2 cases retain public,
actor-scoped history while approve/reject fail with a stable remediation blocker and no writes;
return/correction/independent-review produces a separate complete v3 cycle. Historical register
JSON is null-safe and formal approver identity no longer reads mutable user profiles.

## Standards

The independent standards pass initially found empty communication `{}` was not normalized to null
and terminal-remediation policy was duplicated across the engine and action writer. Both were fixed:
the serializer now accepts only a non-empty communication object, and one engine decision owns the
blocker code/message while canonical permission/state/assignment precedence remains intact. The
verification pass found no remaining standards regression.

## Spec

The independent spec pass initially requested explicit permission-precedence, empty-communication,
replacement/action-time identity, legacy-null identity, and out-of-scope total evidence. The final
public tests cover all of them; the verification pass found no remaining spec gap or scope creep.

## Traceability

- Slice requirement 1 says new packages need a new version: credit emits `approval-review-v3`,
  verified by the remediation-cycle test.
- Requirements 2/5 say v2 history remains readable but terminal writes fail closed and correction
  creates a new immutable cycle: verified by
  `test_pre_007o_v2_case_remains_actor_scoped_and_readable`,
  `test_pre_007o_v2_terminal_actions_are_blocked_but_return_is_available`, and
  `test_return_correction_fresh_review_creates_immutable_second_cycle`.
- Requirement 3 says legacy register rows are actor-scoped and null-safe without reconstruction:
  verified for approved/rejected rows, `{}` source/terminal/communication facts, standard
  pagination, and outsider zero totals by
  `test_legacy_approved_and_rejected_register_rows_are_null_safe`.
- Requirement 4 says formal identities are immutable: routed names, replacement action-time names,
  immutable ids/times, post-action renames, and unavailable legacy replacement names are verified
  by the three `formal_register`/`legacy_replacement` tests.

## Validation

- Backend: all 707 tests passed, 20 expected PostgreSQL-only skips; 93% coverage (85% required).
- Focused: all 124 approval routing/action/register tests passed.
- Django: system check and migration-drift check passed.
- Frontend: build, typecheck, lint, and all 269 tests passed; no frontend file changed.
- Diff: one additive migration, no dependency/protected/source change, below 30 files/2,000 lines.

## Recommended Next Action
Independent orchestrator validation/commit/merge/push, then run sharpened 007S.
