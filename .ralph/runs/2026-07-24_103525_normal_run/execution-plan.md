# Execution Plan

Selected slice: `012E-operational-dashboard-hardening`

## Scope and constraints

- Harden the existing staff dashboard read model only; do not implement the later task engine.
- Derive the effective dashboard context from the authenticated user's role. Reject caller-supplied
  role or other query overrides.
- Add the four section-43 routes, enforce each dedicated route's authorised context, and return
  stable cards whose counts and links use existing canonical domain/report selectors.
- Preserve `tasks: []`, ordinary access logging, and read-only behaviour.
- Reuse the existing Dashboard layout and state patterns. Do not add styling or mock fallback data.
- Produce the exact trusted-browser spec and populated, empty, error, and forbidden screenshots.

## Permission and safety check

- Intended product paths are under `sfpcl_credit/**` and `sfpcl-lms/src/**`; browser specs are under
  the repository's existing frontend E2E location; all are allowed by `.ralph/permissions.json`.
- Evidence is confined to `.ralph/runs/2026-07-24_103525_normal_run/**`.
- Protected configuration, workflow scripts, source documents, state/progress, selected-slice
  status, and mechanical handoff files will not be edited.
- No migration or dependency change is planned.

## TDD sequence

1. Add one backend API behaviour test for an authenticated role card reconciling to its canonical
   selector and scoped link; capture RED, implement the minimal card catalogue/selector seam, and
   capture GREEN.
2. Add role-by-role API tests incrementally for Credit, Compliance/CS, CFO, Treasury, and Accounts;
   cover dedicated-route denial, no-role/multi-role resolution, cross-team/object isolation,
   caller override rejection, empty tasks, no mutation, and bounded query count.
3. Add frontend tests incrementally for real API data, loading, empty, partial/error, forbidden,
   refresh, scoped navigation, and absence of mock fallback; implement only the necessary wiring.
4. Add the exact trusted browser acceptance spec and deterministic fixtures, then capture the four
   required screenshots using the declared localhost server capability.

## Verification and evidence

- Run focused backend tests with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`; save red/green and focused outputs.
- Run impacted frontend tests, typecheck, lint, and build; save outputs.
- Run Django check and migration-sync checks, but not the complete backend suite/coverage lane.
- Record the role/card reconciliation matrix and representative query-count/performance evidence.
- Review the final diff against repository standards and the selected slice, repair findings, then
  complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Set the review packet Result exactly to `Ready for independent validation`.

## Completion

- Backend RED/GREEN, canonical-scope repair, focused API tests, query budgets, Django check, and
  migration drift checks completed.
- Frontend focused tests, typecheck, lint, build, exact E2E spec, and browser launch attempt
  completed. Trusted validation must rerun screenshots because local Chromium aborted on launch.
- Independent standards/spec reviews were run and their actionable implementation findings repaired;
  final risk and review artifacts completed for validation.
