# Review Packet

Slice: `006D2-credit-assessment-deep-module-boundary`
Run: `2026-07-10_135716_repair`

## Change Summary

- Added the `sfpcl_credit.credit` package and public credit module seams:
  - `credit.modules.eligibility_assessment`
  - `credit.modules.loan_limit_calculator`
  - `credit.modules.appraisal_workflow`
- Added `configurations.modules.configuration_resolver` for effective loan-policy lookup and
  validation.
- Moved eligibility and loan-limit behavior out of `applications.services`, including transaction
  orchestration, validation, persistence coordination, snapshot projection, audit, and workflow
  evidence.
- Updated application views for eligibility/loan-limit endpoints to call the credit module
  interfaces and translate typed module errors.
- Added `test_credit_modules.py` with module-interface tests and an import-boundary regression.
- Added ADR-0002 and follow-up slice 006D3 for non-destructive model ownership migration.
- Updated the Epic 006 digest and sharpened 006E to use the new appraisal workflow seam.

## Architecture Map

```text
applications.views
  authenticate + parse HTTP
  |
  +--> credit.modules.eligibility_assessment.EligibilityAssessmentModule
  |      - permission/object access
  |      - state guard
  |      - source-backed eligibility checks
  |      - assessment persistence
  |      - eligibility.assessed audit/workflow evidence
  |
  +--> credit.modules.loan_limit_calculator.LoanLimitCalculator
         - permission/object access
         - eligibility prerequisite
         - source fact validation, including 006C2 acreage agreement
         - configurations.modules.configuration_resolver.resolve_effective_loan_policy
         - lower-of-two formula and one-to-one snapshot persistence
         - canonical response/audit snapshot
         - loan_limit.calculated audit/workflow evidence
```

`applications.services` remains the application-intake/completeness module and no longer exposes
public credit aliases for run/calculate/serialize/policy lookup.

## Traceability

- Source says views must authenticate/parse, call a module interface, and not calculate loan limits
  (`docs/source/codebase-design.md` §§6.2-6.3, §7.3). Code now routes credit endpoints through
  `EligibilityAssessmentModule` and `LoanLimitCalculator`; verified by
  `CreditModuleBoundaryTests.test_credit_module_import_boundary_has_no_application_service_aliases`.
- Source names `credit.modules.eligibility_assessment`, `credit.modules.loan_limit_calculator`, and
  `credit.modules.appraisal_workflow` (§§12.1-12.3). Code adds these modules and a 006E-ready
  appraisal seam; verified by module import-boundary tests.
- Source requires transactional eligibility/loan-limit writes and snapshot decisions
  (`codebase-design.md` §22; `data-model.md` §34; `api-contracts.md` §3). Code keeps transaction
  boundaries in the credit modules and preserves audit/workflow writes; verified by full API tests.
- Source requires testing through module interfaces (`codebase-design.md` §26). Code adds direct
  module tests for eligibility and loan-limit snapshots, not private helper tests.
- Source data-model tables remain `eligibility_assessments` and `loan_limit_assessments`
  (§§14.1-14.2). No migration was generated; ADR-0002 stages model ownership migration with
  explicit table/UUID/FK preservation requirements.

## Validation Evidence

- New module RED: `evidence/terminal-logs/006D2-credit-modules-red.log`
- New module GREEN: `evidence/terminal-logs/006D2-credit-modules-green.log`
- Pre-refactor characterization: `evidence/terminal-logs/006D2-characterization-green.log`
- Post-refactor characterization: `evidence/terminal-logs/006D2-characterization-after-refactor.log`
- Backend check: `backend-check-results.md`
- Backend tests: `backend-test-results.md` (304 tests)
- Migration sync: `backend-migrations-results.md`
- Coverage: `backend-coverage-results.md` (95%)
- Frontend lint/typecheck/tests/build: `lint-results.md`, `typecheck-results.md`, `test-results.md`,
  `build-results.md`
- Diff hygiene: `diff-check-results.md`

## Model Ownership Decision

Model ownership is staged. The behavior/interface extraction is complete, but the Django model
classes stay in `applications.models` until 006D3 can perform a state-only ownership migration
without destructive table movement.
