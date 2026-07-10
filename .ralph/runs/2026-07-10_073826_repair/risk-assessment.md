# Risk Assessment

Risk level: High

Selected slice: `006C-loan-limit-configuration-and-calculator`

## Why High

- Introduces a financial eligibility calculation used by later appraisal and sanction decisions.
- Adds a durable assessment table and financial snapshot migration.
- Consumes mutable member/share/land/crop facts and versioned Board-approved policy configuration.
- Enforces privileged credit permission and application object scope.

## Controls implemented

- No formula percentage, cap, scale, or loan amount is hard-coded. Exactly one active/effective,
  Board-referenced policy must provide the operative positive values.
- Stored 006B normal eligibility is a hard precondition; pending/ineligible paths cannot calculate.
- All source facts are validated to the application member and the request amount must match the
  stored loan application.
- Decimal arithmetic snapshots both formula branches, lower-of-two result, rule version, actor,
  timestamp, and amount-boundary flags.
- Calculation, audit metadata, and workflow evidence are one atomic transaction. All denied,
  invalid-state, and validation paths are tested to produce no success evidence.
- One-to-one persistence prevents duplicate assessments; reruns update the existing UUID.
- Migration sync, 288 backend tests, 95% coverage, and all frontend gates passed.

## Residual risks

- Client confirmation of 30% vs 10% vs Rs 200/share remains unresolved. Assumption A-047 records
  the explicit configuration interpretation; calculation blocks when no positive operative rule is
  configured.
- 006C's immediate response includes configuration-source metadata selected from the active policy,
  while immutable stored readback is deliberately owned by 006D.
- No override/exception approval is implemented; above-limit requests are only flagged for later
  source-backed approval workflow slices.

## Scope and approval

- Standing owner approval applies; no `[revoked]` entry was encountered.
- No protected file, source document, dependency, frontend production file, external service, or
  deployment was changed.
- Manual review focus: A-047 cap interaction, same-member validation, policy effective-date
  selection, decimal snapshots, and no-side-effect denial paths.
