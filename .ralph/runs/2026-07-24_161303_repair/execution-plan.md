# Execution Plan

Selected slice: 012EA-workflow-task-engine-and-task-inbox-apis

## Demonstrated failure

Independent complete-suite coverage reached
`CreditAssessmentModelOwnershipMigrationTests.test_forward_move_preserves_rows_relationships_and_evidence_references`
and Django rejected a migration plan that mixed a backwards migration for `credit.0001` with a
forwards migration for `workflows.0002`.

## Bounded repair

1. Use the exact failing Django test as the fast, red-capable feedback loop and retain its failure
   output under `evidence/terminal-logs/`.
2. Inspect only the migration test, the new `workflows.0002` dependency graph, and the prior
   ownership-migration contract needed to distinguish test-isolation from product-schema defects.
3. Rank and test the migration-plan hypotheses, then make the smallest repair in that validation
   domain. Preserve the existing 012EA candidate and do not change task-engine behavior.
4. Rerun the exact named validator test until green, then run the owning migration-test module and
   migration consistency/system checks as focused regressions. Independent Ralph validation
   remains responsible for the authoritative complete coverage lane.
5. Save the diagnosis, RED/GREEN output, risk assessment, final summary, and review packet with
   the exact ready result.

## Permission check

The only anticipated product edit is under `sfpcl_credit/tests/**`; repair artifacts are under
`.ralph/runs/2026-07-24_161303_repair/**`. Both are allowed by `.ralph/permissions.json`.
Protected configuration, scripts, source documents, orchestrator-owned state/progress/status
files, and Git metadata will not be edited.
