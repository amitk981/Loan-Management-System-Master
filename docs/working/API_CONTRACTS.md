# API Contracts

Source contract baseline: `docs/source/api-contracts.md`.

This working file tracks implementation status and slice-level decisions. It must be updated whenever a slice changes frontend/backend assumptions.

## Dev Setup

Backend development uses environment-driven Django settings and a persistent local SQLite database at
`sfpcl_credit/db.sqlite3`. After dependencies are installed from `sfpcl_credit/requirements-dev.txt`,
run:

```bash
/Users/amitkallapa/Loan\ Management\ System\ Development/.ralph/venv/bin/python sfpcl_credit/manage.py migrate
/Users/amitkallapa/Loan\ Management\ System\ Development/.ralph/venv/bin/python sfpcl_credit/manage.py runserver 127.0.0.1:8000
cd sfpcl-lms && npm run dev
```

The React dev server origin `http://localhost:5173` is allowed by default for local CORS. Override
with `SFPCL_CORS_ORIGINS` as a comma-separated list when needed.

| Contract Area | Status | Related Screens | Source Contract | Notes |
|---|---|---|---|---|
| Backend health endpoints | Implemented in slice 002A; envelope unified in 002C2 | None | `technical-architecture.md` R1 health checks; standard response envelope from `api-contracts.md` §6.1 | `GET /api/v1/health/live/`, `/ready/`, and `/deep/` return `{ success, data, meta }` via the shared envelope helper; `meta` now includes `request_id`, `timestamp`, and `api_version: "v1"`. Ready/deep include database connectivity status. |
| Authentication and current user | Current-user implemented through slice 002D; frontend shell wired in 002E | Login, dashboards, portal auth | `docs/source/api-contracts.md`, `auth-permissions.md` | Implemented `POST /api/v1/auth/login/`, `/refresh/`, `/logout/`, and `GET /api/v1/auth/me/` with standard envelopes, active-user-only access, refresh rotation, session revocation, role/team token claims, effective role permissions, current action availability, and auth audit logs for login/refresh/logout. The staff React shell now logs in through `/auth/login/`, stores bearer/refresh tokens in local browser storage, loads `/auth/me/` before rendering protected staff navigation, clears local state on `TOKEN_EXPIRED`/`INVALID_TOKEN`, and posts the refresh token to `/auth/logout/`. Password reset, change password, and admin session controls remain future slices. |
| Early end-to-end tracer | Implemented in slice 002EX | Staff Tracer screen | `docs/source/api-contracts.md` §3-6; `docs/source/data-model.md` §26.1-26.2 | Thin dev proof only. Protected by session-bound bearer auth and explicit `tracer.lifecycle.run` permission. Endpoints: `POST /api/v1/tracer/members/`, `POST /api/v1/tracer/members/{member_id}/loan-applications/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/sanction/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/loan-account/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/disburse/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/repayments/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/close/`. Minimal models only; every transition writes `audit_logs` and `workflow_events`; invalid state transitions return `409 INVALID_STATE_TRANSITION`; missing/revoked auth returns the standard `401` envelope before domain writes. |
| Role/permission/team catalogue | Seeded in slice 002C; exposed for current user in 002D | None directly | `auth-permissions.md` §12-15, §38 | Canonical `Permission`, `Role`, `Team`, `RolePermission` catalogue seeded idempotently via `python manage.py seed_role_catalogue` (`sfpcl_credit/identity/catalogue.py`). `/api/v1/auth/me/` exposes the authenticated user's effective permission codes from this data. |
| Members and KYC | Draft from source | Members, borrower profile, application intake | `data-model.md`, `api-contracts.md` | Prototype uses mock data. |
| Loan applications | Draft from source | Applications, completeness | `api-contracts.md` | Needs real draft/submit/check endpoints. |
| Appraisal and loan limit | Draft from source | Appraisal workbench | `functional-spec.md`, `api-contracts.md` | Financial rules require tests before implementation. |
| Sanction and approvals | Draft from source | Sanction workbench | `auth-permissions.md`, `api-contracts.md` | Approval matrix is high-control. |
| Documentation and securities | Draft from source | Documentation hub | SOP PDFs, `api-contracts.md` | Must preserve disbursement blockers. |
| SAP and disbursement | Draft from source | Disbursement and CFC | SOP PDFs, `api-contracts.md` | Integration is manual/adapter-first for MVP. |
| Loan account, repayment, interest | Draft from source | Loan account, repayments, interest | `data-model.md`, `api-contracts.md` | Financial calculations are high risk. |
| Default, recovery, closure | Draft from source | Default, closure | `functional-spec.md`, `api-contracts.md` | Recovery approvals require audit evidence. |
| Compliance, registers, reports | Draft from source | Compliance, registers, reports | `api-contracts.md`, `auth-permissions.md` | Export masking must be tested. |

## Contract Rules
- Do not implement API-consuming frontend code without a matching contract entry.
- Do not treat mock data shape as the final backend shape without checking `docs/source/api-contracts.md` and `docs/source/data-model.md`.
- Mark uncertain contracts as Draft and record assumptions in `ASSUMPTIONS.md`.

## Implemented Auth Subset

Implemented endpoints:

| Endpoint | Request | Success Data | Key Rules |
|---|---|---|---|
| `POST /api/v1/auth/login/` | `email`, `password` | bearer `access_token`, `refresh_token`, `expires_in`, user profile with role/team codes | Only `active` users receive tokens; invalid credentials and non-active users receive `401 INVALID_CREDENTIALS`; successful and failed attempts are audited. |
| `POST /api/v1/auth/refresh/` | `refresh_token` | rotated bearer token payload | Refresh tokens are matched against `user_sessions.refresh_token_hash`; successful refresh rotates the token; replayed, revoked, expired, malformed, or status-invalid tokens return `401`. |
| `POST /api/v1/auth/logout/` | `refresh_token` | `{ "logged_out": true }` | Logout revokes the matching session with reason `logout`; the same refresh token cannot be used again; logout is audited. |
| `GET /api/v1/auth/me/` | `Authorization: Bearer <access_token>` | user identity (`user_id`, `full_name`, `email`, `mobile_number`, `status`), `roles`, `teams`, compatibility `role_codes`/`team_codes`, `permissions`, `available_actions` | Access token must be signed, unexpired, type `access`, and bound to an active `user_sessions` row for an active user. Missing token returns `401 AUTH_REQUIRED`; expired access tokens return `401 TOKEN_EXPIRED`; refresh/wrong-type, malformed, revoked-session, inactive-user, or unknown-session tokens return `401 INVALID_TOKEN`. |

Full 002D3 current-user example responses are saved in `.ralph/runs/2026-07-03_214932_normal_run/api-response-examples.md`.

## Early tracer API (002EX)

The 002EX tracer is a deliberately thin integration proof, not the final member/application/finance contract. It follows the source API rules for versioning, envelopes, explicit action endpoints, backend-enforced transitions, and audit/workflow observability.

Rules:
- All endpoints require `Authorization: Bearer <access_token>`.
- The access token must validate through the session-bound auth path used by `/auth/me/`; logout/revocation returns `401 INVALID_TOKEN`.
- The authenticated user's effective permission list must include `tracer.lifecycle.run`; otherwise the API returns `403 PERMISSION_DENIED`.
- Amounts must be positive decimal strings and are serialized as strings.
- Allowed status path: member `active`; application `draft -> sanctioned`; account `pending_disbursement -> active -> closed`; repayment `posted`.
- Every successful transition writes one `audit_logs` row whose action starts with `tracer.` and one `workflow_events` row.

Response examples for login, `/auth/me`, every tracer transition, and persistent SQLite counts are saved in `.ralph/runs/2026-07-03_234219_normal_run/api-response-samples.md`.

## Shared response envelope (002C2)

Health and auth endpoints use one production envelope implementation in `sfpcl_credit/api.py`
(`success_response`, `error_response`, `response_meta`). All success and error responses expose the
same `meta` keys — `request_id`, `timestamp`, `api_version` — matching `docs/source/api-contracts.md`
§6.1/§6.4. Auth token/session/audit behavior now lives behind explicit module functions in
`sfpcl_credit/identity/modules/` (`tokens.py`, `auth_service.py`); views only parse HTTP, call the
module, and translate known errors. `auth_service.validate_access_session` is the session-bound
validator used by `GET /api/v1/auth/me/`, resolving A-008 for current-user reads: a logged-out,
revoked, expired-session, or inactive-user access token cannot retrieve profile or permission data.

## Current user response (002D3)

`GET /api/v1/auth/me/`

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-me-001
```

Success data:

```json
{
  "user_id": "uuid",
  "full_name": "Credit Manager",
  "email": "credit.manager@sfpcl.example",
  "mobile_number": "+919999999999",
  "status": "active",
  "roles": [
    {
      "role_code": "credit_manager",
      "role_name": "Credit Manager"
    }
  ],
  "teams": [
    {
      "team_code": "credit_assessment",
      "team_name": "Credit Assessment"
    }
  ],
  "role_codes": ["credit_manager"],
  "team_codes": ["credit_assessment"],
  "permissions": ["approvals.case.create", "credit.appraisal.review"],
  "available_actions": ["approvals.case.create", "credit.appraisal.review"]
}
```

Rules:
- `permissions` are sorted, de-duplicated `RolePermission.permission.permission_code` values for the user's active primary role.
- `roles` contains the active primary role as `{ role_code, role_name }`; inactive primary roles return empty `roles`, empty `role_codes`, and empty `permissions`.
- `teams` contains active memberships to active teams as `{ team_code, team_name }`, sorted by `team_code`; inactive memberships and inactive teams are excluded.
- `role_codes` and `team_codes` are additive compatibility fields derived from `roles` and `teams`.
- Roles with no seeded permission links, including the A-007 `sales_team_user`, `it_head`, and `management_viewer` cases, return an empty permission list until source documents define grants.
- `available_actions` currently mirrors effective permission codes; later workflow/object-level slices may narrow it per resource while backend enforcement remains authoritative.
- 002D3 corrected the architecture-review gap by matching `docs/source/api-contracts.md` §11.4 before 002E frontend route-shell wiring consumes `/auth/me/`.
- 002E maps canonical backend permission codes to the existing prototype `can(...)` permission names only for currently implemented UI affordances. Unmapped backend codes do not grant frontend visibility; backend enforcement remains authoritative and future slices should extend the mapping when they add screens/actions.
