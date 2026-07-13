# Repair Validation Summary

## Reproduction

- Original trusted runs: both failed at the exact ordinary PATCH assertion because received
  `mobile_number` was a masked value such as `********0001` while the test expected the original
  plain contact value.
- Mounted red regression: 1 failed, 13 skipped; exact unexpected field was
  `mobile_number: "********3210"`.

## Green Checks

- Focused routed regression: 1 passed.
- Member governance form suites: 19 passed.
- Mounted production-container matrix: 14 passed.
- Frontend full suite: 201 passed across 29 files.
- Frontend build, TypeScript typecheck, and ESLint: passed.
- Playwright declared-spec collection: 1 test in 1 file.
- Django system check and migration sync: passed.
- Backend: 462 tests passed, 8 expected SQLite skips, 93% coverage (85% required).

## Trusted Browser Boundary

Chromium launch inside the coding sandbox failed at macOS Mach-port registration with permission
denied, before test execution. No screenshots were fabricated. Ralph's independent localhost browser
gate must run the declared spec twice and produce the five named screenshots.
