# Review Packet: 2026-07-24_041849_normal_run

## Result
Ready for independent validation

## Slice
012B-register-exports

## Delivered

- Persisted idempotent export jobs with `queued/running/completed/failed`, lifecycle timestamps,
  stable failure codes, checksum, retention, and leased worker claim.
- `POST /api/v1/reports/exports/`, owner-bound status, and signed/expiring byte download.
- CSV/XLSX/PDF/JSON serialization from the registered 012A selectors, with canonical filter and
  generator metadata.
- Thin Celery generation/cleanup tasks, deterministic local storage adapter, sanitized request/
  denial/failure/download audits, and one non-destructive migration.
- Explicit format matrix and lifecycle contract in `docs/working/API_CONTRACTS.md`; operational
  assumptions A-170/A-171.

## Traceability

- The source says large or over-five-second exports are asynchronous, status-tracked, expiring,
  permissioned, audited, and retry-idempotent (`api-contracts.md` §§40.7-40.8; `test-plan.md`
  §§22.2/24.1). The code persists an export job, commits a leased `running` claim before generation,
  issues only signed short-lived grants, and deduplicates request/worker races. Verified by
  `test_request_and_replay_return_one_queued_job_for_canonical_identity`,
  `test_expired_export_cleanup_removes_file_and_old_grant_is_denied`, and the exact PostgreSQL
  acceptance.
- The source says report exports must reuse report selectors and carry generator/time/filter
  metadata (`codebase-design.md` §§33.1/33.3; slice 012B). The code exhausts `run_report` pages and
  renders the same rows into four documented formats. Verified by
  `test_supported_format_matrix_produces_parseable_reconciled_files` and 33 unchanged selector/
  catalogue regressions.
- The source says report read does not imply export permission and audit payloads must not contain
  exported values (`product-requirements.md` §11.31; digest shared invariants 3-4). The code requires
  both current selector authority and `reports.export`, keeps restricted audit export disabled, and
  records reference-only audit facts. Verified by
  `test_export_permission_denial_is_audited_without_filter_values` and the download audit
  assertions.

In plain language: the source requires one safe background job for the exact report and filters the
staff member requested; the implementation does that, and the tests prove retries/races do not make
extra jobs or files, all four files contain the selector's row and metadata, and expired or
unauthorised downloads fail closed.

## Validation Evidence

- Focused export API/service/task registration: 8 passed in the final rerun
  (`33-focused-export-worker-registration.txt`).
- Exact PostgreSQL runtime acceptance: 1 passed (`26-postgresql-final.txt`).
- Existing report selector/catalogue reverse consumers: 33 passed
  (`21-report-selector-regressions.txt`).
- Django system check: no issues (`34-django-check-worker-registration.txt`).
- Migration sync: no changes detected (`35-migrations-worker-registration.txt`).
- RED/GREEN, API examples, format/checksum reconciliation, permission/expiry negatives, and hashes:
  `evidence/report-export-evidence.md`.
- No frontend files or screens were changed; frontend gates/visual evidence are not applicable to
  this backend-only slice. The authoritative impacted/full lane remains owned by the orchestrator.

## Review Focus

- Confirm the new migration and report app registration are selected by the independent backend
  lane.
- Confirm the composite request identity and lease semantics under the orchestrator's fresh
  PostgreSQL databases.
- Confirm A-170/A-171 remain acceptable until 012C/012D and production operations governance.

## Recommended Next Action
Run Ralph independent validation and commit only if every selected gate passes.
