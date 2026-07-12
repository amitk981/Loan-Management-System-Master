# Quality Gate Results

Run on 2026-07-13 with the required managed Python interpreter.

- Slice queue lint: PASS, no output/problems.
- Protected/source diff scan: PASS, no protected/source paths changed.
- `git diff --check`: PASS.
- Frontend `npm run build`: PASS; Vite built 1,871 modules.
- Frontend `npm run typecheck`: PASS.
- Frontend `npm run lint`: PASS.
- Frontend `npm test -- --run`: PASS; 29 files, 204 tests.
- Backend `manage.py check`: PASS; zero issues.
- Backend `manage.py makemigrations --check --dry-run`: PASS; no changes detected.
- Backend coverage suite: PASS; 478 tests, 8 expected skips, 54.723 seconds.
- Backend coverage report: PASS; 93%, above the 85% floor.

Backend commands used `/Users/amitkallapa/LMS/.ralph/venv/bin/python`. No install, network,
PostgreSQL mutation, browser launch, or production-code command was needed for this docs-only review.

