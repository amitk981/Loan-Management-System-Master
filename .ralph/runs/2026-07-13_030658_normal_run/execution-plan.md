# Execution Plan

Selected slice: 006Y16-witness-parent-scope-and-contract-closure

1. Add a public witness PATCH regression that gives a permissioned Credit Manager three parent
   identifiers: an existing Credit Assessment application, an existing initial-stage application,
   and a random UUID. Assert that Credit Assessment scope reaches child lookup, while the latter
   two return the same `403 OBJECT_ACCESS_DENIED` envelope and preserve complete witness/history/
   audit/workflow snapshots.
2. Run that focused test with the mandated Ralph Python interpreter and retain the failing output
   under `evidence/terminal-logs/`.
3. Remove the absent-parent Credit Manager role shortcut from the application authority module so
   unresolved identifiers use the same explicit, row-independent scope vocabulary as existing
   parents. Run the focused witness tests green and retain the output.
4. Update `docs/working/API_CONTRACTS.md` and the Epic 004 digest with the authority-first parent/
   child lookup ordering and exact `403`/`404` behavior. Run a focused dependency scan.
5. Run all configured frontend and backend gates with the mandated interpreters, then perform the
   required standards/spec review and save the review packet, risk assessment, changed-files list,
   final summary, progress/state/handoff updates, and slice completion status.
6. Sharpen the next one or two Not Started slices only from source documents already opened during
   this run; do not broaden source loading merely to manufacture queue edits.
