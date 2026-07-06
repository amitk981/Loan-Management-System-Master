# Execution Plan — 002C Role and Permission Catalogue Seed

Selected slice: `002C-role-and-permission-catalogue-seed`
Risk: High (RBAC/permissions area). Runs under standing approval (HIGH_RISK_APPROVALS.md; 002C not revoked).

## Source of truth
- `docs/source/auth-permissions.md`: §9.2–9.3 (role/team types), §10.2–10.5 (roles/permissions/role_permissions/teams data model), §11–11.1 (naming convention/verbs), §12.1–12.13 (full permission catalogue), §13.1 (role catalogue), §15.1–15.12 (per-role Key Permissions = seed source), §38.1–38.2 (MVP seed roles/teams), §4.1–4.2 (internal + external/future users).
- Digest: `docs/working/digests/epic-002-platform-auth.md`.
- A-005 (`docs/working/ASSUMPTIONS.md`): prototype aliases `export`/`export_reports`/`view_loans` to reconcile.

## What exists
`sfpcl_credit/identity/models.py` already has `Role`, `Team`, `User`, `UserTeamMembership`, `UserSession`, `AuditLog` (migration `0001_initial`). No `Permission` or `RolePermission` models yet.

## Design
1. **Models** (`identity/models.py`): add `Permission` (permission_id UUID PK, permission_code unique, permission_name, module_name, description, risk_level) and `RolePermission` (role_permission_id UUID PK, role FK, permission FK, granted_by_user FK nullable, granted_at) with a unique (role, permission) constraint. Non-destructive; per §10.3–10.4.
2. **Migration**: exactly one new migration `0002_permission_rolepermission.py` (limit = 1).
3. **Seed module** (`identity/catalogue.py`): declarative catalogue data —
   - `PERMISSIONS`: every §12.1–12.13 code (module_name = code prefix; risk_level lowercased).
   - `ROLES`: §13.1 catalogue + §4.2 external/future roles (external/future seeded `status="inactive"`, `is_system_role=False`).
   - `TEAMS`: §9.3/§38.2 eight team types.
   - `ROLE_PERMISSIONS`: per-role Key Permissions from §15.1–15.12, filtered to codes that exist in the §12 catalogue (no invented codes).
   - `PROTOTYPE_PERMISSION_ALIASES`: A-005 map `export`/`export_reports` → `reports.export`, `view_loans` → `finance.loan_account.read`.
   - `seed_catalogue()`: idempotent upsert of permissions, roles, teams, role-permission links; returns a non-secret summary dict. Single seed interface used by the command and the tests.
4. **Management command** (`identity/management/commands/seed_role_catalogue.py`): thin wrapper calling `seed_catalogue()` and printing the summary.

## Not invented (recorded, not stubbed with fake data)
- §15 references a few codes absent from §12 (`communications.communication.create`, `grievances.manage`, `credit.appraisal.read`, `credit.loan_limit.read`, `finance.repayment.read`): excluded from links, recorded as new assumption A-007.
- Roles with no §15 detail (`sales_team_user`, `it_head`, `management_viewer`, external/future): seeded with empty permission sets (assigning permissions would invent a business rule) — recorded in A-007.

## TDD (mandatory)
Test file `sfpcl_credit/tests/test_catalogue_seed.py` (SimpleTestCase + manual schema_editor pattern, matching `test_auth_api.py`):
1. seed creates all standard internal role codes and all team codes.
2. seed creates representative permission codes across every §12 module group.
3. rerunning seed is idempotent (no duplicate rows).
4. A-005 alias targets exist in canonical seeded permissions.
5. role-permission links created via `seed_catalogue()`; every link references a catalogue permission; spot-check role has expected §15 codes.
Save red then green output to `evidence/terminal-logs/`.

## Gates
`manage.py check`, full `manage.py test`, `makemigrations --check`, coverage ≥ 85%. Frontend untouched. API_CONTRACTS unchanged (no endpoint added) — DB/seed-only.

## Artifacts
changed-files.txt, risk-assessment.md, review-packet.md, final-summary.md, updated ASSUMPTIONS (A-005 resolved, A-007 added), digest note, HANDOFF, state.json, progress.md. Sharpen next slices 002C2/002D.
