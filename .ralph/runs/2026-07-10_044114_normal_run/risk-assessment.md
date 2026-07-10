# Risk Assessment

Selected slice: 005I2-application-detail-api-state-hardening

Risk level: Medium.

Why:
- Staff application detail is a staff-facing API/UI surface with object access and rejection-note
  metadata.
- The change does not add a database migration, dependency, endpoint, financial formula, or
  external integration.
- Frontend changes reuse existing Application Detail cards, badges, tabs, and empty-state text.

Controls applied:
- Backend TDD red/green covered nullable staff detail `rejection_note`, object-scope denial, no
  read audit/workflow side effects, and borrower portal omission.
- Frontend TDD red/green covered API-backed `LO00000035`, rejection-note metadata, and
  nominee/witness unavailable states.
- Full backend tests, migration check, coverage, frontend lint/typecheck/tests/build, and
  `git diff --check` passed.

Residual risk:
- Application Detail still contains downstream appraisal/sanction/security/disbursement prototype
  panels outside the 005I2 corrective scope. This slice removed the specific status/document/owner,
  witness, nominee-sensitive, and rejection-note hardcoding called out by the architecture review.
