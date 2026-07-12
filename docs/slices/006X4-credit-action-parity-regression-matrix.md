# Slice 006X4: Credit Action Parity Regression Matrix

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Close the unimplemented backend half of 006X2's acceptance contract: prove through public module
interfaces that every projected credit action and its authoritative write share the same locked
state, role, permission, object, maker-checker, provenance, history, and concurrent-change result.

## Depends On
- 006X3

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Source / Review References
- `docs/source/api-contracts.md` §22-§24 and §44
- `docs/source/auth-permissions.md` §25.3, §26.2, and §34.4
- `docs/source/codebase-design.md` §12.3, §26.1-§26.3, and §42.2
- `docs/source/functional-spec.md` M04-FR-004 through M04-FR-011
- `docs/slices/006X2-credit-action-predicate-and-container-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_092009_architecture_review`

## Scope

- Add a table-driven public-interface matrix for eligibility run, loan-limit calculate, appraisal
  create/update/revalidate/submit-review, reviewed/returned/rejected review decisions, and sanction
  submission. Do not test private helpers as the primary evidence.
- For every action, pair the projected six-field action with the same actor/resource write and
  assert enabled succeeds; disabled returns the same stable reason/category and produces no success
  state, audit, workflow, rejection-note, review-history, or approval-case evidence.
- Cover formal reference/completeness/stage, frozen eligibility and limit facts, appraisal
  provenance, immutable review consistency, exact role/permission, object scope, maker-checker,
  rejection fields, stale state, and concurrent mutation. Preserve ADR-0005 ownership.
- Run the existing authoritative PostgreSQL races and add a projection/write race only where the
  matrix exposes an untested lock boundary. Fix production predicates only when a failing public-
  interface test proves divergence; do not change business rules or frontend presentation.

## Test Cases

- One enumerated matrix proves every named action has both enabled/write-success and disabled/
  write-denial cases with exact six-field projection assertions.
- Permission, role, object-scope, maker-checker, provenance, frozen-history, and rejection variants
  assert zero success evidence on denial.
- PostgreSQL acceptance proves a concurrent state change cannot leave a stale enabled projection
  capable of committing an invalid write.
- Existing mounted-container, real-browser, dependency-direction, and full quality gates remain green.

## Evidence Required

Failing-first matrix log, green public-interface matrix, PostgreSQL five-race log, action/write
trace table, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every 006X2-named backend action is paired with its public write across the complete authority and
  state matrix; a single eligibility denial test is not sufficient evidence.
- No action/write divergence or denial-side success evidence remains.
