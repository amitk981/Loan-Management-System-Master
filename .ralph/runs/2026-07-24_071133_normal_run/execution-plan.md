# Execution Plan

Selected slice: 012D-audit-explorer

## Permission check

- Worktree: `/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_071133_normal_run`
- Allowed product scope: `sfpcl_credit/**`
- Allowed evidence/contract scope: `.ralph/runs/2026-07-24_071133_normal_run/**` and
  `docs/working/**`
- Protected and forbidden paths will not be edited, including `docs/source/**`, workflow scripts,
  Ralph configuration/permissions, policy documents, and Git metadata.
- No dependency installation, Git staging, commit, or push is planned.

## Source contract

Implement three strictly read-only, separately permissioned resources over the existing immutable
stores: audit logs, workflow events, and version histories. Each resource must use the standard
envelope/pagination contract, deterministic newest-first ordering, supported canonical filters,
scope-safe selectors, and sanitised projections. Audit export remains a handoff to the restricted
012C export policy rather than a new download route.

## TDD behavior sequence

1. Add one public-API behavior test for a scoped, sanitised, filterable audit-log page; retain the
   failing output, implement the smallest selector/view changes, and retain the green output.
2. Add the next public-API behavior for workflow-event filtering, permission/scope, deterministic
   pagination, linked-record projection, and read-only methods; make it green before proceeding.
3. Add the next public-API behavior for version-history filtering, permission/scope, deterministic
   pagination, sanitisation, and read-only methods; make it green before proceeding.
4. Add combined/invalid filter, authentication/authorization, cross-scope, empty-result,
   sensitive-value, query-count/PERF-010, and restricted-export-handoff behaviors incrementally.
5. Run focused regressions covering immutable recorders and existing sensitive reveal/restricted
   download/export consumers. Run Django check and migration-sync; do not run the complete backend
   suite or coverage lane.

## Documentation and evidence

- Update `docs/working/API_CONTRACTS.md` with supported query names and sanitised response fields.
- Save red/green, focused regression, Django check, and migration-sync logs under
  `evidence/terminal-logs/`.
- Save representative filtered response evidence under `evidence/api-responses/`.
- Complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; set the review result
  exactly to `Ready for independent validation` only after focused work is green.
