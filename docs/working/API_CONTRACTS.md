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
| Authentication and current user | Current-user implemented through slice 002D; frontend shell wired in 002E; member portal auth implemented in 005FA | Login, dashboards, MP00, MP01, MP02, MP25 | `docs/source/api-contracts.md`, `auth-permissions.md`, `screen-spec-member-portal.md` | Implemented `POST /api/v1/auth/login/`, `/refresh/`, `/logout/`, and `GET /api/v1/auth/me/` with standard envelopes, active-user-only access, refresh rotation, session revocation, role/team token claims, effective role permissions, current action availability, and auth audit logs for login/refresh/logout. 005FA adds portal activation/login/password-reset/password-change endpoints under `/api/v1/portal/auth/`; borrower access tokens and `/auth/me` include `member_id`, `portal_account_id`, and `portal_role = borrower_member` while exposing only portal own-data permissions, not staff completeness/deficiency permissions. The React shell now logs in staff through `/auth/login/`, member portal users through `/portal/auth/login/`, stores bearer/refresh tokens in local browser storage, loads `/auth/me/` before rendering protected navigation, clears local state on `TOKEN_EXPIRED`/`INVALID_TOKEN`, and posts the refresh token to `/auth/logout/`. Admin session controls remain future slices. |
| Admin user management | Implemented in slice 002G; action-specific permission gating added in 002G2 | Admin User Management | `api-contracts.md` §6-7, §11.4, §12; `auth-permissions.md` §12.1, §15.12, §19 | `GET /api/v1/admin/users/`, `GET /api/v1/admin/users/{user_id}/`, and assignment action endpoints bind existing `Role`/`Team` catalogue rows only. All routes require session-bound bearer auth. Since 002G2 each action requires the specific canonical user-admin permission (`auth-permissions.md` §12.1), not just any user-admin grant: list/detail read requires `users.user.read` OR any write user-admin permission (read fallback per A-015 because seeded `system_admin` lacks `users.user.read`); role assignment and team add/remove require `users.user.update`; suspending a user requires `users.user.disable`; restoring a user to active requires `users.user.update`. A partial-permission actor receives `403 PERMISSION_DENIED` with no `AuditLog` write and no session revocation. Order of checks: `401` (auth) → `403` (permission) → `400`/`404`. Successful role/team/status changes write `AuditLog`; suspending a user revokes active sessions; changing/suspending the last active `system_admin` is blocked per A-014. The frontend continues to map the write user-admin permissions to prototype `manage_users` for nav/route visibility. |
| Early end-to-end tracer | Implemented in slice 002EX | Staff Tracer screen | `docs/source/api-contracts.md` §3-6; `docs/source/data-model.md` §26.1-26.2 | Thin dev proof only. Protected by session-bound bearer auth and explicit `tracer.lifecycle.run` permission. Endpoints: `POST /api/v1/tracer/members/`, `POST /api/v1/tracer/members/{member_id}/loan-applications/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/sanction/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/loan-account/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/disburse/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/repayments/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/close/`. Minimal models only; every transition writes `audit_logs` and `workflow_events`; invalid state transitions return `409 INVALID_STATE_TRANSITION`; missing/revoked auth returns the standard `401` envelope before domain writes. |
| API contract test harness | Implemented in slice 002J | None | `api-contracts.md` §6.1-6.4, §7.1-7.3, §44 | Test-only assertions live in `sfpcl_credit/tests/api_contracts.py`. Future endpoint slices should use them to prove standard success envelopes, error envelopes, top-level list pagination, and target §44 `available_actions` item shapes without importing test utilities from production code. The harness regression tests cover `/auth/me/`, admin users pagination, `401 AUTH_REQUIRED`, revoked-session `401 INVALID_TOKEN`, `403 PERMISSION_DENIED`, partial-admin write denial, and tracer `409 INVALID_STATE_TRANSITION`. A-016 records that current `/auth/me/` still returns flat permission-code strings for `available_actions`; the object shape is asserted against an internal sample for future detail endpoints. |
| Local demo staff seed | Implemented in slice 002K; corrected in 002K2 | Login, dashboard smoke, admin/tracer permission smoke | `implementation-roadmap.md` §10, §20-22; `technical-architecture.md` §8-12, §17-18; `auth-permissions.md`; `api-contracts.md` §11-12, §43-44 | `python manage.py seed_demo_users` is a guarded local/dev seed path. It refuses unless `SFPCL_DEBUG=true` and `SFPCL_ALLOW_DEMO_SEED=true`, calls `seed_catalogue()`, creates or updates deterministic `demo.*@sfpcl.example` staff users with active primary roles and memberships, and does not alter `e2e.*` users. Demo users authenticate through the real `/auth/login/` and `/auth/me/` endpoints; there is no demo auth bypass. The zero-permission user returns `permissions: []` and `available_actions: []`; the tracer-only user uses the guarded local/dev-only `local_demo_tracer_user` role and returns only `tracer.lifecycle.run`; the shared source-catalogue `sales_team_user` role remains permission-neutral until source documents define grants; system admin preserves canonical action-specific user-admin permissions without broad `manage_users` aliases. |
| Role/permission/team catalogue | Seeded in slice 002C; exposed for current user in 002D | None directly | `auth-permissions.md` §12-15, §38 | Canonical `Permission`, `Role`, `Team`, `RolePermission` catalogue seeded idempotently via `python manage.py seed_role_catalogue` (`sfpcl_credit/identity/catalogue.py`). `/api/v1/auth/me/` exposes the authenticated user's effective permission codes from this data. |
| Members and KYC | Member directory list implemented in 004A; masked member profile detail implemented in 004B; nominee list/create implemented in 004D; shareholding list/create implemented in 004F; land/crop list/create implemented in 004G; KYC profile/document upload/verify implemented in 004H; member bank-account/cancelled-cheque metadata implemented in 004J; Borrower 360 Epic 004 UI wiring implemented in 004K with corrective DTO hardening queued in 004K2 | Member Directory, Member Profile, borrower profile, application intake | `api-contracts.md` §13.1/§13.3/§13.5/§14.1-§14.3/§15.1-§15.2/§17.1-§18.4; `data-model.md` §10.1-§10.4/§11.1/§11.7-§12.4; `auth-permissions.md` §12.2-§12.3/endpoint map | `GET /api/v1/members/` is API-backed with standard list pagination, `members.member.read`, masked mobile numbers, no PAN/Aadhaar fields, and strict §13.1 query validation. `GET /api/v1/members/{member_id}/` returns masked PAN/Aadhaar objects, address, profile shell fields, share/active-member shell fields, and object-shaped `available_actions[]`. `GET/POST /api/v1/members/{member_id}/nominees/`, `/shareholdings/`, `/land-holdings/`, `/crop-plans/`, `/bank-accounts/`, and `/cancelled-cheques/` are API-backed with their documented validations and metadata-only create audits. `GET/POST/PATCH /api/v1/kyc-profiles/`, KYC document upload, and KYC document verify are implemented for member parties only with KYC permissions. Sensitive bank-account reveal, re-KYC task management, share certificate/demat, bank verification letters, disbursement bank gates, and loan-application/loan-account/repayment/risk/audit Borrower 360 data remain future scope. |
| Loan applications | Draft create/read/update implemented in 005A; submit in 005B; reference generation/register in 005C; object access hardened in 005C2; application document/checklist metadata implemented in 005D; completeness workbench/pass implemented in 005E; deficiency return/list/resolve implemented in 005F | Applications, completeness | `api-contracts.md` §19.2-§21; `data-model.md` §13.1 and application-document/deficiency tables; `auth-permissions.md` §12.4, §19.2, §34.3, §37.3 | `POST /api/v1/loan-applications/`, `GET /api/v1/loan-applications/{id}/`, `PATCH /api/v1/loan-applications/{id}/`, submit, reference-generation, application-document list/upload/verify, document-checklist read/refresh, completeness-check read/pass, return-with-deficiencies, deficiency list, and deficiency resolve endpoints persist and advance application facts with stable UUID IDs, nullable/formal `LO...` reference numbers, member summaries, optional land/crop/bank/cancelled-cheque references, masked bank metadata, document-file links, permissions, object access, audit, workflow events, register metadata, and structured deficiency metadata. Eligibility, loan limits, appraisal, sanction, and disbursement remain future slices. |
| Appraisal and loan limit | Draft from source | Appraisal workbench | `functional-spec.md`, `api-contracts.md` | Financial rules require tests before implementation. |
| Sanction and approvals | Draft from source | Sanction workbench | `auth-permissions.md`, `api-contracts.md` | Approval matrix is high-control. |
| Documentation and securities | Document-file upload foundation implemented in 003C; secure download descriptor implemented in 003D; broader loan document workflows remain draft | Documentation hub | SOP PDFs, `api-contracts.md` §26; `data-model.md` §16.1 | `POST /api/v1/document-files/` stores file bytes outside the database through the local adapter and stores metadata in `document_files`. `GET /api/v1/document-files/{document_id}/download/` returns a permissioned, time-limited local download descriptor and writes document-access audit. Checklist, template, signature, stamp, notarisation, and loan-document flows remain future slices. |
| Versioned configuration | Loan-policy shell implemented in 003E; calculations and broader config types remain draft | Settings/config shell | `api-contracts.md` §41.1, §42.3; `data-model.md` §25.1, §26.3; `functional-spec.md` M01-FR-001/M01-FR-002/M01-FR-015 | `loan_policy_configs` and `version_histories` are persisted. `GET/POST/PATCH/activate` loan-policy APIs and filtered version-history reads are protected, audited where mutating, and versioned on activation. M01-FR-003 through M01-FR-014 calculations/rules are explicitly deferred; only neutral source model fields are stored. |
| Communication templates and communication history | Content-template metadata shell implemented in 003F; communication send/list shell implemented in 003I; real delivery and notification-center UI remain draft | None directly | `api-contracts.md` §39.1-§39.3; `data-model.md` §24.1-§24.2; `functional-spec.md` M16-FR-001-M16-FR-007/M18-FR-006 | `content_templates` and `communications` are persisted. `GET/POST/PATCH /api/v1/content-templates/` is protected by narrow A-022 content-template permissions. `POST /api/v1/communications/send/` renders approved/effective template snapshots, persists a pending communication record, and audits metadata only; `GET /api/v1/communications/` lists records for a supplied related entity with standard pagination. No real email/SMS/courier/phone provider is called yet. |
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
| `GET /api/v1/auth/me/` | `Authorization: Bearer <access_token>` | user identity (`user_id`, `full_name`, `email`, `mobile_number`, `status`), `roles`, `teams`, compatibility `role_codes`/`team_codes`, `permissions`, `available_actions` | Access token must be signed, unexpired, type `access`, and bound to an active `user_sessions` row for an active user. Missing token returns `401 AUTH_REQUIRED`; expired access tokens return `401 TOKEN_EXPIRED`; refresh/wrong-type, malformed, revoked-session, inactive-user, unknown-session tokens, or sessions linked to non-active portal accounts return `401 INVALID_TOKEN`. When a linked `PortalAccount` is suspended/inactive/deleted-member scoped, the active session is revoked with reason `portal_account_status_changed` before `/auth/me` returns. |

Member portal endpoints added in 005FA:

| Endpoint | Request | Success Data | Key Rules |
|---|---|---|---|
| `POST /api/v1/portal/auth/activation/start/` | `folio_or_member_id`, `contact`, optional `pan_last4`, optional `aadhaar_last4` | `challenge_id`, `masked_contact`, `expires_at` | Member/contact/last-four facts must match a non-deleted member; already-active accounts return `409 PORTAL_ACCOUNT_ACTIVE`; no full PAN/Aadhaar or OTP is returned. Creates an OTP challenge, a pending communication-shell row, and `portal.auth.activation.started` audit metadata. |
| `POST /api/v1/portal/auth/activation/complete/` | `challenge_id`, `otp`, `password`, `confirm_password` | `portal_account` with `portal_account_id`, `member_id`, `status`, masked contact facts | OTP must be pending and unexpired; password must match and be at least 10 characters. Creates/updates a `borrower_portal_user` user linked one-to-one to the member, activates the portal account, and writes `portal.account.activated`. |
| `POST /api/v1/portal/auth/login/` | `identifier`, `password` | bearer token payload plus user payload | Identifier may match portal user email, member email, or member mobile. Invalid/inactive/suspended cases return generic `401 INVALID_CREDENTIALS` and write `portal.login.failed`; successful login writes `portal.login.success`. Access tokens include `member_id`, `portal_account_id`, and `portal_role = borrower_member` only for active, non-deleted member portal accounts; `/auth/me` returns the same member scope and only portal own-data permissions while the portal account remains active. |
| `POST /api/v1/portal/auth/password-reset/start/` | `identifier` | generic message plus challenge details when a valid account exists | Returns a generic response to avoid account enumeration; valid active portal accounts receive an OTP challenge and `portal.auth.password_reset.started` audit metadata. |
| `POST /api/v1/portal/auth/password-reset/complete/` | `challenge_id`, `otp`, `password`, `confirm_password` | `{ "reset": true }` | OTP is single-use and expiring; successful reset updates the password hash, revokes all active sessions with reason `portal_password_reset`, and writes `portal.auth.password_reset.completed`. Replay returns `400 OTP_INVALID`. |
| `POST /api/v1/portal/auth/password/change/` | bearer token plus `current_password`, `new_password`, `confirm_password` | `{ "password_changed": true }` | Requires a portal bearer session whose linked portal account is still active. Suspended/inactive portal accounts using old bearer tokens receive `401 INVALID_TOKEN` and the session is revoked with reason `portal_account_status_changed`. Current password must match. Successful change updates the password hash, revokes other active sessions with reason `portal_password_change`, keeps the current session active, and writes `portal.password.changed`. |

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

## Member Directory API (004A)

`GET /api/v1/members/`

Request headers:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-members-list
```

Supported query parameters:
- `search` — matches member number, legal/display name, or folio number.
- `member_type` — `individual_farmer`, `fpc`, or `producer_institution`.
- `membership_status` — `active`, `inactive`, or `pending_verification`.
- `kyc_status` — `verified`, `missing`, `rekyc_due`, or `pending`.
- `default_status` — `no_default`, `existing_default`, or `past_default`.
- `page`, `page_size` — standard list pagination; `page_size` is capped at 100.

Success data uses the standard top-level list envelope from source §6.2. Each item contains:

```json
{
  "member_id": "uuid",
  "member_number": "MEM-00125",
  "member_type": "individual_farmer",
  "legal_name": "Ramesh Patil",
  "display_name": "Ramesh Patil",
  "folio_number": "FOL-456",
  "membership_status": "active",
  "kyc_status": "verified",
  "rekyc_due_date": "2027-06-22",
  "default_status": "no_default",
  "mobile_number": "******7890",
  "email": "ramesh@example.com",
  "share_summary": {
    "number_of_shares": 100,
    "holding_mode": "physical",
    "available_share_count": 100
  },
  "active_member_status": {
    "status": "active",
    "verified_at": "2026-06-22T10:30:00Z"
  }
}
```

Rules:
- Missing bearer token returns `401 AUTH_REQUIRED`; users without `members.member.read` return `403 PERMISSION_DENIED`.
- Unknown query parameters or unsupported enum values return `400 VALIDATION_ERROR` with `field_errors`.
- The directory response never includes PAN or Aadhaar fields. `mobile_number` is masked to last four digits.
- Read-only list access writes no audit/workflow event. Exports, create/update, nominee, witness, KYC verification, share certificate, demat, land/crop, loan application, and Borrower 360 behavior are explicitly deferred.

## Member Profile Detail API (004B, extended by 004C)

`GET /api/v1/members/{member_id}/`

Rules:
- Requires a session-bound bearer token and `members.member.read`; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 PERMISSION_DENIED`, and a valid UUID that is
  unknown or soft-deleted returns `404 NOT_FOUND`.
- Returns the standard success envelope with member identifiers, status fields, masked mobile,
  registered address, share and active-member shell fields, `pan`/`aadhaar` as
  `{ "masked": "...", "can_view_full": boolean }`, nullable type-specific profile objects, and
  §44-shaped `available_actions[]`. `can_view_full` is true only for the matching field-specific
  reveal permission; it never includes the full source value in the profile response.
- `available_actions[]` is currently empty for member profile detail. The profile read does not infer
  `create_loan_application` from `membership_status`, `kyc_status`, `default_status`, or
  `applications.loan_application.create`; slice 005A and later eligibility slices own the
  source-backed loan-start action and blockers.
- For `member_type = individual_farmer`, `individual_profile` is either `null` when no row exists
  or contains `first_name`, nullable `middle_name`, `last_name`, nullable `gender`,
  `date_of_birth`, nullable `occupation`, `land_area_under_cultivation_acres`, `primary_crop`,
  `services_availed_flag`, and nullable `employment_or_service_years`.
- For `member_type = fpc` or `producer_institution`, `producer_institution_profile` is either
  `null` when no row exists or contains `institution_type`, nullable `registration_number`,
  `authorised_signatory_name`, `board_resolution_required_flag`, `services_availed_flag`, and
  nullable `produce_supply_years`. Decimal values are serialized as fixed two-decimal strings;
  dates are ISO `YYYY-MM-DD`.
- Profile persistence rejects an individual profile whose member is not `individual_farmer` and
  rejects a producer-institution profile whose member is not `fpc` or `producer_institution`.
- The response never serializes `pan_encrypted`, `aadhaar_encrypted`, `pan_hash`, `aadhaar_hash`, or
  full source values. Producer authorised-signatory PAN/Aadhaar fields are not stored or returned.
- Masked read-only profile access writes no workflow event and no profile-access audit row beyond
  normal authentication audit.

## Member Sensitive Reveal API (004I)

`POST /api/v1/members/{member_id}/reveal-sensitive-field/`

Request:

```json
{
  "field_name": "pan",
  "reason": "KYC verification during loan application"
}
```

Success response:

```json
{
  "success": true,
  "data": {
    "field_name": "pan",
    "value": "ABCDE1234F",
    "expires_at": "2026-06-22T10:35:00Z"
  },
  "meta": { "request_id": "req-id", "timestamp": "2026-06-22T10:30:00Z", "api_version": "v1" }
}
```

Rules:
- Implemented fields are member `pan` and `aadhaar` only. Nominee, witness, signatory, document,
  bank, export, and generic sensitive-data reveal remain deferred.
- Requires a session-bound bearer token, the base member read permission `members.member.read`, and
  the field-specific permission: `members.sensitive.reveal_pan` for `pan` and
  `members.sensitive.reveal_aadhaar` for `aadhaar`. Broad member read, KYC, document, admin, or
  export permissions do not grant reveal.
- Missing auth returns `401 AUTH_REQUIRED` without a reveal audit because no actor is known. Missing
  base read returns `403 PERMISSION_DENIED`; missing field-specific permission returns
  `403 SENSITIVE_FIELD_ACCESS_DENIED`; unsupported/missing `field_name`, blank `reason`, or an
  unavailable source value return `400 VALIDATION_ERROR`; unknown or soft-deleted members return
  `404 NOT_FOUND`.
- Successful reveal returns the full value only in the immediate response with a five-minute
  `expires_at` timestamp. The response includes `Cache-Control: no-store` and `Pragma: no-cache`.
  The existing masked member profile remains masked; the frontend keeps full values only in
  temporary component state and clears the reason after success.
- Successful reveals write one `AuditLog` action `members.sensitive_field.revealed`. Authenticated
  denied reveal attempts write `members.sensitive_field.reveal_denied`. Audit metadata includes
  actor, member ID, field name, reason, outcome, denial reason when applicable, request ID, IP,
  user-agent, and expiry for successful reveals. Audit rows never include full PAN/Aadhaar,
  encrypted token columns, hash values, or submitted identifier-derived values.
- Sensitive reveal writes no `WorkflowEvent`.

## Loan Application Draft, Submit, and Reference API (005A-005C2)

`POST /api/v1/loan-applications/`

Request:

```json
{
  "member_id": "uuid",
  "required_loan_amount": "400000.00",
  "requested_tenure_months": 12,
  "declared_purpose": "Crop production loan for grape cultivation",
  "purpose_category": "crop_production",
  "loan_type_requested": "short_term",
  "land_holding_id": "uuid",
  "crop_plan_id": "uuid",
  "bank_account_id": "uuid",
  "cancelled_cheque_id": "uuid",
  "borrower_request_notes": "Assisted intake notes",
  "terms_acceptance_flag": false
}
```

`GET /api/v1/loan-applications/{loan_application_id}/`

`PATCH /api/v1/loan-applications/{loan_application_id}/`

Patch accepts only the draft facts above except `member_id`; borrower ownership is preserved.

`POST /api/v1/loan-applications/{loan_application_id}/submit/`

Request body is accepted as a JSON object. `submission_notes` may be supplied by clients, but 005B
does not persist notes because no source-backed column exists yet.

`POST /api/v1/loan-applications/{loan_application_id}/generate-reference/`

Request body is accepted as a JSON object. In 005C this endpoint represents the successful
completeness-pass transition only; it does not evaluate document checklist items, nominee rules,
deficiencies, eligibility, appraisal, sanction, or disbursement.

`GET /api/v1/loan-applications/{loan_application_id}/completeness-check/`

Returns the derived completeness workbench for a submitted application:

```json
{
  "loan_application_id": "uuid",
  "application_reference_number": null,
  "application_status": "submitted",
  "current_stage": "initial_loan_request",
  "completeness_status": "not_started",
  "member": {
    "member_id": "uuid",
    "display_name": "Ramesh Patil",
    "member_type": "individual_farmer",
    "folio_number": "FOL-005A"
  },
  "required_checklist_items": [
    {
      "document_type": "borrower_pan",
      "required_flag": true,
      "submission_status": "submitted",
      "verification_status": "rejected",
      "latest_application_document_id": "uuid",
      "latest_version_number": 2,
      "complete": false,
      "reason_code": "not_verified"
    },
    {
      "document_type": "crop_plan",
      "required_flag": true,
      "submission_status": "pending",
      "verification_status": "pending",
      "latest_application_document_id": null,
      "latest_version_number": null,
      "complete": false,
      "reason_code": "missing_metadata"
    }
  ],
  "blocking_document_types": ["borrower_pan", "crop_plan"],
  "can_generate_reference": false
}
```

`POST /api/v1/loan-applications/{loan_application_id}/completeness-check/pass/`

Request body is accepted as a JSON object. On success the endpoint returns the canonical serialized
loan application after calling `generate_reference_after_completeness_pass(...)`, including the
generated `LO...` reference and `loan_request_register_entry` summary.

`POST /api/v1/loan-applications/{loan_application_id}/return-with-deficiencies/`

Request:

```json
{
  "communication_mode": "email",
  "message": "Please submit corrected documents to proceed.",
  "items": [
    {
      "item_code": "borrower_pan",
      "remarks": "PAN name does not match the member profile."
    }
  ]
}
```

005F uses `items[].item_code` to select source-backed blocking facts from the 005E completeness
workbench. The source §19.7 example uses `deficiency_ids`, but prior slices did not create
deficiency rows before the return action; A-040 records this request-shape decision.

Success data:

```json
{
  "loan_application_id": "uuid",
  "application_reference_number": null,
  "application_status": "incomplete_returned",
  "current_stage": "initial_loan_request",
  "completeness_status": "incomplete",
  "communication_mode": "email",
  "message": "Please submit corrected documents to proceed.",
  "items": [
    {
      "deficiency_id": "uuid",
      "loan_application_id": "uuid",
      "item_code": "borrower_pan",
      "deficiency_type": "not_verified",
      "source_reason_code": "not_verified",
      "description": "borrower pan is submitted but not verified.",
      "remarks": "PAN name does not match the member profile.",
      "resolution_status": "open",
      "raised_by_user_id": "uuid",
      "raised_at": "2026-07-09T15:30:00Z",
      "resolved_by_user_id": null,
      "resolved_at": null,
      "resolution_notes": ""
    }
  ]
}
```

`GET /api/v1/loan-applications/{loan_application_id}/deficiencies/`

Returns `{ "loan_application_id": "uuid", "items": [...] }` using the deficiency item shape above.

`POST /api/v1/deficiencies/{deficiency_id}/resolve/`

Request:

```json
{
  "resolution_notes": "Nominee Aadhaar uploaded and verified."
}
```

Success returns the resolved deficiency item with `resolution_status = resolved`, resolver actor,
and `resolved_at`.

Rules:
- All endpoints require session-bound bearer authentication.
- `POST` requires `applications.loan_application.create`; `GET` requires
  `applications.loan_application.read`; `PATCH` requires
  `applications.loan_application.update`; submit requires
  `applications.loan_application.submit`; reference generation requires
  `applications.loan_application.complete_check`.
- Detail, patch, submit, and reference-generation endpoints also enforce object access after the
  global permission check and after `404` lookup. Created/received users can access their
  applications; Credit Manager access is explicitly limited to applications already in the
  `credit_assessment` stage. A same-permission actor outside those scopes receives
  `403 OBJECT_ACCESS_DENIED`.
- 005A stores draft applications. 005B permits only `draft -> submitted`.
  `current_stage` remains `initial_loan_request`, `completeness_status` remains
  `not_started`, and submitted applications are locked from `PATCH`.
- `application_reference_number` remains nullable through submit. 005C generates the formal
  `LO...` number only from the submitted state at the source-backed completeness-pass point,
  using the `loan_application_reference` system sequence (`LO` prefix, 8-digit padding, starting
  at `LO00000001`). On success it sets `application_status = reference_generated`,
  `current_stage = credit_assessment`, and `completeness_status = complete`.
- 005E makes the source-backed completeness pass explicit. Workbench read requires
  `applications.loan_application.read`; pass requires
  `applications.loan_application.complete_check`. Both endpoints reuse the application object-access
  boundary after global permission and `404` checks.
- The pass endpoint first enforces submitted/non-duplicate state and returns
  `409 INVALID_STATE_TRANSITION` for draft, already-reference-generated, or register-existing
  applications. It then evaluates the latest 005D metadata row for each mandatory application-stage
  document code and requires `submission_status = submitted` plus
  `verification_status = verified`. Missing latest metadata returns `reason_code =
  missing_metadata`; submitted but pending/rejected latest metadata returns `reason_code =
  not_verified`. Validation failures return `400 VALIDATION_ERROR` with item-level
  `required_checklist_items` and create no sequence/register/audit/workflow side effects.
- 005F return-with-deficiencies requires `applications.loan_application.complete_check`; deficiency
  list requires `applications.loan_application.read`; deficiency resolve requires
  `applications.loan_application.complete_check`. All reuse
  `applications.services.evaluate_application_object_access(...)` after global permission and
  `404` checks.
- Return-with-deficiencies is limited to submitted applications that do not yet have an
  `LO...` reference and do not have a loan request register entry. Draft, already-returned
  `incomplete_returned`, and reference-generated attempts return `409 INVALID_STATE_TRANSITION`;
  A-041 records the blocked repeat-return assumption because source docs do not define a repeat
  return rule.
- Return items must match current blocking 005E completeness facts. `missing_metadata` source facts
  become `deficiency_type = missing_document`; `not_verified` source facts become
  `deficiency_type = not_verified`. Empty selections, duplicate item codes, arbitrary item codes,
  missing communication mode/message, or unknown fields return `400 VALIDATION_ERROR`.
- Successful return-with-deficiencies sets `application_status = incomplete_returned`, keeps
  `current_stage = initial_loan_request`, sets `completeness_status = incomplete`, creates open
  `deficiencies` rows, writes
  `applications.loan_application.returned_with_deficiencies` audit metadata, and records a
  `loan_application` workflow event from submitted to incomplete_returned with trigger reason
  "Application returned with completeness deficiencies." It does not generate a reference, create a
  loan request register row, advance to credit assessment, or visibly advance the sequence.
- Deficiency resolve closes only open rows and writes `applications.deficiency.resolved` audit
  metadata plus an `application_deficiency` workflow event from open to resolved. Borrower portal
  re-upload, borrower response drafting, application resubmission, rejection notes, and
  communications delivery are deferred to later slices.
- Required draft validation is intentionally narrow: known borrower member,
  well-formed UUID references, subresource references owned by the borrower
  member, and positive requested amount when supplied.
- Draft saves allow incomplete KYC/documents. 005B submit requires the
  source-backed request facts already persisted by 005A: borrower member,
  positive `required_loan_amount`, nonblank `declared_purpose`, and nonblank
  `purpose_category`. Nominee, application-document placeholder, completeness,
  and deficiency gates remain future slices.
- Responses include member identity summaries plus land/crop and masked
  bank/cancelled-cheque metadata by ID. They never include PAN, Aadhaar, full
  bank account numbers, encrypted values, protected tokens, or hash fields.
  005B responses additionally include nullable `submitted_at` and
  `submitted_by_user_id`. 005C responses additionally include nullable
  `loan_request_register_entry` metadata sourced from the application/member record:
  register entry ID, loan application ID, reference number, member ID, received/reference dates,
  received channel, register status, borrower name, folio, member type, requested amount,
  purpose category, current stage, owner role, and pending downstream statuses.
- Successful create writes `applications.loan_application.created` audit metadata
  plus one `loan_application` workflow event into `draft`. Successful patch
  writes `applications.loan_application.updated` audit metadata and does not
  create a workflow event because no source-backed state transition occurs.
  Successful submit writes `applications.loan_application.submitted` audit
  metadata plus one `loan_application` workflow event from `draft` to
  `submitted`. Successful reference generation writes
  `applications.loan_application.reference_generated` audit metadata plus one
  `loan_application` workflow event from `submitted` to `reference_generated`.
- Unknown applications return `404 NOT_FOUND`; missing global permissions return
  `403 PERMISSION_DENIED`; object-scope mismatches return `403 OBJECT_ACCESS_DENIED`; invalid submit
  facts return `400 VALIDATION_ERROR`; re-submit, other non-draft submit, draft reference generation,
  or duplicate reference attempts return `409 INVALID_STATE_TRANSITION`. Object-access denials do
  not write success audit rows, workflow events, register rows, application references, or visible
  sequence advancement. Return-with-deficiencies permission/object denials additionally create no
  deficiency rows and no deficiency success audit/workflow events.

## Application Document and Checklist API (005D)

`GET /api/v1/loan-applications/{loan_application_id}/application-documents/`

Returns:

```json
{
  "loan_application_id": "uuid",
  "items": [
    {
      "application_document_id": "uuid",
      "loan_application_id": "uuid",
      "document_type": "borrower_pan",
      "party_type": "borrower",
      "party_id": "uuid",
      "document_file": {
        "document_id": "uuid",
        "file_name": "borrower-pan.pdf",
        "mime_type": "application/pdf",
        "file_size_bytes": 256,
        "sensitivity_level": "restricted",
        "uploaded_at": "2026-07-09T14:00:00Z"
      },
      "required_flag": true,
      "submission_status": "submitted",
      "verification_status": "pending",
      "verified_by_user_id": null,
      "verified_at": null,
      "remarks": "PAN copy received at branch.",
      "version_number": 1,
      "created_at": "2026-07-09T14:00:00Z",
      "created_by_user_id": "uuid",
      "updated_at": "2026-07-09T14:00:00Z",
      "updated_by_user_id": "uuid"
    }
  ]
}
```

`POST /api/v1/loan-applications/{loan_application_id}/application-documents/`

Request:

```json
{
  "document_type": "borrower_pan",
  "party_type": "borrower",
  "party_id": "uuid",
  "document_file_id": "uuid",
  "remarks": "PAN copy received at branch."
}
```

`POST /api/v1/application-documents/{application_document_id}/verify/`

Request:

```json
{
  "verification_status": "verified",
  "remarks": "PAN name matches member profile."
}
```

`GET /api/v1/loan-applications/{loan_application_id}/document-checklist/`

`POST /api/v1/loan-applications/{loan_application_id}/document-checklist/refresh/`

Checklist responses contain the source-required item codes with pending placeholders until metadata
exists: `loan_application_form`, `borrower_pan`, `borrower_aadhaar_ovd`, `nominee_pan`,
`nominee_aadhaar_ovd`, `share_certificate_copy`, `land_document_7_12`, `crop_plan`, and
`six_month_bank_statement`.

Rules:
- All endpoints require session-bound bearer authentication.
- Application-document list and checklist read/refresh require
  `applications.loan_application.read`. Upload requires `applications.document.upload`. Verify
  requires `applications.document.verify`.
- Application-scoped endpoints return `404 NOT_FOUND` for unknown applications before object-scope
  checks, then use `applications.services.evaluate_application_object_access(...)`. Same-permission
  actors outside the application scope receive `403 OBJECT_ACCESS_DENIED`; missing global permission
  returns `403 PERMISSION_DENIED`.
- Upload links metadata to an existing `documents.DocumentFile` by `document_file_id`; 005D does not
  upload or duplicate file bytes. Upload is accepted only after application submit and creates a new
  version row for duplicate document type/party combinations instead of overwriting prior history.
- Supported `party_type` values are `borrower`, `nominee`, and `witness`. Supported verification
  values are `pending`, `verified`, and `rejected`.
- Successful upload writes `applications.application_document.attached`; successful verification
  writes `applications.application_document.verified`. Both audit rows are metadata-only and never
  include raw file bytes, storage keys, checksums, PAN, Aadhaar, full bank-account numbers, encrypted
  token values, or hashes.
- Checklist refresh is currently a derived read operation under A-039 because the source names the
  endpoint but no exact checklist-refresh mutation or permission is defined yet. It writes no audit
  or workflow event.

## Member Bank Account and Cancelled Cheque Metadata API (004J)

`GET /api/v1/members/{member_id}/bank-accounts/`

Rules:
- Requires a session-bound bearer token and `members.member.read` under A-034; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 PERMISSION_DENIED`, and an unknown or
  soft-deleted member returns `404 NOT_FOUND`.
- Returns the standard top-level list envelope. Each item contains `bank_account_id`,
  `owner_party_type`, `owner_party_id`, `account_holder_name`, masked `account_number` as
  `{ "masked": "...", "last4": "...", "can_view_full": false }`, `ifsc`, nullable `bank_name`,
  nullable `branch_name`, `verification_status`, nullable `cancelled_cheque_id`, nullable
  `signature_verified_flag`, `status`, and `created_at`.
- The response never serializes full account numbers, `account_number_encrypted`, or
  `account_number_hash`.

`POST /api/v1/members/{member_id}/bank-accounts/`

Request:

```json
{
  "account_holder_name": "Ramesh Patil",
  "account_number": "123456789012",
  "ifsc": "HDFC0001234",
  "bank_name": "HDFC Bank",
  "branch_name": "Nashik Road",
  "verification_status": "pending",
  "cancelled_cheque_id": null,
  "signature_verified_flag": null,
  "status": "active"
}
```

Rules:
- Requires `members.member.update` under A-034.
- Account holder name, account number, and IFSC are required. Account numbers must contain at least
  four digits. `verification_status` is limited to `pending`, `verified`, or `rejected`; `status` is
  limited to `active` or `inactive`; malformed `cancelled_cheque_id` returns
  `400 VALIDATION_ERROR`.
- The stored row keeps only a protected token, keyed hash, and last four digits for the account
  number. The create response is masked and `can_view_full` is always false.
- Successful create writes `members.bank_account.created` audit metadata with member ID,
  bank-account ID, masked last four, IFSC, verification status, signature flag, status, request/IP,
  and user-agent. Audit metadata never includes full account numbers, protected tokens, hashes,
  cheque images, or file bytes.

`GET /api/v1/members/{member_id}/cancelled-cheques/`

Rules:
- Requires `members.member.read` under A-034.
- Returns the standard top-level list envelope. Each item contains `cancelled_cheque_id`,
  nullable `loan_application_id`, `member_id`, `document_id`, masked `account_number` as
  `{ "masked": "...", "last4": "...", "can_view_full": false }`, `ifsc`, nullable
  `branch_name`, `verification_status`, `signature_mismatch_flag`, and `created_at`.
- Full account numbers, protected token values, and hashes are never serialized.

`POST /api/v1/members/{member_id}/cancelled-cheques/`

Request:

```json
{
  "loan_application_id": null,
  "document_id": "uuid",
  "account_number": "987654324321",
  "ifsc": "SBIN0000456",
  "branch_name": "Lasalgaon",
  "verification_status": "pending",
  "signature_mismatch_flag": false
}
```

Rules:
- Requires `members.member.update` under A-034.
- `document_id`, account number, and IFSC are required. `loan_application_id` is accepted only as a
  nullable UUID placeholder because real loan applications do not exist yet. `verification_status`
  is limited to `pending`, `verified`, or `rejected`.
- Successful create writes `members.cancelled_cheque.created` audit metadata with member ID,
  cheque ID, nullable loan application ID, document ID, masked last four, IFSC, verification status,
  signature mismatch flag, request/IP, and user-agent.
- Read/list endpoints write no audit row and no workflow event. Create endpoints write no workflow
  event.
- Explicit deferrals: duplicate-active-borrower warnings, bank verification letters, signature
  mismatch resolution, blank-dated cheque custody, payment initiation, disbursement readiness gates,
  bank-account full reveal, and Member Profile/Borrower360 UI wiring.

## Member Nominee API (004D)

`GET /api/v1/members/{member_id}/nominees/`

Rules:
- Requires a session-bound bearer token and `members.nominee.read`; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 PERMISSION_DENIED`, and an unknown or
  soft-deleted member returns `404 NOT_FOUND`.
- Returns the standard top-level list envelope. Each nominee item contains `nominee_id`,
  `nominee_name`, nullable `date_of_birth`, `age_at_application`, `gender`, nullable
  `relationship_to_borrower`, masked `pan`/`aadhaar` as `{ "masked": "...", "can_view_full": false }`,
  `kyc_status`, `minor_flag`, `signature_required_flag`, and `created_at`.
- Read-only nominee access writes no workflow event and no nominee-access audit row.

`POST /api/v1/members/{member_id}/nominees/`

Request data:

```json
{
  "nominee_name": "Sita Patil",
  "date_of_birth": "1985-05-20",
  "gender": "female",
  "relationship_to_borrower": "Spouse",
  "pan": "ABCDE1234F",
  "aadhaar": "123412341234",
  "signature_required_flag": true
}
```

Rules:
- Requires `members.nominee.create`, not `members.nominee.read`.
- Persists member-level nominees only. `loan_application_id` exists as nullable storage for a future
  application snapshot but is not accepted or populated by the 004D API.
- PAN and Aadhaar are required. Missing values return `400 MISSING_REQUIRED_FIELD`; invalid source
  formats return `400 INVALID_PAN_FORMAT` or `400 INVALID_AADHAAR_FORMAT`.
- Nominees below legal majority return `400 NOMINEE_MINOR_NOT_ALLOWED`; 004D uses age 18 per A-031.
- Stored identity values use protected tokens plus keyed hashes. Responses and audit logs never
  include full PAN/Aadhaar, `pan_encrypted`, `aadhaar_encrypted`, `pan_hash`, `aadhaar_hash`, or
  values derived from submitted PAN/Aadhaar identifiers.
- Successful creation returns the nominee item in the standard success envelope, sets
  `kyc_status: "pending"`, `minor_flag: false`, stores the calculated `age_at_application`, and
  writes `members.nominee.created` audit metadata without a workflow event.

## Member Shareholding API (004F)

`GET /api/v1/members/{member_id}/shareholdings/`

Rules:
- Requires a session-bound bearer token and `members.shareholding.read`; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 PERMISSION_DENIED`, and an unknown or
  soft-deleted member returns `404 NOT_FOUND`.
- Returns the standard top-level list envelope. Each item contains `shareholding_id`,
  `folio_number`, `number_of_shares`, `holding_mode`, nullable `valuation_per_share`, nullable
  `valuation_effective_date`, `pledged_share_count`, `available_share_count`,
  `future_shares_pledge_flag`, and `status`.
- Read-only shareholding access writes no workflow event and no access audit row.

`POST /api/v1/members/{member_id}/shareholdings/`

Request data:

```json
{
  "folio_number": "FOL-456",
  "number_of_shares": 100,
  "holding_mode": "physical",
  "valuation_per_share": "2000.00",
  "valuation_effective_date": "2026-04-01",
  "pledged_share_count": 15,
  "future_shares_pledge_flag": true
}
```

Rules:
- Requires `members.shareholding.create`, not `members.shareholding.read`.
- `holding_mode` is limited to `physical`, `demat`, or `mixed`. Demat account and latest valuation
  references are accepted as nullable UUID fields only when supplied; demat account table behavior
  remains deferred.
- `number_of_shares` and `pledged_share_count` must be non-negative integers, and pledged shares
  cannot exceed total shares. `available_share_count` is maintained as
  `number_of_shares - pledged_share_count` and protected by a database check constraint.
- Successful create updates the member directory/profile share summary from active shareholdings:
  total shares, total available shares, and holding mode (`mixed` when multiple active modes exist).
- Successful create writes `members.shareholding.created` audit metadata without a workflow event.
- `PATCH /api/v1/shareholdings/{shareholding_id}/`, share certificates, demat account management,
  CDSL integration, share valuation calculation, pledge eligibility, and loan-limit rules are
  deferred to later slices.

## Member Land Holding and Crop Plan API (004G)

`GET /api/v1/members/{member_id}/land-holdings/`

Rules:
- Requires a session-bound bearer token and `members.member.read` per A-032; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 PERMISSION_DENIED`, and an unknown or
  soft-deleted member returns `404 NOT_FOUND`.
- Returns the standard top-level list envelope. Each item contains `land_holding_id`,
  `document_type`, nullable location/survey fields, `area_acres`, `document_id`,
  `verification_status`, nullable verifier/timestamp fields, and `created_at`.
- Read-only list access writes no workflow event and no access audit row.

`POST /api/v1/members/{member_id}/land-holdings/`

Request data:

```json
{
  "document_type": "7_12_extract",
  "survey_number": "123/4",
  "village": "Village Name",
  "taluka": "Niphad",
  "district": "Nashik",
  "state": "Maharashtra",
  "area_acres": "5.00",
  "document_id": "uuid"
}
```

Rules:
- Requires `members.member.update` per A-032.
- `document_type`, positive `area_acres`, and valid non-null `document_id` are required.
- Successful create sets `verification_status: "pending"` and writes
  `members.land_holding.created` audit metadata without a workflow event.

`GET /api/v1/members/{member_id}/crop-plans/`

Rules:
- Requires a session-bound bearer token and `members.member.read` per A-032.
- Returns the standard top-level list envelope. Each item contains `crop_plan_id`,
  nullable `loan_application_id`, `crop_type`, nullable `season`, `planned_area_acres`,
  nullable `estimated_cost_amount`, `loan_purpose_alignment`, nullable `document_id`,
  `verification_status`, nullable verifier/timestamp fields, and `created_at`.
- Read-only list access writes no workflow event and no access audit row.

`POST /api/v1/members/{member_id}/crop-plans/`

Request data:

```json
{
  "loan_application_id": "uuid",
  "crop_type": "grapes",
  "season": "FY2026 Kharif",
  "planned_area_acres": "5.00",
  "estimated_cost_amount": "100000.00",
  "loan_purpose_alignment": "agriculture_aligned",
  "document_id": "uuid"
}
```

Rules:
- Requires `members.member.update` per A-032.
- `crop_type`, positive `planned_area_acres`, and `loan_purpose_alignment` are required.
- `loan_application_id` and `document_id` are optional, but malformed UUIDs are rejected.
- Successful create sets `verification_status: "pending"` and writes
  `members.crop_plan.created` audit metadata without a workflow event.
- Detail/update endpoints, verification actions, loan-limit calculations, scale-of-finance,
  eligibility blockers, and purpose decisions are deferred to later application/eligibility slices.

## Member KYC Profile and Document API (004H)

`GET /api/v1/kyc-profiles/?party_type=member&party_id={member_id}`

Rules:
- Requires a session-bound bearer token and `kyc.profile.read`.
- 004H supports `party_type=member` only. Unknown or soft-deleted members return `404 NOT_FOUND`.
- Success returns one profile object with status, CKYC consent, beneficial-ownership flag, risk
  rating, last verification fields, re-KYC due date, rejection reason, and embedded KYC document
  metadata. `ckyc_identifier_encrypted` and sensitive identity values are never serialized.

`POST /api/v1/kyc-profiles/` and `PATCH /api/v1/kyc-profiles/{kyc_profile_id}/`

Rules:
- Create requires `kyc.profile.create`; patch requires `kyc.profile.update`.
- Create requires `party_type`, `party_id`, and `ckyc_consent_flag`; risk rating is limited to
  `low`, `medium`, or `high`.
- Duplicate member-party create requests return `400 VALIDATION_ERROR` with `party_id:
  "A KYC profile already exists for this member."`; clients should use
  `GET /api/v1/kyc-profiles/?party_type=member&party_id={member_id}` to read the existing profile
  and `PATCH /api/v1/kyc-profiles/{kyc_profile_id}/` to update it.
- Successful create/update writes `kyc.profile.created` / `kyc.profile.updated` audit metadata only.

`POST /api/v1/kyc-profiles/{kyc_profile_id}/documents/`

Multipart fields: `document_type`, `file`, `self_attested_flag`.

Rules:
- Requires `kyc.document.upload`.
- `document_type` is limited to `pan`, `aadhaar`, `photo`, and `ckyc_consent`.
- PAN and Aadhaar require `self_attested_flag=true`.
- The uploaded file is stored as a restricted `document_files` row and returned through KYC document
  metadata only; no document download endpoint is added by 004H.
- Successful upload writes `kyc.document.uploaded` audit metadata and no workflow event.

`POST /api/v1/kyc-documents/{kyc_document_id}/verify/`

Rules:
- Requires `kyc.document.verify`.
- `verification_status` is limited to `verified` or `rejected`; remarks are optional metadata.
- Successful verification updates the KYC document verifier/timestamp and, per A-033, updates the
  profile/member KYC status and a two-year re-KYC due date for verified results.
- Successful verification writes `kyc.document.verified` audit metadata only. Audit rows exclude
  PAN/Aadhaar plaintext, identity hashes, encrypted CKYC identifiers, and file bytes.
- Re-KYC review endpoints (§18.5), KYC deficiencies, sensitive reveal, CKYC provider integration,
  appraisal/disbursement blockers, and nominee/witness/signatory KYC remain deferred.

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

## Communication adapter shell (003I)

`POST /api/v1/communications/send/`

`GET /api/v1/communications/?related_entity_type=loan_application&related_entity_id=uuid`

Protected endpoints matching `docs/source/api-contracts.md` §39.2-§39.3 and
`docs/source/data-model.md` §24.2. The send endpoint is a no-provider shell: it validates and
renders snapshots from an approved/effective `ContentTemplate`, persists one `communications` row,
and leaves delivery pending. It does not send email, SMS, courier letters, phone calls, or in-app
notifications.

Send request fields:
- Required: `related_entity_type`, `related_entity_id`, `recipient_party_type`, `channel`,
  `content_template_id`, `merge_data`.
- Optional: `recipient_party_id`, `recipient_address`.
- `related_entity_id`, `recipient_party_id`, and `content_template_id` must be UUIDs when supplied.
- `channel` is limited to `email`, `sms`, `phone`, or `courier`.
- `content_template_id` must reference an `approved` template whose `effective_from`/`effective_to`
  window includes the server's current local date.
- Per A-025, `merge_data` must exactly match `ContentTemplate.variables_json`; missing or extra keys
  return `400 VALIDATION_ERROR` before any communication or audit write.

Success data:

```json
{
  "communication_id": "uuid",
  "related_entity_type": "loan_application",
  "related_entity_id": "uuid",
  "recipient_party_type": "borrower",
  "recipient_party_id": "uuid",
  "recipient_address": "borrower@sfpcl.example",
  "channel": "email",
  "content_template_id": "uuid",
  "subject_snapshot": "Sanction LA-2026-0001",
  "body_snapshot": "Dear Ananya Rao, your loan LA-2026-0001 is sanctioned.",
  "sent_by_user_id": "uuid",
  "sent_at": null,
  "delivery_status": "pending",
  "acknowledgement_status": null,
  "external_message_id": null
}
```

List query parameters:
- Required: `related_entity_type`, `related_entity_id`.
- Optional: `page`, `page_size` using standard top-level pagination.
- Unknown query parameters or invalid UUIDs return `400 VALIDATION_ERROR`.

Rules:
- Missing bearer token returns `401 AUTH_REQUIRED`; revoked/invalid token returns the existing auth
  `401`; authenticated users without the relevant communication permission return
  `403 PERMISSION_DENIED` before any write.
- Permission assumption A-025: list/read requires `communications.communication.read` or
  `communications.communication.send`; send requires `communications.communication.send`. These
  narrow codes are used instead of broad report, document-template, or config permissions.
- Successful send writes exactly one `AuditLog` row with action
  `communications.communication.created`, `entity_type: "communication"`, and `entity_id` equal to
  the new communication id. Audit metadata includes related entity, recipient party, address,
  channel, template id, sender id, and delivery status. It deliberately omits `subject_snapshot`,
  `body_snapshot`, `merge_data`, provider credentials, and external secrets.
- M16-FR-001 through M16-FR-007 are partially traced only: this shell supports communication
  metadata/snapshot creation, template usage, delivery-status storage, and generic attachment to a
  related entity. Real email/SMS/letter delivery, manual phone-call reminder workflows, provider
  acknowledgement updates remain deferred. Current-user notification-center read/unread/action state
  is implemented separately by 003IA under `GET /api/v1/notifications/`.
- Response examples are saved in
  `.ralph/runs/2026-07-06_105004_normal_run/evidence/api-examples/communications-api-examples.json`.

## Notification inbox APIs (003IA)

`GET /api/v1/notifications/`

Protected current-user inbox endpoint for S04. It is intentionally separate from
`GET /api/v1/communications/`, which remains related-entity communication history.

Query parameters:
- Optional: `page`, `page_size` using standard top-level pagination.
- Optional: `read_status` (`all`, `read`, `unread`; default `all`).
- Optional: `severity` (`info`, `warning`, `urgent`).
- Optional: `category`.
- Unknown query parameters return `400 VALIDATION_ERROR`.

Success data items include:
- `notification_id`, optional `communication_id`, `notification_type`, `category`, `severity`,
  `title`, `message`;
- optional linked record fields `related_entity_type`, `related_entity_id`, `action_label`,
  `action_url`;
- `sender`, `recipient`, `read`, `read_at`, `read_by_user_id`, `read_state_version`, and
  `created_at`.

Response examples are saved in
`.ralph/runs/2026-07-06_164949_normal_run/evidence/api-responses/notifications-api-example.json`.

`POST /api/v1/notifications/{notification_id}/mark-read/`

Request:

```json
{ "read_state_version": 1 }
```

Rules:
- Missing bearer token returns `401 AUTH_REQUIRED`; revoked/invalid token returns the existing auth
  `401`; authenticated users without `communications.notification.read` return
  `403 PERMISSION_DENIED`.
- List and mark-read are scoped to notifications addressed directly to the current user, to the
  current user's active primary role code, or to one of the current user's active team codes.
  Other users' notifications are excluded from list results and return `404 NOT_FOUND` on mark-read.
- `read_state_version` is required on mark-read. If the submitted version does not match the
  persisted notification version, the endpoint returns `409 STALE_WRITE`.
- Successful mark-read persists `read_at`, `read_by_user_id`, increments `read_state_version`, and
  writes one `AuditLog` row with action `communications.notification.marked_read`.
- 003IA also creates a notification row when `POST /api/v1/communications/send/` addresses a staff
  recipient using `recipient_party_type` of `user`, `staff_user`, or `internal_user` and a
  `recipient_party_id` matching a backend user. Borrower/member communications and provider
  delivery remain outside this inbox.
- Permission assumption A-026: `communications.notification.read` is the narrow S04 permission and
  is seeded to active internal roles with existing source-backed permission sets. The deliberately
  permission-neutral `it_head` and `sales_team_user` demo/source roles remain ungranted pending
  source confirmation.

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

## Member portal dashboard/profile/supply APIs (005FB)

Protected borrower portal endpoints:
- `GET /api/v1/portal/dashboard/`
- `GET /api/v1/portal/profile/`
- `GET /api/v1/portal/produce-supply/`

Rules:
- The member scope comes only from the authenticated active `PortalAccount` linked to the bearer
  token user. Client-supplied `member_id` query values are ignored and never grant authority.
- If the linked `PortalAccount` becomes suspended/inactive after token issuance, the shared
  session-bound auth validator revokes the active session with reason
  `portal_account_status_changed` and these endpoints return `401 INVALID_TOKEN`.
- Staff or non-portal tokens return `403 PERMISSION_DENIED`; missing/invalid bearer tokens return
  the standard auth errors.
- Dashboard returns own member snapshot, own application counts from implemented
  `loan_applications`, active loan placeholder counts of zero until loan accounts exist, open
  deficiency pending-action count from `deficiencies`, and zero placeholders for future signature,
  repayment, KYC-update, and closure actions.
- Profile returns the existing masked member profile plus own nominees, shareholdings, land
  holdings, crop plans, KYC profile, bank accounts, and cancelled cheques. Portal profile responses
  force PAN/Aadhaar `can_view_full = false` and expose no full bank account values.
- Produce supply returns an empty read-only shell with `source_status = model_not_implemented`
  because `data-model.md` defines `produce_supply_records` but no backend model exists yet.

Frontend wiring:
- MP03, MP04, and prototype `MP22_ProduceSupply.tsx` call these endpoints through
  `sfpcl-lms/src/services/portalApi.ts` with the stored portal bearer session.

## Member portal application APIs (005G)

Protected borrower portal endpoints:
- `GET /api/v1/portal/applications/`
- `POST /api/v1/portal/applications/`
- `GET /api/v1/portal/applications/{loan_application_id}/`
- `PATCH /api/v1/portal/applications/{loan_application_id}/`
- `POST /api/v1/portal/applications/{loan_application_id}/submit/`

Rules:
- Scope comes only from the authenticated active `PortalAccount.member_id`. Query/path/payload
  member IDs cannot broaden access.
- If the linked `PortalAccount` becomes suspended/inactive after token issuance, the shared
  session-bound auth validator revokes the active session with reason
  `portal_account_status_changed`; old-token portal application calls return
  `401 INVALID_TOKEN` before creating applications, audit rows, workflow events, register rows,
  references, or visible sequence side effects.
- Staff or non-portal tokens return `403 PERMISSION_DENIED`; cross-member create/read/update/submit
  returns `403 OBJECT_ACCESS_DENIED` and creates no application, audit row, workflow event, register
  row, reference, or visible sequence side effect.
- Create/update/submit reuse the existing 005A/005B application service behavior and workflow
  events with the linked portal user as actor. Borrower portal routes write metadata-only source
  portal audit actions: `portal.application.draft_created`, `portal.application.saved`, and
  `portal.application.submitted`. Staff application routes keep internal
  `applications.loan_application.created`, `applications.loan_application.updated`, and
  `applications.loan_application.submitted` audit actions.
- Draft save can be incomplete. Submit requires existing 005B persisted facts: own member, positive
  requested amount, declared purpose, and purpose category.
- Submitted applications remain without an `LO...` reference until staff completeness pass
  generates it.
- Returned-incomplete applications serialize borrower-facing rectification state:
  `application_status = incomplete_returned`, `completeness_status = incomplete`,
  `current_stage = initial_loan_request`, `pending_with = Borrower`, open deficiency count, and
  open deficiency item metadata.
- Responses expose portal-safe application summary/detail fields only: application IDs/reference
  display, dates, requested amount, purpose, status/stage/completeness, pending owner, borrower
  action, open deficiency count, member snapshot, timeline, and open deficiency metadata.
- Responses do not expose staff completeness/reference-generation/return/resolve actions, PAN,
  Aadhaar, full bank-account values, encrypted values, token hashes, raw document contents, or
  staff-only document internals.

Example detail response:

```json
{
  "success": true,
  "data": {
    "loan_application_id": "uuid",
    "application_reference_number": null,
    "display_reference": "A1B2C3D4",
    "application_status": "submitted",
    "current_stage": "initial_loan_request",
    "completeness_status": "not_started",
    "pending_with": "SFPCL",
    "borrower_action": "No action required",
    "open_deficiency_count": 0
  }
}
```

Frontend wiring:
- MP05 saves/submits through these endpoints.
- MP09 renders list, loading, empty, error, and returned-incomplete states from
  `GET /api/v1/portal/applications/`.
- MP10 renders selected application status/detail from
  `GET /api/v1/portal/applications/{loan_application_id}/`.
