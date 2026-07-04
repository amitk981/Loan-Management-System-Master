# Execution Plan

Selected slice: `002I-object-level-permission-test-harness`

## Scope
- Add a backend-only, domain-neutral object-level permission helper under the existing identity module boundary.
- Add a test-only service harness through Django tests; no public endpoint, schema change, migration, frontend screen, or source-doc edit.
- Keep object scope separate from the workflow transition guard implemented in 002H.

## Source Trace
- `auth-permissions.md` §3/§3.1: backend enforces role permission, team/assignment scope, object-level access, workflow-state checks, and sensitive data rules as separate layers.
- `technical-architecture.md` §7.2/§10.4/§18.1: permission classes/services combine role, team, object, workflow, and sensitive checks while keeping service boundaries explicit.
- `api-contracts.md` §44/§50: frontend action availability is UX only; backend services remain authoritative.
- `implementation-roadmap.md`: R1 includes RBAC and object-access foundations.

## TDD Plan
1. RED: add focused service tests for object access allowing owner and team matches, denying missing module permission, denying mismatched scope, denying unknown scope, and allowing unknown scope only when the caller explicitly supplies global override.
2. GREEN: add the smallest helper API needed to pass those tests, using explicit permission/team inputs and returning typed result/reason codes.
3. Add a regression test that real user/role/team inputs can be supplied from `auth_service.effective_permission_codes(user)`, `User.team_codes()`, and `auth_service.team_payload(user)`.
4. Run targeted backend tests, then full Ralph backend/frontend gates.

## Edit Permissions Checked
- Allowed by `.ralph/permissions.json`: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, `.ralph/state.json`, and `.ralph/runs/**`.
- Protected/read-only paths will not be modified: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, `docs/source/**`, `.git/**`.

## Evidence To Save
- Red and green targeted backend logs in `.ralph/runs/2026-07-04_181736_normal_run/evidence/terminal-logs/`.
- Full backend check/test/migration/coverage and frontend typecheck/lint/test/build logs in the run folder.
- Changed files, risk assessment, review packet, final summary, progress/state/handoff updates, and slice status update.
