# Execution Plan

Selected slice: 010MB-interest-and-monitoring-frontend-wiring

## Scope and seams

- Extend the existing `servicingApi` module interface with typed interest, DPD, and reminder reads/mutations. Keep standard-envelope parsing, idempotency headers, and permission predicates inside that module.
- Add the narrowly missing scoped monitoring read projections only where the backend has no canonical read: current portfolio DPD rows/summary and retained per-loan reminders. Reuse the existing loan-object scope and serializers; expose no recipient or message content.
- Replace the two prototype pages' fixtures and role-string policy with canonical projections and exact backend permissions while preserving their existing layout, table, badge, alert, and card patterns.
- Extend the existing trusted-browser spec for the two owned S47-S52 workflows without auth mocks. Do not execute Chromium locally if the sandbox probe remains unavailable; collection plus component/service tests are local feedback and the orchestrator owns the twice-run browser gate.

## TDD sequence

1. RED/GREEN: backend monitoring read-projection tests prove canonical DPD bucket counts/rows, retained reminder delivery/follow-up evidence, object scope, nondisclosure, and all-or-error behavior.
2. RED/GREEN: servicing transport tests prove exact URLs/envelopes, Money fidelity, caller-stable idempotency keys, permission predicates, and 403/validation propagation.
3. RED/GREEN: Interest Management component tests prove canonical invoice/accrual/preview/result rendering, exact trigger visibility, stable-key refresh, and loading/empty/error/unauthorised/validation states.
4. RED/GREEN: Monitoring Dashboard component tests prove server bucket/row fidelity, retained reminder evidence, partial-failure visibility, and removal of mock/local DPD/reminder policy.
5. Extend browser collection for `interest-management.png` and `monitoring-dashboard.png`, using real login/current-user authority and deterministic backend projections.

## Verification and evidence

- Save each focused failing and passing command under `evidence/terminal-logs/`, including explicit exit codes.
- Run focused backend tests only if backend projection code changes, always with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`; then `manage.py check` and migration sync.
- Run focused frontend service/page tests, Playwright collection, typecheck, lint, and build. Run static mock/auth/policy audits and inspect diff stats/targeted hunks before review.
- Complete risk assessment, independent review packet, and final summary. Set the review result exactly to `Ready for independent validation`; do not edit orchestrator-owned state/progress/status/changed-files facts and do not commit.

## Stop boundary

Stop and report rather than widen the slice if the candidate exceeds 1,350 forecast lines, 30 files, one migration, or touches a protected/forbidden path.
