# Slice 006X9: Credit Object-Scope Isolated Execution Matrix

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Replace 006X8's process-global, order-dependent result ledger with eight independently executable
object-scope rows that each prove projection, public write, denial category, and unchanged evidence.

## Depends On
- 006X8

## Runtime Capabilities

none

## Source / Review References
- `docs/source/codebase-design.md` §26.1-§26.3 and §42.2
- `docs/source/api-contracts.md` §22-§24 and §44
- `docs/slices/006X8-credit-executed-object-scope-regression-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_234227_architecture_review`

## Scope

- Remove `EXECUTED_OBJECT_SCOPE_RESULTS`, class-name ordering, and any aggregate that depends on
  other test methods having run in the same process.
- Build one explicit parameter table for the eight production action codes. Each row must arrange
  the persisted resource, project the exact disabled six-field action, invoke the matching public
  write, assert `OBJECT_ACCESS_DENIED`, and compare the complete before/after evidence snapshot.
- Every row must pass when selected alone, under reversed/random order, and in a separate test
  worker. A row may not mark a phase complete by mutating bookkeeping flags directly.
- Preserve existing HTTP `403` non-disclosure, state/provenance/maker-checker, and PostgreSQL race
  regressions. Do not change production credit behavior.

## Test Cases

- Run each of the eight rows by its individual test identifier and assert it is self-contained.
- Delete/omit the real projection, public write, category assertion, or evidence comparison in a
  deliberate incomplete-row fixture and obtain a focused failure without shared mutable state.
- Execute the table in normal and reversed order and obtain the exact same eight substantive rows.

## Evidence Required

Failing isolated-ledger run, green individual-row and reversed-order runs, exact eight-row table,
focused HTTP denials, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Credit object-scope completeness is derived from eight self-contained production interface tests;
  test order, sharding, selection, retries, and module-global state cannot change the result.
- Production credit behavior and all existing authority/race invariants remain unchanged.
