# Repair Execution Plan

Selected slice: 009H3BA-communications-dispatcher-outbox-freeze

1. Preserve the quarantined 009H3BA implementation and reproduce the independent validator's
   single failure with the exact historical receipt-owner migration test under the mandated Ralph
   Python interpreter.
2. Minimise the failure around the migration test's schema projection and reused public advice
   fixture. Rank and test only hypotheses that explain why `communication_delivery_outboxes` is
   absent when the dispatcher is invoked.
3. Add or tighten the failing regression at the historical-migration seam before the repair, save
   RED output, and change only the demonstrated test-isolation/projection defect. Do not alter the
   dispatcher, outbox schema, public advice contract, or production migration behavior unless the
   repro proves that is necessary.
4. Save GREEN output for the exact failed test and the smallest ordered migration/advice test set
   capable of detecting leaked schema state. Run focused communications/advice tests, Django
   check, migration sync, compile/static ownership checks, protected-path inspection, and diff
   review. Leave complete coverage to the independent orchestrator.
5. Refresh the repair evidence, changed-files list, risk assessment, review packet, final summary,
   state/progress/handoff/slice bookkeeping, and Epic 009 digest with the exact cause and repair.
   Recheck the next concrete Not Started slices without speculative edits.
