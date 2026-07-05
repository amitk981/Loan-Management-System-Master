# Risk Assessment

Risk level: Medium

- Selected slice: 003C-document-metadata-and-storage-adapter
- Mode: normal_run
- Manual review required: normal orchestrator review only.

## Risk Drivers
- Adds a new persisted backend table (`document_files`) and one migration.
- Adds a new authenticated upload endpoint that accepts file bytes.
- Touches the permission boundary for document upload through existing `documents.file.upload`.
- Writes audit rows for a compliance-sensitive document action.

## Controls Applied
- TDD red/green evidence saved:
  - `evidence/terminal-logs/backend-red.txt`
  - `evidence/terminal-logs/backend-green-focused.txt`
- File bytes are stored outside the database through `LocalDocumentStorage`; only metadata,
  storage key, and checksum are persisted.
- Upload permission is not broadened: endpoint requires session-bound bearer auth and the seeded
  `documents.file.upload` permission.
- Permission/validation failures are tested to write no `DocumentFile` and no document-upload
  `AuditLog`.
- Successful uploads write exactly one audit row and do not include raw file bytes in audit metadata.
- No frontend screens, loan-document workflows, download URLs, templates, signatures, stamping,
  or notarisation flows were added.

## Residual Risk
- Local filesystem storage is dev/test only. Production S3/DMS adapter, signed downloads, virus
  scanning, retention enforcement, and sensitivity-specific object rules remain future slices.
- A-019 records source-silent defaults for HTTP success status, sensitivity case-normalization,
  and where category/related-entity facts are persisted.
