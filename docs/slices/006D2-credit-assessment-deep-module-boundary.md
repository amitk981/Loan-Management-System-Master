# Slice 006D2: Credit Assessment Deep Module Boundary

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Close architecture drift from review `2026-07-10_092630_architecture_review`: move eligibility and
loan-limit behavior out of the generic 2,789-line application service into the documented deep
credit modules before appraisal adds more rules.

## User Value
Eligibility, financial calculation, snapshot, and audit rules have one explicit testable interface,
reducing the chance that later appraisal/sanction work duplicates or bypasses them.

## Depends On
- 006C2

## Source / Review References
- `docs/source/codebase-design.md` §§6.2-6.3, §7.3, §§12.1-12.3, §22, §26, and §42.2
- `docs/source/data-model.md` §14.1-§14.4 and §34
- `docs/source/api-contracts.md` §3, §22-§24
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_092630_architecture_review`

## Architecture Scope
- Establish the source-named `sfpcl_credit.credit` Django/domain package with public module seams:
  `credit.modules.eligibility_assessment` and `credit.modules.loan_limit_calculator`.
- Move rule evaluation, validation, transaction/locking, persistence coordination, snapshot DTO,
  audit/workflow coordination, and public result types behind those interfaces. Application views
  authenticate/parse, call one interface, and translate the returned result/error only.
- Move effective loan-policy lookup/validation behind
  `configurations.modules.configuration_resolver`; the calculator must not query/interpret active
  configuration directly.
- Eliminate the duplicated public-response/audit-snapshot projection by producing one redacted
  immutable snapshot representation with explicit audit/request metadata added at the boundary.
- Split eligibility/loan-limit behavior tests from the 3,305-line application HTTP suite. Add pure
  calculator/module-interface tests for formulas/policy/acreage and retain focused HTTP contract,
  permission, object-scope, transaction, and no-side-effect tests.
- Future 006E appraisal code must enter through `credit.modules.appraisal_workflow`; do not add any
  appraisal behavior to `applications.services`.

## Model Ownership / Migration Safety
- Credit-assessment models belong to the credit bounded context. Move Django model ownership using
  a non-destructive, data-preserving migration/state strategy: do not rename/drop/recreate existing
  `eligibility_assessments` or `loan_limit_assessments` tables and do not lose UUIDs/FKs.
- If Django state ownership cannot be moved safely inside one migration/diff limit, record the
  staged ownership decision in an ADR and create a separately queued, concrete model-ownership
  slice; the behavior/module extraction in this slice is still mandatory and 006E must target the
  credit interface, not the legacy service.

## Behavior Preservation
- Preserve all existing 006A-006D contracts, permissions, object access, error codes, formulas,
  explicit rerun semantics, immutable read behavior, and metadata-only audit/workflow output.
- No new endpoint, rule, field, styling, or dependency is part of this refactor.

## Test Cases
- Characterization tests are green before extraction and the same HTTP payload/status/evidence
  assertions remain green after it.
- Direct module tests cover eligible/ineligible/pending, share/land lower-of-two, below/equal/above
  boundaries, policy ambiguity, cultivated-acreage blockers, snapshot serialization, and failed
  rerun preservation.
- Views are tested as thin adapters; module tests prove transaction rollback and locking behavior.
- Migration tests prove existing assessment rows/UUIDs remain readable after model-state changes.

## Evidence Required
Characterization and refactor green logs, module/API test logs, migration data-preservation proof,
an architecture map in the review packet, and all standard quality gates.

## Risk Level
High

## Acceptance Criteria
- Eligibility and loan-limit callers depend on explicit deep credit-module interfaces.
- Configuration selection has one configuration-resolver seam.
- No behavior regression or destructive model/table migration occurs.
- 006E has a documented appraisal module seam and cannot deepen `applications.services`.

## Done Checklist
- [ ] Execution plan written
- [ ] Characterization tests written or confirmed
- [ ] Code implemented
- [ ] Architecture/ADR updated, if staged ownership is required
- [ ] Migration/data preservation tested, if needed
- [ ] API contracts unchanged or reconciled
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
