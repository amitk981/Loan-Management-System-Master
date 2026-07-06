# Risk Assessment

Selected slice: 002K2-demo-tracer-permission-isolation

Risk level: Medium

## Risk Summary

This slice changes a local/dev guarded seed command in an authorization-sensitive area.
No production RBAC catalogue grants, schema, public API response shapes, frontend route
rules, or protected files were changed.

## Main Risks

- Authorization regression: `tracer.lifecycle.run` could remain attached to the shared
  `sales_team_user` role and make all local Sales users tracer-capable.
- Demo repair regression: databases that already ran the old 002K seed could keep a stale
  Sales-role tracer grant unless the corrected seed removes it.
- Fixture drift: the local/dev-only tracer role could be mistaken for a source-backed
  production role in future audit/workflow slices.

## Controls

- Added failing-first backend regression for a non-demo `sales_team_user` with a stale
  old tracer grant, then proved the guarded seed removes the stale grant and `/auth/me/`
  returns `permissions: []` and `available_actions: []`.
- `demo.tracer@sfpcl.example` still returns exactly `["tracer.lifecycle.run"]`.
- `demo.zero@sfpcl.example` remains neutral.
- API contracts, assumptions, and Epic 002 digest document that `local_demo_tracer_user`
  is local/dev-only and not part of the source RBAC catalogue.
- 003A/003B slices were sharpened to avoid using the local demo tracer role as an
  audit/workflow permission fixture.

## Gate Result

All required backend and frontend gates passed. Coverage: 96% against 85% floor.

Manual review required: normal orchestrator review/commit only.
