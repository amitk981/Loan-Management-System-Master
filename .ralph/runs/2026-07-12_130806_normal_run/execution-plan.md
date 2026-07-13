# Execution Plan

Selected slice: 006X5-credit-public-action-write-matrix-closure

1. Read the Epic 006 digest, cited source sections, 006X4 regression test, public credit/approval
   module seams, and their existing fixtures; verify the High-risk approval is not revoked.
2. RED: replace the projection-only regression with an enumerated public action/write matrix that
   executes success and denial variants for eligibility, loan limit, appraisal lifecycle, each
   review outcome, and sanction submission; preserve the failing output in
   `evidence/terminal-logs/`.
3. GREEN incrementally through public interfaces: align any projection/write predicate or stable
   denial mismatch exposed by the matrix, asserting six-field actions and zero state/audit/
   workflow/history/note/case evidence for denied writes.
4. Add the PostgreSQL stale-enabled-action race through public module seams and run the declared
   five-race acceptance command twice without skips, saving both logs and a generated matrix result
   table plus dependency scan.
5. Run configured backend and frontend quality gates, save self-contained evidence and run
   artifacts, assess risk, and review the diff against the slice/source contract.
6. Update the selected slice, Ralph state/progress/handoff, and sharpen the next one or two eligible
   Not Started slices only from already-opened source/digest material.
