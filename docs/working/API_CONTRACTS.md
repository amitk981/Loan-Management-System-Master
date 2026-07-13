# API Contracts

## Shared authenticated permission denial (002J2)

Authenticated users who lack a required global permission receive HTTP `403` with error code
`FORBIDDEN`, matching `docs/source/api-contracts.md` §7.1. The shared envelope boundary also
normalizes the retired `PERMISSION_DENIED` code for compatibility, while production callers and the
typed object-access seam emit `FORBIDDEN` directly. Authentication/token errors and the specialized
`OBJECT_ACCESS_DENIED`, `SENSITIVE_FIELD_ACCESS_DENIED`, and `APPROVAL_AUTHORITY_REQUIRED` codes are
unchanged. This is a response-contract alignment only: permission grants, role assignments, object
scope, status codes, messages, successful payloads, audit behavior, and workflow behavior did not
change.

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
| Admin user management | Implemented in slice 002G; action-specific permission gating added in 002G2 | Admin User Management | `api-contracts.md` §6-7, §11.4, §12; `auth-permissions.md` §12.1, §15.12, §19 | `GET /api/v1/admin/users/`, `GET /api/v1/admin/users/{user_id}/`, and assignment action endpoints bind existing `Role`/`Team` catalogue rows only. All routes require session-bound bearer auth. Since 002G2 each action requires the specific canonical user-admin permission (`auth-permissions.md` §12.1), not just any user-admin grant: list/detail read requires `users.user.read` OR any write user-admin permission (read fallback per A-015 because seeded `system_admin` lacks `users.user.read`); role assignment and team add/remove require `users.user.update`; suspending a user requires `users.user.disable`; restoring a user to active requires `users.user.update`. A partial-permission actor receives `403 FORBIDDEN` with no `AuditLog` write and no session revocation. Order of checks: `401` (auth) → `403` (permission) → `400`/`404`. Successful role/team/status changes write `AuditLog`; suspending a user revokes active sessions; changing/suspending the last active `system_admin` is blocked per A-014. The frontend continues to map the write user-admin permissions to prototype `manage_users` for nav/route visibility. |
| Early end-to-end tracer | Implemented in slice 002EX | Staff Tracer screen | `docs/source/api-contracts.md` §3-6; `docs/source/data-model.md` §26.1-26.2 | Thin dev proof only. Protected by session-bound bearer auth and explicit `tracer.lifecycle.run` permission. Endpoints: `POST /api/v1/tracer/members/`, `POST /api/v1/tracer/members/{member_id}/loan-applications/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/sanction/`, `POST /api/v1/tracer/loan-applications/{loan_application_id}/loan-account/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/disburse/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/repayments/`, `POST /api/v1/tracer/loan-accounts/{loan_account_id}/close/`. Minimal models only; every transition writes `audit_logs` and `workflow_events`; invalid state transitions return `409 INVALID_STATE_TRANSITION`; missing/revoked auth returns the standard `401` envelope before domain writes. |
| API contract test harness | Implemented in slice 002J | None | `api-contracts.md` §6.1-6.4, §7.1-7.3, §44 | Test-only assertions live in `sfpcl_credit/tests/api_contracts.py`. Future endpoint slices should use them to prove standard success envelopes, error envelopes, top-level list pagination, and target §44 `available_actions` item shapes without importing test utilities from production code. The harness regression tests cover `/auth/me/`, admin users pagination, `401 AUTH_REQUIRED`, revoked-session `401 INVALID_TOKEN`, `403 FORBIDDEN`, partial-admin write denial, and tracer `409 INVALID_STATE_TRANSITION`. A-016 records that current `/auth/me/` still returns flat permission-code strings for `available_actions`; the object shape is asserted against an internal sample for future detail endpoints. |
| Local demo staff seed | Implemented in slice 002K; corrected in 002K2 | Login, dashboard smoke, admin/tracer permission smoke | `implementation-roadmap.md` §10, §20-22; `technical-architecture.md` §8-12, §17-18; `auth-permissions.md`; `api-contracts.md` §11-12, §43-44 | `python manage.py seed_demo_users` is a guarded local/dev seed path. It refuses unless `SFPCL_DEBUG=true` and `SFPCL_ALLOW_DEMO_SEED=true`, calls `seed_catalogue()`, creates or updates deterministic `demo.*@sfpcl.example` staff users with active primary roles and memberships, and does not alter `e2e.*` users. Demo users authenticate through the real `/auth/login/` and `/auth/me/` endpoints; there is no demo auth bypass. The zero-permission user returns `permissions: []` and `available_actions: []`; the tracer-only user uses the guarded local/dev-only `local_demo_tracer_user` role and returns only `tracer.lifecycle.run`; the shared source-catalogue `sales_team_user` role remains permission-neutral until source documents define grants; system admin preserves canonical action-specific user-admin permissions without broad `manage_users` aliases. |
| Role/permission/team catalogue | Seeded in slice 002C; exposed for current user in 002D | None directly | `auth-permissions.md` §12-15, §38 | Canonical `Permission`, `Role`, `Team`, `RolePermission` catalogue seeded idempotently via `python manage.py seed_role_catalogue` (`sfpcl_credit/identity/catalogue.py`). `/api/v1/auth/me/` exposes the authenticated user's effective permission codes from this data. |
| Members and KYC | Member directory list implemented in 004A; masked member profile detail implemented in 004B; nominee list/create implemented in 004D; shareholding list/create implemented in 004F; land/crop list/create implemented in 004G; KYC profile/document upload/verify implemented in 004H; member bank-account/cancelled-cheque metadata implemented in 004J; Borrower 360 Epic 004 UI wiring implemented in 004K with corrective DTO hardening queued in 004K2 | Member Directory, Member Profile, borrower profile, application intake | `api-contracts.md` §13.1/§13.3/§13.5/§14.1-§14.3/§15.1-§15.2/§17.1-§18.4; `data-model.md` §10.1-§10.4/§11.1/§11.7-§12.4; `auth-permissions.md` §12.2-§12.3/endpoint map | `GET /api/v1/members/` is API-backed with standard list pagination, `members.member.read`, masked mobile numbers, no PAN/Aadhaar fields, and strict §13.1 query validation. `GET /api/v1/members/{member_id}/` returns masked PAN/Aadhaar objects, address, profile shell fields, share/active-member shell fields, and object-shaped `available_actions[]`. `GET/POST /api/v1/members/{member_id}/nominees/`, `/shareholdings/`, `/land-holdings/`, `/crop-plans/`, `/bank-accounts/`, and `/cancelled-cheques/` are API-backed with their documented validations and metadata-only create audits. `GET/POST/PATCH /api/v1/kyc-profiles/`, KYC document upload, and KYC document verify are implemented for member parties only with KYC permissions. Sensitive bank-account reveal, re-KYC task management, share certificate/demat, bank verification letters, disbursement bank gates, and loan-application/loan-account/repayment/risk/audit Borrower 360 data remain future scope. |
| Loan applications | Draft create/read/update implemented in 005A; submit in 005B; reference generation/register persistence in 005C; object access hardened in 005C2; application document/checklist metadata implemented in 005D; completeness workbench/pass implemented in 005E; deficiency return/list/resolve implemented in 005F; rejection-note create/send shell implemented in 005H; staff list/register UI wiring reads implemented in 005I; staff detail rejection-note summary hardening implemented in 005I2; eligibility assessment through default/document/terms/purpose/nominee checks implemented in 006A-006B; loan-limit calculation and snapshots implemented in 006C-006D; cultivated-acreage source hardening implemented in 006C2 | Applications, completeness, rejection note shell, Loan Request Register, eligibility assessment, loan-limit assessment | `api-contracts.md` §8, §19.1-§23; `screen-spec.md` S13/S15; `data-model.md` §13.1, application-document/deficiency/rejection-note/register tables, and §14.1-§14.2; `auth-permissions.md` §12.4, §19.2, §34.3, §37.3 | Existing loan-application, register, document, checklist, completeness, deficiency, rejection-note, and eligibility endpoints retain their documented contracts. `POST /api/v1/loan-applications/{id}/loan-limit-assessment/calculate/` requires a stored normally eligible assessment, same-member verified source facts, an application-linked verified crop plan, agreement among applicable cultivated-acreage evidence, an active Board-referenced policy version, `credit.loan_limit.calculate`, and existing application object access; it atomically snapshots the lower of shareholding/land limits with audit and workflow evidence. Staff detail reads include nullable `rejection_note` summary metadata when a staff rejection note exists; `application_status` remains backend-owned and unchanged by the summary. Staff list reads support standard `search`, `application_status`/`status`, `current_stage`, `member_id`, `ordering`, `page`, and `page_size` with `page_size` capped at 100. Register reads support `search`, `register_status`/`status`, `current_stage`, `member_type`, `ordering`, `page`, and `page_size`. Appraisal, sanction, document generation, real communication delivery, and disbursement remain future slices. |
| Appraisal and loan limit | Eligibility/loan limit implemented through 006D2C; appraisal preparation, frozen provenance, Credit Manager review/return/rejection, immutable review history, and legacy remediation implemented through 006E4 | Appraisal workbench | `functional-spec.md` §9.8/M04; `api-contracts.md` §22-§24 | Appraisals freeze canonical redacted eligibility and loan-limit projections, block unproven legacy provenance until explicit scoped revalidation, enforce both `credit.appraisal.review` and active `credit_manager` role authority, retain every review reason in appraisal-owned append-only history, and create the existing rejection-note draft for terminal rejection. Legacy draft and review-pending rows can pin current projections without inheriting review authority; a legacy reviewed row reopens to draft and requires maker resubmission plus fresh Credit Manager review. Rejected/submitted terminal rows remain quarantined for governed repair. |
| Sanction and approvals | Approval workflow/workbench implemented through 007L; later register/settings closure remains queued | Sanction workbench, registers, approval settings | `auth-permissions.md`, `api-contracts.md` §25/§44, `screen-spec.md` S21-S25 | Approval matrix is high-control; case reads and actions use frozen actor-scoped projections. |
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
- The authenticated user's effective permission list must include `tracer.lifecycle.run`; otherwise the API returns `403 FORBIDDEN`.
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
- Authenticated users without canonical user-admin permission return `403 FORBIDDEN`.
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
- Missing bearer token returns `401 AUTH_REQUIRED`; users without `members.member.read` return `403 FORBIDDEN`.
- Unknown query parameters or unsupported enum values return `400 VALIDATION_ERROR` with `field_errors`.
- The directory response never includes PAN or Aadhaar fields. `mobile_number` is masked to last four digits.
- Read-only list access writes no audit/workflow event. Exports, create/update, nominee, witness, KYC verification, share certificate, demat, land/crop, loan application, and Borrower 360 behavior are explicitly deferred.

## Member Profile Detail API (004B, extended by 004C)

`GET /api/v1/members/{member_id}/`

Rules:
- Requires a session-bound bearer token and `members.member.read`; missing auth returns
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and a valid UUID that is
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
  base read returns `403 FORBIDDEN`; missing field-specific permission returns
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
  "nominee_id": "uuid",
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
`nominee_id` may be null while a draft is incomplete, but a supplied value must identify one
same-member nominee with adult age/date-of-birth evidence. Cross-member, unknown, minor, and
missing-age selections return `400 VALIDATION_ERROR` without application/audit/workflow changes.

Staff detail serializes `nominee` as metadata only: `nominee_id`, `nominee_name`, nullable
`age_at_application`, `minor_flag`, `kyc_status`, nullable `relationship_to_borrower`,
and `signature_required_flag`. It never includes PAN/Aadhaar values,
tokens, hashes, or reveal controls.

Staff list/detail return `assigned_owner: null` until an assignment/task owner is persisted by its
owning future slice. `received_by_user` and `created_by_user` remain intake/audit facts and are never
projected as assignment facts. Detail also returns §44-shaped `available_actions[]`. The currently implemented
detail action is `submit`: it is returned only to an object-scoped actor with
`applications.loan_application.submit` while the application is a draft, and its `enabled` /
`disabled_reason` fields reflect whether the persisted submit facts are complete. Submitted and
later-stage applications return an empty action list until their owning workflow APIs supply
actions. Documentation, sanction, security, SAP, and disbursement facts remain absent rather than
being inferred by the detail response or frontend.

`POST /api/v1/loan-applications/{loan_application_id}/submit/`

Request body is accepted as a JSON object. A stored adult `nominee_id` is required. `submission_notes` may be supplied by clients, but 005B
does not persist notes because no source-backed column exists yet.

`POST /api/v1/loan-applications/{loan_application_id}/generate-reference/`

Request body is accepted as a JSON object. In 005C this endpoint represents the successful
completeness-pass transition only; it requires the stored nominee selection but does not evaluate document checklist items,
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
  "nominee": {
    "nominee_id": "uuid",
    "nominee_name": "Sita Patil",
    "age_at_application": 42,
    "minor_flag": false,
    "kyc_status": "verified",
    "relationship_to_borrower": "Spouse",
    "signature_required_flag": true
  },
  "nominee_selection_status": "valid",
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
  "can_generate_reference": false,
  "available_actions": [
    {
      "action_code": "pass_completeness",
      "label": "Generate reference number",
      "enabled": false,
      "disabled_reason": "Required nominee and document checks must be complete.",
      "required_permission": "applications.loan_application.complete_check",
      "required_role": "deputy_manager_finance"
    }
  ]
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

Returns `{ "loan_application_id": "uuid", "items": [...], "available_actions": [...] }` using
the deficiency item shape above and the same completeness resource-action projection as the
completeness read.

`POST /api/v1/deficiencies/{deficiency_id}/resolve/`

Request:

```json
{
  "resolution_notes": "Nominee Aadhaar uploaded and verified."
}
```

Success returns the resolved deficiency item with `resolution_status = resolved`, resolver actor,
and `resolved_at`.

`POST /api/v1/loan-applications/{loan_application_id}/rejection-note/`

Request:

```json
{
  "rejection_stage": "credit_assessment",
  "rejection_reason_category": "eligibility",
  "detailed_reason": "Borrower does not meet active member criteria.",
  "reapply_allowed_flag": true,
  "communication_mode": "email"
}
```

Success data:

```json
{
  "rejection_note_id": "uuid",
  "loan_application_id": "uuid",
  "rejection_stage": "credit_assessment",
  "rejection_reason_category": "eligibility",
  "detailed_reason": "Borrower does not meet active member criteria.",
  "reapply_allowed_flag": true,
  "note_status": "draft",
  "communication_status": "not_sent",
  "prepared_by_user_id": "uuid",
  "approved_by_user_id": null,
  "communication_mode": "email",
  "communication_id": null,
  "sent_by_user_id": null,
  "sent_at": null,
  "created_at": "2026-07-10T01:57:23Z",
  "updated_at": "2026-07-10T01:57:23Z",
  "updated_by_user_id": "uuid"
}
```

`POST /api/v1/rejection-notes/{rejection_note_id}/send/`

Request:

```json
{
  "recipient_email": "borrower@example.com",
  "message_override": null
}
```

Success returns the rejection note shape above with `note_status = sent`,
`communication_status = sent`, `sent_by_user_id`, and `sent_at` populated. The derived
`communication_status` is `not_sent` while `sent_at` is null. The send endpoint is a
metadata/status transition only in 005H; it does not call a real email/SMS/courier provider and
does not create a `communications` row.

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
- 005E2 wires the staff Completeness Workbench to the list, document-checklist,
  completeness-check, deficiency, and rejection-note APIs with no mock fallback. Submitted and
  `incomplete_returned` queue rows are requested as separate status-filtered list reads. 005E4
  completes the six-field §44 `available_actions` on completeness and deficiency reads. Pass,
  return, resolve, and rejection-note creation respectively require
  `applications.loan_application.complete_check`,
  `applications.loan_application.return_deficiency`, `applications.deficiency.resolve`, and
  `applications.rejection_note.create`; each projection and write boundary uses the same
  application object scope and state/resource predicate. The UI intersects that projection with
  `/auth/me` only for usability and never infers resource authority. Pass sends `{}`; return sends only
  `communication_mode`, `message`, and current blocker `items[{item_code, remarks?}]`; deficiency
  resolution sends only `resolution_notes`; rejection-note creation sends the exact 005H draft
  fields. Every successful action re-reads the canonical queue, document checklist, completeness,
  and full deficiency history. A `409` is not retried and refresh occurs only after an explicit
  user choice.
- The pass endpoint first enforces submitted/non-duplicate state and returns
  `409 INVALID_STATE_TRANSITION` for draft, already-reference-generated, or register-existing
  applications. It then evaluates the latest 005D metadata row for each mandatory application-stage
  document code and requires `submission_status = submitted` plus
  `verification_status = verified`. Missing latest metadata returns `reason_code =
  missing_metadata`; submitted but pending/rejected latest metadata returns `reason_code =
  not_verified`. Validation failures return `400 VALIDATION_ERROR` with item-level
  `required_checklist_items` and create no sequence/register/audit/workflow side effects.
- Return-with-deficiencies requires `applications.loan_application.return_deficiency`; deficiency
  list requires `applications.loan_application.read`; deficiency resolve requires
  `applications.deficiency.resolve`. All reuse
  `applications.services.evaluate_application_object_access(...)` after global permission and
  `404` checks.
- Rejection-note creation requires `applications.rejection_note.create`; the separate send shell
  retains its existing send boundary pending its owning workflow work. Both endpoints reuse the
  application object-access boundary after global permission and `404` checks. Borrower portal
  tokens have only portal own-data permissions and receive `403 FORBIDDEN` on staff
  rejection-note routes; suspended portal sessions receive `401 INVALID_TOKEN` before any
  rejection-note side effect.
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
- Rejection-note creation is limited to submitted applications without an `LO...` reference, loan
  request register entry, or existing rejection note. Draft, already-returned
  `incomplete_returned`, reference-generated, and duplicate-create attempts return
  `409 INVALID_STATE_TRANSITION` and create no rejection note, success audit row, workflow event,
  reference, register row, or sequence advancement.
- Rejection-note payload validation requires `rejection_stage`, `rejection_reason_category`,
  nonblank `detailed_reason`, boolean `reapply_allowed_flag` when supplied, and
  `communication_mode`; unknown fields return `400 VALIDATION_ERROR`. Supported stages are
  `completeness`, `credit_assessment`, and `sanction_committee`. Supported reason categories are
  `missing_document`, `eligibility`, `default`, `purpose_mismatch`, `limit_issue`,
  `committee_rejection`, and `other`. Supported communication modes are `email`, `courier`,
  `hard_copy`, and `sms_summary`.
- Successful rejection-note creation writes one `rejection_notes` row with `note_status = draft`,
  writes `applications.rejection_note.created` metadata-only audit, and records a
  `rejection_note` workflow event into `draft`. It does not change `loan_applications` status in
  005H because the current source-backed status vocabulary lacks a generic intake rejection state;
  A-045 records this deferral.
- Send requires an existing draft rejection note and a nonblank `recipient_email`. Unknown send
  fields return `400 VALIDATION_ERROR`; duplicate send attempts return `400 VALIDATION_ERROR` with
  no second audit/workflow event. Successful send stamps `sent_by_user_id` and `sent_at`, writes
  `applications.rejection_note.sent` metadata-only audit, and records a `rejection_note` workflow
  event from `draft` to `sent`.
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
- 005I2 staff detail responses additionally include `rejection_note`, either `null` or a
  metadata-only summary with `rejection_note_id`, `note_status`, `rejection_stage`,
  `rejection_reason_category`, `reapply_allowed_flag`, prepared/approved/sent actor IDs,
  timestamps, `communication_mode`, and nullable `communication_id`. Staff detail does not include
  rejection-note `detailed_reason`, does not change `application_status`, and read-only detail
  access writes no success audit/workflow event. Borrower portal application routes continue to
  omit staff rejection-note metadata.
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
  `403 FORBIDDEN`; object-scope mismatches return `403 OBJECT_ACCESS_DENIED`; invalid submit
  facts return `400 VALIDATION_ERROR`; re-submit, other non-draft submit, draft reference generation,
  or duplicate reference attempts return `409 INVALID_STATE_TRANSITION`. Object-access denials do
  not write success audit rows, workflow events, register rows, application references, or visible
  sequence advancement. Return-with-deficiencies permission/object denials additionally create no
  deficiency rows and no deficiency success audit/workflow events. Rejection-note permission/object
  denials additionally create no rejection-note rows and no rejection-note success audit/workflow
  events.

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
  returns `403 FORBIDDEN`.
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
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and an unknown or
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
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and an unknown or
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
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and an unknown or
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
  `401 AUTH_REQUIRED`, missing permission returns `403 FORBIDDEN`, and an unknown or
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
  authenticated user without the audit-read permission → `403 FORBIDDEN`.

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
  authenticated user without `audit.workflow_event.read` → `403 FORBIDDEN`.
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
  permission return `403 FORBIDDEN` with no config/audit/version write.

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
  `403 FORBIDDEN`.
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
  `403 FORBIDDEN`.
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
  auth `401`; authenticated users without content-template permission return `403 FORBIDDEN`
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
  `403 FORBIDDEN` before any write.
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
  `403 FORBIDDEN`.
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
  authenticated user without the dashboard scope returns `403 FORBIDDEN`.
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
  token user. A client-supplied `member_id` query value that differs from that account returns
  `403 OBJECT_ACCESS_DENIED`; it is never ignored, disclosed, or used for a read/write.
- If the linked `PortalAccount` becomes suspended/inactive after token issuance, the shared
  session-bound auth validator revokes the active session with reason
  `portal_account_status_changed` and these endpoints return `401 INVALID_TOKEN`.
- Staff or non-portal tokens return `403 FORBIDDEN`; missing/invalid bearer tokens return
  the standard auth errors.
- Dashboard returns own member snapshot, own application counts from implemented
  `loan_applications`, active loan placeholder counts of zero until loan accounts exist, open
  deficiency pending-action count from `deficiencies`, and zero placeholders for future signature,
  repayment, KYC-update, and closure actions.
- Profile returns the existing masked member profile plus own nominees, shareholdings, land
  holdings, crop plans, KYC profile, bank accounts, and cancelled cheques. Portal profile responses
  force PAN/Aadhaar `can_view_full = false` and expose no full bank account values.
- Produce supply returns portal-account-scoped persisted records with no member identifier or
  staff actions. Every record includes the member module's `qualifying` boolean and stable nullable
  `non_qualifying_reason`; summary includes the immutable `result_id` and
  `calculated_as_of_date`. `source_status` is `persisted_qualifying_verified_records` when source-eligible
  verified history exists and `persisted_no_qualifying_verified_records` otherwise. Summary totals
  and continuity derive only from canonical-year, eligible-entity/route, evidence-referenced,
  verified rows; pending and malformed legacy rows remain visible but do not contribute.
  because `data-model.md` defines `produce_supply_records` but no backend model exists yet.

Frontend wiring:
- MP03, MP04, and prototype `MP22_ProduceSupply.tsx` call these endpoints through
  `sfpcl-lms/src/services/portalApi.ts` with the stored portal bearer session.

### Staff produce-supply capture and verification (006Z/006Z3)

- `POST /api/v1/members/{member_id}/produce-supply-records/` requires
  `members.active_status.calculate` and an object body containing the current integer member
  `version`, canonical `financial_year` (`YYYY-YY`), eligible `supplied_to_entity_type`, consistent
  `supply_route`, and non-blank `evidence_reference`. Unknown fields, invalid UUID relationships,
  and negative/over-precision quantity or value facts return `400 VALIDATION_ERROR`; stale member
  versions return `409 STALE_WRITE` without record, history, or audit evidence.
  An existing member outside the actor's action-specific persisted scope returns
  `403 OBJECT_ACCESS_DENIED` without supply, member-version, history, or audit writes.
- Direct supply forbids `producer_institution_member_id`; the Producer Institution route requires
  an active, non-self FPC/Producer Institution member UUID. Subsidiary and step-down subsidiary
  destinations require `supplied_to_entity_id`.
- `POST /api/v1/produce-supply-records/{record_id}/verify/` retains maker-checker separation and
  the current supply-record `version`; stale verification returns `409 STALE_WRITE`. Object-scope
  denial is `403 OBJECT_ACCESS_DENIED`, while maker-checker denial remains `403 FORBIDDEN`.
- `POST /api/v1/members/{member_id}/active-status/verify/` requires
  `members.active_status.verify` plus `result_id`, current member `version`, ISO `as_of_date`,
  `decision` (`active`, `inactive`, or `relaxation`), and a non-blank `reason`; missing/future dates
  and unknown fields return `400 VALIDATION_ERROR`. The permission authorizes only the named action;
  object access additionally requires the same persisted, action-specific member-scope assignment
  used by member list/detail (`global`, actor-team/member, actor/member assignment, or created-by).
  Role provenance, action permission alone, caller flags, and unowned records never create scope.
  A missing or existing out-of-scope member returns the same `403 OBJECT_ACCESS_DENIED`. The
  calculated route and decision must
  agree exactly (`pass`/`active`, `relaxation`/`relaxation`, otherwise `inactive`); mismatches return
  `409 INVALID_DECISION`. It rejects actors who captured or verified any qualifying supply/service/
  relaxation evidence, stale/changed results, stale versions, unsupported decisions,
  and repeated decisions without audit/history evidence. A winner returns the exact complete dated
  result snapshot and atomically creates an effective-dated `active_member_statuses` record, closes
  the prior current record, points the Member projection at the new record primary key, and records
  the same projection in member history and audit. Internal snapshots retain row/evidence/verifier
  facts; borrower portal supply rows deliberately omit those internal fields.

### Staff member list/detail scope and nondisclosure (006Z11)

- `GET /api/v1/members/` first requires `members.member.read`, then applies the authenticated
  actor's persisted action-specific member scope before search, filtering, count, and pagination.
  `pagination.total_count`, pages, and rows therefore contain no fact about excluded members.
- `GET /api/v1/members/{member_id}/` applies the identical predicate. An existing excluded member
  returns `403 OBJECT_ACCESS_DENIED`; an in-scope unknown identifier returns `404 NOT_FOUND`.
- Scope and action are independent. A global assignment for read does not authorize verify,
  identity approval, update, calculation, or evidence maintenance; each write requires its own
  action permission and assignment/creator fact. No default global assignment is seeded.
- Service/relaxation evidence retains every creator and material updater as immutable maker
  provenance. Any maker is denied verification of a derived active-member result with zero status,
  history, audit, or workflow writes, even after another actor updates the evidence.

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
- Staff or non-portal tokens return `403 FORBIDDEN`; cross-member create/read/update/submit
  returns `403 OBJECT_ACCESS_DENIED` and creates no application, audit row, workflow event, register
  row, reference, or visible sequence side effect.
- Create/update/submit reuse the existing 005A/005B application service behavior and workflow
  events with the linked portal user as actor. Borrower portal routes write metadata-only source
  portal audit actions: `portal.application.draft_created`, `portal.application.saved`, and
  `portal.application.submitted`. Staff application routes keep internal
  `applications.loan_application.created`, `applications.loan_application.updated`, and
  `applications.loan_application.submitted` audit actions.
- Draft save can be incomplete. Create/update accept `nominee_id` through the shared application
  nominee-validation module interface. Unknown, cross-member, minor, and missing-age-evidence
  create/PATCH attempts return `400 VALIDATION_ERROR` with `field_errors.nominee_id` and preserve
  the previously serialized application, status, selection, audit counts, and workflow counts.
  Submit requires own member, positive requested amount, declared purpose, purpose
  category, and one stored adult own-member nominee.
- Submitted applications remain without an `LO...` reference until staff completeness pass
  generates it.
- Returned-incomplete applications serialize borrower-facing rectification state:
  `application_status = incomplete_returned`, `completeness_status = incomplete`,
  `current_stage = initial_loan_request`, `pending_with = Borrower`, open deficiency count, and
  open deficiency item metadata.
- Detail responses expose the same metadata-only `nominee` summary as staff detail. MP10 renders
  nominee ID, name, age snapshot, minor/adult status, KYC status, relationship, and signature-required
  status. Responses expose portal-safe application summary/detail fields only: application IDs/reference
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

### Portal application limit projection (006Z2)

- `GET /api/v1/portal/application-limit-projection/?requested_amount={money}` derives member scope
  only from the active `PortalAccount` and is read-only. A different client-supplied `member_id`
  returns `403 OBJECT_ACCESS_DENIED` without assessment, audit, or workflow writes.
- `status = available` returns the server-calculated shareholding, land, and effective lower limit,
  the effective policy version/date, and the server-owned requested-amount advisory flags.
- Missing, stale, future, closed, manual, or provenance-mismatched active-member authority—and
  incomplete or contradictory verified share/land facts—returns `status = unavailable` with null
  amounts and no guessed zero.
- The response deliberately omits member/effective-record/result IDs, evidence rows/references,
  verifier and decision facts, configuration IDs, and staff actions.

## Eligibility assessment APIs (006A-006B)

Protected staff endpoints:
- `POST /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/run/`
- `GET /api/v1/loan-applications/{loan_application_id}/eligibility-assessment/`

Rules:
- Run requires `credit.eligibility.run` and the existing loan-application object-access boundary.
  A user missing the global run permission receives `403 FORBIDDEN`; a user with the
  permission but outside the application scope receives `403 OBJECT_ACCESS_DENIED`.
  After application authority succeeds, a query/body `member_id` different from the application's
  stored member also returns `403 OBJECT_ACCESS_DENIED` without assessment, audit, or workflow
  writes; the actorless member calculation always derives its member from the application.
- Read requires the existing `applications.loan_application.read` permission and object-access
  boundary used by application detail.
- Missing applications return `404 NOT_FOUND`. Reading before an assessment exists returns
  `404 NOT_FOUND`.
- Run is allowed only after formal reference generation: `application_reference_number` starts
  with `LO`, `application_status = reference_generated`, `completeness_status = complete`, and
  `current_stage = credit_assessment`. Other states return `409 INVALID_STATE_TRANSITION`.
- `member_active_check` is calculated through `members.modules.active_member_status`:
  - `pass` when an active individual/FPC/Producer Institution has recorded service usage and four
    uninterrupted, completed financial years of qualifying verified produce-supply evidence.
  - `relaxation` for an individual with three recorded continuous employment/service years, or for
    a recorded relaxation backed by at least one completed qualifying supply year.
  - `fail` when the member's `membership_status` is not `active`.
  - `manual_evidence_required` when BR-004 through BR-007 require produce/service history but the
    current persistence has no source-backed history rows to calculate it.
- Responses persist and expose `active_member_snapshot`, including `result_id`,
  `calculated_as_of_date`, member/rule route facts, continuity, and every classified supply row.
  Later member/supply changes never rewrite an application's stored eligibility snapshot.
- 006B computes these additional source-backed checks:
  - `default_check = no_default` only when `Member.default_status = no_default`; other existing
    default-like values return `default_found`.
  - `document_check = complete` only when the 005D/005E required checklist metadata has no
    blocking submitted/verified item; otherwise it returns `incomplete`.
  - `terms_acceptance_check = accepted` only when `LoanApplication.terms_acceptance_flag = true`;
    otherwise it returns `pending`.
  - `purpose_check = agriculture_aligned` only when `purpose_category` is `crop_production` or
    `agriculture_activity`; otherwise it returns `non_agriculture`.
  - `nominee_check` reads only `LoanApplication.nominee`: `valid` for the stored adult nominee,
    `minor` for a legacy invalid stored nominee, and `pending` for a legacy null or missing-age
    selection. Reverse-linked member nominee rows never influence the result.
- `overall_result = eligible` only when every implemented check passes. It is `ineligible` when
  membership/default/document/terms/purpose/minor-nominee blockers fail, and
  `pending_manual_evidence` when active-member or application-specific nominee evidence remains
  unresolved.
- Ineligible assessment results do not advance `application_status` or `current_stage`.
- Successful run writes metadata-only `eligibility.assessed` audit and an
  `eligibility_assessment` workflow event. Denied and invalid-state paths create no assessment,
  audit row, or workflow event.

Response data fields:

```json
{
  "eligibility_assessment_id": "uuid",
  "loan_application_id": "uuid",
  "member_active_check": "pass",
  "default_check": "no_default",
  "document_check": "complete",
  "terms_acceptance_check": "accepted",
  "purpose_check": "agriculture_aligned",
  "nominee_check": "valid",
  "overall_result": "eligible",
  "assessment_notes": "All mandatory eligibility criteria passed.",
  "assessed_by_user_id": "uuid",
  "assessed_at": "2026-07-10T00:00:00Z"
}
```

## Loan-limit calculation and stored snapshot APIs (006C-006D)

Protected staff endpoints:
- `POST /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/calculate/`
- `GET /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/`

Request fields:
- `shareholding_id`, non-empty `land_holding_ids`, `crop_plan_id`, positive `requested_amount`,
  and ISO `calculation_date` are required; unknown fields return `400 VALIDATION_ERROR`.

Rules:
- Requires `credit.loan_limit.calculate` plus the existing application object-access boundary.
- Requires the stored 006B assessment to have `overall_result = eligible`; absent,
  `pending_manual_evidence`, and `ineligible` assessments return `409 INVALID_STATE_TRANSITION`.
- Shareholding, every land holding, and crop plan must belong to the application member. Every
  selected land holding must be `verified`. The selected crop plan must be `verified`, linked to
  this loan application, and agriculture aligned. Null crop-plan links, links to another
  application, and non-agriculture-aligned crop plans are rejected. The request amount must match
  the persisted application request amount.
- Cultivated acreage is accepted only when the normalized Decimal values agree across the total
  selected verified land acreage, the application-linked verified crop plan's planned acreage, and
  the member profile's `land_area_under_cultivation_acres` when that profile value exists. Decimal
  formatting differences such as `5`, `5.0`, and `5.00` are equal. A disagreement returns
  `400 VALIDATION_ERROR` with `error.field_errors.cultivated_acreage =
  "CULTIVATED_ACREAGE_UNRESOLVED"` and creates no assessment, audit, or workflow evidence.
- Exactly one active loan policy must cover `calculation_date`; it must include Board approval
  metadata, a positive scale of finance, and a positive percentage and/or per-share cap. Missing,
  overlapping, or unresolved policy configuration returns `400 VALIDATION_ERROR` and creates no
  calculation evidence.
- Percentage rule: `valuation_per_share × percentage / 100`; when a per-share cap is configured,
  it is the ceiling. Share limit is shares multiplied by the resulting per-share amount.
- Land limit uses the agreed cultivated acreage multiplied by configured scale of finance. Final
  eligible amount is the lower of share and land limits.
- Requested amount equal to or below the final limit needs no exception. An amount above it sets
  both boundary flags and returns `REQUESTED_AMOUNT_EXCEEDS_LIMIT`.
- A successful rerun updates the one-to-one assessment while preserving its UUID. Each successful
  calculation atomically writes `loan_limit.calculated` audit metadata and a
  `loan_limit_assessment` workflow event; denied/invalid/validation paths write none.
- GET requires `applications.loan_application.read` and the existing application object-access
  boundary. It returns `404 NOT_FOUND` when the application or stored assessment does not exist.
- GET performs no calculation and writes no audit/workflow evidence. Every response field below,
  including warning output and `configuration_source`, is serialized from the assessment row.
- Number/share valuation, percentage/cap, land area/scale, all computed amounts, requested amount,
  boundary flags, member/shareholding identifiers, rule version, actor/time, and policy config
  UUID/name/Board reference are immutable snapshot facts until a new successful calculate call
  replaces them. Changes to application, member source records, land/crop/shareholding rows, or
  loan-policy config do not alter an existing GET response.
- Failed reruns leave the prior assessment and evidence counts unchanged. Successful rerun audit
  metadata contains the complete prior and replacement assessment snapshots.

Response data fields:

```json
{
  "loan_limit_assessment_id": "uuid",
  "loan_application_id": "uuid",
  "member_id": "uuid",
  "shareholding_id": "uuid",
  "number_of_shares": 100,
  "valuation_per_share": "2000.00",
  "share_limit_percentage": "10.0000",
  "per_share_cap_amount": "200.00",
  "shareholding_based_limit_amount": "20000.00",
  "land_area_acres": "5.00",
  "scale_of_finance_per_acre_amount": "20000.00",
  "land_based_limit_amount": "100000.00",
  "final_eligible_loan_amount": "20000.00",
  "requested_amount": "400000.00",
  "amount_within_limit_flag": false,
  "exception_required_flag": true,
  "calculation_rule_version": "loan-policy-v1.0",
  "configuration_source": {
    "type": "loan_policy_config",
    "loan_policy_config_id": "uuid",
    "policy_name": "Board-approved member loan policy",
    "board_approval_reference": "BOARD/2026/006C"
  },
  "calculated_by_user_id": "uuid",
  "calculated_at": "2026-07-10T00:00:00Z",
  "warnings": [
    {
      "code": "REQUESTED_AMOUNT_EXCEEDS_LIMIT",
      "message": "Requested amount exceeds final eligible loan amount."
    }
  ]
}
```

## Appraisal-note preparation and Credit Manager review APIs (006E/006E2/006F/006F2/006E3/006E4)

Protected staff endpoints:
- `POST /api/v1/loan-applications/{loan_application_id}/appraisal-note/`
- `GET /api/v1/loan-applications/{loan_application_id}/appraisal-note/`
- `PATCH /api/v1/loan-applications/{loan_application_id}/appraisal-note/`
- `POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/submit-for-review/`
- `POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/revalidate-prerequisites/`
- `POST /api/v1/appraisal-notes/{loan_appraisal_note_id}/review/`

Rules:
- Create requires `credit.appraisal.create`, `credit.risk_assessment.manage`, and the existing
  application object-access boundary. It requires a stored eligibility projection with
  `overall_result = eligible` and a stored loan-limit projection; missing or non-eligible facts
  return `409 INVALID_STATE_TRANSITION` without appraisal, risk, audit, or workflow rows.
- One appraisal and one linked risk assessment are stored per loan application. Create copies the
  exact canonical redacted projections returned by `EligibilityAssessmentModule` and
  `LoanLimitCalculator`, plus their UUID provenance. GET, PATCH amount/exception validation,
  submit, review, and sanction consumers use those appraisal-owned frozen projections; a later
  successful same-UUID assessment rerun cannot reinterpret the appraisal.
- Required summaries and `repayment_capacity_notes` are non-blank. Recommended amount is positive; optional tenure is a positive
  integer; supplied interest type is `floating`; recommendation is `approve`, `reject`, or
  `conditions`; all four risk ratings are `low`, `medium`, or `high`. Unknown top-level or nested
  fields return `400 VALIDATION_ERROR`.
- A recommendation above the frozen final eligible amount is rejected unless that frozen
  loan-limit projection already has `exception_required_flag = true`; this contract does not create an
  exception approval.
- PATCH is draft-only and changes supplied fields only. It requires `credit.appraisal.update`;
  changing nested risk fields additionally requires `credit.risk_assessment.manage`.
- GET is side-effect free and is allowed to scoped holders of create/update/submit-review or the
  Credit Manager review permission. Missing notes return `404 NOT_FOUND`.
- `tat_due_at` is application `created_at + 2 days` and never resets. At the exact due instant TAT
  is `within_tat`; later preparation/submission is `breached`.
- Submit requires `credit.appraisal.submit_review`, object scope, and non-blank `remarks`; it
  persists trimmed remarks on the appraisal and atomically transitions `draft -> review_pending`
  once. Submit additionally requires `prerequisite_provenance = verified`; repeated submit and
  later PATCH return `409 INVALID_STATE_TRANSITION`.
- The revalidation action accepts only `{}`, requires `credit.appraisal.update` plus
  `credit.risk_assessment.manage` and object scope, and replaces prerequisite IDs/projections/
  provenance with the current public eligible projections. Malformed JSON and unknown fields
  return `400 VALIDATION_ERROR` without writes. A legacy `draft` stays draft; a legacy
  `review_pending` stays pending for an independent Credit Manager decision. A legacy `reviewed`
  row returns to `draft` and clears only its mutable latest-review projection (decision, comments,
  reviewer, and decision time), while immutable `review_history[]` remains unchanged. It then
  requires maker resubmission and a fresh review before sanction. Legacy `rejected` and
  `submitted_to_sanction_committee` rows return `409 INVALID_STATE_TRANSITION` and remain visibly
  quarantined for governed manual repair. Revalidation never changes recommendation, repayment,
  risk, summary, TAT, preparer, or prior-history facts.
- Create/update/submit write `appraisal.created`, `appraisal.updated`, or
  `appraisal.submitted_for_review` metadata-only audit/workflow evidence. Free-text summaries,
  mitigation notes, repayment-capacity notes, and submit remarks are never copied into evidence
  JSON. Submit audit metadata records only `submission_reason_exists` and its appraisal owner ID;
  revalidation metadata records projection UUIDs, provenance, prior/new appraisal state, and a
  boolean review-authority-invalidated flag only; it does not copy review comments, appraisal
  summaries, financial values, or risk text.
- Review always requires `decision` and non-blank `review_comments`; `decision` is `reviewed`,
  `returned`, or `rejected`. `reviewed` and `returned` continue to accept exactly those two fields.
  `rejected` additionally requires the existing 005H rejection-note fields
  `rejection_reason_category`, non-blank `detailed_reason`, boolean `reapply_allowed_flag`, and
  `communication_mode`; the workflow fixes `rejection_stage = credit_assessment`. Missing, invalid,
  blank, or unknown fields return `400 VALIDATION_ERROR` without success evidence.
- Every review decision requires `credit.appraisal.review`, active primary-role membership as
  `credit_manager`, Credit Manager credit-domain object access, `review_pending` state,
  `prerequisite_provenance = verified`, and a reviewer other than the preparer. Permission granted
  to another role and owner/receiver scope do not confer review authority. Missing role/permission
  returns `403 FORBIDDEN`; an actual Credit Manager outside the domain returns the distinct
  `403 OBJECT_ACCESS_DENIED`.
- `reviewed` transitions to terminal appraisal state `reviewed`. `returned` records the same
  reviewer/time/comment/decision facts and transitions to `draft`, where the maker must revise and
  resubmit before another review. Draft, reviewed, repeated, and other non-pending review attempts
  return `409 INVALID_STATE_TRANSITION`.
- `rejected` atomically transitions to terminal appraisal state `rejected` and creates exactly one
  linked existing 005H rejection-note draft. Its response nests the serialized `rejection_note`,
  including `note_status = draft`, derived `communication_status = not_sent`, null send facts, and
  the appraisal/application/note IDs. It does not send communication or create a sanction/approval
  case. Repeated rejection returns `409` and cannot create a duplicate note.
- Every successful `reviewed`, `returned`, or `rejected` action appends one immutable
  `review_history[]` item with `appraisal_review_decision_id`, decision, non-blank comments,
  reviewer summary, decision time, from/to states, and `history_provenance`. New decisions use
  `native`; migration backfill uses `legacy_latest_only` and represents only the latest known
  legacy decision. The appraisal's top-level decision/comments/reviewer/time remain the latest
  projection and may be replaced by a later review cycle without changing history.
- Review never reads current eligibility or loan-limit rows. It preserves the appraisal-owned
  projections, recommendation/terms, repayment-capacity and submission reasons, linked risk, and
  TAT facts. Successful decisions atomically write `appraisal.reviewed` or `appraisal.returned`
  audit/workflow evidence containing the immutable decision ID plus appraisal/application IDs,
  state, decision, actor/time, and request ID; free-text review comments and appraisal/risk
  projections are excluded.
- Rejected review uses the same outer transaction for appraisal state, rejection-note persistence,
  both metadata evidence streams, and both workflow events. Any note/audit/workflow failure rolls
  back all writes. `appraisal.rejected` evidence may contain the note ID, category, state, actor,
  time, and request ID, but excludes `review_comments` and `detailed_reason`.

Rejected review request:

```json
{
  "decision": "rejected",
  "review_comments": "Independent credit review completed.",
  "rejection_reason_category": "eligibility",
  "detailed_reason": "Verified appraisal facts do not meet credit criteria.",
  "reapply_allowed_flag": true,
  "communication_mode": "email"
}
```

Response data includes appraisal/application/prerequisite IDs, exact `eligibility_snapshot` and
`loan_limit_snapshot`, `prerequisite_provenance = verified|legacy_unverified`, prepared-user
summary/time, immutable TAT due/status, `repayment_capacity_notes`, all stored recommendation-term
facts, linked risk assessment, recommendation, latest review decision/comments/reviewer/time,
ordered immutable `review_history[]`, and
`appraisal_status = draft|review_pending|reviewed|rejected`. A successful rejected-review response
also includes the nested existing rejection-note representation and links its UUID to the appraisal
audit metadata.

## Submit appraisal to Sanction Committee API (006G/006G2/006G3)

Protected Credit Manager endpoint:

- `POST /api/v1/loan-applications/{loan_application_id}/submit-to-sanction-committee/`
- `GET /api/v1/loan-applications/{loan_application_id}/sanction-case/`

The submit response and every later case read return the exact workflow-event UUID durably linked
to that approval case. The read path never substitutes a newer application workflow event.

POST request is exactly `{ "remarks": "non-blank reason" }`. Malformed JSON, a non-object body,
missing/blank remarks, or any unknown field returns `400 VALIDATION_ERROR`. The action requires active `credit_manager` role authority,
`credit.appraisal.submit_sanction`, and the existing Credit Manager credit-domain object boundary;
permission/role failures return `403 FORBIDDEN` and out-of-domain applications return
`403 OBJECT_ACCESS_DENIED`.

Submission requires one `reviewed` appraisal with verified frozen prerequisite projections, a
complete linked risk assessment, populated latest review facts, and at least one immutable review
row. The latest ordered row must be `native|legacy_latest_only` and exactly match the appraisal's
`reviewed` decision, reviewer, time, comments, and `to_state`. Missing, draft, review-pending,
returned, rejected, inconsistent, or repeated paths return `409 INVALID_STATE_TRANSITION` without
case, state, audit, workflow, history, or rejection-note side effects.

The mutation locks application, appraisal, immutable review history, then the case namespace. It
atomically creates one unique pending sanction case, copies only the frozen loan-limit exception
flag, and changes both application and appraisal status to
`submitted_to_sanction_committee`. It does not evaluate the approval matrix, assign approvers,
create an exception decision, or perform a committee action.

Response data:

```json
{
  "approval_case_id": "uuid",
  "loan_application_id": "uuid",
  "loan_appraisal_note_id": "uuid",
  "appraisal_review_decision_id": "uuid",
  "workflow_event_id": "uuid",
  "application_status": "submitted_to_sanction_committee",
  "appraisal_status": "submitted_to_sanction_committee",
  "submission_status": "pending",
  "exception_required_flag": false,
  "submitted_by": {
    "user_id": "uuid",
    "full_name": "Credit Manager"
  },
  "submitted_at": "2026-07-10T20:30:00+00:00",
  "available_actions": []
}
```

GET is authenticated and applies the same application object-access boundary. It returns the exact
same backend-owned projection as the successful POST, including case, latest-review, and workflow
event UUIDs; it never returns submission remarks or other frozen free text. A real application
without a sanction case returns `404 NOT_FOUND`; denied scope returns `403 OBJECT_ACCESS_DENIED`.

Successful submission writes one `appraisal.submitted_to_sanction` audit record and one
`sanction_submission` workflow event with application/appraisal/case/latest-review IDs, states,
actor/time, exception flag, and request ID. Generic evidence excludes request remarks, review
comments, appraisal summaries, risk notes, and rejection text. Approval-case storage retains the
trimmed request remarks as the action reason.

## Application Witness API (004E, hardened by 004E2)

Application-scoped endpoints:

- `GET /api/v1/loan-applications/{loan_application_id}/witnesses/`
- `POST /api/v1/loan-applications/{loan_application_id}/witnesses/`

GET requires `members.witness.read` plus application object access and returns the standard list
envelope in deterministic created order. POST requires `members.witness.create` plus application
object access and accepts exactly `member_id`, `witness_name`, `address`, optional `mobile`, `pan`,
and `aadhaar`. Address is required free text up to 500 characters; a supplied mobile contains 7-15
digits after spaces are removed.

The selected member must exist, the trimmed/case-normalized witness name must match its legal or
display name, member KYC must be `verified`, and persisted shareholding evidence must include an
`active` row with `number_of_shares > 0`. Missing records return `404 NOT_FOUND`; non-shareholders
return `400 WITNESS_NOT_SHAREHOLDER`; missing/invalid identity, KYC, name, unknown, or
caller-supplied verification fields return the applicable standard 400 envelope. Malformed JSON,
arrays/scalars, missing fields, and unknown fields never escape the adapter: they return a standard
`400 VALIDATION_ERROR` envelope and write no witness, audit, or workflow row.

Successful response data contains `witness_id`, application/member IDs,
`verification_shareholding_id`, immutable verification-time `folio_number`, name, masked
PAN/Aadhaar objects, `shareholder_verified_flag: true`,
`verification_status: verified`, verifier/time, and creation time. Plaintext identities, protected
tokens, and keyed hashes are never returned or audited. Creation writes one metadata-only
`applications.witness.created` audit row and no workflow event or application-state transition.
Later shareholding folio/status/count changes or newly created holdings do not change witness read
evidence. Legacy rows whose creation audit folio does not resolve to exactly one member
shareholding expose both evidence fields as `null` rather than selecting current facts.
### Witness correction and resource actions (006Y4, closed by 006Y8)

- The collection GET additionally returns top-level six-field `actions` for `read` and `create`;
  each witness returns `version` plus six-field `actions` for `read`, `correct_contact`, and
  `correct_identity`. Contact and identity entries separately project the authority for the exact
  fields they govern; clients do not infer correction authority from field names.
- `GET/PATCH /api/v1/loan-applications/{loan_application_id}/witnesses/{witness_id}/` requires
  `members.witness.read/update` respectively and exact application object access.
- PATCH requires current positive-integer `version` and accepts only `witness_name`, `address`,
  optional `mobile`, `pan`, and
  `aadhaar`. Verification evidence/provenance fields are immutable. Invalid fields return 400;
  stale version returns `409 VERSION_CONFLICT`, both with zero domain/evidence writes.
- Verified identity correction requires a different authorised actor from the verification actor.
  Success increments version, stores protected identity, returns masked values, writes masked
  history, and emits metadata-only `applications.witness.corrected` audit evidence.
- Collection/resource action arrays always contain their entries in the standard six-field shape.
  Denied actions remain present with the exact permission, application-object, or maker-checker
  reason; projection and PATCH consume the same correction evaluation, including current version.

#### Parent authority and non-disclosure ordering (006Y16)

Witness resource GET/PATCH applies response-decision precedence in this order: required witness
permission, parent application object scope, parent absence, then child lookup. Credit Manager scope is all existing
applications whose persisted `current_stage` is `credit_assessment`; the role does not confer a
row-independent global scope for an unresolved application identifier.

Consequently, a Credit Manager with the required witness permission receives normal child lookup
semantics for an existing Credit Assessment parent, including `404 NOT_FOUND` with message
`Witness was not found.` when the child is absent. An existing application outside that domain and
a random parent UUID both stop before witness lookup with the same HTTP 403 error fact:

```json
{
  "success": false,
  "error": {
    "code": "OBJECT_ACCESS_DENIED",
    "message": "You do not have access to this loan application.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": "<request-id>",
    "timestamp": "<timestamp>",
    "api_version": "v1"
  }
}
```

Only an actor with a separately documented application-wide scope that is independent of facts on
the unresolved row may pass parent authority and receive `404 NOT_FOUND` with message
`Loan application was not found.` for a missing parent. No current witness-correction role has that
scope. Every denied parent/child path leaves Witness, WitnessChangeHistory, AuditLog, and
WorkflowEvent unchanged.

The normal missing-child envelope after successful parent authority is:

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Witness was not found.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": "<request-id>",
    "timestamp": "<timestamp>",
    "api_version": "v1"
  }
}
```

If a future row-independent application-wide scope is documented, the corresponding missing-parent
envelope is:

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Loan application was not found.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": "<request-id>",
    "timestamp": "<timestamp>",
    "api_version": "v1"
  }
}
```

# Epic 006 authoritative workbench actions (006H4)

Eligibility, loan-limit, appraisal-note, appraisal transition, and sanction submit/read success
responses now include `data.available_actions[]` in the source §44 shape: `action_code`, `label`,
`enabled`, `disabled_reason`, `required_permission`, and nullable `required_role`. The projection is
object-, state-, permission-, and role-aware. Appraisal actions are `credit.appraisal.update`,
`revalidate_appraisal_prerequisites`, `credit.appraisal.submit_review`, `credit.appraisal.review`,
and `credit.appraisal.submit_sanction`; disabled actions remain present with a reason. Clients must
not supplement this resource projection from `/auth/me.available_actions`.
# Member create/update and identity governance (006Y)

- `POST /api/v1/members/` requires `members.member.create` and accepts the §13.2 individual-farmer
  or FPC/producer-institution payload. New members start with `membership_status =
  pending_verification`, `kyc_status = pending`, `default_status = no_default`, and `version = 1`.
- `PATCH /api/v1/members/{member_id}/` requires `members.member.update`, accepts the §13.4 contact,
  address, and name fields plus mandatory current `version`, and returns `409 STALE_WRITE` without
  writes when the version is stale.
- Verified `pan`/`aadhaar` changes through PATCH return `409 VERIFIED_IDENTITY_LOCKED`; the rejected
  attempt changes no member/history state and writes a metadata-only rejection audit.
- `POST /api/v1/members/{member_id}/reverification/` requires the same update permission, current
  `version`, at least one valid `pan`/`aadhaar`, and `reason`. Success masks history values, resets
  member KYC to `pending`, clears `rekyc_due_date`, increments `version`, and records audit/history.
- Member detail now returns `version` and exact six-field resource actions for
  `members.member.update` and `members.member.reverify_identity`. Resource actions, not `/auth/me`
  permissions alone, are authoritative for mutation UI.

## Member governance and witness UI closure (006Y2)

- Staff UI calls the 006Y member POST/PATCH/reverification endpoints and performs a canonical
  member-detail GET after successful update/reverification. It preserves backend 400/403/409
  errors and uses only the resource's update/reverification actions for profile mutation controls.
- Application Detail calls the 004E2 witness GET/POST endpoint and performs a canonical witness
  GET after successful capture. Immutable verification-time shareholding/folio evidence is rendered
  from that read response; identity values remain masked after capture.
- The former witness-correction mismatch is closed by 006Y4's versioned resource contract.

## Member Registry and approved identity change (006Y3)

- `POST /api/v1/members/{member_id}/identity-change-requests/` requires
  `members.member.update`, current `version`, a reason, and at least one valid PAN/Aadhaar. It
  persists protected proposed values and returns only request metadata; the member remains verified
  and unchanged until approval. The legacy `/reverification/` route is a compatibility adapter to
  this request operation.
- `POST /api/v1/member-identity-change-requests/{request_id}/approve/` requires the dedicated
  `members.member.identity_change.approve` permission and a different actor. It applies a pending,
  current-version request once, resets KYC to pending, clears the re-KYC due date, increments member
  version, and writes masked history/audit. Stale or repeated approval returns `409`.
- Member detail includes nullable `pending_identity_change` metadata and six-field request/approval
  actions. Duplicate PAN/Aadhaar create attempts return `400 VALIDATION_ERROR` field errors and the
  database also enforces nonblank hash uniqueness.

# Approval matrix and sanction committee configuration (007A)

- `GET/POST /api/v1/approval-matrix-rules/` and
  `PATCH /api/v1/approval-matrix-rules/{approval_matrix_rule_id}/` implement source §25.1.
  Reads require `approvals.matrix.read`; POST/PATCH require the Critical
  `approvals.matrix.manage` permission. PATCH is a supersede operation: it closes the prior row
  the day before the replacement's `effective_from` and returns a new rule id/version.
- Rule responses expose `approval_matrix_rule_id`, decision/condition, nullable inclusive amount
  bounds, `required_approver_roles`, `required_director_count`, joint-approval and register facts,
  effective range, status, and `version_number`. Overlapping amount plus effective ranges for the
  same decision/condition return `409 CONFIGURATION_CONFLICT` with no configuration, version, or
  audit writes. Invalid/non-finite amounts return `400 VALIDATION_ERROR`.
- `GET/POST /api/v1/sanction-committees/` and
  `PATCH /api/v1/sanction-committees/{sanction_committee_id}/` are the exact committee management
  paths selected for data-model §15.1. They use the same permissions and immutable supersession
  convention and return CFO/director user ids, Board meeting reference, effective range, status,
  and version.
- The approval-owned resolver interface accepts typed `decision_type`, canonical nullable
  `condition_code`, finite non-negative amount, and authoritative `decision_date`; it returns one
  immutable rule-id/version projection or stable no-effective/ambiguous/invalid-facts domain errors.
# Approval Configuration Collections and Committee Resolution (007A2)

`GET /api/v1/approval-matrix-rules/` and `GET /api/v1/sanction-committees/` use the standard
top-level paginated list envelope. They accept only positive `page` and `page_size`; `page_size` is
capped at 100 and unknown parameters return `400 VALIDATION_ERROR`. Ordering is deterministic.

Committee POST/PATCH payloads retain the 007A fields, but the three referenced active users must
carry persisted authority types `cfo`, `director`, and `director` respectively and must be distinct.
Approval-owned `resolve_sanction_committee(decision_date)` returns the immutable committee id,
version, decision date, CFO user id, and both Director user ids. No match and multiple matches have
stable `NO_EFFECTIVE_SANCTION_COMMITTEE` and `AMBIGUOUS_SANCTION_COMMITTEE` domain codes.

# Approval Configuration Maker-Checker Governance (007A3)

Rule and committee POST/PATCH payloads now require a non-blank `reason`; success returns a pending
proposal with `approval_configuration_proposal_id`, `proposal_type`, nullable `target_entity_id`,
immutable `payload`, `reason`, `status`, `version`, maker/checker ids, nullable `decided_at`,
rejection reason, and §44-shaped
`available_actions`. It does not make configuration effective.

- `GET /api/v1/approval-configuration-proposals/{proposal_id}/`
- `POST /api/v1/approval-configuration-proposals/{proposal_id}/approve/` — `{"version": 1}`
- `POST /api/v1/approval-configuration-proposals/{proposal_id}/reject/` —
  `{"version": 1, "reason": "Policy evidence incomplete"}`

Proposal detail returns `401 AUTH_REQUIRED` without a valid session and `403 FORBIDDEN` to an
authenticated user who is neither the maker, an active persisted CFO/Company Secretary checker,
nor a holder of `approvals.matrix.read`. Those participants/readers receive 200. This boundary does
not infer access from display role names and prevents unrelated users from seeing Critical change
reasons, actor ids, or action eligibility.

The checker must be active, distinct from the maker, and carry persisted `cfo` or
`company_secretary` authority. Self-decision and missing authority return
`403 MAKER_CHECKER_VIOLATION` and `403 APPROVAL_AUTHORITY_REQUIRED`; stale version returns
`409 STALE_VERSION`; terminal replay returns `409 TRANSITION_CONFLICT`; approval-time lifecycle
conflicts return `409 CONFIGURATION_CONFLICT` or `409 PROPOSAL_STALE`. Validation uses the standard
`400 VALIDATION_ERROR` field-error envelope. Approval atomically activates/supersedes and writes
separate author/approver VersionHistory plus `config.changed`; rejection changes no effective row.

# Approval-case enrichment from appraisal (007B)

`POST /api/v1/loan-applications/{loan_application_id}/approval-cases/` requires an authenticated
holder of `approvals.case.create` with object access to the application. It accepts exactly the
source §25.2 fields `approval_type = sanction`, an `amount` equal to the reviewed appraisal's
recommended amount, a non-blank `reason_for_approval`, and boolean `force_exception_route`.
When the frozen assessment requires an exception or the caller forces that route, the request also
requires a distinct non-blank `business_reason` and may include a string `risk_assessment`.
An assessment-required route has canonical `exception_type = exceeds_loan_limit`; a forced
within-limit route must explicitly name `stage_bypass` or `waiver` so the register never claims a
limit breach that did not occur.

The adapter never creates a row. It enriches the unique pending shell created by the §24.5 sanction
submission or returns `404 NOT_FOUND`. It derives application/appraisal identity from that shell,
uses the latest immutable review date, and consumes the stored verified loan-limit assessment's
condition and policy provenance. Missing/stale provenance is `409 INVALID_STATE_TRANSITION`;
missing or ambiguous effective approved configuration uses the resolver's stable 400 code.

Success returns the existing submission projection plus immutable `approval_type`, amount,
rule/committee ids and versions, decision date, concrete `required_approvers`, empty
`excluded_approvers`, related-entity facts, reason, canonical exception condition, complete matrix
and committee projections, loan-limit provenance, and case `version`. An identical repeat returns
the same projection without writes. A conflicting repeat or decided case returns 409. Later matrix,
committee, pending-proposal, or losing-proposal changes never rewrite the stored projection.

# Approval-case queue and detail reads (007C)

`GET /api/v1/approval-cases/` requires `approvals.case.read` and accepts only `current_status`,
`approval_type`, `assigned_to_me`, `page`, and `page_size`. It returns the standard top-level
pagination envelope. `approval_type`, when present, is exactly `sanction`; `current_status`, when
present, is exactly `pending`, `approved`, `rejected`, `returned_for_clarification`, or
`blocked_by_conflict`. Unknown values return `400 VALIDATION_ERROR` rather than an empty successful
page. `assigned_to_me=true` includes only complete version-2-or-later 007B routing
snapshots where the caller remains in `required_approvers`, is absent from `excluded_approvers`,
has no immutable `approval_actions` row, and the case is still pending. Missing/default snapshot
facts never fall back to amount, the current matrix, or the current committee.

`GET /api/v1/approval-cases/{approval_case_id}/` also requires `approvals.case.read`. Any global
object scope must be persisted separately; the permission alone is not global scope. A complete
routed case is visible when its immutable `required_approvers` snapshot names the caller (including
the caller's own acted history), when a Credit Manager owns the case submission or passes the
existing application object-scope decision, or when the caller's active role has an active persisted approval-case
read-scope grant. The bounded grant types are `legal_readonly`, `audit_readonly`, and
`management_readonly`; the default catalogue seeds only Company Secretary legal read-only and
Internal Auditor audit read-only grants. The broad `management_readonly` permission, role display
text, and caller query flags never imply a grant. Unassigned Directors, unrelated case makers, and
arbitrary custom-role permission holders receive an empty scope-filtered collection
(`total_count = 0`) and direct detail returns `403 OBJECT_ACCESS_DENIED`. A non-reader receives
`403 FORBIDDEN`; an incomplete or internally contradictory snapshot is not a public case and
returns `404 NOT_FOUND`. Reads and denials write no audit or workflow evidence.

Object scope is applied before pagination and count calculation. `assigned_to_me=true` is the
narrower queue filter: the caller must additionally be pending, unexcluded, and without an
immutable action. The ordinary collection does not bypass object scope and keeps acted cases in
the assigned actor's readable history. Read-only role grants and Credit Manager ownership never
create an assignment, enable an action, or bypass its action-specific permission. The collection
selector narrows candidates in the database by persisted role scope, immutable approver candidacy,
or Credit Manager ownership before the remaining JSON coherence validation runs.

The selector's indexed `routing_snapshot_is_coherent` and attributable-reader projection are
updated only through the explicit approval-owned projection interface. Case creation, workflow
linkage, enrichment, and actions/abstention invoke it atomically; an ordinary approval-case or
appraisal save has no hidden cross-table side effect. A later live appraisal mutation cannot rewrite
the coherence or reader index of a frozen historical cycle. The reader projection contains only
original routed actors, current effective replacements, and actors with an immutable action. It
narrows the database scan, but the approval-owned frozen-validity and actor-scope decision runs
over every narrowed candidate before collection/register filters, counts, page normalization,
`LIMIT/OFFSET`, or serialization. Detail, action, sanction-decision, and register reads execute the
same decision and never trust the projection as read or action authority.

For the approval-case collection, coarse actor scope plus valid approval type, status, and
assignment/index filters run before canonical Python validation. Every remaining candidate still
passes through the single frozen-validity/read-scope decision before totals, pages, or rows are
produced. A stale true projection can therefore add validator work but cannot create a page hole or
inflate `total_count`; unrelated actors, types, and statuses are not materialized for validation.

Detail returns stored authority/provenance (`approval_matrix_rule_id` and version,
`sanction_committee_id` and version, `decision_date`, ordered required/excluded approvers,
matrix/committee/loan-limit snapshots, distinct `reason_for_approval` and `exception_reason`, and
case `version`). Per-approver `decision`/`acted_at` are
read from the immutable source §15.4 `approval_actions` ledger; 007C creates no action records.

The nested `review_facts` object is frozen into each enriched approval cycle. The current
`approval-review-v2` schema includes credit-owned snapshot provenance; borrower member id,
application reference, name, and type; and the reviewed sanction terms (tenure, interest type,
and security summary) in addition to the review sections below. Legacy or partial packages without
the complete terminal copy facts are nondisclosing. Reads and terminal writes never reconstruct
missing facts from current owning rows:

- `eligibility` and eligible amount come from the appraisal-owned frozen eligibility/loan-limit
  snapshots.
- requested amount, purpose, and documentation/completeness status come from the owning loan
  application.
- borrowing history, recommendation amount, and sanction terms come from the owning appraisal
  note at review-package creation.
- risk ratings/mitigation come from the owning risk assessment.
- `source_references` links the application, appraisal, eligibility, and loan-limit owner APIs.

Changing current matrix/committee rows cannot change queue membership, stored provenance, or
action assignment for an existing case.

Every list/detail item also returns `workbench_summary`, derived only from the frozen review package,
frozen matrix/case flags, immutable action ledger, and approval-case timestamps. It contains
`borrower_name`, `member_type`, requested/recommended/eligible amounts, `approval_path`, exception
and related-party booleans, `risk_rating`, `submitted_at`, `current_decision_status`, and nullable
`pending_age`. A pending case with an immutable approval reports `partially_approved`; otherwise the
decision status matches the case. `pending_age` is labelled `Elapsed pending time` and includes
server-projected elapsed seconds/display only while pending. It does not claim a target or breach
before the later workflow-TAT policy boundary exists.

The S21 frontend sends `approval_type=sanction` on every collection request. The assigned pending
queue additionally sends `current_status=pending&assigned_to_me=true`; historical filters send their
exact status without assignment. Every request also sends explicit `page` and `page_size=20`; S21
renders `pagination.total_count`, exposes the existing previous/next pattern, resets to page one on
filter changes, and replaces rows plus pagination from the same response. Collection failure clears
both. The shared authenticated paginated client accepts success only when `data` is an array and all
six top-level pagination fields are present, non-negative/in-range, and internally consistent; it
returns `MALFORMED_RESPONSE` rather than fabricating empty pagination. S22 renders every immutable `approval_actions` actor, role,
decision/abstention, comment/reason, and acted-at confirmation separately from required/effective
authority.

Routability is one approval-owned validation contract shared by list, detail, action,
sanction-decision, and register
seams. Case/application/type/amount/decision/exception facts must agree with the stored matrix;
rule and committee ids, versions, and dates must match; the snapshot must contain exactly the
stored CFO and required distinct Directors with unique ids; required roles/director count and
joint/register facts must be complete; and the loan-limit assessment/application/exception/policy
provenance must be internally complete. The credit-owned enrichment interface validates the locked
appraisal and loan-limit source once, then freezes the complete provenance and `review_facts` on
the case. Existing-cycle validation never compares those facts with the mutable live appraisal or
a later revision. Invalid or contradictory frozen snapshots are hidden and non-actionable without
writes or count leakage; live appraisal, rule, committee, or user membership is never queried to
repair them.

The §25.2 enrichment success projection now includes source-required `current_status`. Enrichment,
list, and detail compose the same canonical immutable routing projection (status, rule/committee,
decision date, required/excluded authority, and loan-limit provenance). Detail adds immutable
decision history, review read-throughs, and caller-specific actions; existing submission fields
remain backward-compatible additions.

For a case whose frozen projection requires General Meeting evidence, detail also includes the
resource action `record_general_meeting_approval`. The backend enables it only when the actor has
canonical case scope, belongs to the §19.4 legal audience, and holds
`approvals.general_meeting.record`, `approvals.case.read`, and `documents.file.download`; otherwise
the same action is returned disabled with a reason. Ordinary cases omit this inapplicable action.
The frontend may intersect the enabled resource action with `/auth/me` permissions for usability,
but a global permission never creates or enables the action.

An enrichment replay is exact only when the locked reviewed decision date and recommended amount,
assessment/application ids, exception flag, calculation rule, policy id/name, and calculation time
equal the frozen case provenance. Any changed reviewed or credit fact returns stable
`409 INVALID_STATE_TRANSITION` and leaves case/action/audit/workflow ledgers unchanged. A later
effective governed configuration version does not rewrite an otherwise coherent historical case.

# Approval-case actions and sanction decision creation (007D)

`POST /api/v1/approval-cases/{approval_case_id}/approve/`, `reject/`, and
`return-for-clarification/` accept exactly optimistic integer `version` and optional `comments`;
comments are mandatory and non-blank for reject/return. The caller must hold the action-specific
permission and remain a pending, unexcluded actor in the coherent immutable case snapshot.
Permission failure is `403 FORBIDDEN`, missing object scope is `403 OBJECT_ACCESS_DENIED`, stale
version is `409 STALE_VERSION`, and acted/closed/excluded state is `409 TRANSITION_CONFLICT`.
The submitted `version` must be a positive JSON integer; booleans, zero, negative values, strings,
missing values, and unknown request fields return `400 VALIDATION_ERROR` without writes. Approve
permits omitted/blank comments; reject and return require a non-blank string.

Success returns the §25.5 action identifiers/status/sanction flags merged with the canonical 007C2
case detail projection. Collection, detail, and action responses now compose the same history-aware
projection: route provenance is immutable, while each required approver's `decision`/`acted_at` and
the caller's `available_actions` reflect the action ledger immediately. Each action increments case `version`, creates one immutable §15.4 row,
and immediately disables every action for that actor. Partial joint approval remains pending. Final
approval atomically closes the case, advances the application to `approved_by_sanction_committee`,
and creates the unique per-application §15.5 sanction decision. Reject advances the application to
`rejected_by_sanction_committee`; return restores the application to `appraisal_reviewed` and the
appraisal to editable `draft` so clarification can be supplied.
Every successful action writes attributable audit/workflow evidence. Each terminal outcome crosses
the communication-owned internal adapter in the same transaction, persisting one source §24.2
`pending` email `Communication` snapshot, one linked in-app notification to the persisted
`credit_assessment` team, and a metadata-only communication audit. Any adapter persistence failure
rolls back the action, case/application outcome, sanction, register, workflow, communication,
notification, and audits. Application, appraisal, and case source states are re-evaluated through
the shared transition guard after locking and before mutation. As delivered by 007H, an approved
or rejected terminal action also freezes exactly one Credit Sanction Register row in this same
transaction; partial approval, return, and conflict-blocked outcomes do not.

# Exception approval and generated Exception Register (007F)

An exception-routed §25.2 enrichment requires both `approvals.case.create` and
`approvals.exception.create`. It atomically creates exactly one
`exception_register_entries` row for that approval case/cycle. The canonical type is
`exceeds_loan_limit`; the bounded future-caller vocabulary is `stage_bypass` and `waiver`, and an
unknown type is rejected. The entry copies the request's distinct `business_reason` and optional
`risk_assessment`, links the loan application and approval case, and begins `pending`. An ordinary
within-limit route creates no entry. Exact enrichment replay creates no duplicate or evidence.

The same request may include optional `supporting_document_ids` as an ordered list of at most 20
distinct UUIDs. The documents owner validates every supplied id through public-upload provenance,
exact application attribution, legal category, matching sensitivity, document permission, role,
workflow, and object scope before the locked enrichment writes. Approvals stores only the returned
immutable display projection (`document_id`, file name, MIME type, size, sensitivity, upload time)
on the exact register entry/cycle and never queries `DocumentFile`. Empty/omitted evidence freezes
an empty list. Exact ordered-id replay is zero-write; any changed ordered list after routing returns
the existing immutable-snapshot `409` conflict.

Inside the locked approval-action transaction, partial approval leaves the entry pending. Final
approval changes it to `approved`; rejection changes it to `rejected`; both copy the case
`closed_at`. Return-for-clarification and `blocked_by_conflict` also copy the case closure time but
remain `pending`, because source data-model §15.7 defines no additional status. Denied conflicted
actions never mutate the entry. Creation and outcome projection write attributable
`exception_register.*` audit plus `exception_register` workflow evidence.

`GET /api/v1/exception-register/?status=&exception_type=&page=&page_size=` requires
`approvals.exception_register.read`, accepts only the source status/type vocabulary, and returns
the standard pagination envelope. It is generated/read-only: mutation methods are not routed.
Object scope delegates to the canonical approval-case selector before count and pagination. Each
row includes register/application/case ids, `cycle_number`, type, description, business/risk facts,
entry/case statuses, conflict reason, timestamps, `authority_applied_summary`, and canonical
`route_approvers`, `required_approvers`, and complete `approval_actions`. Reads never re-run
conflict replacement or consult live committee membership. Each row also includes
`supporting_documents` with the frozen metadata above. Register visibility and metadata never grant
download; S25 exposes no download control unless a separate document resource independently
authorises an action.

The nullable `loan_account_id` is currently a UUID reference, not a foreign key to the tracer app's
synthetic demo account. A protected FK is deferred to the production finance loan-account owner
(A-084); exception entries created before sanction naturally carry no loan account.

## Exception predicate and coherence closure (007F2)

For a non-forced route, the reviewed `recommended_amount` must exceed the frozen
`final_eligible_loan_amount` exactly when the frozen `exception_required_flag` is true. Either
contradiction returns `409 INVALID_STATE_TRANSITION` before matrix/committee resolution and leaves
the existing submission shell, routing, register, audit, workflow, and communication ledgers
unchanged. `force_exception_route = true` is the only within-limit exception path and still requires
truthful `stage_bypass` or `waiver` type plus a non-blank business reason.

`reason_for_approval` belongs to the sanction case and becomes the sanction decision reason.
`business_reason` belongs to the generated Exception Register; the case freezes it separately as
`exception_reason`. These independently authored reasons are not required to be equal. An
exception-conditioned routing snapshot is coherent only when the same-case register row matches
the case/application, `exception_reason`, truthful exception type, optional risk shape, frozen
amount/limit predicate, the `exceeds_permissible_limit` matrix condition, two-Director authority,
and `register_required = exception_register`. Exact replay is zero-write; changed reason, risk,
type, amount, or frozen provenance conflicts without rewriting or hiding the original case.

# Returned approval cycles and resubmission (007D3)

Every sanction approval case now carries positive `cycle_number`, immutable
`appraisal_review_decision_id`/`appraisal_revision`, and frozen `review_facts`. The database enforces
unique `(loan_application, cycle_number)` and at most one pending cycle per application. Existing
cases migrate to cycle 1; collection, detail, submission, enrichment, and action success projections
all expose `cycle_number`.

A returned case is closed history and never becomes assigned or actionable again. Its case,
approver/action snapshot, frozen appraisal/configuration facts, audit/workflow, and communication
evidence remain attached to that exact cycle. The maker may PATCH the returned draft through the
existing appraisal boundary; only a non-empty `appraisal.updated` changed-field ledger after the
return counts as correction. A no-op PATCH does not create revision authority.

The existing `POST /api/v1/loan-applications/{loan_application_id}/submit-to-sanction-committee/`
boundary creates cycle N+1 only when the latest prior cycle is `returned_for_clarification`, the
appraisal has a later attributable correction ledger, and the latest immutable Credit Manager
`reviewed` decision follows that correction. Pending, approved, rejected,
uncorrected, stale-review, or otherwise incompatible submissions return
`409 INVALID_STATE_TRANSITION` without a new case or sanction-submission evidence. The standard
application -> appraisal -> approval-case lock order plus database uniqueness serializes competing
resubmissions to one new shell/evidence set.

Cycle N+1 is enriched from its own current reviewed appraisal/configuration facts. Its action ledger
starts empty, so a user who acted in cycle N may independently act again when snapshotted in cycle
N+1. Final approval creates the application-unique sanction decision only from the latest pending
cycle; prior returned actions never count toward joint approval.

# Conflict-of-interest exclusions and abstention (007E)

Approval enrichment evaluates source conflict declarations plus frozen application/appraisal maker
facts for that exact `cycle_number`. It leaves ordered `required_approvers` unchanged and writes
unique `excluded_approvers` objects containing `user_id`, `conflict_code`, and non-blank `reason`.
Director/relative declarations set `general_meeting_evidence_required = true`. A frozen same-role
committee alternate may fill an excluded Director slot; the stored matrix role/count never shrinks.
If no frozen alternate can preserve required CFO/Director authority, the case becomes
`blocked_by_conflict`, closes without a sanction decision, and exposes `conflict_block_reason`.

An excluded actor has limited case-detail/history access only: they never enter
`assigned_to_me`, never receive an enabled action, and no permission or live committee membership
widens that scope. Every attempted approve/reject/return returns `409` with the exact source body:

```json
{
  "success": false,
  "error": {
    "code": "CONFLICTED_APPROVER_NOT_ALLOWED",
    "message": "This user is marked as conflicted for the approval case and cannot approve it.",
    "details": {
      "approval_case_id": "uuid",
      "conflict_reason": "Borrower is relative of Director."
    },
    "field_errors": {}
  }
}
```

The denial adds one `approval_case.conflicted_action_denied` audit row naming the exact case,
cycle, attempted action, reason, actor, request, IP, and user agent. It creates no ApprovalAction and
changes no case/application/appraisal/sanction/workflow/communication ledger.

`POST /api/v1/approval-cases/{approval_case_id}/abstain/` accepts exactly positive integer
`version` and mandatory non-blank `comments`. It uses the existing approval authority permission
and immutable action ledger with decision `abstained`, increments case version, and adds a
`self_declared_abstention` exclusion. The case stays pending when frozen alternate authority can
satisfy the matrix; otherwise it closes as `blocked_by_conflict` and notifies the Credit Assessment
team through the communication adapter. Prior-cycle exclusions/abstentions never populate a later
cycle; every enrichment recomputes from that cycle's frozen facts.

# Conflict authority, history projection, and scope closure (007E2)

Conflict replacement fills frozen role slots with distinct users. A user can occupy at most one
effective CFO/Director slot; a two-Director route with either Director excluded therefore blocks
when the frozen committee has only one remaining distinct Director. `conflict_block_reason` names
the exact missing CFO or Director authority, the case closes atomically, and no sanction is
created. `required_approvers_json` remains immutable route provenance.

Collection, detail, action success, and historical-cycle reads share these authority facts (the
§25.2 enrichment response preserves its backward-compatible raw `required_approvers` shape):

- `route_approvers`: the unchanged ordered matrix/committee route snapshot.
- `required_approvers`: the currently executable distinct actors with `role_code`, `user_id`,
  `full_name`, nullable `decision`/`acted_at`, and `replacement_for_user_id` only when the actor
  replaces an excluded original.
- `approval_actions`: every immutable action with `approval_action_id`, role/user/name, decision,
  comments, acted time, and replacement attribution when applicable.

These three fields are identical in collection, detail, and the case portion of action responses;
only caller-specific `available_actions` and the action endpoint's top-level result fields differ.
An excluded original may retain COI-005 history access only because it is an original, effective,
or already-acted cycle participant. Frozen committee candidacy, an unused-alternate declaration,
or action permission alone grants no row, count, detail, queue, or write scope. An unused alternate
therefore receives `total_count: 0` and direct `403 OBJECT_ACCESS_DENIED`.

Active borrower and Director-relative declarations set
`general_meeting_evidence_required = true` even when the related Director/committee member is not
assigned to this case. Material-interest and maker-checker facts alone do not set the flag.
Exclusions remain limited to frozen authority candidates, and database validation rejects empty or
whitespace-only declaration reasons.

# General-meeting evidence and final-sanction gate (007G)

`POST /api/v1/loan-applications/{loan_application_id}/general-meeting-approval/` requires
`approvals.general_meeting.record`, `approvals.case.read`, canonical object scope to the latest
routed approval cycle, and `documents.file.download`. The case's immutable
`general_meeting_evidence_required` flag must be true. The request accepts only:

```json
{
  "related_party_type": "director_relative",
  "related_party_user_id": "uuid-or-null",
  "relationship_description": "Borrower is a relative of a Director.",
  "meeting_date": "2026-07-15",
  "notice_document_id": "uuid",
  "minutes_document_id": "uuid",
  "resolution_document_id": "uuid",
  "approval_status": "pending | approved | rejected"
}
```

`related_party_type` is exactly `director`, `director_relative`, or `committee_member`.
Description and ISO date are mandatory. Notice, minutes, and resolution must be three distinct,
existing document files resolved through the documents module's reference-authorization interface.
Each file must have immutable `documents.file.uploaded` provenance from the public upload path,
`related_entity_type = application`, the exact loan-application id, category `legal`, and sensitivity
matching one of the document model's source-defined levels (`public`, `internal`, `confidential`, or
`restricted`). The approval owner supplies a typed reference context only after the latest routed
case has canonical object access and its immutable related-party evidence flag proves the
`related_party_sanction_case` workflow scope; the documents owner combines that decision with each
file's provenance and the source §19.4 legal audience (Compliance Team, Company Secretary, Credit
Manager, or an attributable case approver). Audit-only or generic case read scope is not legal-file
reference authority even if the global permissions are granted. Missing, cross-application,
unattributed, wrong-category, unsupported/mismatched-sensitivity, and otherwise inaccessible files all return the same nondisclosing
`400 VALIDATION_ERROR` text on each denied request field. Missing record/document permission returns
`403 FORBIDDEN`; missing case scope returns `403 OBJECT_ACCESS_DENIED`; a non-related-party cycle
returns `409 INVALID_STATE`. Denial creates no meeting/audit/workflow/case/exception mutation and
never emits a `documents.file.downloaded` audit.

Success returns the standard envelope with the request fields plus
`general_meeting_approval_id`, `recorded_by_user_id`, `recorded_at`, and nullable
`supersedes_general_meeting_approval_id`. Exact replay returns the existing id with no audit,
workflow, or row write. A changed payload creates a new immutable row whose `supersedes` link
names the prior unsuperseded application record; it never updates the prior row. Creation writes
`general_meeting_approval.recorded`; a changed outcome writes
`general_meeting_approval.status_changed`; other changed evidence writes
`general_meeting_approval.superseded`. Each real write has matching
`general_meeting_approval` workflow evidence.

The locked approval action transaction evaluates this gate only after object scope, version,
conflict, assignment/action permission, and distinct effective authority establish that an
`approve` action would be final. Missing, pending, and rejected current evidence return 409 with
codes `GENERAL_MEETING_EVIDENCE_REQUIRED`, `GENERAL_MEETING_APPROVAL_PENDING`, and
`GENERAL_MEETING_APPROVAL_REJECTED`. Details contain `approval_case_id`, `cycle_number`, and the
same nullable `general_meeting_approval` object used by case readers. These denials insert no action
or sanction and do not close/project an Exception Register entry. A conflict still returns the
earlier canonical `CONFLICTED_APPROVER_NOT_ALLOWED` contract.

While an evidence-required cycle is `pending`, collection, detail, action success, and final-gate
details expose the application's current unsuperseded record as nullable `general_meeting_approval`;
the object has `evidence_scope = current_pending`. Successful final approval, rejection, return for
clarification, and an abstention that closes the case as `blocked_by_conflict` freeze whichever
current record exists on that exact cycle (final approval still requires `approved`; other terminal
outcomes do not). Returned and terminal readers expose only that frozen
record with `evidence_scope = cycle_frozen`, beside unchanged `route_approvers`,
`required_approvers`, and `approval_actions`. Later application-level supersession cannot change
historical case or register references. A later pending cycle resolves the then-current
unsuperseded application record independently. §25.11 success remains the source record shape
without `evidence_scope`; the scope discriminator belongs to case/gate projections.

# Sanction decision and Credit Sanction Register reads (007H/007O)

`GET /api/v1/loan-applications/{loan_application_id}/sanction-decision/` requires
`approvals.sanction.read`. It returns the source §25.8 decision shape: id, decision, sanctioned
amount/tenure, interest type/value, repayment date, penal rate, `charges`, security summary,
conditions precedent, and decision reason. It returns `404 NOT_FOUND` when no sanctioned decision
exists, including before terminal approval and after rejection. A-079 remains binding: numeric
rates, repayment date, and penal rate are nullable, charges are `{}`, and the blank conditions
snapshot is projected as `null` until an approved owner supplies those facts. Sanctioned amount,
tenure, interest type, and security summary are copied exclusively from the canonically validated
routed `review_facts`; terminal creation never reads their mutable appraisal-note counterparts.

Permission and row scope are independent. The endpoint first delegates to the approval-owned
coherent-case/read-index selector and revalidates the canonical case decision, then looks up the
immutable approved-cycle decision. Original, effective, conflicted, or acted historical approvers can read
their attributable cycle. An actor with only `approvals.sanction.read`, including an unused
committee Director, receives nondisclosing `403 OBJECT_ACCESS_DENIED` for an unrelated approved
application. A caller with case object scope but without the endpoint permission receives
`403 FORBIDDEN`. Persisted `legal_readonly`, `audit_readonly`, or `management_readonly` grants can
provide case scope only when the caller separately holds the sanction permission; they never grant
approval actions or document access. The deliberate `404 NOT_FOUND` contract still applies when no
sanction decision exists, including before approval and after rejection.

`GET /api/v1/credit-sanction-register/?financial_year=FY2026-27&decision=sanctioned&page=1&page_size=20`
requires `approvals.sanction_register.read` and returns the standard list/pagination envelope.
`decision` is exactly `sanctioned` or `rejected`; `financial_year` is canonical `FYyyyy-yy` and
uses the April 1 inclusive / following April 1 exclusive window (A-086). Page defaults to 1,
page size defaults to 20 and is capped at 100. Unknown parameters or invalid filter values return
`400 VALIDATION_ERROR`. The collection is generated/read-only: POST is method-denied and there is
no row detail/update/delete route. The slice's named readers—CFO and Director committee members,
Company Secretary, and Internal Auditor—receive this read grant in the canonical role seed;
possession of other approval/case permissions does not imply register access.

The collection delegates to the same approval-owned coherent-case/read-index selector before
financial-year or decision filters, ordering, `total_count`, page-bound normalization, and row
serialization. Consequently an original/effective/conflicted/acted Director sees only attributable
cycles and cannot infer unrelated decisions from empty pages, totals, total pages, or filter
results. Persisted legal/audit/management readers see exactly the sanction cases covered by their
active role grant, but only when they also hold `approvals.sanction_register.read`. Register
permission does not become global object authority and grants neither case actions, sanction
decision permission, document-reference authority, nor document download. The selector—not
`routing_snapshot_is_coherent`, register permission, Exception Register presence, or evidence
metadata—is the object-authority source.

A later direct appraisal save or public return/correction/re-review changes only the new credit
owner state. It cannot hide, rewrite, or reattribute an earlier enriched cycle. Pending case
detail/queue/actions, returned-cycle history, terminal case detail, the immutable sanction
decision, and the generated register row continue to use that cycle's byte-for-byte
`loan_limit_provenance` and `review_facts`. A new approval cycle freezes its newly reviewed facts
independently. Conversely, a malformed frozen case is removed before every count/page and returns
nondisclosing detail/action/decision results even when its stale projection flag/index remains true.

Every approved or rejected terminal case creates exactly one immutable
`credit_sanction_register_entries` row in the locked approval action transaction. Approved rows
link the §15.5 sanction decision; rejected rows deliberately keep that link/amount null rather than
inventing a sanction decision. The row also stores the exact terminal `sanction_approval` workflow
event, a byte-for-byte `source_review_facts_json` copy of the validated routed package (including
purpose and risk), and one attributable `credit_sanction_register.created` audit. Stale/closed
retries cannot duplicate the one-to-one case row. Partial approvals, returns, conflict-blocked
cycles, malformed frozen packages, and general-meeting gate denials create no row.

The 15 functional-spec fields and their frozen sources are:

| Response field | Frozen source |
|---|---|
| `application_number` | routed review package's application reference |
| `borrower_name` | routed review package's borrower name |
| `borrower_type` | routed review package's borrower type |
| `requested_amount` | routed review package's requested amount |
| `eligible_amount` | routed review package's verified eligible amount |
| `recommended_amount` | routed review package's reviewed recommendation |
| `sanctioned_amount` | linked sanction decision; null for rejection |
| `approval_authority` | case's canonical effective required-authority/action snapshot |
| `approver_names` | ordered immutable actions for that case/cycle |
| `approval_date` | terminal case closure date |
| `decision` | terminal case outcome mapped to `sanctioned`/`rejected` |
| `reasons` | case approval or rejection reason |
| `exception_reference` | that case's one-to-one 007F row: id/type/business reason/status/cycle |
| `conflict_abstention_details` | that case's frozen exclusions plus attributable abstention action |
| `general_meeting_approval_reference` | that case's frozen 007G row: id/outcome/date/party/user/document metadata ids |

The response additionally includes register/case/application/sanction/workflow ids and
`recorded_at`. Register permission never grants document download: the three general-meeting
document values are metadata ids only, and the document module retains its own permission and
sensitivity checks. No template/Annexure code is stored or projected because OC-002 still leaves
the Annexure K label conflicted (A-087).

# Approval registers and matrix frontend consumption (007J)

`RegistersHub` consumes S23 only from `GET /api/v1/credit-sanction-register/` and S25 only from
`GET /api/v1/exception-register/`. Each filter or page change replaces the rows and pagination
object with that endpoint's latest actor-scoped response. The client does not combine the two
collections, recover hidden rows from case/detail APIs, retain an earlier total, calculate approval
authority or money, or turn case/application/document metadata ids into actions or downloads.

The S71 matrix panel consumes `GET /api/v1/approval-matrix-rules/?page=1&page_size=100` and renders
active, inactive, and retained superseded versions as returned. Each rule additionally projects
display-ready `authority_summary` and numeric `minimum_approver_count` from the approvals
configuration owner; React renders these facts verbatim and does not recompute role or Director
cardinality. A holder of
`approvals.matrix.manage` may submit a complete successor through
`PATCH /api/v1/approval-matrix-rules/{approval_matrix_rule_id}/`; success is a pending governed
configuration proposal, not an immediate edit. The active rule remains unchanged until a distinct
active CFO or Company Secretary approves the proposal through the existing 007A3 boundary.

Register export remains deferred to 012B/012C. The existing `Export Register` action is visible
only with canonical `reports.export`; in 007J it displays an explicit deferred-state notice and
makes no network request, creates no file, and does not imply broader register visibility. This
interim behavior must be replaced, not extended, when the export-job contract lands.

As of 007N, the register/matrix feature service delegates bearer/session headers, request ids,
standard envelope and field-error parsing, malformed-response handling, and pagination extraction
to the shared authenticated frontend client. The feature boundary owns only its exact endpoints,
query filters, successor payload, and typed DTOs.
