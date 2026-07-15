# Validation Summary

- Architecture-review bank terminal-scope probe: RED at HTTP 200, then GREEN at nondisclosing 403.
- Architecture-review missing response-event probe: RED at fabricated `responded`, then GREEN at
  `evidence_invalid` with resubmission disabled.
- Focused public API suites: 45 tests passed; two SQLite-only PostgreSQL skips were expected.
- PostgreSQL acceptance: changed bank decision versus current-case invalidation passed twice with
  exact one-winner/zero-loser decision, audit, workflow, and version ledgers.
- Django: system check passed; `makemigrations --check --dry-run` reported no changes.
- Backend: 912 tests passed, 48 declared concurrency/browser-environment skips, 91% coverage against
  the configured 85% floor.
- Frontend: build, TypeScript, ESLint, and 311 Vitest tests passed.

Full command output is retained under `terminal-logs/` in this evidence directory.
