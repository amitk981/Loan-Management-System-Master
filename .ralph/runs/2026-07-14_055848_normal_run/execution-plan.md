# Execution Plan

Selected slice: `008A-document-template-model-and-versioning`

## Scope and seams

- Add the immutable, versioned document-template catalogue in the existing Django `documents`
  module, reusing the established document metadata foreign key, permission catalogue, standard
  response envelope, bounded pagination, audit log, request-id, and idempotency conventions.
- Expose only `GET/POST /api/v1/document-templates/` and
  `PATCH /api/v1/document-templates/{document_template_id}/`. PATCH creates a successor and never
  edits the addressed row. No generation, download descriptor/action, lifecycle action route, or
  Annexure J/K/L routing rule belongs to this slice.
- Keep validation and concurrency control behind a small catalogue mutation interface so API
  callers do not duplicate date-range, merge-field, history, audit, or locking rules.

## TDD sequence

1. Inspect the existing documents/configuration/audit/idempotency modules and migrations, then add
   one public-API test for create/list/successor behaviour. Run it and save the expected RED log.
2. Add the model/migration, permissions, serializers/views/routes, and catalogue mutation module
   minimally to make the tracer test GREEN. Save the GREEN log.
3. Add one public-interface test at a time for validation and zero-write failures, filters and
   bounded pagination, reader/manager/unauthorised access, inaccessible file metadata, immutable
   history/audit payloads, exact idempotent replay, and metadata-only responses; make each pass.
4. Add the declared PostgreSQL one-winner five-race acceptance test using the repository's existing
   skip/acceptance convention and enforce successor creation atomically.

## Documentation and evidence

- Update `docs/working/API_CONTRACTS.md` with request/response/filter/error and permission details.
- Record the unresolved approval-state wording and Annexure conflict only where needed; do not
  invent a business mapping.
- Save scoped red/green logs, API response examples, model/migration checks, and final full quality
  gate output beneath this run's `evidence/` directory.
- Review the implementation against the slice/source traceability, write `changed-files.txt`,
  `risk-assessment.md`, `review-packet.md`, and `final-summary.md`, then update progress, handoff,
  state, and only the selected slice status.
- Before finishing, sharpen the next one or two Not Started Epic 008 slices from source material
  already opened and update the Epic 008 digest if new distilled requirements were needed.
