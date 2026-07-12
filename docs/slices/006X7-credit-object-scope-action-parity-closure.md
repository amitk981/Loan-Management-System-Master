# Slice 006X7: Credit Object-Scope Action Parity Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Replace 006X6's labelled-but-unexecuted object-scope rows with real disabled projections and matching
public-write denials on the same persisted credit resources.

## Depends On
- 006X6

## Runtime Capabilities

none

## Source / Review References
- `docs/source/api-contracts.md` §22-§24 and §44
- `docs/source/auth-permissions.md` §19, §24.3, §25.3, §26.2, and §34.4
- `docs/source/codebase-design.md` §26.1-§26.3 and §42.2
- `docs/slices/006X6-credit-authority-state-parity-matrix-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_203645_architecture_review`

## Scope

- Replace `EXECUTED_CASES` declarations that can claim coverage independently of an assertion with
  executable case records/functions. The completeness check must derive action/variant coverage only
  from cases that actually run a projection and matching public write.
- For eligibility run, loan-limit calculate, appraisal create/update/revalidate/submit-review/review,
  and sanction submit, evaluate a real six-field action for an actor outside the persisted
  application's object scope, then invoke the production public write with that same actor/resource.
- Assert exact disabled reason and stable error-category parity plus zero changes to application,
  assessment, appraisal, risk, review-history, rejection-note, approval-case, audit, and workflow
  evidence. An enabled projection captured before ownership is changed is not object-scope proof.
- Preserve HTTP non-disclosure: object-denied detail endpoints may continue to return `403` rather
  than a resource body. The shared public authority evaluation used before serialization/write must
  still be directly testable without leaking resource facts to HTTP callers.
- Keep existing role, permission, maker-checker, provenance, immutable-review, rejection-payload,
  stale-state, and PostgreSQL race assertions green; do not change business rules to enable a case.

## Test Cases

- Deleting any one object-scope case makes the derived completeness assertion fail.
- Every object-scope case asserts the exact six action fields, disabled reason/category, matching
  public exception, and unchanged full evidence snapshot.
- Endpoint regressions confirm object-denied reads/writes remain standard `403` envelopes and expose
  no application or credit resource body.

## Evidence Required

Failing-first false-completeness output, green generated matrix, exact object-denial/evidence table,
dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- No static catalogue can advertise an object-scope variant that the suite did not execute.
- Credit action projection and write authority agree for every object-scoped public action without
  weakening resource non-disclosure.
