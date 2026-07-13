# Execution Plan

Selected slice: `002J2-forbidden-permission-error-contract-alignment`

1. Add failing contract regressions that require authenticated global-permission denials to return
   `403 FORBIDDEN`, preserve object/sensitive/approval denial codes, and reject production uses of
   the legacy `PERMISSION_DENIED` literal outside the shared compatibility boundary.
2. Run the focused backend contract tests with the mandated Ralph virtualenv and save the failing
   output under `evidence/terminal-logs/`.
3. Centralise legacy-code normalization in the shared API envelope, migrate typed object-access and
   all production callers/tests to `FORBIDDEN`, and leave grants, check ordering, object scope,
   status codes, messages, success bodies, and side effects unchanged.
4. Update the working API contract and save representative before/after examples plus the complete
   migrated endpoint-family inventory.
5. Run focused tests green, then all configured backend/frontend gates; save logs and reviewable
   evidence.
6. Complete changed-files, risk, review, final-summary, slice/state/progress/handoff updates, and
   sharpen the next two Not Started slices using requirements already available in their existing
   digests/review notes.
