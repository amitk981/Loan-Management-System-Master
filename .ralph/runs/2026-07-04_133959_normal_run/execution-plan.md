# Execution Plan

Selected slice: 002H-state-machine-and-transition-guard-foundation

## Scope
- Add a domain-neutral backend workflow guard module under `sfpcl_credit/` with typed transition definitions containing entity type, allowed source state(s), target state, action code, required permission, audit label, and workflow label.
- The guard will accept current state, requested action, and explicit actor permission codes. It will not query users, roles, sessions, admin assignments, loan eligibility, sanction authority, money amounts, or document completeness.
- Migrate only the existing tracer transition proof from local status checks to the shared guard while preserving URLs, response envelopes, status codes, audit logs, workflow events, and public payloads.

## Source Trace
- `docs/source/technical-architecture.md` §7.2/§8: views parse/respond, service layer owns business operations, workflow layer owns state transitions and guard conditions.
- `docs/source/auth-permissions.md` §3/§3.1: backend must enforce role permission and workflow-state checks; frontend hiding is not security.
- `docs/source/api-contracts.md` §7.3: invalid workflow transitions return `409 INVALID_STATE_TRANSITION`; §44 says backend remains authoritative for available actions.
- `docs/source/data-model.md` §26.1-26.2: successful workflow actions write append-only audit/workflow evidence.
- `docs/source/domain-model.md` §21: lifecycle state machines exist as explicit domain concepts; this slice only provides the reusable guard foundation.

## TDD Plan
1. RED: add focused unit tests for the shared guard covering allowed transition, unknown action, invalid current state, missing permission, and no-op/error behavior.
2. GREEN: implement the smallest workflow module and typed errors to satisfy those tests.
3. RED/GREEN regression: add tracer API tests proving missing `tracer.lifecycle.run` still returns `403 PERMISSION_DENIED`, invalid state with the permission still returns the same `409 INVALID_STATE_TRANSITION`, and neither failure writes success audit/workflow events.
4. Migrate tracer service transitions to call the shared guard with explicit actor permissions passed from the view/auth boundary.

## Validation
- Use `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python` for all backend commands.
- Save red/green and gate logs under `.ralph/runs/2026-07-04_133959_normal_run/evidence/terminal-logs/`.
- Run backend tests/check/migration check/coverage and frontend lint/typecheck/test/build gates because Ralph validation requires them.
- No schema change expected; stop at in-code transition definitions.
