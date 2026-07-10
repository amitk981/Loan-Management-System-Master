# Ralph Handoff

## Last Run
2026-07-10_181310_normal_run

## Current Status
Completed `006E2-appraisal-source-contract-and-snapshot-hardening` under standing High-risk
approval.

- Appraisal creation copies the exact canonical redacted projections from
  `EligibilityAssessmentModule.get(...)` and `LoanLimitCalculator.get_assessment(...)` into
  appraisal-owned JSON, retaining assessment UUIDs only as provenance. GET and draft amount/
  exception validation no longer reread mutable current assessments.
- Added required non-blank `repayment_capacity_notes`. Submit persists trimmed §24.3 remarks on the
  appraisal; audit JSON records only reason existence and owning appraisal ID.
- One additive migration copies legacy projections only when source timestamps and audit chronology
  prove no successful post-appraisal rerun. Ambiguous history remains `legacy_unverified` and is
  blocked from submit/review.
- Added `POST /api/v1/appraisal-notes/{id}/revalidate-prerequisites/`: empty-body, draft-only,
  one-way legacy repair requiring appraisal-update plus risk-management scope and object access.
  It changes only frozen prerequisite IDs/projections/provenance and writes metadata-only atomic
  evidence.
- Static regressions positively require both public prerequisite module imports, reject concrete
  assessment access, and allow harmless extra public workflow methods.

## Validation
Backend check and migration sync passed. Full default suite: 353 tests ran successfully with two explicit
PostgreSQL-only concurrency skips; coverage 95% (floor 85%). Frontend lint/typecheck, 107 tests, and
build passed. Focused migration proof covers safe-copy and ambiguous chronology. Evidence is in
`.ralph/runs/2026-07-10_181310_normal_run/`.

The calculator locking implementation did not change. Preserve the existing independent
PostgreSQL gate whenever future appraisal/calculator imports or projections change:
`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_credit_modules.LoanLimitConcurrencyTests --settings=sfpcl_credit.config.postgres_test_settings -v 2`
from `sfpcl_credit/`; SQLite skips are not concurrency proof.

## Next Run
Run sharpened `006F-credit-manager-review` through `AppraisalWorkflow.review(...)`. It must require
`prerequisite_provenance = verified`, consume only the frozen appraisal projections, preserve
repayment/submission/recommendation/risk/TAT facts, and never revalidate on the reviewer's behalf.
Then run `006F2` before `006G`.
