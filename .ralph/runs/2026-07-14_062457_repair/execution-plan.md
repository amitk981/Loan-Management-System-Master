# Execution Plan

Selected slice: `008A-document-template-model-and-versioning`
Mode: `repair`

## Demonstrated failure

Independent PostgreSQL acceptance fails deterministically in
`SanctionSubmissionConcurrencyTests.test_concurrent_returned_cycle_resubmissions_create_one_cycle_two_ledger`.
The `return_case` path issues `SELECT ... FOR UPDATE` across a nullable outer join and PostgreSQL
raises `NotSupportedError: FOR UPDATE cannot be applied to the nullable side of an outer join`.
The quarantined 008A implementation and its existing evidence must be preserved.

Progressive finding: direct execution of 008A's own declared PostgreSQL race exposed the same
invalid lock shape on its nullable template-file eager load. It is covered by the same minimal
lock-target repair and separate red/green evidence.

## Repair sequence

1. Re-run the single PostgreSQL test as the tight red-capable feedback loop and save the RED output.
2. Inspect only the failing approval action query, its model relationships, and the existing test seam.
3. Rank and test minimal hypotheses. Prefer narrowing the lock target to the approval-case row while
   retaining eager reads, unless evidence shows a different nullable join is responsible.
4. Add or strengthen a regression assertion only if the existing PostgreSQL test does not already
   exercise the real failing path; then apply the smallest query-only fix.
5. Re-run the single PostgreSQL test twice, the full declared five-race acceptance command twice,
   and the relevant SQLite approval/sanction suite. Save all outputs under this repair run.
6. Run Django check, migration sync, full backend coverage, and frontend build/typecheck/lint/tests.
7. Update only repair artifacts plus the demonstrated production/test fix, then refresh
   changed-files, risk assessment, review packet, final summary, progress, state, handoff, and the
   selected slice status if required by the Ralph artifact contract.

## Scope guard

No 008A catalogue behaviour, frontend surface, schema, source document, protected file, or unrelated
quality rule will change. The orchestrator owns independent revalidation and any commit/merge/push.
