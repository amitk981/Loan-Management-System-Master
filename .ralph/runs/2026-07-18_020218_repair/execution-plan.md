# Execution Plan

Selected slice: 009H3A-communications-advice-persistence-and-provider-identity
Mode: repair

1. Reproduce the independent coverage failure with the smallest serial pair: run the new
   communications owner migration test immediately before one retained migration test that needs
   the current application schema. Capture the red output.
2. Verify the failure is test-global migration state leakage: the new forward/reverse/reapply test
   ends at its two explicit targets instead of restoring every app to the migration-graph leaves.
3. Add only the missing migration-test cleanup seam, following the repository's existing
   `TransactionTestCase` migration-test pattern. Do not alter production models, migrations, or
   advice behavior.
4. Re-run the exact serial pair and the focused 009H3A migration/ownership/adapter regressions;
   capture green output, Django check, and migration-sync evidence.
5. Refresh the repair run artifacts, bookkeeping, and next-slice sharpening assessment, then leave
   complete-suite coverage to the orchestrator's independent validation.
