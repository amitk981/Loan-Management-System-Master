# Risk Assessment

Risk level: Medium

- Selected slice: 002K-seed-data-and-demo-users
- Mode: normal_run
- Manual review required: normal Ralph review only; no owner approval needed beyond standing
  autonomous approval.

## Risk Areas
- Predictable credentials: mitigated by requiring both `SFPCL_DEBUG=true` and
  `SFPCL_ALLOW_DEMO_SEED=true`; command refuses without them.
- Permission drift: demo users use existing active catalogue roles/teams. The only dev-only
  permission exception is A-011 `tracer.lifecycle.run`, isolated to the guarded demo path.
- E2E fixture interference: demo emails are `demo.*@sfpcl.example`; tests prove `e2e.*`
  users are not created or changed.
- Authorization regression: tests prove system admin keeps canonical user-admin permission
  codes without `manage_users`, tracer-only has exactly `tracer.lifecycle.run`, zero user has
  no permissions/actions, and internal auditor receives standard `403 PERMISSION_DENIED` for
  an admin update action.

## Database Impact
- No schema or migration changes.
- Local command writes only seed data in the target database when explicit local/dev guard
  flags are present.

## Gates
- Backend check: pass.
- Backend tests: 107/107 pass.
- Backend migrations: `makemigrations --check --dry-run` pass.
- Backend coverage: 96%, above 85% floor.
- Frontend typecheck/lint/tests/build: pass.
