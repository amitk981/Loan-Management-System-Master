# Risk Assessment

Risk level: High (selected-slice declaration); Low incremental repair risk.

- Demonstrated failure: Ralph counted 2,001 changed lines after trusted-browser setup generated a
  three-line PDF inside `sfpcl_credit/e2e-document-storage/`; the configured limit is 2,000.
- Root cause: Playwright's default E2E document-storage root lived inside the measured worktree.
  The deterministic portal seed correctly wrote its Term Sheet there before browser launch.
- Repair scope: the disposable default store now lives below the OS temp directory and is
  namespaced by worktree basename. An explicit `SFPCL_DOCUMENT_STORAGE_ROOT` override remains
  authoritative. No production API, business rule, schema, permission, styling, or source file
  changed in this repair.
- Controls: exact validator-equivalent line count, real Playwright server setup, filesystem proof
  that the seed PDF is outside the repository, build/typecheck/lint/319 frontend tests, Django
  check, Playwright collection, `git diff --check`, and protected-path inspection.
- Residual risk: local Chromium remains sandbox-denied before page creation. Independent Ralph
  validation must run the declared spec twice and verify four non-empty screenshots.
