# Gate Summary

| Gate | Result | Evidence |
|---|---|---|
| Backend check | Pass | `backend-check-results.md` |
| Backend migration sync | Pass | `backend-migrations-results.md` |
| Backend full tests/coverage | Pass: 397 tests, 94% | `backend-coverage-results.md`, terminal log |
| Frontend lint | Pass | `lint-results.md` |
| Frontend typecheck | Pass | `typecheck-results.md` |
| Frontend tests | Pass: 148 tests | `test-results.md` |
| Frontend build | Pass | `build-results.md` |
| Focused red/green | Pass | `evidence/terminal-logs/005e3-*-red.log`, matching green logs |
| Playwright collection | Pass | `evidence/terminal-logs/005e3-playwright-list.log` |
| Playwright browser | Environment blocked | `evidence/terminal-logs/005e3-playwright.log` |
| Protected paths | Pass by final diff inspection | No protected source path changed |
| Diff limits | Pass | 13 tracked files, 477 tracked lines before artifacts; no dependency/migration |
