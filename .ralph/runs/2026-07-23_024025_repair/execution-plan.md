# Execution Plan — 011K Same-Worktree Repair

## Failure boundary

Preserve the existing 011K candidate and repair only the complete backend coverage failure recorded
for `CreditAssessmentModelOwnershipMigrationTests`. The failure occurs while constructing the
historical pre-credit-move migration state after the new compliance app was added.

## Feedback loop

1. Run the exact historical migration-test class with the mandated Ralph virtualenv interpreter and
   retain the failing output.
2. Inspect only migration-graph dependencies needed to distinguish whether the new compliance leaf
   pulls post-move credit state into the historical projection.
3. Make the smallest compatibility correction in that migration-test projection; do not change the
   011K schema, domain behavior, APIs, or protected workflow files.
4. Rerun the exact test class until green, then run the focused compliance test labels plus Django
   check and migration-sync checks. Leave the authoritative complete backend coverage rerun to Ralph.

## Evidence and completion

- Save focused repair RED/GREEN output under this repair run's `evidence/terminal-logs/`.
- Record the demonstrated cause and bounded risk in `risk-assessment.md` and `review-packet.md`.
- Finish the review-packet Result as exactly `Ready for independent validation`.

## Permissions

The planned edit is under `sfpcl_credit/tests/**`; run artifacts are under this repair run folder.
Both are allowed by `.ralph/permissions.json`. No protected, source, state, progress, slice-status, or
changed-files artifact will be edited.
