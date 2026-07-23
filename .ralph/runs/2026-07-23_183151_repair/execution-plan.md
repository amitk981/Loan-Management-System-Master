# Execution Plan

Selected slice: 011N-grievance-workflow
Mode: same-worktree repair
Failed validator: trusted PostgreSQL acceptance for
`sfpcl_credit.tests.test_compliance_postgresql_acceptance.GrievanceWorkflowPostgreSQLAcceptanceTests`
(expected count: 2, two independent runs).

## Demonstrated Failure

Both independent PostgreSQL runs execute exactly two tests. The concurrent create test passes, while
`test_concurrent_resolve_and_escalate_retain_one_terminal_chain` errors because grievance resolution
queues a borrower communication without an HTTP request and the communications audit helper
dereferences `request.META`.

## Permission Check

- Permitted edit surfaces: `sfpcl_credit/**`, `docs/working/**`, and this run's
  `.ralph/runs/2026-07-23_183151_repair/**` artifacts.
- Protected/forbidden paths will not be edited.
- No frontend work is required.

## Repair Steps

1. Inspect the grievance notice handoff, generic communication audit helper, and the exact
   PostgreSQL acceptance test to identify the narrow request-independent audit seam.
2. Reproduce the retained failure with the exact slice-owned PostgreSQL test label and save RED
   evidence in this run's `evidence/terminal-logs/`.
3. Add or tighten one focused regression test at the real service/dispatcher boundary, observe RED,
   then apply the minimal fix so non-HTTP service callers retain audit truth without fabricating
   request metadata.
4. Run the focused regression test GREEN, then rerun the exact PostgreSQL validator label until all
   two tests pass; repeat it independently with a second isolated database.
5. Run the focused grievance/reverse-consumer checks relevant to the changed boundary plus Django
   check and migration-drift check. Do not run the complete backend suite.
6. Save PostgreSQL environment and exact-count evidence, update risk assessment and review packet,
   and set the review result exactly to `Ready for independent validation`.

## Outcome

- Steps 1-6 completed.
- The minimized requestless-resolution regression changed from RED to GREEN.
- The exact two-test PostgreSQL label passed twice against isolated databases.
- Focused grievance/communications checks, Django check, and migration drift check passed.
