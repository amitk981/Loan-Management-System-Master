# Review Findings

Independent review log, written by architecture-review runs (newest first). Each entry lists: slices reviewed, findings (severity + plain-English description), and the corrective slice or ADR created for each significant finding. The owner can read this file to see what the independent reviewer thought of recent work without reading code.

## 2026-07-04 19:03 - Architecture Review 2026-07-04_190302_architecture_review

Reviewed commits since the prior architecture review (`7908071`):
- `002G2-admin-user-action-permission-granularity` (`62f0ea9`)
- `002I-object-level-permission-test-harness` (`383ec74`)
- `002J-api-contract-test-harness` (`71087c2`)
- `002K-seed-data-and-demo-users` (`7707942`)

### Finding 1 - Medium - Demo tracer seeding grants the tracer permission to the shared Sales role

`002K` correctly guards predictable demo credentials behind `SFPCL_DEBUG=true` and `SFPCL_ALLOW_DEMO_SEED=true`, uses the real `/auth/login/` and `/auth/me/` path, and keeps the zero-permission demo user neutral. The permission isolation for the tracer demo user is weaker than the slice implies, though: `seed_demo_users` defines `demo.tracer@sfpcl.example` with role `sales_team_user`, then `_ensure_tracer_permission()` creates/updates `tracer.lifecycle.run` and attaches it to the shared `sales_team_user` role (`sfpcl_credit/identity/management/commands/seed_demo_users.py:52`, `:112-122`). Because `/auth/me/` derives permissions from primary-role `RolePermission` rows, every local user with `sales_team_user` becomes tracer-capable after the demo seed runs. A-007 says `sales_team_user` has no source-defined grants, and A-011 says the tracer permission is a dev/test smoke exception. The current tests assert the demo tracer user has exactly the tracer permission, but they do not create a non-demo Sales user and prove that user remains neutral after seeding.

Corrective action: created `docs/slices/002K2-demo-tracer-permission-isolation.md`. It must keep the guarded local/demo behavior but isolate tracer authority to the intended demo user/role path, with a failing-first regression proving a non-demo `sales_team_user` still gets `permissions: []` after seeding.

### Finding 2 - Pass - 002G2 closes the prior admin permission boundary finding

The reviewed diff replaces the broad `has_manage_users_permission()` check with action-specific backend gates. Tests cover create-only, update-only, disable-only, and read-only partial roles, plus negative side effects: forbidden writes produce `403 PERMISSION_DENIED` without audit rows or session revocation. A-015 clearly documents the read fallback needed because the seeded `system_admin` role has write user-admin grants but not `users.user.read`.

Corrective action: none.

### Finding 3 - Pass - 002I and 002J add narrow test infrastructure without production coupling

`002I` adds a pure `evaluate_object_access(...)` helper that takes explicit actor/object facts, does not query future domain models, and returns typed allow/deny reasons including `scope_unknown` with `approval_required=True`. `002J` adds test-only API contract assertions under `sfpcl_credit/tests/` and regression coverage for existing auth/admin/tracer endpoints. Red/green logs exist in both run folders and the final full backend/frontend gates are green.

Corrective action: none.

### Finding 4 - Pass with queue sharpening - 003A/003B are ready to start after the corrective slice

The next Epic 003 slices were already sharpened from the digest. This review added current-schema details: `003A` must serialize nullable `AuditLog.actor_user` rows as `actor: null`, and `003B` must preserve tracer `workflow_event_id` response behavior while reconciling the existing tracer-owned `workflow_events` table.

Corrective action: no additional defect slice beyond `002K2`; `003A` and `003B` were sharpened.

## 2026-07-04 13:52 - Architecture Review 2026-07-04_135247_architecture_review

Reviewed commits since the prior architecture review (`0939e01`):
- `002EYA-e2e-baseline-and-seed-safety` (`e8a166f`) plus operator baseline commit `9c4e97b`
- `002F2-navigation-render-regression-tests` (`17a85e6`)
- `002G-admin-user-and-role-management-shell` (`dd223ea`)
- `002H-state-machine-and-transition-guard-foundation` (`fd020d9`)

### Finding 1 - Medium - Admin user-management collapses distinct source permissions into one backend authority

`002G` added useful user-management endpoints and tests, but the backend gate in `sfpcl_credit/identity/modules/admin_users.py` grants full list/detail/role/team/status authority when the actor has any one of `users.user.create`, `users.user.update`, or `users.user.disable`. The source catalogue defines these as separate risk-rated permissions (`auth-permissions.md` §12.1), with `users.user.disable` marked Critical, and the route map names `users.user.read` for `/settings/users`. Current seeded `system_admin` has all three write permissions, so today's happy path works, but a future role with only create or update would be able to suspend users and revoke sessions. The tests do not include partial-permission roles, so this drift would not be caught.

Corrective action: created `docs/slices/002G2-admin-user-action-permission-granularity.md` and made `002I`/`002J` depend on it. 002G2 must enforce action-specific backend permissions while preserving current `system_admin` access and the last-admin lock-out guard.

### Finding 2 - Low - The new Admin Users screen has functional tests but no visual screenshot evidence

`002G` added a frontend page under the existing app shell and the implementation reuses the current table/card/status patterns. The run packet records that the in-app browser target was unavailable, so no screenshots were captured for the new screen's loading, list/detail, validation, or unauthorized states. This is an evidence gap rather than a found visual defect, but it matters because `FRONTEND_DESIGN_RULES.md` makes screenshot evidence binding for frontend changes.

Corrective action: no standalone product slice. If 002G2 changes frontend action visibility, it must save visual evidence for the Admin Users page; otherwise the next browser-capable operator review should capture this screen.

### Finding 3 - Pass - Prior E2E/evidence corrective slices materially closed the earlier review gaps

`002EYA` now has six committed Playwright PNG baselines, a config-level fail-fast when `E2E_DJANGO_PYTHON` is unset, and `seed_e2e_users` refuses unless both `SFPCL_DEBUG=true` and `SFPCL_ALLOW_E2E_SEED=true` are present. The reviewed run folders now contain the claimed nested `evidence/terminal-logs/` paths, including red/green targeted logs. The operator baseline commit says normal `npm run e2e` passed twice in comparison mode on a browser-capable machine; the agent sandbox still records the expected local `EPERM` server-start limitation.

Corrective action: none.

### Finding 4 - Pass - 002F2 and 002H deepen shared boundaries without production drift

`002F2` moved Sidebar visibility through `visibleStaffNavItems()` and covers zero-permission, unknown-role, tracer-only, admin-user, and per-item route-guard cases without adding frontend test dependencies or styling changes. `002H` introduced a small domain-neutral `workflows.guard` module and migrated tracer transitions by passing explicit actor permissions; tests cover allowed transitions, unknown action, invalid state, missing permission, no-op rejection, and tracer API preservation of `403 PERMISSION_DENIED` / `409 INVALID_STATE_TRANSITION` with audit/workflow-event counts.

Corrective action: none beyond 002G2.

## 2026-07-04 08:51 - Architecture Review 2026-07-04_085117_architecture_review

Reviewed commits since the prior architecture review (`ba78859`):
- `002EY-e2e-and-visual-regression-harness` (`0cb56c3`)
- `002F-role-aware-sidebar-header-navigation` (`84ba391`)
- `002FL-frontend-lint-baseline` (`cc0c134`)

### Finding 1 - Medium - The Playwright harness is authored, but the visual-regression contract is still incomplete

`002EY` required committed visual baselines and a local `npm run e2e` proof for login, dashboard, tracer closed state, invalid login, missing/revoked auth, and zero-permission dashboard. The diff adds Playwright specs with `toHaveScreenshot()`, but `sfpcl-lms/e2e/` contains no `*-snapshots/` directories or PNG baselines, and `.ralph/runs/2026-07-04_072505_normal_run/review-packet.md` says first baseline generation is still an operator step. That means a clean `npm run e2e` will not yet satisfy the slice's own acceptance criteria; it still needs `--update-snapshots` on a browser-capable machine before it can be a real regression gate.

Corrective action: created `docs/slices/002EYA-e2e-baseline-and-seed-safety.md` to generate and commit baselines, prove `npm run e2e` passes without update mode, and save real E2E evidence.

### Finding 2 - Medium - The deterministic E2E seed command can create known-password users without an explicit E2E guard

`sfpcl_credit/identity/management/commands/seed_e2e_users.py` creates active login users with the known password `E2eTracer123!` and a tracer-only role/permission. This is appropriate for the isolated Playwright database, and A-011/A-013 document the dev-only intent, but the management command itself has no runtime guard: if run against the wrong database, it will insert active known-password accounts. The Playwright config points `SFPCL_DB_PATH` at an E2E sqlite file, which reduces normal risk, but the command should still refuse outside explicit local/E2E setup.

Corrective action: `002EYA` now requires a `seed_e2e_users` guard plus tests proving the command refuses without an explicit E2E flag and succeeds only in local/E2E mode.

### Finding 3 - Medium - The 002F navigation tests do not prove the actual Sidebar hiding behavior

The implementation is directionally good: `PAGE_PERMISSIONS` lives in `navigationPermissions.ts`, `App.tsx` uses `resolveNavigationAttempt()`, and `Sidebar` filters `allNavItems` through `can(requiredPermission)`. The test named "hides every protected sidebar item when the user lacks its required permission", however, does not render `Sidebar` or call the filtering path. It builds a set of every other permission and asserts that the current permission is absent from that set. If `Sidebar` later stopped filtering by permission, that test would still pass. Given this is the staff-shell permission boundary, the coverage needs to exercise behavior, not just the exported table.

Corrective action: created `docs/slices/002F2-navigation-render-regression-tests.md` to add render-level or shared-helper coverage for Sidebar visibility and guarded navigation, including tracer-only, zero-permission, unknown-role, and future admin-management cases.

### Finding 4 - Medium - Run packets repeatedly reference red/green evidence paths that are absent

The reviewed run packets and progress entries for `002EY`, `002F`, and `002FL` refer to logs under `.ralph/runs/<run-id>/evidence/terminal-logs/`, but the committed run folders contain only root-level gate result files; no `evidence/terminal-logs/` directories exist for those three runs. The final root gate logs are useful and green, but the missing red/green paths weaken auditability, especially for frontend permission and E2E infrastructure work. This repeats the evidence-path issue found in the 2026-07-03 architecture review.

Corrective action: `002EYA` and `002F2` explicitly require evidence paths that exist in the final artifacts. Owner/operator should also inspect why claimed nested evidence directories are not surviving into committed run folders; agents cannot edit protected Ralph scripts during a run.

### Finding 5 - Low - The lint baseline packet overstates its recorded evidence

`002FL` correctly adds `npm run lint`, pinned ESLint packages, and a flat config. However, `.ralph/runs/2026-07-04_082747_repair/lint-results.md` says lint was skipped because `.ralph/config.yaml` still has `quality_gates.lint: false`, and the claimed `evidence/terminal-logs/lint-final.log` path is absent. Its review packet also says rule downgrades are documented in `final-summary.md`, but that file is only the generic success template; the useful justification lives in `risk-assessment.md`. This is an audit packet defect, not a product-code defect.

Corrective action: no separate product slice. This review packet records the limitation, and `HANDOFF.md` keeps the owner/operator action to flip the protected lint gate once validation confirms it.

### Finding 6 - Pass - The core 002F and 002FL implementation shapes are reasonable

The route-guard extraction in `002F` removes duplicated page-permission data from `App.tsx`, keeps `tracer.lifecycle.run` isolated to `run_tracer`, and preserves the neutral `backend_staff` role path from 002E2. `002FL` uses approved pinned lint dependencies and avoided visual, label, layout, and permission-table changes while fixing lint-safe issues. Current review-run gates passed after these commits.

Corrective action: none beyond Findings 3-5.

## 2026-07-04 07:13 - Architecture Review 2026-07-04_071340_architecture_review

Reviewed commits since the prior architecture review (`ced57b0`):
- `002E2-frontend-role-bridge-hardening` (`9a9d3bb`)
- `002EX-early-end-to-end-tracer-bullet` (`027b5b0`)

### Finding 1 - Medium - The tracer app squats on the canonical `workflow_events` table that slice 003B must own

`002EX` was scoped to MINIMAL skeleton models (Member, LoanApplication, LoanAccount, Repayment) plus an audit event per transition. The domain models are correctly namespaced under `tracer_*` table names, so they will never collide with the real member/application/finance tables that slices 004x/005x/009x/010x own. However, the tracer also added an *extra* model, `WorkflowEvent`, and gave it the global table name `db_table = "workflow_events"` (`sfpcl_credit/tracer/models.py`, migration `sfpcl_credit/tracer/migrations/0001_initial.py`). That is the canonical table that the still-`Not Started` slice `003B-workflow-event-foundation` is meant to own, and `docs/working/API_CONTRACTS.md` even cites `data-model.md §26.1-26.2` for it. When 003B lands, it will either try to `CreateModel` a second `workflow_events` table (migration fails at migrate time with "table already exists") or be silently forced to inherit the tracer's ad-hoc shape instead of the source `data-model.md §26` schema. This is architecture drift: a deliberately throwaway dev tracer (the tracer route is dev-only and A-011 says the tracer permission must be removed before production) has grabbed a permanent, canonical foundation table name.

Corrective action: sharpened `docs/slices/003B-workflow-event-foundation.md` to (1) treat the tracer `workflow_events` table as pre-existing drift that must be reconciled in the same slice — either relocate the canonical `WorkflowEvent` model into 003B's owning app and repoint `sfpcl_credit/tracer/services.py`, or rename the tracer copy to `tracer_workflow_events` — with no table-name collision at migrate time; and (2) base the real schema on `data-model.md §26` rather than the tracer's minimal fields.

### Finding 2 - Low - Dead ternary in the tracer frontend API client

`sfpcl-lms/src/services/tracerApi.ts` builds the "Sanction" display row with `status: disbursement ? 'recorded' : 'pending'`. `disbursement` is the resolved `ActionResponse` object returned by `tracerRequest`, which either returns a truthy object or throws — so the ternary is always `'recorded'` and the `'pending'` branch is unreachable. It is cosmetic (a display label on a dev-only screen) and did not affect gates, but `DECISION_POLICY.md §2` forbids dead code without an owning slice.

Corrective action: added a cleanup item to `docs/slices/002EY-e2e-and-visual-regression-harness.md` (which already owns the tracer UI and will render this row) to replace the always-true ternary with the actual sanction status from the sanction response.

### Finding 3 - Pass - 002E2 removed the unsafe `auditor` fallback cleanly and with real edge-case tests

`002E2` closed the Medium finding from `2026-07-03_224536`: `mapBackendUserToFrontendUser()` now falls back to a new neutral `backend_staff` role instead of `auditor`, unmapped backend role codes (`it_head`, `management_viewer`, `nominee`, `bank_user`, `subsidiary_user`, `external_auditor`) map to `backend_staff` with zero prototype permissions, and the `Dashboard` default card branch, the exceptions/tasks/applications lists, the alerts banner, and the profile-menu Settings item were all audited so a neutral backend role sees a "No workspaces available" state rather than inheriting auditor/admin/credit-manager widgets. Tests assert `backend_staff` mapping, retention of `roleName`/`roleCodes`/`teamName`, empty permission mapping, and that the role is explicitly *not* `auditor`/`admin`/`borrower`. Good behaviour-oriented coverage.

Corrective action: none.

### Finding 4 - Pass - 002EX backend proves the plumbing with strong, behaviour-oriented tests

The tracer service layer keeps transitions behind `select_for_update` + `transaction.atomic`, enforces an inline status guard (`_require_status`), writes one `audit_logs` row and one `workflow_events` row per transition, and requires the explicit `tracer.lifecycle.run` permission through the session-bound `/auth/me/` validation path. `test_tracer_api.py` asserts the full persisted lifecycle (7 workflow events, 7 tracer audit rows), out-of-order rejection at multiple points (account-before-sanction, repeated sanction, repayment-before-disburse, close-before-repayment) returning `409 INVALID_STATE_TRANSITION`, positive-amount validation, unauthenticated `401 AUTH_REQUIRED`, revoked-token `401 INVALID_TOKEN`, and permission-denied `403 PERMISSION_DENIED` — each verifying no domain/audit rows were written on rejection. These are real regression tests, not coverage padding.

Corrective action: none (see Finding 1 for the one drift issue).

### Finding 5 - Pass with known gap - 002EX frontend regressions are mapping-level, not render-level

The 002EX slice lists three "Frontend regression" cases (a `backend_staff`/empty-permission session cannot see or run the tracer, and unmapped roles do not inherit auditor behaviour). These are asserted at the mapping/service layer in `authSession.test.ts` (e.g. `mapCanonicalPermissions(['tracer.lifecycle.run']) === ['run_tracer']`, zero-permission roles map to `[]`), but there is no component/render test that mounts the Sidebar/App/TracerBullet to prove the Tracer nav item is hidden and the Run button is disabled. This is the same class of gap the prior review flagged for 002E, and it is already owned: `002EY` items 11, 14, 15 and its test cases now require a real Playwright browser assertion for a zero-permission role not exposing tracer navigation/actions and for clicking through the tracer to the closed state, and `002F` test cases require permission-gated nav coverage including `tracer.lifecycle.run -> run_tracer`.

Corrective action: none beyond confirming 002EY/002F already own it.



Reviewed commits since the prior architecture review:
- `002D3-current-user-contract-fidelity` (`c225f90`)
- `002E-protected-frontend-route-shell` (`f732df7`)

### Finding 1 - Medium - The frontend auth bridge maps unmapped backend roles to auditor behavior

`002E` correctly moved staff login to backend `/auth/login/` + `/auth/me/`, hides the demo role switcher by default, and maps canonical backend permissions to existing route checks. However, `mapBackendUserToFrontendUser()` falls back to `role: 'auditor'` when a backend role has no prototype mapping. The source role catalogue includes backend roles such as `it_head` and `management_viewer` that are not mapped in 002E, and A-007 intentionally leaves some roles with no seeded permissions until the source grants are clarified. Because many shell pages still branch directly on `currentUser.role`, an unmapped backend role can inherit auditor-shaped dashboard/profile content even though permission-gated navigation is blocked. That is architecture drift from R1-AC-004 role-aware UI and from the 002E rule that unknown permissions must not invent grants.

Corrective action: created `docs/slices/002E2-frontend-role-bridge-hardening.md` before 002EX. 002E2 must replace the `auditor` fallback with a neutral/no-affordance path, add explicit tests for `it_head` and `management_viewer`, and audit shell-level role branches.

### Finding 2 - Low - 002E visual evidence is a harness, not screenshots

The 002E slice required screenshots for login, loading/current-user fetch, authenticated dashboard, invalid login, and unauthorized/permission-blocked navigation. The run recorded that local Django/Vite servers could not bind sockets and Chrome exited before screenshots were written, so it saved HTML harness pages instead. That is understandable in this sandbox and the functional gates passed, but it means visual fidelity was not independently captured as image evidence for a frontend auth-shell change.

Corrective action: sharpened `docs/slices/002EY-e2e-and-visual-regression-harness.md` to explicitly close this gap with real Playwright screenshots/baselines for the 002E states plus tracer state.

### Finding 3 - Pass - 002D3 closed the prior `/auth/me/` contract gap cleanly

`002D3` enriched `/api/v1/auth/me/` with `mobile_number`, `roles[{role_code, role_name}]`, and `teams[{team_code, team_name}]`, while preserving session-bound access validation, active-user enforcement, compatibility fields, sorted permissions, and thin-view service boundaries. The API/module tests assert the new shape, inactive-role behavior, team sorting, and compatibility-code derivation.

Corrective action: none.

### Finding 4 - Pass with test gap - 002E has meaningful service tests, but no React integration test yet

The frontend auth-session tests assert credential post, token storage, `/auth/me/` fetch, invalid-login rejection, expired-token clearing, logout request body, role/team object-derived display state, and unknown canonical permissions granting no prototype permission. The remaining gap is that these tests exercise the service/mapping layer rather than rendering `App`/`LoginScreen` through the full login-to-dashboard flow. 002EY should cover that in a real browser before the visual/e2e gate is promoted.

Corrective action: sharpened `002EY` browser requirements; no additional product-code slice beyond 002E2 is needed from this item.

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
