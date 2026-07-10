# Risk Assessment

## Slice
006B-default-document-purpose-and-terms-eligibility-checks

## Risk Level
Medium

## Why
- The slice changes backend business-rule behavior for eligibility assessment results.
- It affects the gate that later loan-limit/appraisal slices must depend on.
- No schema migration, new dependency, frontend UI change, external service call, payment action,
  or protected-file edit was introduced.

## Controls
- TDD red/green evidence saved for the eligible API path.
- Focused API tests cover eligible, default/document/purpose/terms/minor-nominee blockers,
  pending nominee evidence, rerun one-to-one behavior, permission denial, object-scope denial,
  invalid state, and no-success-evidence behavior.
- Full backend and frontend gates passed.
- API contract and Epic 006 digest were updated.
- Ineligible results do not advance application status/stage.

## Residual Risk
- Nominee selection is still limited by current persistence. 006B only treats
  `Nominee.loan_application_id` as application-specific nominee evidence; missing application
  nominee evidence remains pending manual evidence by design.
- Loan-limit policy ambiguity remains deferred to 006C and later config slices.
