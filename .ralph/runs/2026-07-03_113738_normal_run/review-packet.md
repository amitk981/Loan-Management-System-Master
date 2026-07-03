# Review Packet: 2026-07-03_113738_normal_run

## Result
Passed (all gates green) — awaiting orchestrator's independent validation and commit.

## Slice
002C-role-and-permission-catalogue-seed (High risk; standing approval)

## What this slice does, in plain English
The frontend prototype had roles and made-up permission words. This slice puts the *real*,
official list of roles, teams, and permissions into the backend database, exactly as the
source specification writes them down, so every future screen and API checks the same names.
It adds a repeatable command (`seed_role_catalogue`) that fills the database and can be run
again safely without creating duplicates.

## Traceability (source says X → code does X → test proves it)
1. **Permissions.** `auth-permissions.md` §12.1–12.13 lists the permission catalogue.
   → `catalogue.PERMISSIONS` transcribes all 171 codes; `seed_catalogue()` stores them with
   module + risk. → `test_seed_creates_representative_permission_per_module_group` checks one
   real code per module group and that every code has a module and a valid risk level.
2. **Roles.** §13.1 (internal) + §4.2 (external/future). → 15 internal roles seeded `active`,
   5 external/future seeded `inactive`. → `test_seed_creates_standard_role_and_team_codes`
   asserts all internal role codes exist and `borrower_portal_user` is inactive/non-system.
3. **Teams.** §9.3 / §38.2 list eight teams. → `catalogue.TEAMS`. → same test asserts the
   exact team-code set.
4. **Role→permission grants.** §15.1–15.12 "Key Permissions". → `catalogue.ROLE_PERMISSIONS`
   (filtered to catalogue codes) linked via `RolePermission`. →
   `test_role_permission_links_use_catalogue_and_seed_interface` asserts every link points to
   a real catalogue permission and that `credit_manager` has expected §15 codes.
5. **Idempotency.** Validation rule: "deterministic and idempotent." → `update_or_create` /
   `get_or_create` + unique constraint. → `test_seed_is_idempotent` (counts stable across two
   runs) and a fresh-DB double-run in `evidence/api-responses/seed-fresh-db.log`.
6. **A-005 alias reconciliation.** → `PROTOTYPE_PERMISSION_ALIASES`. →
   `test_prototype_aliases_map_to_canonical_permissions`. A-005 marked resolved (backend).

## Honest gaps (recorded, not hidden)
- **A-007:** five permission codes referenced only in §15 (not §12) are not seeded; and
  `sales_team_user`, `it_head`, `management_viewer` have no permission links because the source
  docs don't state their permission sets. Assigning any would invent a business rule
  (DECISION_POLICY §1.3), so they are recorded for a future slice/doc fix.

## Evidence
- `evidence/terminal-logs/backend-tests-red.log` (failing first), `.../backend-tests-green.log`,
  `.../backend-coverage.log` (94%), `evidence/api-responses/seed-fresh-db.log` (fresh-DB seed).

## Gates
backend check ✓ · 19/19 tests ✓ · makemigrations --check ✓ · coverage 94% ≥ 85 ✓ ·
frontend typecheck ✓ · frontend tests 5/5 ✓ · frontend build ✓ · no protected files touched.

## Recommended Next Action
Promote and run the next slice `002C2-standard-api-envelope-and-auth-service-boundary`
(lowest-numbered Not Started), then `002D`.
