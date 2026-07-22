# Execution Plan

Selected slice: 011D-non-payment-note-workflow

## Repair boundary

- Preserve the existing 011D candidate and change only the demonstrated PostgreSQL acceptance
  failure domain reported by the prior run.
- The exact validator is
  `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.NonPaymentNotePostgreSQLAcceptanceTests`
  under `sfpcl_credit.config.postgres_test_settings`; it must discover and pass exactly two tests.
- Do not broaden product behavior, alter the acceptance contract, edit frontend code, or touch any
  protected/source/mechanical bookkeeping path.
- Permissions were checked before product edits: `.ralph/permissions.json` permits
  `sfpcl_credit/**` and `.ralph/runs/**`; protected configuration and `docs/source/**` remain
  untouched.

## Diagnosis and repair

1. Use the two saved independent PostgreSQL failures as the initial red evidence. Both terminate at
   `RecoveryWorkflow.create_non_payment_note()` with PostgreSQL rejecting `FOR UPDATE` on the
   nullable side of an outer join.
2. Inspect the exact locking queryset and related model nullability. Preserve the source-derived
   note behavior and concurrency contract while narrowing the row lock to a PostgreSQL-valid query.
3. Run the exact two-test PostgreSQL validator with the mandated Ralph interpreter and save the
   repair output. If it exposes another error in the same validator, repair that error in the same
   bounded domain and rerun until all two tests pass.
4. Run focused SQLite workflow/reverse tests plus Django check and migration-drift checks only if
   the product repair changes shared behavior. Do not run the complete backend suite or coverage.

## Completion evidence

- Save exact command, discovered count, PostgreSQL environment evidence, pass/fail result, and exit
  status under this repair run's `evidence/terminal-logs/`.
- Inspect targeted diff hunks and protected-path status.
- Complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; set the review packet
  Result exactly to `Ready for independent validation` only after the named validator is green.

## Completion record

- Diagnosed the saved deterministic PostgreSQL failures and repaired only the two locking queries in
  `recovery_workflow.py`.
- The exact two-test validator progressed through each same-domain error and is finally green with
  explicit lock targets and no nullable eager joins.
- PostgreSQL environment evidence, focused workflow regression, system check, and migration-drift
  evidence are saved under `evidence/`.
