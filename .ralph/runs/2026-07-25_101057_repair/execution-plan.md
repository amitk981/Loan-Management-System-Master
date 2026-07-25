# Execution Plan

Selected slice: 012G-critical-e2e-uat-smoke-scenarios

## Repair boundary

- Preserve the current multi-run candidate and repair only the authoritative backend impacted
  validation failure reported by
  `.ralph/runs/2026-07-25_094752_repair/failure-summary.md`.
- Treat the two Chrome launch closures as pre-page infrastructure evidence; do not change
  application/browser behavior or claim new screenshots for them.
- Do not modify protected workflow files, source documents, mechanical orchestrator facts,
  unrelated slices, or unrelated product domains.

## Feedback loop and diagnosis

1. Reproduce
   `TracerApiTests.test_authenticated_user_without_tracer_permission_cannot_write_domain_rows`
   with the mandated backend interpreter and save the red output.
2. Inspect only the tracer test, URL configuration, and test isolation seams that determine why
   `/api/e2e/tracer/lifecycle/` resolves to 404 in the impacted lane after returning the required
   403 in isolation.
3. Rank falsifiable hypotheses and use a minimal deterministic test-order reproducer to identify
   the state leak or route-contract defect.

## Minimal repair and verification

- Add or retain a regression test at the real failing seam before changing implementation.
- Apply the smallest repair that restores the source-required backend denial contract without
  broadening tracer permission or production route exposure.
- Save focused red/green evidence under
  `.ralph/runs/2026-07-25_101057_repair/evidence/terminal-logs/`.
- Rerun the exact authoritative impacted validator command from
  `backend-impacted-results.md` until every error in that validation domain is green.
- Run Django system check and migration-drift check. Run frontend gates only if a frontend file is
  changed during this repair.
- Save a diagnosis, risk assessment, final summary, and review packet whose Result is exactly
  `Ready for independent validation`.
