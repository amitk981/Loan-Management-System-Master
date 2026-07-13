# Risk Assessment

Risk level: High

- Selected slice: 007H3-frozen-case-provenance-and-read-scope-parity-closure
- Mode: normal_run
- Standing approval: active; no veto entry exists.

## Security and integrity assessment

- The change closes a confidentiality split where malformed or live-diverged cases could affect
  detail, decision, and register boundaries differently. Frozen validity and actor scope now run
  before collection/register counts and pagination, preventing row-count disclosure.
- Approval actions still lock application, appraisal, and case in the existing transaction. A
  malformed frozen case returns before any action/audit/workflow/register write; the retained
  public regression compares the complete action ledger.
- The stored coherence flag and reader index remain explicit database-narrowing projections only.
  No signal, model-save side effect, permission widening, schema migration, dependency, or external
  communication was added.

## Regression and operational risk

- Requiring `final_eligible_loan_amount` makes the canonical frozen provenance match the complete
  shape already produced by the credit enrichment interface. Existing migration and approval
  suites pass, including legacy read-scope migration coverage.
- Full validation materializes the already database-narrowed candidate set before counts. This adds
  one bounded approval-case query to scoped collections; the query-count regression proves growth
  remains constant in query count. A future performance slice may batch/deepen validation if
  persisted global scopes become large, but correctness and nondisclosure take priority here.
- No PostgreSQL runtime capability was declared. The 19 concurrency tests skipped under SQLite are
  expected and unchanged; this slice does not modify a concurrency-critical write path.

## Gate outcome

- Backend: check and migration sync green; 679 tests green with 19 expected skips; 93% coverage.
- Frontend: build, typecheck, lint, and 208 tests green.
- Diff: 11 tracked files plus Ralph artifacts, no migration/dependency, within configured limits.
- Manual review required: orchestrator independent validation before commit/merge/push.
