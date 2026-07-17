# Execution Plan

Selected slice: 009G3-post-transfer-aggregate-and-checklist-integrity-closure

Mode: repair

1. Preserve the quarantined 009G3 implementation and diagnose the prior migration-validation
   failure from its exact failure summary.
2. Add only the missing disbursements migration for the already-implemented protected register
   relation, with a fail-closed coherent-evidence backfill.
3. Verify migration sync, fresh migration application, the exact coverage-crashing test, the
   protected-register regression, the transfer-success test class, and Django check.
4. Save self-contained evidence and Ralph bookkeeping, leaving complete coverage and PostgreSQL
   acceptance to the independent orchestrator.
