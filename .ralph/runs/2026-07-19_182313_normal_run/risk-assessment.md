# Risk Assessment

Risk level: High

## Boundary and Data Risks

- Public Loan Account authorization is fail-closed on active role, the dedicated
  `finance.loan_account.read` permission, and the role's exact object scope. The initiation
  workspace now uses a separately named candidate interface, so mutation authority cannot widen
  the public list or detail boundary.
- SAP delivery/completion selection now evaluates retained communication/task relations, actors,
  action URLs, audit/workflow evidence, file identity, the stored Annexure-I checksum, and a
  send-time encrypted-storage checksum snapshot before count and pagination. This adds one schema
  migration and makes existing rows without the immutable snapshot ineligible until recreated by
  the owner workflow.
- Loan Account list and detail consume the same selected candidate owner. Projection no longer
  re-resolves selected SAP/creation/transfer facts and silently removes a page identity.
- CFC selection now composes the loan-creation owner and verifies current borrower/source bank
  links in the database selector. Exact JSON/digest behavior is exercised on PostgreSQL.

## Operational Risks

- Migration `sap_workflow/0002_sapcustomerprofilerequest_delivery_storage_checksum_sha256`
  is additive and nullable. Rollback removes only the new snapshot column; no source document or
  existing financial record is rewritten.
- Playwright full-suite selection now seeds the union of staff, portal, and Epic 009 fixture
  families. Targeted Epic 009 selection remains isolated to its fixture family. The backend seed
  remains guarded by both `SFPCL_DEBUG` and `SFPCL_ALLOW_E2E_SEED` and is idempotent.
- Chromium could not launch in the coding sandbox because macOS service access was denied. No
  screenshots were fabricated. The declared two-run/nine-screenshot contract remains for Ralph's
  trusted browser environment.

## Verification and Residual Risk

- Focused final backend run: 83 tests passed, 9 PostgreSQL-only skips on SQLite.
- Final owner-boundary rerun: 35 tests passed.
- Declared PostgreSQL label: 6 tests passed twice on fresh databases with no skips.
- Frontend: 355 tests passed; typecheck, lint, and production build passed.
- Backend system check and migration drift check passed.
- Residual risk is concentrated in the breadth of the existing Epic 009 synthetic browser fixture
  and in the externally owned Chromium acceptance. Independent validation should reject the slice
  if the full backend coverage gate, exact PostgreSQL label, or either browser run disagrees.
