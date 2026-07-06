# Risk Assessment

Risk level: Medium

Selected slice: `003F-communication-template-shell`

## Why Medium
- Adds a new backend app, database table, migration, protected API endpoints, and permission gates.
- Touches communication-template metadata and audit logging, which the source classifies as Medium
  risk owned by Communication / Compliance.
- Does not send communications, expose borrower/loan merge output, modify money logic, or change
  existing document/config/audit/workflow migrations.

## Controls Applied
- TDD red/green evidence saved for the content-template API.
- Standard session-bound bearer auth is enforced before permission checks.
- Narrow permission codes are used: `communications.content_template.read` and
  `communications.content_template.manage`.
- A-022 records the source catalogue gap and the temporary Compliance-owner grant.
- `403` tests assert no content-template or audit writes occur.
- Create/update audit rows include metadata only and exclude rendered borrower/loan-specific output.
- One non-destructive migration creates only `content_templates`.

## Residual Risk
- Source docs do not yet define exact §12 content-template permission codes or a dedicated
  Communication role. The chosen codes and Compliance grant should be revisited when the source
  catalogue is clarified.
- This is a metadata shell only; delivery status, communication records, template rendering, and
  notification UI remain future work.

## Gate Result
All required backend and frontend gates passed. No protected or forbidden paths were edited.
