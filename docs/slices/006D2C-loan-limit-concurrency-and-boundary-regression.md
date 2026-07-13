# Slice 006D2C: Loan Limit Concurrency and Boundary Regression

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Close architecture review `2026-07-10_173305_architecture_review` by proving the financial
calculator's locking under competing transactions and making its static module boundary reject
package-level and aliased bypasses without coupling to an exact implementation method set.

## Depends On
- 006D3

## Source / Review References
- `docs/source/codebase-design.md` §§12.2-12.3, §22.3, and §26.1-§26.4
- `docs/source/data-model.md` §14.2 and §34
- `docs/source/api-contracts.md` §3 and §23
- `docs/slices/006D2B-credit-loan-limit-calculator-and-appraisal-seam.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_173305_architecture_review`

## Scope
- Add a `TransactionTestCase`-level competing-calculation regression using independent database
  connections/transactions and a deterministic barrier around the public
  `LoanLimitCalculator.calculate_for_application(...)` interface.
- Prove two competing successful reruns cannot create duplicate assessment rows, lose the
  one-to-one UUID, mix policy/source inputs between snapshots, or leave audit/workflow evidence
  inconsistent with the final row. Document backend-specific lock behavior; do not mistake a
  mocked `.select_for_update.called` assertion for concurrency evidence.
- Cover a competing valid/invalid pair: the invalid transaction must not overwrite the valid
  snapshot or add success evidence.
- Keep the existing lock-call unit regression as a fast diagnostic, but make the transactional
  outcome test authoritative. Where SQLite cannot exercise row locks, run the same interface case
  against the repository's PostgreSQL integration-test configuration; do not silently skip the only
  concurrency proof.
- Strengthen the AST/import boundary helper to inspect `ast.Import` and `ast.ImportFrom`, resolve
  aliases/package imports, reject direct concrete assessment/policy access outside the owning
  modules, and positively require the public calculator/appraisal imports. Replace the exact full
  `AppraisalWorkflow` method-set assertion with required-public-method subset checks.
- No formula, endpoint, persistence, permission, rerun, audit, or response change.

## Test Cases
- Competing valid calculations serialize and leave one assessment UUID with internally consistent
  final snapshot/audit/workflow facts.
- Valid versus invalid competing calculation preserves the valid snapshot and success counts.
- Boundary fixtures prove forbidden direct, package-level, private, and aliased imports fail while
  harmless public-interface refactors/additional methods pass.
- Existing lower-of-two, acreage, policy, rollback, failed-rerun, and HTTP characterization suites
  remain green.

## Evidence Required
Red/green concurrency logs identifying the database backend and transaction ordering, boundary
fixture output, and all standard gates.

## Risk Level
High

## Acceptance Criteria
- Financial locking is proven through competing transactions, not only mocked call counts.
- Static boundaries reject the documented bypass shapes without freezing unrelated class shape.
- No public behavior or stored snapshot changes.

## Done Checklist
- [x] Execution plan written
- [x] Failing tests and red evidence saved first
- [x] Transactional and boundary tests implemented
- [x] Full locally runnable gates passed; PostgreSQL rerun delegated after pinned dependency install
- [x] Risk assessment and handoff updated
- [x] State updated
- [ ] Commit delegated to orchestrator only after passing gates
