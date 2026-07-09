# Execution Plan

Selected slice: 005C2-application-object-access-hardening

## Scope
- Backend-only corrective hardening for loan application detail, draft update, submit, and reference generation.
- No schema, frontend, list filtering, document/completeness, assignment queue, or member portal changes unless existing code forces it.

## Source Trace
- `docs/source/auth-permissions.md` §19.2 scopes Field Officers to created/assigned applications and Credit Manager to the credit-assessment domain.
- `docs/source/auth-permissions.md` §34.3 requires object access for application detail and workflow/state permissions for application mutation endpoints.
- `docs/source/auth-permissions.md` §37.3 explicitly expects a Field Officer viewing an unrelated application to be denied.
- `docs/working/digests/epic-005-application-intake.md` records the architecture-review extract for this corrective slice.

## TDD Plan
1. Add a failing API regression proving a same-permission, unrelated user receives `403 OBJECT_ACCESS_DENIED` on detail, patch, submit, and reference generation.
2. Include side-effect assertions that denied update/submit/reference actions create no success audit rows, workflow transitions, register rows, reference number, or sequence-visible advancement.
3. Keep existing missing-global-permission regressions as `403 PERMISSION_DENIED`.
4. Implement object access through `sfpcl_credit.identity.modules.object_permissions.evaluate_object_access(...)` after authentication/global permission and after `404` lookup, before serialization or mutation.
5. Record the current schema assumption for Credit Manager/global credit-domain override if needed.

## Gates and Evidence
- Save red and green targeted backend test logs under `.ralph/runs/2026-07-09_193538_normal_run/evidence/terminal-logs/`.
- Run backend check, backend tests, migrations check, backend coverage, frontend typecheck/test/build/lint as required by Ralph gates.
- Update `docs/working/API_CONTRACTS.md`, run artifacts, state/progress/handoff, and mark the slice complete only after gates pass.
