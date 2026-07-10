# Slice 006D2A: Credit Eligibility Module and Configuration Seam

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
First half of the superseded 006D2 refactor: establish the source-named `sfpcl_credit.credit`
package, move eligibility-assessment behavior out of `applications.services` behind
`credit.modules.eligibility_assessment`, and put effective loan-policy lookup/validation behind
`configurations.modules.configuration_resolver`. Loan-limit extraction is explicitly OUT of scope
here — it is slice 006D2B.

## User Value
Eligibility rules and configuration resolution get one explicit, testable interface each, so later
appraisal/sanction work cannot duplicate or bypass them.

## Depends On
- 006C2

## Reference Implementation
A fully-gated implementation of the combined 006D2 scope (304 tests green, 95% coverage; failed
only the diff-size limit) is preserved at
`.ralph/runs/2026-07-10_135716_repair/full-implementation.patch`. Reuse its
`credit/modules/eligibility_assessment.py`, `credit/modules/common.py`, `credit/apps.py`,
`configurations/modules/configuration_resolver.py`, and the matching view/service/test hunks.
Take ONLY the eligibility and configuration-resolver portions; leave every loan-limit hunk for
006D2B.

## Source / Review References
- `docs/source/codebase-design.md` §§6.2-6.3, §7.3, §§12.1-12.3, §22, §26, and §42.2
- `docs/source/data-model.md` §14.1-§14.4 and §34
- `docs/source/api-contracts.md` §3, §22-§24
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_092630_architecture_review`
- `docs/adr/ADR-0002-staged-credit-assessment-model-ownership.md` (already recorded — follow it)

## Architecture Scope
- Establish the `sfpcl_credit.credit` Django/domain package with the public module seam
  `credit.modules.eligibility_assessment` (plus shared `credit.modules.common` result/error types).
- Move eligibility rule evaluation, validation, transaction/locking, persistence coordination,
  audit/workflow coordination, and public result types behind that interface. Application views
  authenticate/parse, call the interface, and translate the returned result/error only.
- Move effective loan-policy lookup/validation behind
  `configurations.modules.configuration_resolver`; eligibility code must not query/interpret
  active configuration directly. The resolver seam is built here because eligibility needs it
  first; 006D2B's calculator will reuse it unchanged.
- Loan-limit calculation, snapshot projection, and the appraisal seam stay in
  `applications.services` untouched in this slice; do NOT partially migrate them.
- Add an import-boundary regression proving application views reach eligibility behavior only via
  the public module entrypoint (no private-helper imports through compatibility aliases).

## Diff Budget (hard requirement)
The parent slice failed twice on `limits.max_lines_changed` (2,000). This half must land well
under it: target <= 1,400 changed lines. If the diff approaches the limit, trim scope (e.g. defer
test-file splitting) rather than exceeding it — a green run over the limit is a failed run.

## Behavior Preservation
- Preserve all existing 006A-006D eligibility contracts, permissions, object access, error codes,
  explicit rerun semantics, immutable read behavior, and metadata-only audit/workflow output.
- No new endpoint, rule, field, styling, or dependency. No model, table, or migration changes.

## Test Cases
- Characterization tests green before extraction; the same HTTP payload/status/evidence assertions
  remain green after it.
- Direct module tests cover eligible/ineligible/pending paths and transaction rollback behavior.
- Configuration-resolver tests prove it is the only effective loan-policy query seam for the
  eligibility path.
- Import-boundary regression test for eligibility private helpers.

## Evidence Required
Characterization and refactor green logs, module/API test logs, and all standard quality gates.

## Risk Level
High

## Acceptance Criteria
- Eligibility callers depend on the explicit `credit.modules.eligibility_assessment` interface.
- Configuration selection for eligibility flows through `configuration_resolver`.
- No behavior regression; no migration; changed lines within the diff budget.
- Loan-limit behavior is untouched and still fully green.

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
