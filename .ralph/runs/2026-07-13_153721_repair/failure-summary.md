# Failure Summary

- Run: 2026-07-13_153721_repair
- Mode: repair
- Slice: 007D3-returned-approval-cycle-and-resubmission-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
agent-declared-result-check.md:- FAIL: the agent's review-packet.md declares this run failed or unmergeable (Result: Ready for independent revalidation).
```

## Last 50 lines: review-packet.md

```
Ready for independent revalidation

## Slice

007D3-returned-approval-cycle-and-resubmission-closure

## Demonstrated Failure

Both trusted PostgreSQL commands passed six tests, but the protected acceptance predicate requires
the exact markers `Found 5 test(s).` and `Ran 5 tests in ...`. It therefore rejected both runs and
did not execute the environment probe.

## Repair

- Kept the new returned-cycle resubmission race in the validator-selected
  `SanctionSubmissionConcurrencyTests` class.
- Moved the existing initial-submission serialization race, unchanged, into a separately
  discovered PostgreSQL-only class.
- Changed no production code or protected validator scripts during repair.

## Traceability

- The slice requires concurrent resubmission to create one cycle-two case/evidence set; the trusted
  five-race class still executes
  `test_concurrent_returned_cycle_resubmissions_create_one_cycle_two_ledger`.
- The earlier one-case initial-submission invariant remains protected by
  `InitialSanctionSubmissionConcurrencyTests.test_duplicate_submissions_serialize_to_one_case_and_one_evidence_set`.
- Source invariants remain implemented by the preserved normal-run code: immutable cycles and
  transaction integrity (`data-model.md` §§15.3-15.5/§34), new re-approval cycles after material
  change (`codebase-design.md` §13.1), and M05-FR-007/008.

## Validation

- Exact trusted PostgreSQL selection: 5/5 passed twice.
- Retained legacy PostgreSQL race: 1/1 passed.
- PostgreSQL environment probe: passed; non-secret facts saved.
- Backend: Django check passed; no migration drift; 628 tests passed, 19 expected PostgreSQL-only
  SQLite skips; 93% coverage (85% required).
- Frontend: build, typecheck, lint, and 208 tests passed.
- `git diff --check`: passed; no `[DEBUG-*]` instrumentation remains.

## Reviewer Focus

Confirm the independent validator now records two PASS five-race runs and PostgreSQL environment
evidence, and confirm both sanction concurrency classes remain discoverable in the full suite.

## Recommended Next Action

Run full independent Ralph validation, then let the orchestrator commit/merge/push if every gate
passes. Do not commit manually.
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/007D3-returned-approval-cycle-and-resubmission-closure.md
docs/slices/007E-conflict-of-interest-blocking.md
docs/slices/007F-exception-approval-workflow.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/HANDOFF.md
docs/working/digests/epic-007-sanction-approval-workflow.md
sfpcl_credit/approvals/models.py
sfpcl_credit/approvals/modules/approval_actions.py
sfpcl_credit/approvals/modules/approval_case_engine.py
sfpcl_credit/approvals/modules/sanction_handoff.py
sfpcl_credit/approvals/signals.py
sfpcl_credit/credit/modules/appraisal_workflow.py
sfpcl_credit/tests/test_approval_case_routing_api.py
sfpcl_credit/tests/test_approval_read_scope_migration.py
sfpcl_credit/tests/test_sanction_submission_api.py
.ralph/runs/2026-07-13_145943_normal_run/
.ralph/runs/2026-07-13_153721_repair/
sfpcl_credit/approvals/migrations/0011_approvalcase_appraisal_facts_json_and_more.py
```
