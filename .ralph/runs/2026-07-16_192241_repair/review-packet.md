# Review Packet: 2026-07-16_192241_repair

## Result

Repair complete pending independent orchestrator validation and commit.

## Slice

`009B3A-sap-model-owner-and-state-migration`

## Failure repaired

The authoritative validation run reported six backend errors and a frontend typecheck failure.
The exact nine-test backend order reproduced all six errors. The SAP transfer test passed alone,
which isolated the defect to historical migration-test graph projections rather than the state-only
operation. The new SAP migration leaf reached current loan/application state; two older tests did
not exclude it from their deliberately historical projections. Their model state therefore outran
their reversed physical schema, and failed setup prevented normal teardown before the SAP test.

The frontend failure was the existing Node-only Playwright resolver being included through its
`src` unit test without a `node:fs` declaration or a typed process surface.

## Repair

- Added `sap_workflow` to the downstream-leaf exclusions in the credit-owner and witness historical
  migration tests.
- Added the narrow compile-time `node:fs.existsSync` declaration already used by the resolver.
- Read optional environment data through a typed `globalThis.process` view, preserving exact
  override/bundled/system Chromium resolution behavior.
- Left the SAP models, transfer operation, physical tables, policy boundary, public API, and
  business data unchanged from the quarantined implementation.

## Traceability

| Requirement | Implementation truth | Evidence |
|---|---|---|
| Codebase design assigns SAP state to `sap_workflow` | Canonical models and relations remain in the SAP owner; Finance names are identical imports | 101 impacted tests and canonical ownership assertions |
| Existing data and physical identity must not move | Transfer migration remains state-only and renders no SQL | `evidence/terminal-logs/backend-integrity.txt` |
| Historical migrations must remain loadable | Credit, SAP, and witness migration modules pass together after explicit graph isolation | RED/GREEN migration loop logs |
| Existing uniqueness/races must remain exact | All three request/code concurrency tests pass twice on PostgreSQL | PostgreSQL logs 1 and 2 |
| Configured frontend compilation must pass | Existing resolver is typed without dependency/UI/runtime changes | `frontend-repair-validation.txt` |

## Verification

- Exact migration loop: 9/9 pass after previously producing six errors.
- Impacted backend: 101 pass, four expected PostgreSQL-only skips under SQLite.
- PostgreSQL: 3/3 race tests pass in each of two independent runs.
- Django check: pass.
- Migration sync: no changes detected.
- SQL proof: no writable SQL.
- Frontend resolver: 4/4 tests pass.
- Frontend typecheck, lint, and build: pass.
- `git diff --check`: pass.

## Review findings

- Standards: no remaining repair finding. The historical migration fixtures now explicitly state
  their dependency exclusions and no longer depend on the set of current leaf apps.
- Spec: no remaining repair finding. No SAP business rule, HTTP behavior, permission, audit event,
  persisted identity, or concurrency constraint changed.
- Residual: authoritative full backend coverage and full frontend tests remain the orchestrator's
  required independent gate.

## Next action

Independently validate and commit 009B3A, then execute 009B3B and 009D2 before 009E.
