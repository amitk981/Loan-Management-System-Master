# Failure Summary

- Run: 2026-07-13_145943_normal_run
- Mode: normal_run
- Slice: 007D3-returned-approval-cycle-and-resubmission-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
postgresql-acceptance-results.md:- FAIL: first independent run did not satisfy all acceptance predicates.
postgresql-acceptance-results.md:- FAIL: second independent run did not satisfy all acceptance predicates.
postgresql-acceptance-results.md:- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: postgresql-acceptance-results.md

```
# PostgreSQL Acceptance Results

- FAIL: first independent run did not satisfy all acceptance predicates.
- FAIL: second independent run did not satisfy all acceptance predicates.
- FAIL: PostgreSQL environment evidence is missing.
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
sfpcl_credit/approvals/migrations/0011_approvalcase_appraisal_facts_json_and_more.py
```
