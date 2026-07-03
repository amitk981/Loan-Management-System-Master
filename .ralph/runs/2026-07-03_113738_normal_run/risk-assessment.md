# Risk Assessment — 002C Role and Permission Catalogue Seed

**Slice risk level (from slice file): High.** Runs under the owner's standing approval
(`docs/working/HIGH_RISK_APPROVALS.md`, 2026-07-02); 002C is not `[revoked]`.

## Why the slice is classified High
It defines the canonical RBAC vocabulary (roles, permissions, teams, role→permission
grants) that every later authorization decision depends on. Wrong or invented codes would
propagate into permission checks, the `/auth/me` contract, and the frontend union.

## What was actually changed
- Added two additive models (`Permission`, `RolePermission`) + one non-destructive
  migration (`0002`). No existing table/column altered; no data migration.
- Added a declarative seed module and an idempotent management command. No HTTP endpoint,
  no auth-path change, no external service, no dependency added.

## Residual risk and mitigations
| Risk | Mitigation |
|---|---|
| Wrong/invented permission codes | All 171 codes transcribed verbatim from `auth-permissions.md` §12.1-12.13; module_name derived mechanically from the code prefix. |
| Inventing role→permission grants the docs don't state | Links come only from §15 "Key Permissions", filtered to catalogue codes. Roles with no §15 detail get zero links. Five §15-only codes excluded. Recorded in A-007 rather than fabricated. |
| Seed run twice → duplicate rows | `update_or_create`/`get_or_create` keyed on unique codes + a `unique_role_permission` constraint. Idempotency proven by test and by a fresh-DB double-run (counts identical). |
| Prototype alias drift (A-005) | `PROTOTYPE_PERMISSION_ALIASES` maps the three prototype strings to canonical codes; test asserts each target exists. A-005 marked resolved for backend; frontend re-wiring deferred to 002D/002E. |
| External/future roles usable in MVP | Seeded `status="inactive"`, `is_system_role=False`; test asserts `borrower_portal_user` is inactive. |

## Reversibility
Fully reversible: additive migration; catalogue is data. No destructive or history-rewriting
operation. No secrets or real PII involved (only role/permission metadata).

## Gate results
check ✓ · full test suite 19/19 ✓ · makemigrations --check "No changes detected" ✓ ·
coverage 94% (floor 85) ✓ · frontend typecheck ✓ · frontend test 5/5 ✓ · frontend build ✓.
