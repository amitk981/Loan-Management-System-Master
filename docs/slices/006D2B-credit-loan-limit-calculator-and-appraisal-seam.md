# Slice 006D2B: Credit Loan Limit Calculator and Appraisal Seam

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Second half of the superseded 006D2 refactor: move loan-limit calculation, validation, snapshot
projection, and audit/workflow coordination out of `applications.services` behind
`credit.modules.loan_limit_calculator`, and add the `credit.modules.appraisal_workflow` entry seam
that 006E must use.

## User Value
Financial calculation, snapshot, and audit rules have one explicit testable interface, and future
appraisal work has a documented seam, so sanction/appraisal code cannot bypass or duplicate the
loan-limit rules.

## Depends On
- 006D2A
- 005I5

## 006D2A Handoff Contract
- `EligibilityAssessmentModule.get/run` now owns eligibility locking, persistence, audit/workflow,
  and public snapshots; do not move those helpers back into `applications.services`.
- `resolve_effective_loan_policy(calculation_date=..., for_update=True)` is the sole policy query
  seam. The temporary legacy calculator translates `CreditModuleValidationError.field_errors` to
  `LoanApplicationValidationError`; remove that translation when calculation moves behind the
  shared credit-module result/error interface.
- Preserve the import-boundary test in `tests/test_credit_modules.py`: after 006D2B,
  `applications.services` must also stop exposing `calculate_loan_limit`,
  `serialize_loan_limit_assessment`, `_audit_loan_limit_assessment`, and
  `_loan_limit_assessment_audit_snapshot`.
- 006D2A added no model/table/migration change. Continue to preserve the existing assessment UUID,
  one-to-one row, and table names under ADR-0002.

## 005I5 Handoff Contract
- Eligibility now consumes `applications.modules.nominee_validation.evaluate_nominee_selection`
  as the single public BR-009 authority. Preserve that import and its `valid` / `minor` / `pending`
  classifications while extracting loan-limit behavior; do not copy age/DOB/minority logic into the
  calculator or restore a private eligibility helper.
- Staff `assigned_owner` remains `null` until a persisted assignment/task owner exists. The future
  appraisal seam may expose only its own persisted preparer/assignment facts and must not project
  application receiver/creator as ownership.

## Reference Implementation
A fully-gated implementation of the combined 006D2 scope (304 tests green, 95% coverage; failed
only the diff-size limit) is preserved at
`.ralph/runs/2026-07-10_135716_repair/full-implementation.patch`. Reuse its
`credit/modules/loan_limit_calculator.py`, `credit/modules/appraisal_workflow.py`, and the
matching view/service/test hunks. The eligibility and configuration-resolver portions are already
merged by 006D2A — build on them, do not re-move them.

## Source / Review References
- `docs/source/codebase-design.md` §§6.2-6.3, §7.3, §§12.1-12.3, §22, §26, and §42.2
- `docs/source/data-model.md` §14.1-§14.4 and §34
- `docs/source/api-contracts.md` §3, §22-§24
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_092630_architecture_review`
- `docs/adr/ADR-0002-staged-credit-assessment-model-ownership.md` (already recorded — follow it)

## Architecture Scope
- Move loan-limit rule evaluation, validation, transaction/locking, persistence coordination,
  snapshot DTO, audit/workflow coordination, and public result types behind
  `credit.modules.loan_limit_calculator`. Application views authenticate/parse, call the
  interface, and translate the returned result/error only.
- The calculator resolves policy exclusively through the existing
  `configurations.modules.configuration_resolver` seam from 006D2A; it must not query/interpret
  active configuration directly.
- Eliminate the duplicated public-response/audit-snapshot projection: one canonical redacted
  immutable snapshot representation, with explicit audit/request metadata added at the boundary.
  Tests must fail if the two projections drift in shared financial/policy/acreage fields.
- Add `credit.modules.appraisal_workflow` as the documented 006E entry seam; 006E must not add
  appraisal behavior to `applications.services`.
- Model state ownership follows ADR-0002: staged, non-destructive; the concrete state-only
  migration is the separately queued slice 006D3. Do not rename/drop/recreate
  `eligibility_assessments` or `loan_limit_assessments` tables and do not lose UUIDs/FKs here.
- Add an import-boundary regression proving application views and future appraisal code reach
  loan-limit behavior only via the public module entrypoints.
- Keep dependency direction clean: `configurations.modules.configuration_resolver` must not import
  from `credit`. Define its resolution error/result in the configuration module (or a neutral
  shared module), then translate it inside the credit calculator boundary. No
  `configurations -> credit` dependency may remain.
- Replace the 006D2A runtime identity/`hasattr` boundary check with a static AST/import regression
  that rejects private or aliased credit-helper imports from application views/services and rejects
  direct `LoanPolicyConfig` queries outside the public configuration resolver.

## Cultivated-Acreage Contract (preserve exactly)
Preserve the 006C2 contract inside the extracted calculator: selected `LandHolding.area_acres`,
application-linked `CropPlan.planned_area_acres`, and nullable profile
`land_area_under_cultivation_acres` are normalized through the Decimal path and must agree when
applicable. Disagreement returns `400 VALIDATION_ERROR` with
`error.field_errors.cultivated_acreage = "CULTIVATED_ACREAGE_UNRESOLVED"` before assessment save,
audit, or workflow writes. Module tests must cover the decimal-equivalent path (`5`, `5.0`,
`5.00`), the two-value null-profile path, pending/rejected land or crop evidence, null/wrong
crop-plan application link, and failed-rerun preservation of the stored GET snapshot/evidence
counts.
- Lock every mutable financial source used for a successful snapshot in the calculation
  transaction: application, current assessment, shareholding, selected land holdings, crop plan,
  applicable cultivated-area profile, and effective policy. Tests must prove the public module
  requests the policy resolver with `for_update=True` and does not query policy rows directly.

## Diff Budget (hard requirement)
The parent slice failed twice on `limits.max_lines_changed` (2,000). This half must land well
under it: target <= 1,500 changed lines. If the diff approaches the limit, trim scope (e.g. defer
test-file splitting) rather than exceeding it — a green run over the limit is a failed run.

## Behavior Preservation
- Preserve all existing 006A-006D contracts, permissions, object access, error codes, formulas,
  explicit rerun semantics, immutable read behavior, and metadata-only audit/workflow output.
- No new endpoint, rule, field, styling, or dependency. No destructive model/table migration.

## Test Cases
- Characterization tests green before extraction; the same HTTP payload/status/evidence assertions
  remain green after it.
- Direct module tests cover share/land lower-of-two, below/equal/above boundaries, policy
  ambiguity, cultivated-acreage blockers, snapshot serialization, and failed-rerun preservation.
- Views tested as thin adapters; module tests prove transaction rollback and locking behavior.
- Import-boundary regression for loan-limit private helpers and the appraisal seam.
- Resolver regression patches/calls the public resolver during calculation and asserts
  `for_update=True`; active `LoanPolicyConfig` must never be queried from the calculator module.
- Static dependency regression proves the configuration resolver imports neither `credit` nor
  application-layer result/error types, and aliased private imports fail the boundary test.

## Evidence Required
Characterization and refactor green logs, module/API test logs, an architecture map in the review
packet, and all standard quality gates.

## Risk Level
High

## Acceptance Criteria
- Loan-limit callers depend on the explicit `credit.modules.loan_limit_calculator` interface.
- One canonical redacted snapshot serves both the public response and audit values.
- 006E has a documented appraisal module seam and cannot deepen `applications.services`.
- No behavior regression or destructive migration; changed lines within the diff budget.

## Done Checklist
- [ ] Execution plan written
- [ ] Characterization tests written or confirmed
- [ ] Code implemented
- [ ] API contracts unchanged
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
