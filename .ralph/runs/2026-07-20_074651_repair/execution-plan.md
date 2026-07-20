# Execution Plan

Selected slice: `010F-interest-invoice-generation`

## Repair boundary

Preserve the quarantined annual-interest-invoice implementation and repair only the independently
demonstrated complete-suite failure: six legacy migration-test errors caused by database schema
state leaking between migration test classes when the suite is partitioned across workers.

## Diagnosis loop

1. Run the three failing migration-test classes together with the mandated backend interpreter and
   retain the exact failing output as the repair RED signal.
2. Compare their migration teardown/setup contracts and identify which class leaves the schema at a
   historical migration state or relies on a predecessor's teardown.
3. Rank and test bounded hypotheses one variable at a time; do not alter the invoice calculation,
   issuance, permissions, or public API unless evidence directly implicates them.

## Repair and verification

1. Add the smallest regression guard at the real migration-test lifecycle seam, then restore the
   database schema after each affected class so worker ordering cannot change results.
2. Re-run the exact combined RED command to GREEN and repeat it once for determinism.
3. Run the focused 010F API tests, migration sync, and backend check; do not run the complete backend
   suite because the orchestrator owns full independent coverage revalidation.
4. Save RED/GREEN terminal logs, risk assessment, final summary, and a review packet whose Result is
   exactly `Ready for independent validation`.
