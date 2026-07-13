# e2e Results

Command: rg -q "git rev-parse .*--git-common-dir" e2e/README.md || { echo "FAIL: README E2E command does not resolve the shared venv through Git's common directory."; exit 1; }; rg -q "timezoneId: 'Asia/Kolkata'" playwright.config.ts || { echo "FAIL: Playwright does not pin the dashboard baseline timezone to Asia/Kolkata."; exit 1; }; E2E_DJANGO_PYTHON="/Users/amitkallapa/LMS/.ralph/venv/bin/python" npm run e2e -- e2e/tracer.e2e.spec.ts e2e/auth-negative.e2e.spec.ts --grep "zero-permission staff|logs in, walks" && E2E_DJANGO_PYTHON="/Users/amitkallapa/LMS/.ralph/venv/bin/python" npm run e2e -- e2e/tracer.e2e.spec.ts e2e/auth-negative.e2e.spec.ts --grep "zero-permission staff|logs in, walks"

Node PATH pin: /Users/amitkallapa/.nvm/versions/node/v18.20.4/bin


> sfpcl-lms@1.0.0 e2e
> playwright test e2e/tracer.e2e.spec.ts e2e/auth-negative.e2e.spec.ts --grep zero-permission staff|logs in, walks

[2m[WebServer] [22m[11/Jul/2026 14:30:31] "GET /api/v1/health/ready/ HTTP/1.1" 200 202
[2m[WebServer] [22m[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

Running 2 tests using 1 worker

[2m[WebServer] [22m[11/Jul/2026 14:30:34] "OPTIONS /api/v1/auth/login/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:34] "POST /api/v1/auth/login/ HTTP/1.1" 200 1255
[2m[WebServer] [22m[11/Jul/2026 14:30:34] "OPTIONS /api/v1/auth/me/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:34] "GET /api/v1/auth/me/ HTTP/1.1" 200 454
[2m[WebServer] [22m[11/Jul/2026 14:30:34] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:34] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 14:30:34] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 14:30:34] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
  ✓  1 [chromium] › auth-negative.e2e.spec.ts:53:7 › auth negatives and restricted staff UI › zero-permission staff sees the neutral dashboard, no tracer nav, no settings (2.2s)
[2m[WebServer] [22m[11/Jul/2026 14:30:35] "OPTIONS /api/v1/auth/login/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "POST /api/v1/auth/login/ HTTP/1.1" 200 1258
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/auth/me/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "GET /api/v1/auth/me/ HTTP/1.1" 200 506
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/tracer/members/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "POST /api/v1/tracer/members/ HTTP/1.1" 200 255
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/tracer/members/8ff963f0-ec95-455f-818a-e8fb833f9415/loan-applications/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "POST /api/v1/tracer/members/8ff963f0-ec95-455f-818a-e8fb833f9415/loan-applications/ HTTP/1.1" 200 307
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/tracer/loan-applications/495968c2-aa7b-401e-85f2-a72a57a5ae70/sanction/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "POST /api/v1/tracer/loan-applications/495968c2-aa7b-401e-85f2-a72a57a5ae70/sanction/ HTTP/1.1" 200 352
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/tracer/loan-applications/495968c2-aa7b-401e-85f2-a72a57a5ae70/loan-account/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "POST /api/v1/tracer/loan-applications/495968c2-aa7b-401e-85f2-a72a57a5ae70/loan-account/ HTTP/1.1" 200 381
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/tracer/loan-accounts/25386fd3-9b38-4cf1-9dfb-3a871b6b3015/disburse/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "POST /api/v1/tracer/loan-accounts/25386fd3-9b38-4cf1-9dfb-3a871b6b3015/disburse/ HTTP/1.1" 200 359
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/tracer/loan-accounts/25386fd3-9b38-4cf1-9dfb-3a871b6b3015/repayments/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "POST /api/v1/tracer/loan-accounts/25386fd3-9b38-4cf1-9dfb-3a871b6b3015/repayments/ HTTP/1.1" 200 307
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "OPTIONS /api/v1/tracer/loan-accounts/25386fd3-9b38-4cf1-9dfb-3a871b6b3015/close/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:36] "POST /api/v1/tracer/loan-accounts/25386fd3-9b38-4cf1-9dfb-3a871b6b3015/close/ HTTP/1.1" 200 345
  ✓  2 [chromium] › tracer.e2e.spec.ts:14:7 › staff tracer lifecycle (production auth path) › logs in, walks the tracer to a closed loan, with dashboard + tracer baselines (1.4s)

  2 passed (8.0s)

> sfpcl-lms@1.0.0 e2e
> playwright test e2e/tracer.e2e.spec.ts e2e/auth-negative.e2e.spec.ts --grep zero-permission staff|logs in, walks

[2m[WebServer] [22m[11/Jul/2026 14:30:40] "GET /api/v1/health/ready/ HTTP/1.1" 200 202
[2m[WebServer] [22m[33mThe CJS build of Vite's Node API is deprecated. See https://vite.dev/guide/troubleshooting.html#vite-cjs-node-api-deprecated for more details.[39m

Running 2 tests using 1 worker

[2m[WebServer] [22m[11/Jul/2026 14:30:42] "OPTIONS /api/v1/auth/login/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:42] "POST /api/v1/auth/login/ HTTP/1.1" 200 1255
[2m[WebServer] [22m[11/Jul/2026 14:30:42] "OPTIONS /api/v1/auth/me/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:42] "GET /api/v1/auth/me/ HTTP/1.1" 200 454
[2m[WebServer] [22m[11/Jul/2026 14:30:42] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:42] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 14:30:42] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 14:30:42] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
  ✓  1 [chromium] › auth-negative.e2e.spec.ts:53:7 › auth negatives and restricted staff UI › zero-permission staff sees the neutral dashboard, no tracer nav, no settings (2.0s)
[2m[WebServer] [22m[11/Jul/2026 14:30:43] "OPTIONS /api/v1/auth/login/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:43] "POST /api/v1/auth/login/ HTTP/1.1" 200 1258
[2m[WebServer] [22m[11/Jul/2026 14:30:43] "OPTIONS /api/v1/auth/me/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:43] "GET /api/v1/auth/me/ HTTP/1.1" 200 506
[2m[WebServer] [22m[11/Jul/2026 14:30:43] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:43] "OPTIONS /api/v1/dashboard/ HTTP/1.1" 200 0
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 14:30:43] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22mForbidden: /api/v1/dashboard/
[2m[WebServer] [22m[11/Jul/2026 14:30:43] "GET /api/v1/dashboard/ HTTP/1.1" 403 250
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "OPTIONS /api/v1/tracer/members/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "POST /api/v1/tracer/members/ HTTP/1.1" 200 255
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "OPTIONS /api/v1/tracer/members/6f653c2d-2de3-4446-bb28-15547572eacb/loan-applications/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "POST /api/v1/tracer/members/6f653c2d-2de3-4446-bb28-15547572eacb/loan-applications/ HTTP/1.1" 200 307
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "OPTIONS /api/v1/tracer/loan-applications/f4ce34d0-426e-45ed-9e08-d2a989429696/sanction/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "POST /api/v1/tracer/loan-applications/f4ce34d0-426e-45ed-9e08-d2a989429696/sanction/ HTTP/1.1" 200 352
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "OPTIONS /api/v1/tracer/loan-applications/f4ce34d0-426e-45ed-9e08-d2a989429696/loan-account/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "POST /api/v1/tracer/loan-applications/f4ce34d0-426e-45ed-9e08-d2a989429696/loan-account/ HTTP/1.1" 200 381
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "OPTIONS /api/v1/tracer/loan-accounts/a40aa7a7-0fe5-458c-9390-1ebe16b5dabf/disburse/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "POST /api/v1/tracer/loan-accounts/a40aa7a7-0fe5-458c-9390-1ebe16b5dabf/disburse/ HTTP/1.1" 200 359
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "OPTIONS /api/v1/tracer/loan-accounts/a40aa7a7-0fe5-458c-9390-1ebe16b5dabf/repayments/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "POST /api/v1/tracer/loan-accounts/a40aa7a7-0fe5-458c-9390-1ebe16b5dabf/repayments/ HTTP/1.1" 200 307
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "OPTIONS /api/v1/tracer/loan-accounts/a40aa7a7-0fe5-458c-9390-1ebe16b5dabf/close/ HTTP/1.1" 200 0
[2m[WebServer] [22m[11/Jul/2026 14:30:44] "POST /api/v1/tracer/loan-accounts/a40aa7a7-0fe5-458c-9390-1ebe16b5dabf/close/ HTTP/1.1" 200 345
  ✓  2 [chromium] › tracer.e2e.spec.ts:14:7 › staff tracer lifecycle (production auth path) › logs in, walks the tracer to a closed loan, with dashboard + tracer baselines (1.4s)

  2 passed (7.4s)
