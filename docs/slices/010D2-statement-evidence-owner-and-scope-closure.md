# Slice 010D2: Statement Evidence Owner and Scope Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Replace contradictory/orphanable statement-to-receipt links with one canonical evidence owner and
apply the same permission, object-scope, source-fact, privacy, and migration decision to import,
automatic match, manual match, list, and repayment consumers.

## User Value
Treasury and Accounts can trust that every displayed bank match names one real, in-scope statement
line and receipt, while subsidiary evidence cannot be auto-matched on incomplete narration.

## Depends On
- 010C2

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-STATEMENT-001 | ROOT-010-STATEMENT-EVIDENCE | .ralph/runs/2026-07-20_004623_architecture_review/evidence/review-probes/statement-evidence-boundary.log | AC-STATEMENT-1, AC-STATEMENT-2, AC-STATEMENT-3, AC-STATEMENT-4, AC-STATEMENT-5 |

## Source References
- `docs/source/functional-spec.md` M09-FR-007–009
- `docs/source/user-flows.md` §§27.4, 28.3–28.4
- `docs/source/data-model.md` §19.5 and §§30/34 integrity rules
- `docs/source/auth-permissions.md` §§19.3–19.4, 26.6, 32.1
- `docs/source/security-privacy.md` bank-account masking/encryption and financial audit controls
- `docs/source/api-contracts.md` §§32 and 45
- `docs/slices/010B-direct-repayment-posting.md`
- `docs/slices/010D-bank-statement-matching-unmatched-receipts.md`

## Backend/API Scope
- Establish one database-backed canonical statement-line/repayment relationship. Remove or strictly
  derive the duplicate raw UUID truth, reject new orphan/mismatched links, and migrate retained
  values without inventing counterparts. Unknown legacy UUIDs become explicit reconciliation
  exceptions; migration forwards/backwards behavior must be ownership-safe.
- Direct receipt capture may reference only an existing, eligible, singular statement line through
  the canonical owner. Replay, auto-match, manual match, receipt projection, and concurrency paths
  must consume the same relationship decision.
- Automatic matching requires the match authority and the same loan-object scope as manual match.
  Import-only authority may retain a line but cannot link a receipt outside that boundary. Lists and
  details apply the source role/object scope without leaking inaccessible match identities/counts.
- For `subsidiary_deduction`, require both borrower name and loan application number in retained
  narration as M09-FR-007 states; borrower-only, application-only, account-only, and ambiguous facts
  remain unmatched. Keep the direct-repayment exact-evidence rule separately explicit.
- Replace raw collection-bank-account input/output with a governed opaque identifier or central
  encrypted/masked value seam. Do not echo a full bank account or treat an unverified label as owned.
- Link exception decisions to immutable audit evidence and preserve raw narration/reference/file
  nondisclosure in ordinary responses, errors, and logs.

## Scope Boundaries / Non-Goals
- No subsidiary receipt creation/allocation, split matching, fuzzy/ML matching, bank provider feed,
  OCR, refund, reversal, SAP integration, or frontend work.
- Do not fabricate a BankStatementLine for an unknown legacy UUID and do not weaken one-counterpart
  uniqueness or the 010C2 approval boundary.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_statement_evidence_boundary_postgresql.StatementEvidenceBoundaryPostgreSQLAcceptanceTests`
- Expected tests: 4

## Acceptance and Reverse-Consumer Tests
- Public RED/GREEN regressions retain the review's orphan-UUID and import-only/out-of-scope probes.
- Exact and conflicting two-sided links, migration of coherent/orphan/duplicate legacy values, and
  concurrent auto/manual matches retain one canonical counterpart and one audit decision.
- Subsidiary borrower-only, application-only, account-only, both-present, ambiguous, and missing
  matrices prove M09-FR-007 without changing direct receipt behavior.
- 010B capture/replay, 010C allocation, 010D queue/list/manual match, and 010C2 exception admission
  consume the same owner and remain permission-, privacy-, and query-bounded.

## Evidence Required
- RED/GREEN public API and migration evidence, before/after relationship extracts, permission/scope
  matrix, privacy examples, twice-run PostgreSQL race evidence, and 010B–010D reverse consumers.

## Risk Level
High

## Acceptance Criteria
- [AC-STATEMENT-1] Every receipt/line link resolves through one canonical referentially coherent
  owner; orphaned or contradictory UUID truth cannot be created or treated as matched.
- [AC-STATEMENT-2] Import, automatic match, manual match, list, and receipt consumers enforce the
  same effective permission and loan-object-scope decision before identities, counts, or writes.
- [AC-STATEMENT-3] Subsidiary auto-match requires both borrower and application identifiers, while
  incomplete or ambiguous narration remains in the reconciliation queue.
- [AC-STATEMENT-4] Legacy link migration is deterministic and reversible/ownership-safe, and four
  twice-run PostgreSQL races retain one relationship/audit winner.
- [AC-STATEMENT-5] Collection-account and statement data remain governed, encrypted/masked where
  sensitive, omitted from ordinary responses/logs, and all focused/reverse/full gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] TDD RED/GREEN evidence saved
- [ ] Code, contract, and migration implemented
- [ ] Permission, object-scope, privacy, and source-fact matrices verified
- [ ] PostgreSQL acceptance passed twice
- [ ] Reverse-consumer and full gates passed
- [ ] Risk and review evidence completed
- [ ] Commit delegated to the orchestrator after gates
