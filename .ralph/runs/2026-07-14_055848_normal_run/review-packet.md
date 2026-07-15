# Review Packet: 2026-07-14_055848_normal_run

## Outcome

Slice 008A is implemented and locally green. The documents module exposes the exact §26.3
collection/detail routes, stores immutable version rows, and treats PATCH as one linked successor.
The module owns validation, overlap checks, replay, locking, serialization, and evidence; callers
only cross the small HTTP/catalogue interface.

## Standards review

- The implementation follows the existing Django function-view, standard-envelope, explicit
  permission, `transaction.atomic`, `AuditLog`, and shared `VersionHistory` patterns.
- One additive migration matches the model (`makemigrations --check --dry-run`: no changes).
- Indexed model facts and constraints align with data-model §16.2/§30/§34. No dependency, frontend
  style, mock-data surface, generated artifact, storage adapter, or protected file changed.
- `git diff --check`, Python compilation, queue lint, runtime-capability validation, and state JSON
  validation pass. The diff remains below 30 files/2,000 lines and has one migration.

## Spec review and traceability

- API §26.3 says GET/POST/PATCH with code/name/type/borrower/version/file/merge/status/effective
  facts; the routes and serializer expose exactly those facts plus ids/name metadata and creation
  time. Verified by `test_manager_creates_and_supersedes_template_while_reader_lists_history` and
  `test_permissions_filters_and_bounded_pagination_are_explicit`.
- Data-model §16.2 and functional M18-FR-005 require retained template versions; PATCH never changes
  its target and one successor is linked/audited. Verified by
  `test_successor_replay_retains_predecessor_and_attributable_history`.
- Auth §12.7 separates template read/manage from file download; the code enforces all three
  independently and returns no storage/action/download descriptor. Verified by the permission and
  authorised/inaccessible-file tests.
- The digest/SOP catalogue requires A-I, Board/Sanction Committee metadata, and L while keeping the
  conflicting J/K/L labels out of routing. The catalogue accepts descriptive codes/types without any
  Annexure switch, generator, or selector. A-095 retains the approved-versus-active conflict.
- The slice requires exact replay, rollback evidence, and one-winner concurrency. SQLite tests prove
  zero-write replay/denial; the PostgreSQL-only five-race test proves the locked successor contract
  when run by independent validation.

## Validation

- Backend: 700 tests passed, 20 expected SQLite/PostgreSQL skips; 93% coverage (85% required).
- Scoped API: 7 tests passed with the single PostgreSQL race skipped locally.
- Frontend: build, typecheck, lint, and 269 tests passed; no frontend files changed.
- Django: system check and migration-drift check passed.
- Evidence: RED/GREEN logs, final scoped output, coverage report, frontend gates, and representative
  API responses are under `evidence/`.

Independent validation still owns the declared PostgreSQL five-race acceptance and final commit,
merge, and push.
