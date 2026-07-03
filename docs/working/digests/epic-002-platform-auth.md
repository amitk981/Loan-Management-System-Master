# Digest — Epic 002: Platform Auth and Role Shell

Source of truth: `docs/source/auth-permissions.md` (section numbers below), `docs/source/api-contracts.md` §11–12, 43–44, `docs/source/data-model.md` identity/access tables.

## Already implemented (002A, 002B — merged to main 2026-07-02; 002B2 completed 2026-07-03)
- Django backend `sfpcl_credit/` with health endpoints (`/live`, `/ready`, `/deep`).
- Custom identity models: `User`, `Role`, `Team`, `UserSession`, `UserTeamMembership`, `AuditLog` (`sfpcl_credit/identity/models.py`).
- `POST /api/v1/auth/login/`, `/refresh/`, `/logout/` with refresh rotation, replay rejection, revocation, auth audit events. Contracts in `docs/working/API_CONTRACTS.md`.
- JWT signing now uses PyJWT HS256 with `SECRET_KEY` read from `SFPCL_SECRET_KEY` and local-dev fallback. Refresh-session storage, rotation, replay rejection, and logout revocation behaviour were preserved.

## 002C done (2026-07-03)
- Added `Permission` and `RolePermission` models (`sfpcl_credit/identity/models.py`, migration `0002`). Seed module `sfpcl_credit/identity/catalogue.py` + idempotent management command `seed_role_catalogue`.
- Seeded on a fresh DB: 171 permissions (all §12.1-12.13), 20 roles (15 active internal + 5 inactive external/future), 8 teams, 134 role-permission links (§15 Key Permissions filtered to catalogue codes).
- A-005 resolved for backend via `PROTOTYPE_PERMISSION_ALIASES` (`export`/`export_reports`→`reports.export`, `view_loans`→`finance.loan_account.read`). Frontend union re-wiring deferred to 002D/002E.
- Gaps recorded in A-007: five §15 codes not in §12 are unseeded; `sales_team_user`/`it_head`/`management_viewer` have no permission links (avoiding invented grants). 002D should read effective permissions from `RolePermission`.

## 002C2 done (2026-07-03)
- Single production response envelope now lives in `sfpcl_credit/api.py` (`success_response`, `error_response`, `response_meta`, plus `parse_json_body`, `request_ip`, `request_user_agent`). Health responses gained the missing `meta.api_version: "v1"`; auth envelope unchanged. Duplicate `success_response` helpers removed from `ops.py` and `identity/views.py`.
- Auth behavior moved behind explicit module functions in `sfpcl_credit/identity/modules/`: `tokens.py` (encode/decode/hash/claims + `TokenError`) and `auth_service.py` (`authenticate_user`/`CredentialError`, `issue_login_tokens_and_session`, `validate_refresh_session`, `rotate_refresh_token`, `revoke_session_for_logout`, `validate_access_token`, `record_auth_event`, `auth_payload`). Views are now thin (parse → call module → translate errors). `views.py` re-exports `TokenError` and `decode_token` for backward-compatible imports.
- All 002B/002B2 behavior preserved (verified by unchanged `test_auth_api.py` + new `test_auth_module.py`): PyJWT HS256, lifetimes, claims, refresh rotation, replay rejection, logout revocation, inactive-user rejection, audit events.

## 002D done (2026-07-03)
- Added `GET /api/v1/auth/me/` in `sfpcl_credit/identity/views.py` and `sfpcl_credit/config/urls.py`.
- Current-user reads use `auth_service.current_user_payload_for_access_token()`, which calls the new session-bound `validate_access_session()`: access token must be signed, unexpired, type `access`, bound to an active `UserSession`, and owned by a user whose status can authenticate.
- A-008 resolved for `/auth/me/`: logged-out/revoked sessions and suspended/inactive users cannot retrieve profile, permission, or action data. `validate_access_token()` remains the low-level stateless JWT decode helper.
- Response data: `user_id`, `full_name`, `email`, `status`, `role_codes`, `team_codes`, sorted/de-duplicated `permissions`, and `available_actions`.
- Effective permissions come from `Permission.objects.filter(role_permissions__role=user.primary_role)`. Inactive primary roles return `[]`; A-007 zero-link roles (`sales_team_user`, `it_head`, `management_viewer`) return `[]` until source docs define grants.
- Auth errors use the shared envelope: missing bearer token `401 AUTH_REQUIRED`; expired access token `401 TOKEN_EXPIRED`; refresh/wrong-type, malformed, revoked-session, inactive-user, or unknown-session tokens `401 INVALID_TOKEN`.
- Tests added in `test_auth_api.py` and `test_auth_module.py`: success envelope/meta, missing token, expired token, refresh misuse, inactive user, revoked session, permission sorting/empty cases, available actions, and thin-view service-boundary guardrail.
- API examples saved in `.ralph/runs/2026-07-03_175127_normal_run/api-response-examples.md`.

## 002D3 done (2026-07-03)
- Corrected `/api/v1/auth/me/` source fidelity before frontend shell wiring. The success `data` now includes `mobile_number`, `roles[{role_code, role_name}]`, and `teams[{team_code, team_name}]` in addition to the compatibility `role_codes`, `team_codes`, `permissions`, and `available_actions` fields.
- `roles` is derived from the active primary role; inactive primary roles return `roles: []`, `role_codes: []`, and `permissions: []`.
- `teams` is derived from active memberships to active teams and sorted by `team_code`; `team_codes` is derived from the same payload.
- Security behavior from 002D is unchanged: session-bound bearer access validation, active-user enforcement, standard envelopes, and the existing `AUTH_REQUIRED`, `TOKEN_EXPIRED`, and `INVALID_TOKEN` cases remain covered by tests.
- API examples saved in `.ralph/runs/2026-07-03_214932_normal_run/api-response-examples.md`.

## Next sharpened slices (updated 2026-07-03)
- 002C, 002C2 DONE — see above.
- 002D is DONE — see above.
- 002D2 is DONE.
- 002D3 is DONE — `/auth/me/` now matches `docs/source/api-contracts.md` §11.4 while preserving 002D compatibility fields.
- 002E should replace the staff demo auth shell with backend login → `/auth/me/` → protected shell state using the 002D3 data shape. Preserve the existing visual system exactly, keep borrower portal demo auth out of scope, display role/team names from `roles`/`teams`, keep `role_codes`/`team_codes` as compatibility data, and derive staff navigation/route visibility from backend canonical permissions through a documented mapping layer. Unknown permission mappings must go to `ASSUMPTIONS.md`, not invented grants.
- Architecture review 2026-07-03_170432 found no source-fidelity defect in the 002C/002C2 production behavior, but found two follow-ups:
  - 002D evidence must save actual red/green `/auth/me/` test logs and API examples at paths referenced by the review packet. The two prior run packets referenced `evidence/terminal-logs/`, but those directories were absent from committed artifacts; root green gate logs existed.
  - 002D2 should remove duplicated backend test schema setup. Current tests repeat `django.setup()` + `schema_editor.create_model()` helpers in `test_auth_api.py`, `test_auth_module.py`, `test_api_envelope.py`, and `test_catalogue_seed.py`; after 002D2 they should rely on Django's migrated test database/shared test base.
  - Current worktree validation can still fall back to bare `python3` for backend gates because `.ralph/venv` is outside the worktree. Agents must run backend commands with `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python` until the protected Ralph scripts are repaired by the owner/orchestrator.
- 002D2 should also make dev backend infrastructure usable for frontend stitching: persistent dev SQLite DB (`sfpcl_credit/db.sqlite3`, tests still in-memory), env-driven `SFPCL_SECRET_KEY`/`SFPCL_DEBUG`/`SFPCL_ALLOWED_HOSTS`, pinned CORS support allowing `http://localhost:5173`, and a short API_CONTRACTS dev setup note.
- 002E now explicitly depends on 002D2: staff login/current-user wiring should call the backend directly from Vite origin `http://localhost:5173` without a frontend proxy, use `/auth/me/` after login and after reload, and save CORS evidence for health/auth calls.
- 002EX now explicitly depends on 002E and 002D2: its tracer screen must run through authenticated staff session state, use real APIs and persistent dev SQLite for manual smoke evidence, keep automated tests on the migrated Django test database, and include an unauthenticated `401` envelope regression for at least one tracer endpoint.

## For 002C — Role and Permission Catalogue Seed
- Permission naming convention: §11 (verbs in §11.1); full permission catalogue by module: §12.1–12.13 (auth/user-admin, members, KYC, applications, credit assessment, approvals, documentation, security, SAP/finance, monitoring/default, closure, compliance, reports/audit/config).
- Standard role catalogue: §13.1. Internal roles (§4.1): Field Officer, Deputy Manager–Finance, Credit Manager, Compliance Team Member, Company Secretary, Senior Manager–Finance, Chief Financial Controller (CFC), CFO, Director, Accounts Head, Sales Team User, IT Head, Internal Auditor, System Administrator. External/future (§4.2): Borrower/Member (portal), Nominee, Bank User (not MVP), Subsidiary User, External Auditor.
- Role-to-permission matrix: §14.1 (high level), §15.1–15.12 (per-role detail — the seed data source).
- Role types (§9.2): operational, approval, compliance, finance, administration, read-only. Team types (§9.3): Credit Assessment, Compliance, Treasury, Sanction Committee (CFO + two Executive Directors), Accounts, IT, Audit, Sales.
- Frontend already has a prototype permission model in `sfpcl-lms/src/contexts/RoleContext.tsx` (union `Permission`, `ROLE_PERMISSIONS`) — the seeded backend catalogue is the source of truth; the frontend union gets reconciled in 002D/002E.
- ASSUMPTION made during 2026-07-02 repair (reconcile in this slice): prototype calls `can('export')`/`can('export_reports')`/`can('view_loans')` were mapped to existing `export_registers`/`view_loan_accounts` permissions.

## For 002D — Current User API
- JWT claims: §5.3. Token types/lifetimes: §5.2 (access + refresh; lifetimes configured in `sfpcl_credit/config/settings.py`).
- Account lifecycle/status values: §7.1–7.3 (only active users may log in — already enforced/tested in 002B).
- Session policy: §8.2. Sensitive re-auth flow: §6.5 (later slice).
- Data model tables: §10.1–10.8 (`users`, `roles`, `permissions`, `role_permissions`, `teams`, `user_team_memberships`, `user_sessions`, `sensitive_access_logs`).
- Source API contract §11.4 defines `/api/v1/auth/me/` as current user profile, roles, teams, and permissions. API conventions require `Authorization: Bearer <access_token>` for protected APIs and standard success/error envelopes with `meta.request_id`, `meta.timestamp`, and `meta.api_version`.

## For 002C2 — API Envelope and Auth Module Boundary
- `docs/source/api-contracts.md` §6.1 says success envelopes include `success`, `data`, and `meta.request_id`, `meta.timestamp`, `meta.api_version`.
- Current code before 002C2 has two production success helpers: `sfpcl_credit/ops.py` for health (missing `api_version`) and `sfpcl_credit/identity/views.py` for auth (includes `api_version`).
- `docs/source/technical-architecture.md` §13.1 says Django views should not contain complex workflow orchestration; multi-entity operations, permissions, calculations, and audit logs belong in explicit service classes/functions.
- `docs/source/codebase-design.md` §6-7 says workflow/business logic should live behind explicit module interfaces and tests should exercise those interfaces, not scattered helpers.
- Keep endpoint URLs and auth behavior unchanged: PyJWT HS256, token lifetimes, JWT claims, refresh rotation, replay rejection, logout revocation, inactive-user rejection, and auth audit events.

## Approval authority (needed from 007x onward, recorded for orientation)
- Authority types §16.1; loan sanction authority §16.2 (≤ ₹5,00,000: CFO + 1 Director; above: CFO + 2 Directors — mirrored in prototype `ApprovalPanel.tsx`); disbursement authority §16.3; security authority §16.4.
- Conflict-of-interest rules: §17 (blocks conflicted approvers; API behaviour §17.3).
