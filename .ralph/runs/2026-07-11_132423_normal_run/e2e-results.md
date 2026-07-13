# e2e Results

Command: rg -q "git rev-parse .*--git-common-dir" e2e/README.md || { echo "FAIL: README E2E command does not resolve the shared venv through Git's common directory."; exit 1; }; rg -q "timezoneId: 'Asia/Kolkata'" playwright.config.ts || { echo "FAIL: Playwright does not pin the dashboard baseline timezone to Asia/Kolkata."; exit 1; }; E2E_DJANGO_PYTHON="/Users/amitkallapa/LMS/.ralph/venv/bin/python" npm run e2e -- e2e/tracer.e2e.spec.ts e2e/auth-negative.e2e.spec.ts --grep "zero-permission staff|logs in, walks" && E2E_DJANGO_PYTHON="/Users/amitkallapa/LMS/.ralph/venv/bin/python" npm run e2e -- e2e/tracer.e2e.spec.ts e2e/auth-negative.e2e.spec.ts --grep "zero-permission staff|logs in, walks"

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 e2e
> playwright test e2e/tracer.e2e.spec.ts e2e/auth-negative.e2e.spec.ts --grep zero-permission staff|logs in, walks

[2m[WebServer] [22m[11/Jul/2026 08:01:18] "GET /api/v1/health/ready/ HTTP/1.1" 200 202
[2m[WebServer] [22m[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m
[2m[WebServer] [22m(node:54328) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
[2m[WebServer] [22m(Use `node --trace-warnings ...` to show where the warning was created)

Running 2 tests using 1 worker

[2m[WebServer] [22m[11/Jul/2026 08:01:21] "OPTIONS /api/v1/auth/login/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:21] "POST /api/v1/auth/login/ HTTP/1.1" 200 1255
[2m[WebServer] [22m[11/Jul/2026 08:01:21] "OPTIONS /api/v1/auth/me/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:21] "GET /api/v1/auth/me/ HTTP/1.1" 200 454
[2m[WebServer] [22m[11/Jul/2026 08:01:21] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:21] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 08:01:21] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 08:01:21] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
  ✓  1 [chromium] › auth-negative.e2e.spec.ts:53:7 › auth negatives and restricted staff UI › zero-permission staff sees the neutral dashboard, no tracer nav, no settings (3.2s)
[2m[WebServer] [22m[11/Jul/2026 08:01:23] "OPTIONS /api/v1/auth/login/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:23] "POST /api/v1/auth/login/ HTTP/1.1" 200 1258
[2m[WebServer] [22m[11/Jul/2026 08:01:23] "OPTIONS /api/v1/auth/me/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:23] "GET /api/v1/auth/me/ HTTP/1.1" 200 506
[2m[WebServer] [22m[11/Jul/2026 08:01:23] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:23] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 08:01:23] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 08:01:23] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "OPTIONS /api/v1/tracer/members/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "POST /api/v1/tracer/members/ HTTP/1.1" 200 255
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "OPTIONS /api/v1/tracer/members/26612f95-d50b-4fe1-80fb-5f1021bc20a5/loan-applications/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "POST /api/v1/tracer/members/26612f95-d50b-4fe1-80fb-5f1021bc20a5/loan-applications/ HTTP/1.1" 200 307
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "OPTIONS /api/v1/tracer/loan-applications/f894dc5e-142f-4413-b6ca-d9a5188b1b02/sanction/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "POST /api/v1/tracer/loan-applications/f894dc5e-142f-4413-b6ca-d9a5188b1b02/sanction/ HTTP/1.1" 200 352
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "OPTIONS /api/v1/tracer/loan-applications/f894dc5e-142f-4413-b6ca-d9a5188b1b02/loan-account/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "POST /api/v1/tracer/loan-applications/f894dc5e-142f-4413-b6ca-d9a5188b1b02/loan-account/ HTTP/1.1" 200 381
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "OPTIONS /api/v1/tracer/loan-accounts/e656ec48-cbea-4a24-bbc4-bae10c598117/disburse/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "POST /api/v1/tracer/loan-accounts/e656ec48-cbea-4a24-bbc4-bae10c598117/disburse/ HTTP/1.1" 200 359
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "OPTIONS /api/v1/tracer/loan-accounts/e656ec48-cbea-4a24-bbc4-bae10c598117/repayments/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "POST /api/v1/tracer/loan-accounts/e656ec48-cbea-4a24-bbc4-bae10c598117/repayments/ HTTP/1.1" 200 307
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "OPTIONS /api/v1/tracer/loan-accounts/e656ec48-cbea-4a24-bbc4-bae10c598117/close/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:26] "POST /api/v1/tracer/loan-accounts/e656ec48-cbea-4a24-bbc4-bae10c598117/close/ HTTP/1.1" 200 345
  ✓  2 [chromium] › tracer.e2e.spec.ts:14:7 › staff tracer lifecycle (production auth path) › logs in, walks the tracer to a closed loan, with dashboard + tracer baselines (4.0s)

  2 passed (11.4s)

> sfpcl-lms@1.0.0 e2e
> playwright test e2e/tracer.e2e.spec.ts e2e/auth-negative.e2e.spec.ts --grep zero-permission staff|logs in, walks

[2m[WebServer] [22m[11/Jul/2026 08:01:30] "GET /api/v1/health/ready/ HTTP/1.1" 200 202
[2m[WebServer] [22m[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m
[2m[WebServer] [22m(node:54398) Warning: The 'NO_COLOR' env is ignored due to the 'FORCE_COLOR' env being set.
[2m[WebServer] [22m(Use `node --trace-warnings ...` to show where the warning was created)

Running 2 tests using 1 worker

[2m[WebServer] [22m[11/Jul/2026 08:01:33] "OPTIONS /api/v1/auth/login/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:33] "POST /api/v1/auth/login/ HTTP/1.1" 200 1255
[2m[WebServer] [22m[11/Jul/2026 08:01:33] "OPTIONS /api/v1/auth/me/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:33] "GET /api/v1/auth/me/ HTTP/1.1" 200 454
[2m[WebServer] [22m[11/Jul/2026 08:01:33] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:33] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 08:01:33] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 08:01:33] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
  ✓  1 [chromium] › auth-negative.e2e.spec.ts:53:7 › auth negatives and restricted staff UI › zero-permission staff sees the neutral dashboard, no tracer nav, no settings (2.7s)
[2m[WebServer] [22m[11/Jul/2026 08:01:35] "OPTIONS /api/v1/auth/login/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:35] "POST /api/v1/auth/login/ HTTP/1.1" 200 1258
[2m[WebServer] [22m[11/Jul/2026 08:01:35] "OPTIONS /api/v1/auth/me/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:35] "GET /api/v1/auth/me/ HTTP/1.1" 200 506
[2m[WebServer] [22m[11/Jul/2026 08:01:35] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:35] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 08:01:35] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 08:01:35] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "OPTIONS /api/v1/tracer/members/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "POST /api/v1/tracer/members/ HTTP/1.1" 200 255
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "OPTIONS /api/v1/tracer/members/c3c5de70-1bf6-4be9-b234-3d0c384f81a6/loan-applications/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "POST /api/v1/tracer/members/c3c5de70-1bf6-4be9-b234-3d0c384f81a6/loan-applications/ HTTP/1.1" 200 307
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "OPTIONS /api/v1/tracer/loan-applications/8b831922-aa20-48d9-890d-89ba54f02c3c/sanction/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "POST /api/v1/tracer/loan-applications/8b831922-aa20-48d9-890d-89ba54f02c3c/sanction/ HTTP/1.1" 200 352
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "OPTIONS /api/v1/tracer/loan-applications/8b831922-aa20-48d9-890d-89ba54f02c3c/loan-account/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "POST /api/v1/tracer/loan-applications/8b831922-aa20-48d9-890d-89ba54f02c3c/loan-account/ HTTP/1.1" 200 381
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "OPTIONS /api/v1/tracer/loan-accounts/107bba8a-2f73-44dd-bf8b-a0ea4663b487/disburse/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "POST /api/v1/tracer/loan-accounts/107bba8a-2f73-44dd-bf8b-a0ea4663b487/disburse/ HTTP/1.1" 200 359
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "OPTIONS /api/v1/tracer/loan-accounts/107bba8a-2f73-44dd-bf8b-a0ea4663b487/repayments/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "POST /api/v1/tracer/loan-accounts/107bba8a-2f73-44dd-bf8b-a0ea4663b487/repayments/ HTTP/1.1" 200 307
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "OPTIONS /api/v1/tracer/loan-accounts/107bba8a-2f73-44dd-bf8b-a0ea4663b487/close/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 08:01:37] "POST /api/v1/tracer/loan-accounts/107bba8a-2f73-44dd-bf8b-a0ea4663b487/close/ HTTP/1.1" 200 345
  ✓  2 [chromium] › tracer.e2e.spec.ts:14:7 › staff tracer lifecycle (production auth path) › logs in, walks the tracer to a closed loan, with dashboard + tracer baselines (3.6s)

  2 passed (10.4s)
