# Execution Plan

Selected slice: `010I2-dpd-pointer-and-policy-integrity-closure`

## Delivery boundary

Close only the DPD snapshot-owner finding: make the current pointer relational and same-loan,
freeze reproducible policy/source inputs, route calculation through public owner decisions under the
loan lock, and preserve idempotent newest-pointer behavior. Do not add default transitions,
reminders, DPD bands, manual overrides, or frontend work.

## Plan

1. Inspect the retained architecture-review reproducer, existing DPD module/models/migrations,
   public schedule-ledger-scope interfaces, APIs, and current tests; map every acceptance ID to a
   permanent public test selector.
2. Write one failing observable test for pointer ownership/integrity, run it with the mandated
   backend interpreter, and retain the exact RED output.
3. Implement the minimal relational pointer and additive validating migration; rerun the selector
   to GREEN before adding the next behavior.
4. Repeat one RED/GREEN cycle at a time for frozen policy/source replay, locked public-owner
   decisions and calendar timing, same/older-date idempotency, and PostgreSQL race behavior.
5. Run focused DPD API, reverse-consumer, migration, model-check, and exact five-test PostgreSQL
   acceptance checks (including the required twice-run proof) without running the full backend
   suite or coverage.
6. Save red/green, migration, PostgreSQL, and focused-gate logs; build the machine-readable review
   closure evidence mapping every finding and acceptance ID.
7. Review targeted diffs for scope, protected paths, schema sync, audit/permission fidelity, and
   changed-line limits; complete the risk assessment, review packet, and final summary.
8. Run the exact review-closure validator repeatedly until it prints `PASS`, leaving the review
   packet Result exactly `Ready for independent validation`.

## Verification targets

- Exact permanent selectors named by `review-closure-evidence.md`.
- `sfpcl_credit.tests.test_servicing_postgresql_acceptance.DpdOwnerIntegrityPostgreSQLAcceptanceTests`
  discovers and passes exactly five tests twice on PostgreSQL.
- Focused DPD/API/reverse-consumer tests, `manage.py check`, and `makemigrations --check` pass.
- The independent orchestrator remains responsible for complete-suite coverage and all global gates.
