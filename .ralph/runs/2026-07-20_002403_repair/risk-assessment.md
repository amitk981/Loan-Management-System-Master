# Risk Assessment

Risk level: High

- Selected slice: `010D-bank-statement-matching-unmatched-receipts`
- Mode: `repair`
- Demonstrated risk: PostgreSQL rejected the statement-line `FOR UPDATE` query because its eager
  load traversed nullable `matched_repayment`; both concurrent API requests therefore errored before
  the intended one-winner/one-conflict financial-integrity contract could execute.
- Repair control: `select_for_update(of=("self",))` now locks only the statement-line base table.
  The existing second query still locks the chosen repayment row, and the existing one-to-one/unique
  constraints remain the final singular-counterpart backstop.
- Concurrency evidence: the exact declared one-test PostgreSQL acceptance failed before the repair,
  then passed twice in isolated databases after it. Both green runs retained one link, one manual
  match audit, and the expected `200/409` outcomes.
- Regression exposure: the repair changes one lock-target argument only. It does not alter matching
  candidates, permissions, response fields, database schema, allocation/SAP status, balances,
  schedules, or ledger behavior.
- Focused evidence: 19 statement-matching, direct-repayment, and allocation tests passed; Django
  check and migration-sync checks returned zero.
- Residual risk: the orchestrator must still run authoritative complete backend coverage and all
  independent protected-path, diff-limit, migration, and repeated PostgreSQL gates before commit.
- Frontend risk: none; neither the original slice nor this repair changes frontend code.
