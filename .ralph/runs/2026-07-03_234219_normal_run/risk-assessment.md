# Risk Assessment

Risk level: High

- Selected slice: 002EX-early-end-to-end-tracer-bullet
- Mode: normal_run
- Manual review required: recommended because this adds schema, authenticated APIs, workflow transitions, audit events, and frontend route/action visibility.

## Controls Implemented
- Session-bound bearer auth is required for every tracer endpoint via the same active-session path as `/api/v1/auth/me/`.
- Explicit `tracer.lifecycle.run` permission is required; authenticated users without it receive `403 PERMISSION_DENIED` before domain writes.
- Missing bearer tokens return standard `401 AUTH_REQUIRED`; revoked/logout access sessions return `401 INVALID_TOKEN` before domain writes.
- Amounts must be positive decimals.
- Status transitions are guarded in the service layer and invalid ordering returns `409 INVALID_STATE_TRANSITION`.
- Every successful transition writes one `audit_logs` row and one `workflow_events` row.
- Frontend route/action visibility maps only `tracer.lifecycle.run` to `run_tracer`; zero-permission/unmapped roles keep the neutral 002E2 behavior.

## Deferred Controls
- Real member/KYC/eligibility/appraisal/sanction/documentation/SAP/disbursement/repayment/interest/closure business rules are intentionally deferred to later epics.
- Idempotency-key handling for financial actions is deferred; current duplicate prevention is via status guards only.
- Object-level permission checks are deferred to 002I and later real module slices.
- Browser screenshot evidence is deferred to 002EY because this sandbox blocked local server binding with `EPERM`.

## Evidence
- Backend red/green: `evidence/terminal-logs/backend-red-tracer-api.log`, `backend-green-tracer-api.log`, `backend-green-tracer-api-expanded.log`.
- Frontend red/green: `evidence/terminal-logs/frontend-red-auth-session.log`, `frontend-green-auth-session.log`.
- API samples and persistent SQLite smoke: `api-response-samples.md`.
- Full gates: `backend-test-results.md`, `backend-check-results.md`, `backend-migrations-results.md`, `backend-coverage-results.md`, `test-results.md`, `typecheck-results.md`, `build-results.md`.
