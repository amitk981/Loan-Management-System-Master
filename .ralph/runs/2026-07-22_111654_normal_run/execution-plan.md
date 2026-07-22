# Execution Plan

Selected slice: 011B-grace-period-tracking

## Boundary

Implement only the backend grace-period, cure, expiry, and post-grace assessment behavior owned by
011B. Reuse the existing `defaults.modules.default_workflow` public interface, canonical repayment
schedule/allocation truth, document ownership, workflow/audit evidence, and scheduler metadata seam.
Do not implement extensions, non-payment notes, reminders, frontend work, or policy criteria.

## Permission Check

- Product changes are limited to `sfpcl_credit/**`, which `.ralph/permissions.json` allows.
- Run evidence is limited to this run's `.ralph/runs/2026-07-22_111654_normal_run/**` folder.
- One migration is allowed; protected files and `docs/source/**` remain untouched.

## TDD Tracer Bullets

1. Add a public-interface behavior test proving month-end/leap-year grace boundaries and derived
   active/expired truth, capture RED, minimally implement, then capture GREEN.
2. Add a behavior test proving only fully allocated canonical principal payment during grace cures
   the case without deleting history, capture RED/GREEN, and preserve reverse-consumer reads.
3. Add a behavior test proving the retry-safe expiry processor creates exactly one assessment task
   and workflow/audit evidence while reporting bounded counts, capture RED/GREEN.
4. Add API behavior tests for expired scoped Credit Assessment Team assessment creation and current
   detail/list projection; then add negative atomicity coverage for early, cured/closed,
   foreign-scope, invalid/missing payload/evidence, and duplicate-current attempts.
5. Add the declared PostgreSQL concurrency acceptance proving expiry replay/races produce one task
   and one expiry transition, then implement only the locking/uniqueness needed to satisfy it.

## Implementation Shape

- Add `DefaultAssessment` plus the smallest case pointer/state and scheduler/task persistence needed
  for one current requirement, with database constraints and one migration.
- Keep workflow logic atomic in `DefaultWorkflow`; views only authenticate, parse, dispatch, and map
  standard envelopes/errors.
- Expose server-derived grace state, current assessment, and permission-aware available actions on
  the existing list/detail responses; never accept caller-supplied payment or grace truth.
- Seed `defaults.assessment.create` for the Credit Assessment Team through the migration.
- Update the working API contract because this slice changes the implemented API surface.

## Focused Verification and Evidence

- Save every focused RED/GREEN command under `evidence/terminal-logs/` using the mandated Ralph venv.
- Run focused defaults API/service tests, scheduler regression tests, reverse 011A tests, the exact
  PostgreSQL acceptance label when the configured database is available, Django check, and
  `makemigrations --check`. Do not run the complete backend suite/coverage lane.
- Record migration output, diff stats/targeted review, risk assessment, traceability, API examples,
  and set the review packet Result exactly to `Ready for independent validation`.
