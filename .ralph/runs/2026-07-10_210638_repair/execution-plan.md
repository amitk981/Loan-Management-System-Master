# Execution Plan

Selected slice: 006H-eligibility-appraisal-frontend-integration

1. Diagnose the failed `2026-07-10_203039_normal_run` worktree and reproduce its exact validator
   failure. Treat the 2,000-line diff cap as a continuous repair feedback loop and do not copy or
   salvage the ungated implementation.
2. Inspect the current Appraisal Workbench, Application Detail integration seam, shared loan
   components, current-user permissions, and the completed Epic 006 backend response contracts.
3. Add focused frontend regression tests first for the typed API client, stored backend projections,
   permission/state action gates, ordered review history, exact sanction request/no retry, standard
   errors, and the absence of mock/formula ownership. Save the failing output under
   `evidence/terminal-logs/`.
4. Implement the smallest API-backed integration that reuses the existing workbench and component
   patterns, preserves decimal strings and server-owned workflow facts, and keeps the validator
   count safely below 2,000 lines. Do not add backend logic, persistence, dependencies, styling, or
   source-document changes.
5. Run focused green tests, frontend lint/typecheck/test/build, backend check/coverage/migration
   gates, `git diff --check`, protected-path/diff-limit checks, and save self-contained API and
   visual evidence (or an explicit environment limitation if screenshot capture is impossible).
6. Complete Ralph artifacts, sharpen only the next `Not Started` slice using already-opened source
   material, and update slice status, state, progress, handoff, risk assessment, review packet,
   changed-files list, and final summary without committing, adding, or pushing.
