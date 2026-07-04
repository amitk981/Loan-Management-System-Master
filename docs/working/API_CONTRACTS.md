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

For local demonstrations, deterministic staff demo users are available only after the
guarded seed command is run with both local flags enabled:

```bash
SFPCL_DEBUG=true SFPCL_ALLOW_DEMO_SEED=true \
/Users/amitkallapa/Loan\ Management\ System\ Development/.ralph/venv/bin/python sfpcl_credit/manage.py seed_demo_users
```

The command calls the canonical role/team/permission catalogue seed first, updates only
`demo.*@sfpcl.example` users, and keeps E2E-only users separate. Predictable credentials
are local/dev only; do not use or promote them as production credentials. Demo login and
`/auth/me` examples are saved in `.ralph/runs/2026-07-04_184602_normal_run/api-response-examples.md`.

| Contract Area | Status | Related Screens | Source Contract | Notes |
|---|---|---|---|---|
| Backend health endpoints | Implemented in slice 002A; envelope unified in 002C2 | None | `technical-architecture.md` R1 health checks; standard response envelope from `api-contracts.md` §6.1 | `GET /api/v1/health/live/`, `/ready/`, and `/deep/` return `{ success, data, meta }` via the shared envelope helper; `meta` now includes `request_id`, `timestamp`, and `api_version: "v1"`. Ready/deep include database connectivity status. |
| Authentication and current user | Current-user implemented through slice 002D; frontend shell wired in 002E | Login, dashboards, portal auth | `docs/source/api-contracts.md`, `auth-permissions.md` | Implemented `POST /api/v1/auth/login/`, `/refresh/`, `/logout/`, and `GET /api/v1/auth/me/` with standard envelopes, active-user-only access, refresh rotation, session revocation, role/team token claims, effective role permissions, current action availability, and auth audit logs for login/refresh/logout. The staff React shell now logs in through `/auth/login/`, stores bearer/refresh tokens in local browser storage, loads `/auth/me/` before rendering protected staff navigation, clears local state on `TOKEN_EXPIRED`/`INVALID_TOKEN`, and posts the refresh token to `/auth/logout/`. Password reset, change password, and admin session controls remain future slices. |
| Admin user management | Implemented in slice 002G; action-specific permission gating added in 002G2 | Admin User Management | `api-contracts.md` §6-7, §11.4, §12; `auth-permissions.md` §12.1, §15.12, §19 | `GET /api/v1/admin/users/`, `GET /api/v1/admin/users/{user_id}/`, and assignment action endpoints bind existing `Role`/`Team` catalogue rows only. All routes require session-bound bearer auth. Since 002G2 each action requires the specific canonical user-admin permission (`auth-permissions.md` §12.1), not just any user-admin grant: list/detail read requires `users.user.read` OR any write user-admin permission (read fallback per A-015 because seeded `system_admin` lacks `users.user.read`); role assignment and team add/remove require `users.user.update`; suspending a user requires `users.user.disable`; restoring a user to active requires `users.user.update`. A partial-permission actor receives `403 PERMISSION_DENIED` with no `AuditLog` write and no session revocation. Order of checks: `401` (auth) → `403` (permission) → `400`/`404`. Successful role/team/status changes write `AuditLog`; suspending a user revokes active sessions; changing/suspending the last active `system_admin` is blocked per A-014. The frontend continues to map the write user-admin permissions to prototype `manage_users` for nav/route visibility. |
| Early end-to-end tracer | Implemented in slice 002EX | Staff Tracer screen | `docs/source/api-contracts.md` §3-6; `docs/source/data-model.md` §26.1-26.2 | Thin dev proof only. Protected by session-bound bearer auth and explicit `tracer.lifecycle.run` permission. Endpoints: `POST /api/v1/tracer/members/`, `POST /api/v1/tracer/members/{member_id}/loan-applications/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/sanction/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/loan-account/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/disburse/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/repayments/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/close/`. Minimal models only; every transition writes `audit_logs` and `workflow_events`; invalid state transitions return `409 INVALID_STATE_TRANSITION`; missing/revoked auth returns the standard `401` envelope before domain writes. |
| API contract test harness | Implemented in slice 002J | None | `api-contracts.md` §6.1-6.4, §7.1-7.3, §44 | Test-only assertions live in `sfpcl_credit/tests/api_contracts.py`. Future endpoint slices should use them to prove standard success envelopes, error envelopes, top-level list pagination, and target §44 `available_actions` item shapes without importing test utilities from production code. The harness regression tests cover `/auth/me/`, admin users pagination, `401 AUTH_REQUIRED`, revoked-session `401 INVALID_TOKEN`, `403 PERMISSION_DENIED`, partial-admin write denial, and tracer `409 INVALID_STATE_TRANSITION`. A-016 records that current `/auth/me/` still returns flat permission-code strings for `available_actions`; the object shape is asserted against an internal sample for future detail endpoints. |
| Local demo staff seed | Implemented in slice 002K; corrected in 002K2 | Login, dashboard smoke, admin/tracer permission smoke | `implementation-roadmap.md` §10, §20-22; `technical-architecture.md` §8-12, §17-18; `auth-permissions.md`; `api-contracts.md` §11-12, §43-44 | `python manage.py seed_demo_users` is a guarded local/dev seed path. It refuses unless `SFPCL_DEBUG=true` and `SFPCL_ALLOW_DEMO_SEED=true`, calls `seed_catalogue()`, creates or updates deterministic `demo.*@sfpcl.example` staff users with active primary roles and memberships, and does not alter `e2e.*` users. Demo users authenticate through the real `/auth/login/` and `/auth/me/` endpoints; there is no demo auth bypass. The zero-permission user returns `permissions: []` and `available_actions: []`; the tracer-only user uses the guarded local/dev-only `local_demo_tracer_user` role and returns only `tracer.lifecycle.run`; the shared source-catalogue `sales_team_user` role remains permission-neutral until source documents define grants; system admin preserves canonical action-specific user-admin permissions without broad `manage_users` aliases. |
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

## Admin user management API (002G)

Implemented endpoints:

| Endpoint | Request | Success Data | Key Rules |
|---|---|---|---|
| `GET /api/v1/admin/users/?page=1&page_size=20` | `Authorization: Bearer <access_token>` | List envelope with `data[]` and top-level `pagination` | Requires session-bound active access token and canonical user-admin permission. Items use the `/auth/me/` role/team shape: `roles[{role_code, role_name}]`, `teams[{team_code, team_name}]`. |
| `GET /api/v1/admin/users/{user_id}/` | Bearer access token | One user item | Same permission and serialization shape as list. |
| `POST /api/v1/admin/users/{user_id}/roles/` | `{ "role_code": "accounts_head" }` | Updated user item | `role_code` must reference an existing active `Role`; this changes the user's required `primary_role`; writes `admin.user.role_assigned`. |
| `POST /api/v1/admin/users/{user_id}/teams/` | `{ "team_code": "credit_assessment" }` | Updated user item | `team_code` must reference an existing active `Team`; creates or reactivates a `UserTeamMembership`; writes `admin.user.team_added` when a membership changes. |
| `DELETE /api/v1/admin/users/{user_id}/teams/{team_code}/` | Bearer access token | Updated user item | Existing active membership is marked inactive; writes `admin.user.team_removed`. |
| `PATCH /api/v1/admin/users/{user_id}/status/` | `{ "status": "active" }` or `{ "status": "suspended" }` | Updated user item | Status is limited to `active`/`suspended`; setting `suspended` revokes active `UserSession` rows with reason `admin_status_suspended`; writes `admin.user.status_changed`. |

Rules:
- Missing bearer token returns `401 AUTH_REQUIRED`; malformed or revoked session-bound access tokens return the existing `401 INVALID_TOKEN`/`TOKEN_EXPIRED` envelope.
- Authenticated users without canonical user-admin permission return `403 PERMISSION_DENIED`.
- Unknown role/team codes and unsupported statuses return `400 VALIDATION_ERROR` with `field_errors`.
- A-014 lock-out guard: any role or status change that would leave zero active users whose primary role is `system_admin` returns `400 VALIDATION_ERROR`.
- Role-permission catalogue entries are not edited by this API; this slice binds existing `Role`/`Team` rows only.
- Frontend visibility is still advisory: React maps `users.user.create`, `users.user.update`, and `users.user.disable` to prototype `manage_users`; Django remains authoritative.

Response examples for list, detail, assignment, `401`, `403`, validation failure, and last-admin lock-out are saved in `.ralph/runs/2026-07-04_131908_normal_run/api-response-examples.md`.

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
- Roles with no seeded production permission links, including the A-007 `sales_team_user`, `it_head`, and `management_viewer` cases, return an empty permission list until source documents define grants. The guarded local/demo `seed_demo_users` command keeps those shared source roles neutral; its narrow A-011 exception creates the local/dev-only `local_demo_tracer_user` role and grants that role exactly `tracer.lifecycle.run` for `demo.tracer@sfpcl.example`.
- `available_actions` currently mirrors effective permission codes; later workflow/object-level slices may narrow it per resource while backend enforcement remains authoritative.
- 002D3 corrected the architecture-review gap by matching `docs/source/api-contracts.md` §11.4 before 002E frontend route-shell wiring consumes `/auth/me/`.
- 002E maps canonical backend permission codes to the existing prototype `can(...)` permission names only for currently implemented UI affordances. Unmapped backend codes do not grant frontend visibility; backend enforcement remains authoritative and future slices should extend the mapping when they add screens/actions.
