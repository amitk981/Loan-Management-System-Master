# Grievance API Contract Evidence

The focused Django API tests exercise the real request/response envelope and persistence layer. Dynamic
UUIDs and timestamps are asserted by shape or by persisted identity; this record does not invent runtime
values.

## Create and exact replay

`POST /api/v1/grievances/` with `Idempotency-Key` returns one grievance projection containing a generated
`GRV-<year>-<12 hex>` reference, member and optional source identifiers, owner, retained received/due
dates, server-derived `tat_days`/`is_overdue`, governed supporting-document identifiers, `open` status,
initial history, and available actions. An exact replay returns the same `grievance_id`; a changed replay
returns `409 COMPLIANCE_CONFLICT`.

Verified by
`GrievanceWorkflowApiTests.test_authorised_create_generates_one_scoped_reference_and_initial_evidence`
and `test_create_failures_reject_changed_replay_foreign_sources_and_audit_scope_denial`.

## Scoped list/detail/update

`GET /api/v1/grievances/` returns the repository list envelope plus `page`, `page_size`, `total_count`,
`total_pages`, `has_next`, and `has_previous`. Supported filters are status, member, category, owner,
overdue, page, and page size. `GET`/`PATCH /api/v1/grievances/{id}/` applies member scope before returning
or changing a record. Assignment and investigation append history; invalid backward and post-close
transitions fail.

The borrower primitive derives member identity from an active portal account and its safe projection omits
internal notes, owner, history, and document identifiers.

Verified by `test_staff_reads_are_member_scoped_and_borrower_projection_is_safe`,
`test_active_portal_primitive_creates_only_for_its_own_member`, and
`test_cs_assignment_and_owner_investigation_are_monotonic_and_historic`.

## Resolution, notice truth, escalation, and downloads

`POST /api/v1/grievances/{id}/resolve/` requires `Idempotency-Key` and a nonblank
`resolution_summary`. It retains optional governed resolution evidence, closes once, appends history, and
returns queued delivery state without claiming `borrower_informed` until the related communication has a
real sent timestamp. Exact replay retains the same notice identity.

The 011K job entry point escalates overdue and recovery-conduct records once, records fair-practice source
links, and never resolves them. Governed document download requires grievance scope and writes a grievance
download audit.

Verified by `test_resolution_requires_summary_is_retry_safe_and_queues_honest_notice`,
`test_scheduler_escalates_overdue_and_recovery_cases_once_without_resolving`,
`test_011k_compliance_job_invokes_grievance_escalation_owner`, and
`test_governed_grievance_document_download_is_scoped_and_audited`.

## Gate records

- `16-final-grievance-and-catalogue-green.log`: 27 tests passed.
- `17-final-reverse-consumers-green.log`: 57 tests passed; 12 PostgreSQL-only cases skipped on SQLite.
- `18-django-check-green.log`: Django system check passed.
- `19-migration-drift-green.log`: no model/migration drift.
- `20-postgresql-contract-local.log`: declared class discovered exactly two tests; both correctly skipped
  on SQLite. Ralph's trusted PostgreSQL lane owns their authoritative execution.
- `21-review-boundaries-red.log` / `21-review-boundaries-green.log`: borrower authentication,
  provenance, and inconsistent notice-truth review findings proved red then green.
- `22-final-review-fixes-green.log`: final grievance workflow pack, 11 tests passed.
- `23-final-acceptance-green.log`: expanded final acceptance pack, 12 tests passed.
- `24-final-django-check.log` / `25-final-migration-drift.log`: final system and migration checks clean.
