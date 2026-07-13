# Execution Plan

Selected slice: 006Z15-member-public-action-authority-matrix-closure

1. Inventory the ten production member action boundaries, their request/module contracts, persisted
   effects, and canonical nondisclosure errors. Reuse existing test builders and public interfaces.
2. Replace the evaluator-only matrix with independently selectable public-action rows. For each row,
   capture the complete authority/member/evidence/history/audit/workflow ledger, save a focused RED
   run, add only matching persisted scope, assert the exact successful response/write, and execute a
   differently permissioned action denial.
3. Add representative real-boundary coverage for global, created-by, active-team, inactive-team,
   unrelated-team, and unrelated-member scope, plus staff eligibility, portal, and borrower-limit
   cross-member substitution. Retain only structural AST dependency guards that cannot be observed
   behaviorally.
4. Run the focused matrix and related boundary suites to GREEN, then backend check, migration-sync,
   full coverage, and all frontend build/typecheck/lint/test gates. Save terminal evidence.
5. Review the completed diff against the slice/source requirements, update the Epic 006 digest and
   Ralph state/progress/handoff/slice status, sharpen the next two Not Started corrective slices
   using already-open review context, and finish the required changed-files, risk, review, and
   summary artifacts.

Permissions check: planned edits are limited to `sfpcl_credit/**`, `docs/working/**`,
`docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and this run folder; all are allowed by
`.ralph/permissions.json`. Protected and forbidden paths remain read-only.
