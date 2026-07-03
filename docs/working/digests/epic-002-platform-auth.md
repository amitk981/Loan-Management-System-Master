# Digest — Epic 002: Platform Auth and Role Shell

Source of truth: `docs/source/auth-permissions.md` (section numbers below), `docs/source/api-contracts.md` §11–12, 43–44, `docs/source/data-model.md` identity/access tables.

## Already implemented (002A, 002B — merged to main 2026-07-02; 002B2 completed 2026-07-03)
- Django backend `sfpcl_credit/` with health endpoints (`/live`, `/ready`, `/deep`).
- Custom identity models: `User`, `Role`, `Team`, `UserSession`, `UserTeamMembership`, `AuditLog` (`sfpcl_credit/identity/models.py`).
- `POST /api/v1/auth/login/`, `/refresh/`, `/logout/` with refresh rotation, replay rejection, revocation, auth audit events. Contracts in `docs/working/API_CONTRACTS.md`.
- JWT signing now uses PyJWT HS256 with `SECRET_KEY` read from `SFPCL_SECRET_KEY` and local-dev fallback. Refresh-session storage, rotation, replay rejection, and logout revocation behaviour were preserved.

## Next sharpened slices (updated 2026-07-03)
- 002C should seed canonical roles, teams, permissions, and role-permission links. Use the role catalogue, team types, module groups, and A-005 alias reconciliation notes below.
- 002D should add `GET /api/v1/auth/me/` using PyJWT access-token validation, returning user identity, role codes, team codes, effective permission codes from 002C, and dashboard action availability.

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

## Approval authority (needed from 007x onward, recorded for orientation)
- Authority types §16.1; loan sanction authority §16.2 (≤ ₹5,00,000: CFO + 1 Director; above: CFO + 2 Directors — mirrored in prototype `ApprovalPanel.tsx`); disbursement authority §16.3; security authority §16.4.
- Conflict-of-interest rules: §17 (blocks conflicted approvers; API behaviour §17.3).
