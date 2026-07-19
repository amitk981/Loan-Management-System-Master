# Execution Plan

Selected slice: 009L4-epic-009-canonical-read-and-bounded-pagination-closure

Mode: repair

1. Preserve the existing 009L4 implementation and reproduce the independent validator's exact
   owner-dependency failure with the focused SAP architecture test.
2. Trace the new `loans -> disbursements` edge and choose the smallest boundary correction that
   keeps one canonical, bounded Loan Account selector without copying disbursement-owner rules.
3. Apply only that boundary repair, then rerun the exact failing test and the focused Loan Account
   read/API tests affected by the selector relocation. Save red/green terminal evidence.
4. Run proportionate backend checks plus the already-impacted frontend MP14 test, typecheck, lint,
   and build; leave the complete backend coverage suite to Ralph's independent validator.
5. Record the demonstrated root cause, residual risk, traceability, and independent-validation
   handoff in this run's risk assessment, review packet, and final summary.

Permission check: planned edits are limited to `sfpcl_credit/**` and this run's
`.ralph/runs/2026-07-19_121251_repair/**`, both allowed by `.ralph/permissions.json`. Protected,
forbidden, source, orchestrator-owned state/progress/status, and git metadata paths will not be
edited.
