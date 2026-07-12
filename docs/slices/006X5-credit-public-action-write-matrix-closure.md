# Slice 006X5: Credit Public Action/Write Matrix Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Deliver the exhaustive public-interface matrix promised by 006X4 instead of treating projection-only
permission assertions and a trace table of older tests as paired action/write proof.

## Depends On
- 006X4

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Source / Review References
- `docs/source/api-contracts.md` §22-§24 and §44
- `docs/source/auth-permissions.md` §25.3, §26.2, and §34.4
- `docs/source/codebase-design.md` §26.1-§26.3 and §42.2
- `docs/source/functional-spec.md` M04-FR-004 through M04-FR-011
- `docs/slices/006X4-credit-action-parity-regression-matrix.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_125256_architecture_review`

## Scope

- Replace the five-row projection-only test with one enumerated public-module matrix covering
  eligibility run, loan-limit calculate, appraisal create/update/revalidate/submit-review,
  reviewed/returned/rejected review, and sanction submission.
- Every row must construct the projected six-field action and invoke its exact public write with
  the same actor/resource. Assert enabled/write success and disabled/write denial with the same
  stable reason/category.
- Cover state, role, exact permission, object scope, maker-checker, frozen prerequisite provenance,
  immutable review consistency, rejection payload, stale state, and zero success state/audit/
  workflow/history/rejection-note/case evidence on denial.
- Keep test setup behind public module fixtures. A documentation trace to unrelated tests is not a
  substitute for matrix execution.
- Run the authoritative PostgreSQL five-race command twice and add a projection/write race proving
  a stale enabled action cannot commit after a competing state change.

## Test Cases

- The enumerated matrix fails if any named action lacks both a success and denial write.
- All six projected fields and exact denial parity are asserted for each authority/state variant.
- Rejection and sanction rows assert exact history/note/case cardinality; denied rows assert zero.
- The PostgreSQL race executes, does not skip, and has one valid winner with no loser evidence.

## Evidence Required

Failing-first matrix output, green enumerated matrix, action/write result table generated from the
matrix cases, two PostgreSQL race logs, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every action named by 006X4 is paired with its real public write across the complete matrix.
- Projection-only checks and references to disparate historical tests no longer stand in for the
  required acceptance proof.

