# Quality Gate Log

Run: `2026-07-14_124337_architecture_review`

| Gate | Command | Result |
|---|---|---|
| Slice queue | `bash -lc 'source scripts/lib/ralph-slice-selection.sh; ralph_slice_queue_lint docs/slices'` | PASS; no output, dangling dependency, malformed status, or cycle |
| Frontend build | `npm run build` in `sfpcl-lms` | PASS; 1,877 modules transformed; production bundle built |
| Frontend typecheck | `npm run typecheck` | PASS |
| Frontend lint | `npm run lint` | PASS |
| Frontend tests | `npm test` | PASS; 33 files, 293 tests |
| Django check | `"/Users/amitkallapa/LMS/.ralph/venv/bin/python" sfpcl_credit/manage.py check` | PASS; no issues |
| Migration sync | `"/Users/amitkallapa/LMS/.ralph/venv/bin/python" sfpcl_credit/manage.py makemigrations --check --dry-run` | PASS; no changes detected |
| Backend suite | `"/Users/amitkallapa/LMS/.ralph/venv/bin/python" -m coverage run --source=sfpcl_credit sfpcl_credit/manage.py test sfpcl_credit.tests` | PASS; 746 tests in 194.919s, 23 expected PostgreSQL-only skips |
| Coverage floor | `"/Users/amitkallapa/LMS/.ralph/venv/bin/python" -m coverage report --fail-under=85` | PASS; 27,813 statements, 1,930 missed, 93% total |
| Diff integrity | `git diff --check` | PASS |
| State JSON | `jq empty .ralph/state.json` | PASS |
| Protected/source paths | status path audit against Ralph never-do list | PASS; none changed |
| Production paths | status path audit for `sfpcl-lms/src`, `sfpcl-lms/public`, and `sfpcl_credit` | PASS; none changed |

The Vite chunk-size and deprecated CJS API messages were warnings only and pre-existed this docs-only
review. No localhost browser contract was declared for the architecture-review descriptor.
