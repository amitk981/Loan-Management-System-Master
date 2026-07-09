# Risk Assessment

Risk level: Medium

- Selected slice: 004D-nominee-validation-and-ui
- Mode: normal_run
- Manual review required: normal Ralph review only; no owner approval was required because the
  slice is Medium risk and within standing AFK approval.

## Risk Drivers
- Adds a new persisted nominee table with protected identity fields and one migration.
- Adds a new authenticated API path with separate read/create permissions.
- Handles PAN/Aadhaar validation and masking, which is privacy-sensitive.
- Touches the Member Profile UI with a create form and validation/error states.

## Controls Applied
- TDD red/green evidence saved for backend API behavior and frontend nominee UI/client behavior.
- PAN/Aadhaar are stored as protected tokens plus keyed hashes; full values are not serialized in
  API responses or audit metadata.
- `GET` requires `members.nominee.read`; `POST` requires `members.nominee.create`.
- Validation returns source-backed error codes for missing/invalid PAN/Aadhaar and minor nominees.
- Create writes only metadata to `AuditLog`; masked list/read writes no workflow event.
- Source uncertainty around legal-majority age is recorded as A-031.

## Residual Risk
- Object-level member access remains limited to the current accessible-member boundary until
  source-backed member ownership/team facts are modeled.
- Protected token storage is a local implementation boundary, not a production KMS/encryption
  adapter. A future security hardening slice should replace it when infrastructure exists.
- Loan-application nominee snapshot behavior remains deferred by slice scope.
