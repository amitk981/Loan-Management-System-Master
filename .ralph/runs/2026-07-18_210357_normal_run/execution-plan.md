# Execution Plan

Selected slice: 009H9A-queued-advice-migration-provenance-closure

1. Inspect communications migrations 0007-0009 and their retained migration-test fixtures to map
   the historical schema and the exact queued-job/outbox provenance relationships available to
   migration 0008.
2. Add one public migration test for a genuine queued H5 job, run it against the current migration
   chain, and retain the expected RED output in `evidence/terminal-logs/`.
3. Make the smallest in-place correction to migration 0008 so only a singular, exact queued-job
   relationship with complete internally checksummed frozen snapshots remains verified; keep every
   incomplete, mismatched, malformed, duplicated, cross-linked, or legacy-attempt case ambiguous.
4. Add drift-matrix coverage incrementally, then prove fresh forward, retained forward, safe
   reverse, current-leaf restoration, and reapply while preserving an exact before/after manifest.
5. Run the focused H6/H7 migration and public no-redispatch/portal-exclusion suites with the mandated
   backend interpreter; save GREEN and Django check/migration-sync evidence. No full backend suite
   or coverage run will be duplicated locally.
6. Review the diff for protected paths, migration/history scope, and configured limits; update the
   Epic 009 digest plus Ralph state/progress/handoff/slice status, sharpen the next two Not Started
   slices using already-read source material, and complete changed-files, risk, review, and final
   artifacts for orchestrator validation and commit.
