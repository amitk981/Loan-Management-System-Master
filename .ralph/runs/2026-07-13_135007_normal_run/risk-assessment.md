# Risk Assessment

Risk level: High

- Selected slice: `007C3-approval-case-source-read-scope-closure`.
- This changes sanction-package authorization, catalogue grants, collection scoping, and database
  projections used for nondisclosing counts. A defect could expose an unrelated case, hide a
  source-required reader, or make list/detail authority disagree.
- Mitigation: `approvals.case.read` remains separate from object scope. One attributable module
  decision covers list/detail/actions; exact approver UUID rows replace JSON substring matching;
  read-only grants never enter assignment/action paths; every denial matrix snapshots the full
  case/action/sanction/audit/workflow/notification ledger.
- The indexed coherence projection is derived, not action authority. Approval-case saves update it
  and its exact approver index atomically; appraisal saves refresh it; detail/actions re-run the
  complete live snapshot predicate. Historical 0009 coherent/malformed fixtures prove deterministic
  migration backfill through `MigrationExecutor`.
- SQL evidence requires one scoped COUNT and one LIMIT/OFFSET query after repository growth, with
  inaccessible rows excluded from counts. Full backend and frontend gates pass.
- One forward migration adds the grant, derived approver index, and coherence field. No data is
  deleted; reverse cleanup removes only the exact two seeded grant pairs.
- No frontend, external communication, deployment, protected file, or `docs/source/` change was
  made. Owner standing approval applies and no 007C3 veto entry was present.
- Diff accounting is within Ralph limits: 20 non-run changed files and 1,354 changed/new lines,
  with one migration and no dependency additions.
