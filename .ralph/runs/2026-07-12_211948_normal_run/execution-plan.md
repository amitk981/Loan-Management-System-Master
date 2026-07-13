# Execution Plan

Selected slice: `006Y11-member-form-container-and-error-matrix-closure`

1. Inspect the existing Member Directory/Profile production containers, shared HTTP transport,
   006Y9 tests, and trusted-browser scenario. Keep all edits within the permission allow-list and
   preserve the approved frontend composition.
2. RED: add a mounted transport-boundary tracer test for one complete member variant and capture
   its focused failing output under `evidence/terminal-logs/`.
3. GREEN: make the smallest production/test-harness correction needed for that public interaction,
   then expand incrementally across individual, FPC, Producer Institution, ordinary update, identity
   request, and identity approval success/error cases. Assert exact bodies/counts, one success GET,
   zero error refetch/retry/local merge, and verbatim backend facts.
4. Extend `member-governance-variants.e2e.spec.ts` with collision-proof Producer Institution data,
   exact POST/detail-GET counts, six-field approval-action proof, masked canonical readback, and the
   five declared screenshots. Validate Playwright collection locally without fabricating browser
   evidence.
5. Run focused tests during development, then frontend build, typecheck, lint, and full Vitest.
   Run backend check, migration sync, and the configured coverage suite only if production/backend
   scope or the gate contract requires it. Save all outputs in the run evidence folder.
6. Review the diff against the slice/source contract, sharpen the next one or two Not Started slices
   using already-open digests, and complete changed-files, risk, review, final summary, state,
   progress, handoff, digest, and executed-slice status artifacts.
