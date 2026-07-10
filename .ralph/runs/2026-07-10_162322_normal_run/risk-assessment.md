# Risk Assessment

Risk level: High

- Selected slice: `006D2B-credit-loan-limit-calculator-and-appraisal-seam`
- Mode: `normal_run`
- Standing approval applies; no matching `[revoked]` entry exists.
- No dependency, endpoint, database field/table, migration, frontend, or business-rule change.

## Main risks and controls

- Financial regression: existing HTTP characterization and new direct module tests cover both
  lower-of-two branches, above/equal/below boundaries, exact warning flags, and policy ambiguity.
- Stale mixed-source snapshot: application, eligibility/current assessment, shareholding, selected
  land, crop plan, applicable profile, and effective policy are locked in one atomic transaction.
- Partial rerun: audit failure rolls back snapshot/workflow; cultivated-evidence failure preserves
  the prior UUID, public snapshot, audit count, and workflow count.
- Projection drift/data leakage: one frozen redacted `LoanLimitSnapshot` generates public and audit
  values; request metadata and warnings are added only at their boundaries.
- Architecture regression: AST tests reject private/aliased view imports, application-service
  credit helpers, reverse configuration dependencies, direct policy queries, and appraisal bypass.
- Error-contract regression: payload parsing is deferred inside the calculator until permission,
  not-found, and object-access checks complete, preserving prior response precedence.

## Change size and safety

- Approximately 1,479 changed lines including Ralph state/progress and the two new modules, below
  the slice target of 1,500 and the hard ceiling of 2,000.
- Protected files and `docs/source/` are unchanged. No migration or dependency was added.
- Final gates: 319 backend tests at 95% coverage; frontend lint/typecheck, 107 tests, and build.
