# Review Packet — 003G Dashboard Task Summary API

## Traceability
- Source extract says `api-contracts.md` §43.1 defines `GET /api/v1/dashboard/` with
  `data.role_context`, `data.cards[]` (`code`, `label`, `count`, `link`), and `data.tasks[]`
  (`task_type`, `entity_id`, `title`, `due_at`).
  Code implements this in `sfpcl_credit/dashboard/services.py` and
  `sfpcl_credit/dashboard/views.py`; tests verify the envelope and card/task fields in
  `sfpcl_credit/tests/test_dashboard_api.py`.
- Source extract says functional-spec §12.2-§12.6 names dashboard widgets for Credit Manager,
  sanction committee, compliance, treasury/finance, and management.
  Code returns source-named zero-count card shells for those five contexts; tests cover each context.
- Source extract says the current backend has no implemented application, appraisal, sanction,
  compliance, treasury, DPD, reminder, default, or management-report tables/calculations.
  Code returns zero counts and `tasks: []`; no model or migration was added.
- Source extract says `auth-permissions.md` §19.1 defines `management_readonly` as a
  dashboard/summary access scope, while no exact `dashboard.read` code exists.
  Code requires `management_readonly`, seeds it in the catalogue, and records A-023.
- Slice says dashboard reads should not create audit rows unless a source-backed rule requires it.
  Tests assert no `AuditLog` row is created by a dashboard read.

## Behavioral Coverage
- Authorized Credit Manager receives a standard success envelope and zero-count source-named cards.
- Sanction, compliance, treasury, and management role contexts return their shell card sets.
- Missing bearer token returns `401 AUTH_REQUIRED`.
- Revoked bearer token returns `401 INVALID_TOKEN`.
- Authenticated user without `management_readonly` returns `403 PERMISSION_DENIED`.
- Unknown query parameter returns `400 VALIDATION_ERROR`.
- Read-only access writes no audit row.
- Response does not include borrower/member/loan-account-sensitive values.
- Catalogue seed includes `management_readonly` for dashboard role contexts.
- Demo zero-permission user remains neutral by moving to `it_head`.

## Gates
- Backend check: pass.
- Backend tests: 170 tests pass.
- Backend migrations check: pass, no changes detected.
- Backend coverage: 96%, above 85% floor.
- Frontend typecheck: pass.
- Frontend lint: pass.
- Frontend tests: 26 tests pass.
- Frontend build: pass.

## Evidence
- Red tests:
  - `evidence/terminal-logs/red-dashboard-api-tests.log`
  - `evidence/terminal-logs/red-dashboard-catalogue-test.log`
- Green focused tests:
  - `evidence/terminal-logs/green-dashboard-api-tests.log`
  - `evidence/terminal-logs/green-dashboard-catalogue-test.log`
  - `evidence/terminal-logs/green-dashboard-seed-regression-tests.log`
- Full gates:
  - `evidence/terminal-logs/backend-check.log`
  - `evidence/terminal-logs/backend-tests.log`
  - `evidence/terminal-logs/backend-makemigrations-check.log`
  - `evidence/terminal-logs/backend-coverage.log`
  - `evidence/terminal-logs/frontend-typecheck.log`
  - `evidence/terminal-logs/frontend-lint.log`
  - `evidence/terminal-logs/frontend-tests.log`
  - `evidence/terminal-logs/frontend-build.log`
- API example:
  - `evidence/api-responses/dashboard-api-response.txt`
