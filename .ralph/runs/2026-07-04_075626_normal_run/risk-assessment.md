# Risk Assessment

Risk level: Medium

- Selected slice: 002F-role-aware-sidebar-header-navigation
- Mode: normal_run
- Manual review required: normal review packet only.

## Change Summary
- Extracted the staff page permission table and route guard decision into `sfpcl-lms/src/services/navigationPermissions.ts`.
- Exported the existing staff sidebar nav table for parity tests.
- Exported the canonical-to-prototype permission map for direct tracer isolation tests.
- Extended frontend unit tests and the existing Playwright negative spec for zero-permission, tracer-only, and invalid stored-session shell behavior.

## Risk Factors
- Frontend auth shell controls which staff pages are visible and reachable.
- A guard/table mismatch could expose a protected workspace affordance.

## Mitigations
- New unit tests assert every non-dashboard staff nav item has a matching page permission.
- New unit tests assert blocked page navigation returns to Dashboard with the blocked target.
- Existing runtime `App.tsx` navigation now uses the same helper covered by tests.
- `tracer.lifecycle.run` is asserted to unlock only `run_tracer`.
- Browser spec was extended for production-auth negative flows; local execution was blocked by sandbox localhost restrictions and logged.

## Out of Scope
- No backend, database, API, styling, layout, or dependency changes.
