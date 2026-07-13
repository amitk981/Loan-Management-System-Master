# Risk Assessment

Risk level: High

- Selected slice: `006F2-credit-manager-appraisal-rejection`; standing owner approval applies and
  no veto exists.
- The slice adds a terminal credit decision, cross-domain rejection-note creation, and coordinated
  audit/workflow writes. Incorrect behavior could reject without authority, duplicate borrower
  communication metadata, leak reason text, or leave appraisal and note states inconsistent.
- Mitigations: independent `credit.appraisal.review`; Credit Manager object scope; maker-checker;
  verified frozen provenance; review-pending state; row locks; strict conditional payload fields;
  one-to-one note uniqueness; public rejection-note module seam; outer atomic transaction.
- Tests cover missing permission, out-of-scope, maker self-review, invalid/blank/unknown fields,
  repeated rejection, frozen-fact preservation, metadata redaction, and forced note/audit/workflow
  rollback. Existing reviewed/returned tests remain green.
- No schema migration, dependency, frontend, real communication, approval/sanction case, financial
  calculation, deployment, protected file, or source document was changed.
- The first full suite caught a static module-boundary violation. It was repaired by inserting the
  public applications rejection-note seam; the boundary test and then all 361 backend tests passed.
- Residual risk: the transactional lock behavior is exercised under SQLite state guards, not a
  separate competing PostgreSQL rejection test. Database uniqueness plus row locking remain the
  production concurrency controls; future architecture review should assess whether a dedicated
  competing-review test is warranted.
