# Risk Assessment

Risk level: Medium

- Selected slice: 003H-dashboard-task-ui-wiring
- Mode: normal_run
- Manual review required: no beyond normal Ralph validation.

## Risk Notes
- Frontend-only production change plus a new API client. No backend behavior, database schema, or
  API contract shape changed.
- Permission risk is controlled by relying on the backend `/api/v1/dashboard/` success/error result;
  the UI does not infer dashboard access from frontend permissions.
- Stale-data risk is controlled by rendering `401`, `403`, server, and network failures as existing
  error alerts with no mock dashboard cards/tasks.
- UI-routing risk is recorded in A-024: backend source-style links are translated to existing
  prototype workspaces where possible; unknown future links are left inactive.

## Validation
- Frontend dashboard red/green evidence saved.
- Full frontend tests/typecheck/lint/build passed.
- Backend check/tests/migration sync/coverage passed unchanged.
- Visual evidence saved under `evidence/screenshots/`; browser/server capture was sandbox-blocked,
  so static PNG evidence was generated from the same dashboard states after recording the blocker.
