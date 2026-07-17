# Execution Plan

Selected slice: 009G3-post-transfer-aggregate-and-checklist-integrity-closure

Mode: repair

1. Preserve the quarantined 009G3 implementation and diagnose only the failure recorded in
   `.ralph/runs/2026-07-17_222100_repair/failure-summary.md` and its backend coverage log.
2. Reproduce the exact legacy documentation test failure serially with the mandated backend
   interpreter, saving the red output under this run's `evidence/terminal-logs/` directory.
3. Update only the obsolete regression test whose destructive register tamper now conflicts with
   009G3's required protected aggregate relation. Keep production models and behavior unchanged.
4. Re-run the exact test, the focused documentation approval class, and the 009G3 transfer-success
   class; save green output. Run Django check and migration-sync checks. Do not run the complete
   backend suite or coverage locally because the orchestrator owns those authoritative gates.
5. Inspect the final diff and protected paths, record changed files and risk, then update the Ralph
   review packet, final summary, progress, state, handoff, and already-complete slice bookkeeping.
6. Recheck the next two Not Started slice files against already-open Epic 009 material and sharpen
   only if they remain insufficiently concrete. Delegate commit and full revalidation to Ralph.

The repair feedback loop is the single failing test
`FinalDocumentationApprovalApiTests.test_public_post_disbursement_signature_binds_current_transfer_evidence`.
It deterministically exercises the exact obsolete deletion and completes in seconds.
