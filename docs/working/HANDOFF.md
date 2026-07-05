# Ralph Handoff

## Last Run
2026-07-05_085852_normal_run

## Current Status
Slice `003C-document-metadata-and-storage-adapter` completed successfully.

## What Completed
Generic document-file metadata and local storage now live in `sfpcl_credit.documents`:
- `sfpcl_credit/documents/models.py::DocumentFile` owns the new `document_files` table from
  `docs/source/data-model.md` §16.1. Migration `documents.0001_initial` is the only schema
  migration added in 003C.
- `LocalDocumentStorage` writes bytes outside the database under `DOCUMENT_STORAGE_ROOT`
  (`SFPCL_DOCUMENT_STORAGE_ROOT` override, default `sfpcl_credit/local-document-storage`) and
  returns `storage_provider = "local"`, `storage_key`, byte size, and SHA-256 checksum.
- `POST /api/v1/document-files/` accepts multipart `file`, `document_category`,
  `sensitivity_level`, and optional related entity fields. It requires session-bound bearer auth
  and `documents.file.upload`.
- Successful uploads persist metadata/checksum, return the §26.1 response fields, and write one
  `AuditLog` row with action `documents.file.uploaded`, `entity_type = "document_file"`, and no raw
  file bytes in audit metadata.
- Missing required fields, invalid sensitivity, and invalid `related_entity_id` return standard
  `400 VALIDATION_ERROR`; unauthenticated and no-permission actors get standard `401`/`403` before
  file/metadata/audit writes.

Working docs updated:
- `docs/working/API_CONTRACTS.md` has the document upload contract.
- `docs/working/ASSUMPTIONS.md` A-019 records status/category/case-normalization decisions.
- `docs/working/digests/epic-003-audit-documents-config.md` records 003C completion context plus
  distilled configuration extracts for 003E.
- `docs/slices/003D-secure-document-download-with-audit.md` and
  `docs/slices/003E-versioned-configuration-shell.md` were sharpened.

## Evidence
See `.ralph/runs/2026-07-05_085852_normal_run/`:
- `evidence/terminal-logs/backend-red.txt`: new document upload tests fail before the documents app exists.
- `evidence/terminal-logs/backend-green-focused.txt`: document upload tests pass after implementation.
- `evidence/terminal-logs/backend-tests.txt`: full backend suite passes.
- `evidence/terminal-logs/backend-coverage.txt`: backend coverage passes at 96%.
- `evidence/api-responses/document-files-api-response.txt`: real 200, 400, and 401 examples.

Gates passed:
- Backend `manage.py check`
- Backend tests: 134/134
- Backend `makemigrations --check --dry-run`: no changes detected
- Backend coverage: 96% (floor 85)
- Frontend `npm run typecheck`, `npm run lint`, `npm test` 26/26, `npm run build`

## Current Blocker
None.

## Next Recommended Action
Architecture review is due by cadence (`slices_completed_since_architecture_review = 4`). After
review, run `003D-secure-document-download-with-audit`; it should reuse 003C `DocumentFile` and
the local storage boundary, require `documents.file.download`, and avoid loan-document/checklist UI.
