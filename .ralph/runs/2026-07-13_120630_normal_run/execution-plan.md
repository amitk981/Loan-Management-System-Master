# Execution Plan

Selected slice: `007A6-approval-governance-winner-evidence-content-closure`

1. Preserve the existing four public/module PostgreSQL race interfaces and deepen their shared
   `_race` assertion seam so it identifies the sole newly written `VersionHistory` and
   `config.changed` rows from complete before/after ledgers.
2. RED: assert exact winning proposal, maker/checker, reason, target/resource, request provenance,
   effective dates, and old/new serialized configuration content. Require creation evidence to
   have no predecessor and supersession evidence to name the retained predecessor with its closed
   effective date. Add discriminating winner/loser proposal facts so a count-only or misattributed
   ledger fails.
3. GREEN: make the smallest production correction only if the stronger behavioral assertions
   expose incorrect evidence. Keep activation exclusively behind `decide_proposal` and the shared
   configuration lock; do not duplicate activation logic in the test.
4. Run the exact four independently named PostgreSQL methods twice after migrations 0005-0007,
   save attributable RED/GREEN logs, and run focused approval tests using the mandated Ralph
   virtualenv interpreter.
5. Run backend check, migration sync, full tests/coverage, and frontend build, typecheck, lint, and
   tests. Save self-contained validation evidence and the required changed-files, risk, review, and
   final-summary artifacts.
6. Update the Epic 007 digest, sharpen the next one or two eligible `Not Started` slices only from
   already-opened source/digest material, then mark this slice complete and update state, progress,
   and handoff only after all gates are green.

Permissions check: intended edits are limited to `sfpcl_credit/**`, `docs/working/**`,
`docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and this run folder; these paths are
allowed by `.ralph/permissions.json`. Protected and forbidden paths will remain unchanged.
