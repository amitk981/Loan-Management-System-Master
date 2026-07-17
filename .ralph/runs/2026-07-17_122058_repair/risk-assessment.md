# Risk Assessment

Risk level: High (inherited slice); repair delta Low

- Selected slice: 009E3-disbursement-amount-and-source-bank-governance-closure
- Mode: repair
- Standing approval: applies; no owner veto is recorded.
- Manual review required: independent orchestrator revalidation before commit.

## Demonstrated failure and control

- Risk: a module-level specialized Django `TestCase` subclass was collected as 13 additional tests,
  and three inherited assertions failed because its setup deliberately adds loan-owner facts.
- Control: retain fixture overrides in a plain mixin and create the concrete `TestCase` subclass only
  inside the helper factory used by `FinalDocumentationApprovalApiTests.setUp`.
- Proof: the affected module changes from 70 collected tests with three failures to 57 intended
  tests passing twice; the original 13 checklist tests still pass independently.

## Residual risk

The repair changes no production code, database schema, permission, money rule, API, or frontend.
The original High-risk 009E3 implementation still requires the orchestrator's complete coverage and
PostgreSQL validation before commit. Ruff is not importable in the managed backend interpreter; no
package was installed, and the configured backend test/check/migration gates used here are green.
