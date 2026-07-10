# Risk Assessment

Risk level: High

- Selected slice: 006C2-cultivated-acreage-source-hardening
- Mode: normal_run
- Manual review required: no blocking review required before orchestrator validation; high risk is
  covered by standing approval and independent gates.

## Why High

- This slice changes financial eligibility calculation input validation for BR-020.
- Incorrect behavior could overstate the land-based loan limit or mutate a stored financial
  snapshot on a failed recalculation.

## Controls Applied

- No new business precedence/min/max formula was invented. A-049 remains the source ambiguity; the
  interim behavior blocks calculation unless applicable acreage facts agree.
- Validation runs before `LoanLimitAssessment.save()`, `loan_limit.calculated` audit writes, and
  `loan_limit_assessment` workflow events.
- The error contract is stable:
  `400 VALIDATION_ERROR` with
  `error.field_errors.cultivated_acreage = "CULTIVATED_ACREAGE_UNRESOLVED"`.
- Existing immutable snapshot behavior is preserved on failed reruns.
- No database schema change, migration, new dependency, frontend styling, or external service call.

## Residual Risk

- Source documents still do not define the long-term authoritative acreage precedence rule. The
  current behavior is intentionally conservative and may block applications that need manual policy
  resolution until the business confirms the rule.
