# Execution Plan

Selected slice: 011A-default-case-opening

## Boundary and public interface

- Add the `sfpcl_credit.defaults` domain owner with the source-shaped
  `DefaultWorkflow.open_if_missed_repayment(...)` interface. The workflow will consume the
  loan-owned locked schedule/allocation decision; callers may identify a due date and provide a
  safe reason, but cannot assert that an obligation is missed.
- Add `DefaultCase` persistence and one migration. Database constraints will bound status/trigger
  values, keep the trigger loan/member coherent through the workflow, and prevent duplicate cases
  for the same missed scheduled principal obligation, including concurrent attempts.
- Add thin POST-open, GET-detail, and paginated/filterable-list HTTP adapters with standard
  envelopes, exact read/open permissions, canonical loan object scope, and `available_actions`.
- Record one `default.case_opened` audit row and one canonical workflow transition for the winning
  create. Replays return the existing case and never mutate repayment schedule, allocation,
  outstanding, or DPD truth.

## TDD behavior sequence

1. RED -> GREEN: a source-authorised Credit Manager opens one case for a genuinely unpaid scheduled
   principal line; verify exact three-calendar-month dates, retained trigger facts, audit/workflow
   evidence, API fields, and unchanged servicing balances.
2. RED -> GREEN: exact/manual replay converges on the same case and does not append another
   transition chain.
3. RED -> GREEN: current/fully paid, non-principal, future/invalid due date, forged missed-status,
   wrong permission, foreign/nonexistent loan, and mismatched trigger input produce zero writes and
   nondisclosing error responses.
4. RED -> GREEN: scoped detail/list filtering and pagination expose only authorised cases;
   Credit/CS/configured approver/Auditor readers get the correct read-only or open action projection.
5. RED -> GREEN: PostgreSQL concurrent open attempts produce one case and one transition chain.

Each focused RED and GREEN command uses `/Users/amitkallapa/LMS/.ralph/venv/bin/python` and appends
its complete output under `evidence/terminal-logs/`.

## Expected files

- Product: `sfpcl_credit/defaults/**`, `sfpcl_credit/config/settings.py`,
  `sfpcl_credit/config/urls.py`, and the existing identity permission catalogue where read grants
  are missing.
- Tests: `sfpcl_credit/tests/test_default_case_opening_api.py` and
  `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`.
- Evidence only inside `.ralph/runs/2026-07-22_090320_normal_run/`.

## Focused verification

- Run each focused RED/GREEN test label while developing, then the complete new default API module.
- Run reverse-consumer DPD, repayment allocation, and schedule/ledger test labels.
- Run the declared PostgreSQL race label when the configured PostgreSQL test environment is
  available; preserve the truthful output either way for independent trusted acceptance.
- Run Django `check` and `makemigrations --check`; inspect migration forward/reverse/reapply through
  focused migration commands/tests without running the complete backend suite or global coverage.
- Review changed-file count, diff stat, targeted hunks, protected paths, and migration count before
  writing the risk assessment, review packet, and final summary.
