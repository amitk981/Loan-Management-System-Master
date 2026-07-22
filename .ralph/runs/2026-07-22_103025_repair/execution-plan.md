# Execution Plan

Selected slice: 011A-default-case-opening
Mode: same-worktree repair
Failed validation domain: backend complete-suite coverage, specifically
`WitnessEvidenceMigrationTests.test_backfill_is_idempotent_and_reverse_preserves_legacy_rows`

1. [completed] Preserve the existing 011A candidate and reproduce the recorded historical witness migration
   failure with the exact focused Django test label and mandated Ralph Python interpreter; retain output.
2. [completed] Inspect only the failing migration test, witness migration graph, and current candidate migration
   dependencies; rank falsifiable causes without reopening 011A product decisions.
3. [completed] Use the existing failing behavior as the regression seam, or add one narrowly scoped assertion only
   if it cannot detect the demonstrated schema mismatch; retain RED evidence before the repair.
4. [completed] Apply the smallest correction inside the migration-validation domain. Do not change 011A default
   behavior, unrelated product scope, protected files, source documents, or orchestrator-owned bookkeeping.
5. [completed] Rerun the exact focused validator to GREEN, then run the directly affected witness migration module,
   migration sync, Django system check, and focused 011A API regression. Leave authoritative complete-suite
   coverage to Ralph's independent validator.
6. [completed] Save evidence, update risk-assessment.md and review-packet.md, and set the Result exactly to
   `Ready for independent validation` only after all focused checks pass.

Permissions checked before edits: `.ralph/runs/**` and `sfpcl_credit/**` are allowed by
`.ralph/permissions.json`; protected and forbidden paths will not be modified.

Outcome: `defaults.0001_initial` was the sole included leaf pulling `applications.0012` through
`0017` into the pre-0012 witness projection. The existing red-capable behavior test was retained and
made green by classifying `defaults` with the downstream owners already excluded from that historical
state. No product behavior or schema changed.
