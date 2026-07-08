# Execution Plan

Selected slice: 003J-background-job-scheduling-foundation

## Scope
- Add a dedicated backend scheduler module/app for local scheduled-job metadata.
- Keep the slice internal-only: no public scheduler endpoint, no worker process, no Celery/Redis,
  no real reminder/report/notification generation, and no communication-send changes.
- Use one non-destructive migration for the scheduler table.

## Source Trace
- `docs/source/implementation-roadmap.md` §10.3 names background jobs as an R1 backend story,
  with Celery setup/basic task as later infrastructure.
- `docs/source/implementation-roadmap.md` §30.2 names Redis/Celery for notifications, jobs, and
  reports; this slice avoids adding that dependency because it is not already pinned/importable.
- `docs/source/implementation-roadmap.md` §31.1 says background jobs must not fail silently, and
  mitigation is job run records and alerts.
- `docs/source/api-contracts.md` §40.7-§40.8 shows future export jobs returning queued/completed
  status, but this slice does not add report export endpoints.

## Plan
1. Add failing service-level tests for scheduler enqueue idempotency, atomic duplicate handling,
   legal and illegal transitions, and isolation from dashboard/notification side effects.
2. Implement a `sfpcl_credit.scheduler` app with `ScheduledJob` model and service boundary.
3. Add migration and register the app in Django settings.
4. Run the focused tests to green, then run backend gates and frontend gates required by Ralph.
5. Save red/green/gate evidence, changed files, risk assessment, review packet, final summary,
   and update state/progress/handoff/slice status.

## Permission Check
Allowed by `.ralph/permissions.json`:
- `.ralph/runs/**`
- `sfpcl_credit/**`
- `docs/working/**`
- `docs/slices/**`
- `.ralph/state.json`

Protected or forbidden paths will not be edited:
- `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`,
  `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`,
  `docs/working/FRONTEND_DESIGN_RULES.md`, `docs/source/**`, `.git/**`.
