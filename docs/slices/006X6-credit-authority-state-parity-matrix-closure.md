# Slice 006X6: Credit Authority and State Parity Matrix Closure

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Turn 006X5's permission-only samples into the exhaustive executable action/write matrix required by
the credit public-interface contract.

## Depends On
- 006X5

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Source / Review References
- `docs/source/api-contracts.md` §22-§24 and §44
- `docs/source/auth-permissions.md` §25.3, §26.2, and §34.4
- `docs/source/codebase-design.md` §26.1-§26.3 and §42.2
- `docs/source/functional-spec.md` M04-FR-004 through M04-FR-011
- `docs/slices/006X5-credit-public-action-write-matrix-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_141135_architecture_review`

## Scope

- Replace the static `ACTION_MATRIX` inventory assertion with parameterised cases that each project
  a real six-field action and invoke the exact public write on the same persisted resource.
- For eligibility, loan limit, appraisal create/update/revalidate/submit-review, each review outcome,
  and sanction submission, cover enabled success plus denials for applicable state, role, exact
  permission, application object scope, maker-checker, frozen prerequisite provenance, immutable
  review consistency, rejection payload, and stale version/state facts.
- Assert exact projection/write reason and error-category parity. Actor-permission overrides may
  prepare a case but may not stand in for real role/object/maker-checker actors.
- Record per-row state and audit/workflow/history/rejection-note/approval-case cardinality; every
  denied case must preserve all success evidence and the resource snapshot.
- Keep the PostgreSQL stale-enabled sanction race and add any missing projection/write race exposed
  by the completed matrix. Do not change business rules merely to make a projected action pass.

## Test Cases

- A completeness assertion fails when any required action lacks every applicable authority/state
  variant, an enabled write, or a disabled write.
- Object-scope, maker-checker, provenance/history, malformed rejection, and stale-state cases invoke
  production public modules and assert stable reasons/categories plus zero evidence.
- Review decision variants execute the real `credit.appraisal.review` action while retaining
  decision-specific payload and history/note assertions; synthetic suffixed action codes are not
  accepted as inventory proof.
- The authoritative PostgreSQL acceptance command runs twice without skips and preserves one valid
  winner with no loser evidence.

## Evidence Required

Failing-first matrix output, green generated action/write table, exact denial/evidence cardinalities,
two PostgreSQL logs, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- The matrix itself, rather than prose or references to older tests, executes every required
  authority/state pair through the same public interfaces used by production callers.
- M04-FR-004 through M04-FR-011 have observable success/blocked-path regression proof without
  inventing new workflow rules.
