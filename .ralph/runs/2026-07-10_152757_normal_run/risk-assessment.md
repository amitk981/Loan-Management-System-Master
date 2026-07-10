# Risk Assessment

Risk level: High

- Selected slice: `006D2A-credit-eligibility-module-and-configuration-seam`
- Mode: `normal_run`
- Manual review required: no blocking review before orchestrator validation; the owner's standing
  approval applies and the architecture-review cadence is now due.

## Why High

- Eligibility decisions gate later financial appraisal and sanction work.
- The refactor moves permission/object access, transaction locking, persistence, audit, and workflow
  coordination across a new module seam.
- Effective Board-policy selection is shared by the financial loan-limit calculation.

## Controls Applied

- Behavior was characterized before extraction and the same eligibility HTTP tests passed after
  application views were routed through the public module.
- Direct module tests cover eligible, ineligible, pending-manual-evidence, and forced audit-failure
  rollback paths using the real database/audit/workflow interfaces.
- The resolver preserves the exact missing/overlapping/invalid policy validation messages and the
  legacy calculator translates the shared validation error back to its unchanged API error type.
- An import-boundary regression prevents application services from exposing migrated eligibility
  helpers or a second policy resolver.
- Full backend suite: 308 tests, 95% coverage (85% floor). Django check and migration sync passed.
  Frontend lint/typecheck/build and all 106 tests passed.
- No model, table, migration, endpoint, API payload, dependency, frontend, external call, or
  protected/source file changed.

## Residual Risk

- Loan-limit behavior remains temporarily in `applications.services` until 006D2B. It now delegates
  policy selection to the resolver, but its compatibility error translation is an interim seam that
  006D2B must remove when the calculator moves into `credit.modules.loan_limit_calculator`.
- Eligibility models remain owned by `applications.models` under ADR-0002; the separately queued
  006D3 must perform any state-only ownership migration without touching physical tables or UUIDs.
