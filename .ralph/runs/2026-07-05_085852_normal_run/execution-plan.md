# Execution Plan

Selected slice: 003C-document-metadata-and-storage-adapter

## Scope
- Implement only the generic document-file metadata foundation and local filesystem storage adapter.
- Add `POST /api/v1/document-files/` for authenticated multipart upload.
- Exclude loan-document/checklist/download/template/signature/stamp/notarisation workflows.

## Source Trace
- `docs/source/data-model.md` §16.1 defines `document_files` metadata fields.
- `docs/source/api-contracts.md` §26.1 defines multipart upload fields and response data.
- `docs/source/technical-architecture.md` §15-16 requires metadata in the database and file bytes outside the database.
- `docs/source/auth-permissions.md` maps `POST /document-files/` to `documents.file.upload`.
- `technical-architecture.md` §17.4 requires document upload audit events.

## Implementation Plan
1. Add backend tests first for upload success, storage/checksum metadata, validation failures, permission failures, unauthenticated access, and audit creation.
2. Run the focused backend tests and save RED output in `evidence/terminal-logs/backend-red.txt`.
3. Add a `sfpcl_credit.documents` app with `DocumentFile`, one non-destructive migration, storage adapter/service, and thin upload view.
4. Wire the app into settings and `/api/v1/document-files/`.
5. Update `docs/working/API_CONTRACTS.md` and record any assumptions if source docs are silent.
6. Run focused tests and full gates; save GREEN/gate evidence.
7. Save API response examples, changed files, risk assessment, review packet, final summary, and update handoff/state/slice status.

## Permission Check
- Allowed paths to edit: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/runs/**`, `.ralph/state.json`.
- Protected/read-only paths will not be modified: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, protected decision/risk/design docs.
