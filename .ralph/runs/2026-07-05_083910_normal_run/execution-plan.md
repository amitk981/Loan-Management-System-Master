# Execution Plan

Selected slice: 003B-workflow-event-foundation

## Scope
- Build the canonical workflow-event foundation for `workflow_events` from `docs/source/data-model.md` §26.2.
- Reconcile the 002EX tracer drift without creating a duplicate `workflow_events` table.
- Add the internal `record_workflow_event(...)` write interface and repoint tracer recording through it.
- Add the optional but source-backed `GET /api/v1/workflow-events/` read endpoint using the 003A audit-log endpoint pattern and existing `audit.workflow_event.read` permission.
- Do not touch frontend code; no screens are directly involved.

## Migration Strategy
- Add `sfpcl_credit.workflows` as a Django app and define canonical `WorkflowEvent` there with `db_table = "workflow_events"`.
- Keep the physical table created by `tracer.0001_initial`; add workflow migration state with `SeparateDatabaseAndState` so clean/existing databases do not run a second `CREATE TABLE workflow_events`.
- Add a tracer migration that removes only the tracer app's `WorkflowEvent` state without dropping the physical table.
- Remove the tracer model class and update tracer code/tests to import/use the canonical model/service.

## TDD Cycles
1. RED: add workflow-event service/API tests proving canonical service persistence, read permissions/filtering, and tracer regression import path.
2. GREEN: implement canonical model, service module, view, URL, and migrations.
3. RED/GREEN as needed for tracer lifecycle count and response `workflow_event_id` preservation.

## Documentation and Artifacts
- Update `docs/working/API_CONTRACTS.md` with the implemented workflow-event write/read contract.
- Update the epic digest only if new extracted source facts are used beyond the existing digest.
- Save red/green backend output under `.ralph/runs/2026-07-05_083910_normal_run/evidence/terminal-logs/`.
- Save API response examples under `.ralph/runs/2026-07-05_083910_normal_run/evidence/api-responses/`.

## Gates
- Use `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python` for all backend commands.
- Run backend targeted tests, full backend tests, `manage.py check`, `makemigrations --check --dry-run`, `migrate --plan` or `migrate` as appropriate, and coverage.
- Run frontend typecheck/lint/tests/build even though no frontend code is expected to change, because Ralph gates require them.
