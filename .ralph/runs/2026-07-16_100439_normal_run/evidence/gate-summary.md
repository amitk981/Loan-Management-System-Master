# Gate Summary

- Focused backend owner/query/workspace suite: 36 tests, PASS.
- Full backend coverage run: 951 tests in 451.765 seconds, PASS with 51 expected skips.
- Backend coverage: 91% (`39,474` statements, `3,502` missed).
- Django system check: PASS, no issues.
- Migration drift: PASS, no changes detected.
- Frontend build: PASS.
- Frontend typecheck: PASS.
- Frontend lint: PASS.
- Frontend tests: 36 files / 322 tests, PASS.
- Playwright collection: one real-Django test collected; five screenshot paths declared.
- Local browser execution: Chromium denied macOS Mach-port bootstrap registration before page
  creation; no screenshots fabricated, independent twice-run orchestrator gate authoritative.
- Diff check: PASS.
- Diff limits: 22 files and 1,787 changed lines (limits 30 / 2,000), PASS.

The test runner writes its progress and terminal summary to stderr; the complete captured agent
terminal record is `terminal-logs/codex.log`, while `backend-tests.log` retains stdout and
`backend-coverage.log` retains the complete coverage table.
