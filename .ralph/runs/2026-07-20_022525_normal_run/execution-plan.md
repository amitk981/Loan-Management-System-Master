# Execution Plan

Selected slice: 010D2-statement-evidence-owner-and-scope-closure

## Outcome

Close AR-010-STATEMENT-001 by making `BankStatementLine.matched_repayment` the single canonical
statement/receipt relationship. Remove caller-asserted UUID truth from direct capture and derive all
receipt, allocation, adjustment, list, and match behavior through the statement-evidence module.

## Public Interface and Module Seam

- Keep the existing repayment and statement HTTP endpoints stable where source-compatible.
- Deepen `loans.modules.bank_statement_matching` as the owning module for line eligibility,
  canonical link lookup/creation, permission/object-scope filtering, and privacy-safe projection.
- Treat collection accounts as governed opaque identifiers: imports accept a retained identifier,
  never return it, and never log raw statement/account/narration/reference content.
- Keep direct receipt capture, financial allocation, and manual-allocation approval as callers of
  that interface; they must not query or write statement ownership independently.

## TDD Tracer Cycles

1. Add the permanent public boundary tests named by the slice and prove RED for orphan UUID capture,
   contradictory two-sided truth, import-only/out-of-scope matching, and nondisclosing reads.
2. Implement the canonical relationship and authority/scope seam minimally; rerun the same focused
   selector to GREEN and retain exact logs.
3. Add subsidiary narration matrix tests (borrower only, application only, account only, both,
   ambiguous, missing), prove RED, then implement exact source-fact matching and prove GREEN.
4. Add migration executor tests for coherent, orphan, and duplicate legacy UUID values; implement
   one reversible/ownership-safe schema/data migration that retains unresolved values as explicit
   reconciliation exceptions without creating statement rows.
5. Add four PostgreSQL acceptance races for concurrent auto/manual ownership and decision evidence;
   run the declared class twice when PostgreSQL is available, otherwise retain collection/local
   feedback and leave authoritative execution to the orchestrator.
6. Run focused 010B–010D2 reverse-consumer tests, backend check, migration sync, and relevant lint or
   static checks. Do not run the complete backend suite or coverage locally.

## Evidence and Review

- Save exact RED/GREEN and matrix/reverse-consumer command outputs under
  `evidence/terminal-logs/`, each with the permanent selector and explicit exit status.
- Save `review-closure-evidence.md`, before/after relationship extracts, permission/scope and privacy
  examples, migration evidence, PostgreSQL evidence or collection limitation, risk assessment,
  review packet, and final summary.
- Verify only allowed backend, contract, assumption (if genuinely required), and current-run evidence
  paths changed; do not edit orchestrator-owned state/status/handoff facts.
