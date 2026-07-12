# Execution Plan

Selected slice: `006Y15-witness-authority-matrix-behavioral-closure`

1. Inspect the existing witness PATCH view, public authority/action projection, and the 006Y14
   behavioral matrix without changing production code.
2. Add one public-HTTP regression for an authorised actor requesting a genuinely absent parent;
   run it alone and save the expected RED output.
3. Make the smallest production correction needed to preserve normal `404 NOT_FOUND` semantics
   while keeping existing and random out-of-scope parent IDs at identical `403
   OBJECT_ACCESS_DENIED` responses; rerun and save GREEN output.
4. Add independently selectable contact and identity rows for unknown fields and close any matrix
   projection/write gaps through public action results plus one PATCH per applicable row. Snapshot
   Witness, correction history, AuditLog, and WorkflowEvent for every loser and avoid internal
   authority mocks/call-count assertions. Save RED then GREEN evidence per TDD tracer bullet.
5. Run focused witness API tests, dependency/internal-mock scans, then all configured backend and
   frontend gates. Save terminal logs and summarize any environment-only browser limitation.
6. Produce changed-files, risk, review, and final-summary artifacts; update the slice, progress,
   state, handoff, epic digest, and sharpen the next one or two Not Started slices using only source
   material already opened.

Permitted edit scope: `sfpcl_credit/**`, test files under that tree, `docs/working/**`,
`docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and this run folder. Protected and
forbidden paths remain untouched.
