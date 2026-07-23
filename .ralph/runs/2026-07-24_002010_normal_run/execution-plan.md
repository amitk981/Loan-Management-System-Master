# Execution Plan

Selected slice: 012A-report-api-foundation

## Scope

Implement only the six read-only section-40 reporting endpoints:

1. Application pipeline / Loan Request Register.
2. Documentation readiness.
3. Disbursement pending.
4. Loan portfolio / Loan Register.
5. DPD.
6. Compliance dashboard.

No schema, export, scheduling, saved-view, frontend, or materialized-view work is included.

## Permission Check

- Product edits are confined to `sfpcl_credit/**`, which `.ralph/permissions.json` allows.
- Evidence edits are confined to `.ralph/runs/2026-07-24_002010_normal_run/**`.
- If contract documentation needs a clarification, only `docs/working/API_CONTRACTS.md` may change.
- Protected workflow/configuration paths and `docs/source/**` will not be edited.

## Implementation Sequence

1. Inspect existing public models/selectors, API envelope/pagination helpers, route conventions,
   and permission/object-scope seams for the six owning domains.
2. Add one public API behavior test and save its failing output.
3. Add the minimal `reports` registry, selector, serializer/view, URL, and settings wiring needed
   to make that behavior pass; save green output.
4. Repeat one behavior at a time for the remaining endpoints, filters, deterministic pagination,
   invalid inputs, empty results, authentication/permission denial, and team/object isolation.
5. Add reconciliation and bounded-query assertions against persisted owning-domain records, plus
   read-only reverse-consumer assertions where existing seams support them.
6. Run focused report tests, Django system check, migration-sync check, and targeted lint/static
   checks appropriate to the changed backend files. The orchestrator retains ownership of the
   authoritative impacted/full backend lane.
7. Save six representative response examples (including empty and forbidden), reconciliation and
   query-count evidence, then complete the risk assessment, review packet, and final summary.

## TDD Behaviors

- Each route returns the standard paginated response envelope with stable ordering.
- Contracted filters use inclusive project-timezone dates and reject malformed dates, reversed
  ranges, and unsupported controlled values with the standard 400 error.
- Each report reconciles to canonical persisted records without mutating owning-domain or audit
  state.
- Unauthenticated callers receive 401; callers lacking the mapped owning read permission receive
  403 without totals; authorised callers see only their server-derived team/object scope.
- Representative pages have bounded query counts and empty authorised results remain an empty page.

## Evidence

Red/green and focused gate logs will be written under
`evidence/terminal-logs/`. API examples and reconciliation/query-count summaries will be stored
inside this run directory so they survive worktree cleanup.

## Completion

- [x] Permission boundaries checked before product edits.
- [x] Six report-specific selectors and the stable registry route implemented.
- [x] Behavior-by-behavior RED/GREEN logs saved.
- [x] Filters, pagination, permissions, object scope, reconciliation, and read-only behavior tested.
- [x] Six successful response examples plus empty/forbidden examples captured from passing fixtures.
- [x] Focused suite, reverse consumers, Django check, migration sync, and targeted static checks run.
- [x] Risk assessment and independent-validation review packet completed.
