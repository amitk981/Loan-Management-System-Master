# Execution Plan

Selected slice: 002J-api-contract-test-harness

## Scope
- Add a test-only API contract assertion harness under `sfpcl_credit/tests/`.
- Use existing endpoints as contract fixtures: `/api/v1/auth/me/`, `/api/v1/admin/users/`, admin user-management denied writes, and tracer invalid state transitions.
- Do not add public endpoints, migrations, production imports of test utilities, or frontend changes.

## Source Trace
- `docs/source/api-contracts.md` §6.1 requires `success`, `data`, and `meta.request_id/timestamp/api_version`.
- `docs/source/api-contracts.md` §6.2 requires list `pagination` fields.
- `docs/source/api-contracts.md` §6.4 and §7 require standard error code/message shape, including `AUTH_REQUIRED`, `INVALID_TOKEN`, `PERMISSION_DENIED`, and `INVALID_STATE_TRANSITION`.
- `docs/source/api-contracts.md` §44 defines the target object item shape for `available_actions`; current `/auth/me/` intentionally returns a flat permission-code list per the slice.

## TDD Plan
1. RED: add a helper test showing an incomplete success envelope fails with a clear missing-field assertion.
2. GREEN: implement minimal test-only assertions for success envelope, error envelope, pagination, and `available_actions` item shape.
3. Add one regression test at a time against current endpoints:
   - `/api/v1/auth/me/` success envelope.
   - unauthenticated protected endpoint `401 AUTH_REQUIRED`.
   - revoked access token protected endpoint `401 INVALID_TOKEN`.
   - admin users no-permission `403 PERMISSION_DENIED`.
   - partial admin permission denied write `403 PERMISSION_DENIED`.
   - tracer invalid transition `409 INVALID_STATE_TRANSITION`.
   - admin users list pagination shape.
   - internal target-contract `available_actions` sample.
4. Save red/green logs under `.ralph/runs/2026-07-04_183146_normal_run/evidence/terminal-logs/`.
5. Run backend gates with `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`, then frontend gates because Ralph validation requires them.

## Expected Files
- `sfpcl_credit/tests/api_contracts.py`
- `sfpcl_credit/tests/test_api_contract_harness.py`
- Existing backend tests only if needed to reuse fixtures cleanly.
- Ralph artifacts and docs updates required by the runbook.
