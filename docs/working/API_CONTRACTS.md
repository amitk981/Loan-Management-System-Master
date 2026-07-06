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
| Documentation and securities | Document-file upload foundation implemented in 003C; secure download descriptor implemented in 003D; broader loan document workflows remain draft | Documentation hub | SOP PDFs, `api-contracts.md` §26; `data-model.md` §16.1 | `POST /api/v1/document-files/` stores file bytes outside the database through the local adapter and stores metadata in `document_files`. `GET /api/v1/document-files/{document_id}/download/` returns a permissioned, time-limited local download descriptor and writes document-access audit. Checklist, template, signature, stamp, notarisation, and loan-document flows remain future slices. |
| Versioned configuration | Loan-policy shell implemented in 003E; calculations and broader config types remain draft | Settings/config shell | `api-contracts.md` §41.1, §42.3; `data-model.md` §25.1, §26.3; `functional-spec.md` M01-FR-001/M01-FR-002/M01-FR-015 | `loan_policy_configs` and `version_histories` are persisted. `GET/POST/PATCH/activate` loan-policy APIs and filtered version-history reads are protected, audited where mutating, and versioned on activation. M01-FR-003 through M01-FR-014 calculations/rules are explicitly deferred; only neutral source model fields are stored. |
| Communication templates | Content-template metadata shell implemented in 003F; send/list communications remain draft | None directly | `api-contracts.md` §39.1; `data-model.md` §24.1; `functional-spec.md` M16-FR-004/M18-FR-006 | `content_templates` is persisted. `GET/POST/PATCH /api/v1/content-templates/` is protected by narrow A-022 content-template permissions, returns metadata-only fields, validates dates/status/variables, and writes audit rows for create/update. Communication sending, delivery status, manual call logging, borrower/loan communication attachment, and notification center UI remain future slices. |
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
- Roles with no seeded production permission links, including the A-007 `sales_team_user` and `it_head` cases, return an empty permission list until source documents define grants. A-023 gives `management_viewer` the source-backed `management_readonly` dashboard scope. The guarded local/demo `seed_demo_users` command keeps a neutral `demo.zero@sfpcl.example` user on `it_head`; its narrow A-011 exception creates the local/dev-only `local_demo_tracer_user` role and grants that role exactly `tracer.lifecycle.run` for `demo.tracer@sfpcl.example`.
- `available_actions` currently mirrors effective permission codes; later workflow/object-level slices may narrow it per resource while backend enforcement remains authoritative.
- 002D3 corrected the architecture-review gap by matching `docs/source/api-contracts.md` §11.4 before 002E frontend route-shell wiring consumes `/auth/me/`.
- 002E maps canonical backend permission codes to the existing prototype `can(...)` permission names only for currently implemented UI affordances. Unmapped backend codes do not grant frontend visibility; backend enforcement remains authoritative and future slices should extend the mapping when they add screens/actions.

## Audit log read (003A)

`GET /api/v1/audit-logs/`

Read-only, protected endpoint over the existing append-only `identity.AuditLog` model
(`docs/source/api-contracts.md` §42.1). Serialization, filtering, and pagination live behind
`sfpcl_credit/identity/modules/audit_log.py`; `sfpcl_credit/identity/audit_views.py` is a thin
`require_GET` view. No update/delete endpoint exists; the read creates no audit row.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-audit-list
```

Query parameters (all optional):
- `entity_type` — free-text exact match on `AuditLog.entity_type`.
- `entity_id` — UUID; invalid UUID returns `400 VALIDATION_ERROR` with `field_errors.entity_id`.
- `actor_user_id` — UUID; invalid UUID returns `400 VALIDATION_ERROR` with `field_errors.actor_user_id`.
- `page`, `page_size` — standard top-level pagination (default `page_size` 20, max 100).
- Any other query parameter returns `400 VALIDATION_ERROR` with the unknown key in `field_errors`.

Success (top-level `pagination` envelope, newest-first by `created_at`):

```json
{
  "success": true,
  "data": [
    {
      "audit_log_id": "uuid",
      "actor": { "user_id": "uuid", "full_name": "Ivy Auditor" },
      "actor_type": "user",
      "action": "loan_application.submitted",
      "entity_type": "loan_application",
      "entity_id": "uuid",
      "old_value": { "application_status": "draft" },
      "new_value": { "application_status": "submitted" },
      "ip_address": "10.0.0.1",
      "created_at": "2026-06-22T10:30:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_count": 1, "total_pages": 1, "has_next": false, "has_previous": false },
  "meta": { "request_id": "req-audit-list", "timestamp": "…Z", "api_version": "v1" }
}
```

Rules:
- Permission: `audit.audit_log.read` (002C catalogue; held by `internal_auditor` and
  `chief_financial_controller`). No new permission code is invented; `reports.audit.read` is not used.
- `actor` is `null` for system/no-actor rows (`AuditLog.actor_user` is nullable); the other item
  fields (`actor_type`, `action`, `entity_type`, `entity_id`, `created_at`) remain populated.
- `old_value`/`new_value` surface the stored `old_value_json`/`new_value_json` values; `user_agent`
  is intentionally not exposed (not part of §42.1).
- Missing bearer token → `401 AUTH_REQUIRED`; malformed/revoked/expired session → `401 INVALID_TOKEN`;
  authenticated user without the audit-read permission → `403 PERMISSION_DENIED`.

## Workflow event foundation (003B)

`record_workflow_event(...)`

Internal write interface over the canonical `workflows.WorkflowEvent` model and existing physical
`workflow_events` table (`docs/source/data-model.md` §26.2). The physical table was first created by
the 002EX tracer migration; 003B moves final Django model ownership to `sfpcl_credit.workflows`
without dropping or recreating the table. The tracer proof now calls this service and still returns
`workflow_event_id` in transition responses.

Accepted facts:
- `actor` — authenticated `User` or `None`, stored as `triggered_by_user`.
- `workflow_name`, `entity_type`, `entity_id`, `from_state`, `to_state`, `trigger_reason`.
- `action_code` and `metadata` may be passed by callers as explicit boundary facts, but they are not
  persisted because §26.2 defines no action or metadata columns.

`GET /api/v1/workflow-events/`

Read-only, protected endpoint matching `docs/source/api-contracts.md` §42.2. Serialization,
filtering, and pagination live behind `sfpcl_credit/workflows/events.py`;
`sfpcl_credit/workflows/event_views.py` is a thin `require_GET` view. No update/delete endpoint
exists.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-workflow-list
```

Query parameters (all optional):
- `entity_type` — free-text exact match on `WorkflowEvent.entity_type`.
- `entity_id` — UUID; invalid UUID returns `400 VALIDATION_ERROR` with `field_errors.entity_id`.
- `page`, `page_size` — standard top-level pagination (default `page_size` 20, max 100).
- Any other query parameter returns `400 VALIDATION_ERROR` with the unknown key in `field_errors`.

Success (top-level `pagination` envelope, newest-first by `created_at`):

```json
{
  "success": true,
  "data": [
    {
      "workflow_event_id": "uuid",
      "workflow_name": "application",
      "entity_type": "loan_application",
      "entity_id": "uuid",
      "from_state": "draft",
      "to_state": "submitted",
      "triggered_by_user": { "user_id": "uuid", "full_name": "Ivy Auditor" },
      "trigger_reason": "Application submitted for credit review",
      "created_at": "2026-06-22T10:30:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total_count": 1, "total_pages": 1, "has_next": false, "has_previous": false },
  "meta": { "request_id": "req-workflow-list", "timestamp": "...Z", "api_version": "v1" }
}
```

Rules:
- Permission: `audit.workflow_event.read` (002C catalogue). No new workflow-event permission code is invented.
- `triggered_by_user` is `null` for system/no-actor rows.
- Missing bearer token → `401 AUTH_REQUIRED`; malformed/revoked/expired session → `401 INVALID_TOKEN`;
  authenticated user without `audit.workflow_event.read` → `403 PERMISSION_DENIED`.
- Response examples are saved in `.ralph/runs/2026-07-05_083910_normal_run/evidence/api-responses/workflow-events-api-response.txt`.

## Versioned loan-policy configuration (003E)

`GET /api/v1/config/loan-policy/`

Protected read endpoint over `loan_policy_configs` (`docs/source/data-model.md` §25.1 and
`docs/source/api-contracts.md` §41.1). Results use the standard top-level pagination envelope,
ordered newest/effective-first by `effective_from` with `loan_policy_config_id` as a deterministic
secondary key.

Query parameters:
- `page`, `page_size` — standard top-level pagination (default `page_size` 20, max 100).
- Any other query parameter returns `400 VALIDATION_ERROR`.

`POST /api/v1/config/loan-policy/`

Creates a draft config. Request fields mirror the §41.1 request and §25.1 source columns:
`policy_name`, `policy_version`, `effective_from`, nullable `effective_to`,
duration/month/year settings, approval threshold/default scale/share/per-share/interest fields,
re-KYC/retention/grace/extension settings, and nullable `board_approval_reference`. `status`
defaults to `draft`; new configs cannot be created directly as `active` or `retired`.

`PATCH /api/v1/config/loan-policy/{loan_policy_config_id}/`

Updates draft configs only. Patching a non-draft config returns `409 INVALID_STATE_TRANSITION`.
Unknown fields, invalid ISO dates, `effective_to` before `effective_from`, negative decimals,
non-positive required integer settings, or unsupported status values return `400 VALIDATION_ERROR`
with field errors.

`POST /api/v1/config/loan-policy/{loan_policy_config_id}/activate/`

Activates a draft config only when `board_approval_reference` is present, satisfying
`functional-spec.md` M01-FR-015 for the shell. Missing approval evidence returns
`400 VALIDATION_ERROR` with `field_errors.board_approval_reference`. Activation writes:
- one `VersionHistory` row for `versioned_entity_type: "loan_policy_config"`;
- one `AuditLog` row with action `config.loan_policy.activated`;
- a state change to `active`.

Per A-021, if another loan-policy config is already active, activation retires it and sets its
`effective_to` to the day before the newly activated config's `effective_from`.

Mutation audit actions:
- create: `config.loan_policy.created`;
- update: `config.loan_policy.updated`;
- activate: `config.loan_policy.activated`.

Permissions:
- list/read requires `config.loan_policy.read`;
- create/update/activate require `config.loan_policy.manage`;
- missing bearer token returns `401 AUTH_REQUIRED`; authenticated users without the required
  permission return `403 PERMISSION_DENIED` with no config/audit/version write.

`GET /api/v1/version-histories/`

Read-only, protected version-history endpoint matching `docs/source/api-contracts.md` §42.3 over
`version_histories` (`docs/source/data-model.md` §26.3).

Query parameters:
- `versioned_entity_type` — optional exact match.
- `versioned_entity_id` — optional UUID; invalid UUID returns `400 VALIDATION_ERROR`.
- `page`, `page_size` — standard top-level pagination (default `page_size` 20, max 100).
- Any other query parameter returns `400 VALIDATION_ERROR`.

Response items include `version_history_id`, `versioned_entity_type`, `versioned_entity_id`,
`version_number`, `change_summary`, nullable `author`/`reviewer`/`approver` user summaries,
`board_approval_reference`, `effective_from`, nullable `effective_to`, and `created_at`.
Permission: `audit.version_history.read`.

Functional requirement trace:
- M01-FR-001: one or more persisted loan product configurations are supported.
- M01-FR-002: version/effective dates/Board reference are stored on the config; approval authority
  for activation is captured through the `approver` user on `VersionHistory`.
- M01-FR-015: activation is blocked without `board_approval_reference`.
- M01-FR-003 through M01-FR-014 are deferred to later rule/config slices; 003E persists only neutral
  source model fields and does not implement eligibility, share valuation, scale-of-finance,
  approval matrix, interest, charges, document-template, re-KYC, or compliance calculations.

## Document file upload foundation (003C)

`POST /api/v1/document-files/`

Protected multipart upload endpoint matching `docs/source/api-contracts.md` §26.1 and
`docs/source/data-model.md` §16.1. File bytes are stored outside the database through the local
filesystem adapter (`storage_provider: "local"`); the `document_files` table stores metadata,
storage key, uploader, sensitivity, upload timestamp, and SHA-256 checksum. Loan-document/checklist
workflow remains future scope.

Request headers:

```http
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
X-Request-ID: req-document-upload
```

Multipart fields:
- `file` — required file binary.
- `document_category` — required free-text category from the source vocabulary.
- `sensitivity_level` — required; accepted values are `public`, `internal`, `confidential`,
  `restricted`; input is case-normalized to lower case.
- `related_entity_type` — optional free-text entity type, recorded only in the upload audit metadata
  until downstream domain tables exist.
- `related_entity_id` — optional UUID; invalid UUID returns `400 VALIDATION_ERROR` with
  `field_errors.related_entity_id`.

Success data:

```json
{
  "success": true,
  "data": {
    "document_id": "uuid",
    "file_name": "borrower-pan.pdf",
    "mime_type": "application/pdf",
    "file_size_bytes": 245600,
    "sensitivity_level": "restricted",
    "uploaded_at": "2026-06-22T10:30:00Z"
  },
  "meta": { "request_id": "req-document-upload", "timestamp": "...Z", "api_version": "v1" }
}
```

Rules:
- Permission: `documents.file.upload` from the seeded source catalogue.
- Missing bearer token → `401 AUTH_REQUIRED`; malformed/revoked/expired session →
  `401 INVALID_TOKEN`; authenticated user without `documents.file.upload` →
  `403 PERMISSION_DENIED`.
- Missing `file`, `document_category`, or `sensitivity_level` returns `400 VALIDATION_ERROR` with
  field-level errors and no file, metadata, or audit write.
- Invalid `sensitivity_level` or `related_entity_id` returns `400 VALIDATION_ERROR`.
- Successful upload writes exactly one `AuditLog` row with action `documents.file.uploaded`,
  `entity_type: "document_file"`, and `entity_id` equal to the new `document_id`. The audit
  `new_value` includes metadata such as file name, storage provider/key, checksum, sensitivity,
  category, and related entity facts; it never stores raw file bytes.
- Local adapter root defaults to `SFPCL_DOCUMENT_STORAGE_ROOT` or
  `sfpcl_credit/local-document-storage`; tests override this root with a temp directory. Production
  S3/DMS adapters are future work behind the same storage boundary.
- Response examples are saved in `.ralph/runs/2026-07-05_085852_normal_run/evidence/api-responses/document-files-api-response.txt`.

## Document file secure download descriptor (003D)

`GET /api/v1/document-files/{document_id}/download/`

Protected endpoint matching `docs/source/api-contracts.md` §26.2 response option A. It reuses the
003C `document_files` metadata row and storage boundary; it does not stream raw bytes or create new
document metadata tables.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-document-download
```

Success data:

```json
{
  "success": true,
  "data": {
    "download_url": "/api/v1/local-document-files/uuid/download/?expires_at=2026-07-05T04%3A30%3A00Z",
    "expires_at": "2026-07-05T04:30:00Z"
  },
  "meta": { "request_id": "req-document-download", "timestamp": "...Z", "api_version": "v1" }
}
```

Rules:
- Permission: `documents.file.download` from the seeded source catalogue. The upload permission does
  not grant download access.
- The local adapter uses a deterministic, time-limited descriptor for MVP/dev tests because it cannot
  create a true external signed URL. Default expiry is 15 minutes from issuance.
- Missing bearer token → `401 AUTH_REQUIRED`; malformed/revoked/expired session →
  `401 INVALID_TOKEN`; authenticated user without `documents.file.download` →
  `403 PERMISSION_DENIED`.
- Unknown `document_id` returns `404 NOT_FOUND` without file name, storage key, provider details, or
  checksum information.
- The response body contains only `download_url` and `expires_at`; it never exposes `storage_key`,
  checksum, raw bytes, or upload audit metadata.
- Successful descriptor issuance writes exactly one `AuditLog` row with action
  `documents.file.downloaded`, `entity_type: "document_file"`, and `entity_id` equal to the
  downloaded document. Audit `new_value` includes document id, file name, MIME type, file size,
  storage provider, sensitivity level, and expiry timestamp; it deliberately omits storage key,
  checksum, signed secrets, and raw bytes.
- Failed auth, permission, and not-found requests do not write `documents.file.downloaded` audit rows.
- Public, internal, confidential, and restricted documents currently follow the same
  `documents.file.download` permission path until source docs define an implementable sensitivity
  matrix.
- Response examples are saved in `.ralph/runs/2026-07-05_093205_normal_run/evidence/api-responses/document-download-api-response.txt`.
## Communication template shell (003F)

`GET /api/v1/content-templates/`

`POST /api/v1/content-templates/`

`PATCH /api/v1/content-templates/{content_template_id}/`

Metadata-only endpoints matching `docs/source/api-contracts.md` §39.1 and
`docs/source/data-model.md` §24.1. This shell does not render templates with borrower/loan merge
data and does not send communications.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-content-template
```

Create request fields:
- Required: `template_code`, `template_name`, `template_type`, `audience`, `body_template`,
  `approval_status`, `template_version`, `effective_from`.
- Optional: `language_code`, `subject_template`, `variables`, `effective_to`.
- `variables` must be a JSON array of non-empty strings and is persisted to `variables_json`.
- `approval_status` is limited to `draft` or `approved`.
- `effective_from` and `effective_to` use ISO dates; `effective_to` must be on or after
  `effective_from` when supplied.

Success item fields:

```json
{
  "content_template_id": "uuid",
  "template_code": "loan_rejection_email_v1",
  "template_name": "Loan Rejection Email",
  "template_type": "email",
  "language_code": "en",
  "audience": "borrower",
  "subject_template": "Loan Application {{application_reference_number}} - Rejection Note",
  "body_template": "Dear {{borrower_name}}, your application has been rejected.",
  "variables": ["application_reference_number", "borrower_name", "rejection_reason"],
  "approval_status": "approved",
  "template_version": "1.0",
  "effective_from": "2026-04-01",
  "effective_to": null
}
```

Rules:
- List responses use the standard top-level pagination envelope with `page` and `page_size`
  query parameters only; unknown query parameters return `400 VALIDATION_ERROR`.
- Missing bearer token returns `401 AUTH_REQUIRED`; revoked/invalid token returns the existing
  auth `401`; authenticated users without content-template permission return `403 PERMISSION_DENIED`
  before any database write.
- Permission assumption A-022: read requires `communications.content_template.read` or
  `communications.content_template.manage`; writes require `communications.content_template.manage`.
  These narrow codes are used instead of `config.loan_policy.*`, `documents.template.*`, or
  communication-send permissions.
- Duplicate `template_code` returns `400 VALIDATION_ERROR` with `field_errors.template_code` and no
  audit row.
- Unknown `content_template_id` returns `404 NOT_FOUND`.
- Create/update write `AuditLog` actions `communications.content_template.created` and
  `communications.content_template.updated`. Audit metadata includes template id/code/name/type,
  audience, approval status, version, variables, and effective dates, but no rendered borrower or
  loan-specific merge output.

## Dashboard task summary shell (003G)

`GET /api/v1/dashboard/`

Protected endpoint matching `docs/source/api-contracts.md` §43.1 for the role-based dashboard
summary. Specialist dashboard endpoints from §43.2-§43.4 are deferred; this slice exposes only the
single role-context shell.

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-dashboard
```

Success data:

```json
{
  "role_context": "credit_manager",
  "cards": [
    {
      "code": "applications_pending_completeness",
      "label": "Applications pending completeness",
      "count": 0,
      "link": "/applications?status=pending_completeness"
    }
  ],
  "tasks": []
}
```

Rules:
- No query parameters are supported. Any query parameter returns `400 VALIDATION_ERROR` with the
  unknown parameter in `field_errors`.
- Missing bearer token returns `401 AUTH_REQUIRED`; revoked/invalid token returns `401`; an
  authenticated user without the dashboard scope returns `403 PERMISSION_DENIED`.
- Permission assumption A-023: dashboard read requires `management_readonly`, the source §19.1
  dashboard/summary scope. This is used instead of broad report/export permissions or an invented
  `dashboard.read` code.
- Role contexts currently returned from primary role:
  `credit_manager`, `sanction_committee`, `compliance`, `treasury`, or `management`.
- Cards use source-named shell codes from the §43.1 example and functional-spec §12.2-§12.6
  dashboard widget lists. All `count` values are `0` because application, appraisal, sanction,
  compliance, treasury, DPD, reminder, default, and management-report tables/calculations are not
  implemented yet.
- `tasks` is an empty list because no source-backed task persistence table exists yet.
- The response returns only summary metadata fields: `role_context`, `cards[].code`,
  `cards[].label`, `cards[].count`, `cards[].link`, and `tasks[]`. It does not return borrower,
  member, loan-account, document, or other sensitive entity values.
- Read-only dashboard access does not write `AuditLog` rows in this shell.
- Response examples are saved in
  `.ralph/runs/2026-07-05_200043_normal_run/evidence/api-responses/dashboard-api-response.txt`.
- Frontend wiring implemented in 003H (`2026-07-06_102639_normal_run`): the staff Dashboard page
  now calls this endpoint with the stored bearer session, renders `cards[]` through the existing
  KPI-card pattern, renders `tasks[]` through the existing task-queue pattern, and uses existing
  alert/empty patterns for loading, empty, `401`, `403`, and server/network errors. Frontend link
  translation follows A-024; unknown future links are left inactive instead of creating new routes
  in this dashboard slice.
