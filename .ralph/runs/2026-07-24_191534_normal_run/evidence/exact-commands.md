# Exact Commands

Backend commands used the mandated interpreter:

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_performance_readiness
/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py check
/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py makemigrations --check --dry-run
/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py performance_readiness --run-local --results-output .ralph/runs/2026-07-24_191534_normal_run/evidence/bounded-local-results.json --environment-output .ralph/runs/2026-07-24_191534_normal_run/evidence/bounded-local-environment.json --expected-commit 8690cf46cb1809a2eb67e83b07a02d1fe0f3b240 --matrix-output .ralph/runs/2026-07-24_191534_normal_run/evidence/performance-scenario-matrix.json --output .ralph/runs/2026-07-24_191534_normal_run/evidence/performance-readiness-summary.json --max-age-seconds 86400
```

Frontend and trusted-browser commands:

```text
npm run typecheck
npm run lint
npm test -- --maxWorkers=2
npm run build
RALPH_EVIDENCE_DIR=<current-run-evidence> E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/performance-readiness.e2e.spec.ts
```

The browser command started both local servers, then the installed Chrome process aborted before
page creation in both repetitions. The exact infrastructure failure is retained in
`evidence/terminal-logs/browser-performance-readiness.log`; no screenshot was fabricated.
