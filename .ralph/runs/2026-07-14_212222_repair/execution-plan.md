# Execution Plan

Selected slice: 008F2-security-instrument-boundary-and-poa-lifecycle-closure

1. Reproduce the prior run's exact diff-limit calculation and attribute the 2,965 changed lines to
   tracked edits/deletions and untracked security-boundary files.
2. Preserve the completed security-instruments ownership and PoA lifecycle behavior while reducing
   avoidable repair volume: restore redundant test churn where retained compatibility seams allow
   it, consolidate corrective assertions, and compact the state-only migration without changing its
   database operations or retained-table guarantees.
3. Run the focused boundary and PoA suites with the mandated Ralph virtualenv, then rerun the exact
   diff-limit calculation until it is deterministically at or below 2,000 lines.
4. Run Django check, migration-sync, the full backend coverage gate, and all configured frontend
   build/typecheck/lint/test gates. Save repair evidence and finish the required changed-files, risk,
   review, final-summary, state/progress/handoff, and selected-slice artifacts without broadening the
   slice.
