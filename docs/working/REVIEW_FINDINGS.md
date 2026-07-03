# Review Findings

Independent review log, written by architecture-review runs (newest first). Each entry lists: slices reviewed, findings (severity + plain-English description), and the corrective slice or ADR created for each significant finding. The owner can read this file to see what the independent reviewer thought of recent work without reading code.

## 2026-07-03 21:37 - Architecture Review 2026-07-03_213704_architecture_review

Reviewed commits since the prior architecture review:
- `002D-current-user-api-with-permissions-and-teams` (`52b18da`)
- `002D2-backend-dev-infrastructure` (`13f7dcb`)
- Non-product Ralph workflow fixes also present in the diff window: `d758336`, `96a0d02`

### Finding 1 - Medium - `/auth/me/` is secure and well tested, but its success shape is narrower than the source contract

`002D` correctly added session-bound access validation: missing/expired/wrong-type/revoked/inactive-user cases are covered, the view delegates to `auth_service`, and the response uses the shared envelope. The source contract, however, shows current-user data with `mobile_number`, `roles[{role_code, role_name}]`, and `teams[{team_code, team_name}]` (`docs/source/api-contracts.md` §11.4). The implementation and examples expose only `role_codes` and `team_codes`, plus no `mobile_number`. That is workable for the immediate dashboard shell, but it would make 002E build frontend session state on a reduced contract instead of the documented profile/relationship shape.

Corrective action: created `docs/slices/002D3-current-user-contract-fidelity.md` and sharpened `002E` to depend on it. 002D3 must enrich `/auth/me/` while preserving the 002D security behavior and compatibility fields.

### Finding 2 - Pass - 002D2 removed the test-infrastructure drift and the installed gates now pass

The previous architecture review found repeated manual `schema_editor.create_model` setup in backend tests. `002D2` moved auth/catalogue tests onto Django's migrated test database through `IdentityTestCase`, added a static guardrail against reintroducing the manual setup, configured persistent dev SQLite, env-driven settings, and restricted CORS for `http://localhost:5173`. The committed run artifacts show backend check, tests (50/50), migration check, coverage (96%, floor 85), frontend tests, typecheck, and build passing after the orchestrator installed pinned dependencies.

Corrective action: none.

### Finding 3 - Pass - Test quality is behavior-oriented, not coverage-only

The reviewed tests assert real security and contract behavior: `/auth/me` success data, envelope meta, missing bearer token, expired access token, refresh-token misuse, revoked sessions after logout, suspended-user revocation, sorted permissions, zero-link roles, CORS headers, environment parsing, migration-backed test setup, and shared-envelope delegation. These are meaningful regression tests for the slice risks.

Corrective action: none.

## 2026-07-03 17:04 - Architecture Review 2026-07-03_170432_architecture_review

Reviewed slices / commits since the prior architecture review:
- `002C-role-and-permission-catalogue-seed` (`9b9154d`)
- `002C2-standard-api-envelope-and-auth-service-boundary` (`160c356`)
- Non-slice Ralph workflow fix also present in the diff window: `e373f71`

### Finding 1 - Medium - Prior run packets reference red/green evidence paths that are absent

The `002C` and `002C2` review packets both claim red/green TDD evidence under `evidence/terminal-logs/`, but those directories are not present in the committed run artifacts for `.ralph/runs/2026-07-03_113738_normal_run/` or `.ralph/runs/2026-07-03_115501_normal_run/`. The root gate logs are present and show green backend/frontend validation, but the Ralph workflow requires TDD red/green evidence to be saved before completion. This weakens auditability for high-risk RBAC/auth work even though the final gates passed.

Corrective action: sharpened `docs/slices/002D-current-user-api-with-permissions-and-teams.md` so the next high-risk auth slice must save failing-first `/auth/me/` output, green backend gates, frontend gates, and API response examples at paths that exist in the final review packet.

### Finding 2 - Medium - Backend tests duplicate manual schema setup instead of relying on one test base

`test_auth_api.py`, `test_auth_module.py`, `test_api_envelope.py`, and `test_catalogue_seed.py` repeat `django.setup()`, `schema_editor.create_model()`, and manual table deletion helpers. The new 002C/002C2 tests have real behavior assertions, but this repeated test infrastructure is architecture drift: it can diverge from migrations and makes each new backend test file copy setup code instead of using Django's migrated test database or a shared test base.

Corrective action: sharpened `docs/slices/002D2-backend-dev-infrastructure.md` to remove duplicated per-file schema creation and move backend tests to a shared `TestCase`/fixture pattern while preserving the existing behavior assertions.

### Finding 3 - Medium - Worktree validation still falls back to the wrong backend interpreter

During this architecture-review run, `scripts/ralph-validate.sh` looked for `.ralph/venv/bin/python` inside the active worktree, did not find it, and fell back to bare `python3`. That violates the run prompt's backend-interpreter rule and failed with an architecture-mismatched `_cffi_backend` import. Manual backend gates passed when run with the required repo-level interpreter `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`.

Corrective action: recorded in this review packet and run summary for owner/orchestrator repair. Agents must not edit protected `scripts/` during Ralph runs.

### Finding 4 - Pass - 002C and 002C2 production behavior matches the reviewed source requirements

The role/permission seed transcribes the §12 permission catalogue and records §15 gaps instead of inventing grants (A-007). The shared API helper now supplies `meta.api_version` and both health/auth endpoints delegate to it. Auth token/session/audit behavior moved behind `identity.modules.auth_service` and `identity.modules.tokens`, with direct module tests for refresh rotation, replay rejection, logout revocation, inactive users, and audit events. No additional corrective product-code slice is needed from this review.

## 2026-07-03 08:15 - Architecture Review 2026-07-03_081509_architecture_review

Reviewed slices:
- `001-ralph-bootstrap-verification` (state recorded; no matching slice commit found in this staging history)
- `002A-backend-scaffold-and-health-endpoint` (`766dfd6`)
- `002B-user-model-and-jwt-login-refresh-logout` (`ef0810b`)
- `002B2-auth-hardening-jwt-library-and-packaging` (`7b873d4`)

### Finding 1 - Medium - API response envelope is duplicated and already drifting

`sfpcl_credit/ops.py` defines a health-only `success_response` whose `meta` contains `request_id` and `timestamp` only. `sfpcl_credit/identity/views.py` defines a separate auth `success_response` whose `meta` also contains `api_version: "v1"`. The source API contract's standard success envelope includes `api_version` in `meta` (`docs/source/api-contracts.md` §6.1), and the working contract says 002A health endpoints return the standard envelope. This means health and auth responses already disagree before the second auth endpoint family lands.

Corrective slice created: `docs/slices/002C2-standard-api-envelope-and-auth-service-boundary.md`.

### Finding 2 - Medium - Auth view owns multi-entity workflow and audit logic

`sfpcl_credit/identity/views.py` currently owns token encoding/decoding, claim construction, refresh-session lookup, refresh rotation, logout revocation, response formatting, and audit-log creation. That was acceptable to get the first auth slice through, but it conflicts with the architecture guidance that views translate HTTP and call module interfaces, while multi-entity operations and audit logging live in explicit modules (`docs/source/technical-architecture.md` §13.1 and `docs/source/codebase-design.md` §6-7). If 002D adds `/api/v1/auth/me/` on top of this shape, auth behavior will become harder to test through a stable module interface and easier to duplicate.

Corrective slice created: `docs/slices/002C2-standard-api-envelope-and-auth-service-boundary.md`.

### Finding 3 - Low - Test coverage is behavior-oriented, but one contract gap is now visible

The reviewed tests use real Django client calls, assert rotation/replay/logout behavior, audit creation, inactive-user rejection, PyJWT wrong-secret rejection, expired-token rejection, and environment-secret loading. That is stronger than coverage-only testing. The visible gap is contract coverage for a single shared envelope: health tests and auth tests validate their local response shapes separately, which allowed the `api_version` drift above.

Corrective slice created: `docs/slices/002C2-standard-api-envelope-and-auth-service-boundary.md`.
