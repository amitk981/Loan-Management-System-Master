# Execution Plan

Selected slice: 011A-default-case-opening
Mode: same-worktree repair
Failed validation domain: backend complete-suite coverage, specifically
`CreditAssessmentModelOwnershipMigrationTests.test_forward_move_preserves_rows_relationships_and_evidence_references`

1. [completed] Preserve the existing 011A candidate and reproduce the recorded migration-state failure with the
   exact focused Django test label using the mandated Ralph Python interpreter; retain the output.
2. [completed] Inspect only the migration graph and migration test involved in the missing historical
   `applications.EligibilityAssessment` state, then rank falsifiable causes.
3. [completed] Add or adjust one regression behavior at the correct migration seam if the existing failing test
   does not already lock the demonstrated failure; retain RED output before any product fix.
4. [completed] Apply the smallest correction within the migration-validation domain. Do not alter 011A default
   behavior, unrelated tests, protected files, source documents, or orchestrator-owned bookkeeping.
5. [completed] Rerun the focused migration validator to GREEN, then run migration sync and the directly affected
   default-opening/migration probes. Leave the authoritative complete-suite coverage rerun to Ralph.
6. [completed] Save repair evidence, update the repair risk assessment and review packet, and set the review
   packet Result exactly to `Ready for independent validation` only after focused checks pass.

Permissions checked before edits: `.ralph/runs/**` and `sfpcl_credit/**` are allowed by
`.ralph/permissions.json`; protected/forbidden paths will not be modified.

Outcome: the new `defaults` leaf was the sole graph target pulling `credit.0001` into the legacy
pre-move projection. The existing red-capable ownership behavior test was retained and made green by
classifying `defaults` with the other downstream owners already excluded from that historical state.
