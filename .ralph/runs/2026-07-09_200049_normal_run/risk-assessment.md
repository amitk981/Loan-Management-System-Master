# Risk Assessment

Slice: `005D-application-document-checklist`

Risk level: Medium

## Why Medium
- Adds a new persisted backend table and public API endpoints for loan application document metadata.
- Touches permissions, object-level access, audit evidence, and sensitive document metadata.
- Does not implement financial calculations, eligibility, sanction, disbursement, external services,
  real file scanning, or raw file storage changes.

## Controls Applied
- TDD regression added before implementation and saved as RED/GREEN evidence.
- New endpoints reuse the existing standard API envelope and existing
  `applications.services.evaluate_application_object_access(...)` helper.
- Permission order is explicit: global permission first, `404` lookup for known object types, then
  object-scope denial.
- Upload/verify audit rows are metadata-only.
- Raw file bytes, storage keys, checksums, full PAN/Aadhaar/bank values, encrypted tokens, and hashes
  are excluded from responses and audits.
- Duplicate document type/party upload creates a new version row rather than overwriting history.
- One non-destructive migration only.
- Full backend/frontend gates passed.

## Assumptions
- A-039: checklist refresh is read-derived and gated by `applications.loan_application.read` until a
  future completeness/checklist slice defines exact mutation side effects and permission.

## Residual Risk
- Completeness pass/fail logic is intentionally deferred to 005E. Current checklist statuses are
  metadata-derived and do not by themselves advance the application or generate references.
- Application assignment scope is still based on created/received users plus credit-assessment
  Credit Manager domain access from 005C2; future assignment queue slices should replace this with
  explicit assignment facts.

Manual review required: normal Ralph review only.
