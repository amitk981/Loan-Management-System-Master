# Screenshot Results

Frontend was touched, so Playwright visual evidence was attempted with:

`E2E_DJANGO_PYTHON="/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python" npm run e2e -- auth-negative.e2e.spec.ts`

Result: blocked by the sandbox before the browser assertions could run.

The Playwright backend web server failed to bind localhost:

`Error: [Errno 1] Operation not permitted`

Evidence log:

`.ralph/runs/2026-07-04_075626_normal_run/evidence/terminal-logs/frontend-e2e-auth-negative.log`

Visual behavior is still covered by the extended Playwright spec in `sfpcl-lms/e2e/auth-negative.e2e.spec.ts`; it should run in the orchestrator or any environment that allows localhost binding. Non-browser gates passed: vitest, typecheck, and build.
