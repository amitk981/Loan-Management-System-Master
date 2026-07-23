# Execution Plan

Selected slice: `012A2-finance-and-servicing-report-catalogue`

## Scope and permissions

- Extend only the backend report catalogue and the section-40 working API contract.
- Reuse persisted truth and existing read-scope/selectors owned by approvals, security,
  SAP/disbursements, repayments, interest, and monitoring. Do not add models, migrations,
  export generation, frontend work, or new financial/workflow calculations.
- Authorised edit paths checked against `.ralph/permissions.json`: `sfpcl_credit/**`,
  `docs/working/**`, and this run's `.ralph/runs/**` evidence are allowed. Protected and
  source paths will remain unchanged.

## Public interface

Keep the existing deep reports module interface:

`GET /api/v1/reports/<stable-report-code>/?<documented filters and pagination>`

Each registry entry delegates to one selector. Selectors authenticate with the owning
resource-read permission, apply owner-defined object scope, return deterministic source rows,
and expose standard list pagination without mutations.

## TDD tracer bullets

Implement behavior vertically, preserving RED and GREEN output under
`evidence/terminal-logs/`:

1. Credit catalogue: Credit Sanction and Exception report codes reconcile to approval
   register truth, filters, ordering, pagination, permissions, and scope.
2. Security/SAP catalogue: Security Custody and SAP Pending report codes reconcile to
   owner records, including masking and scope.
3. Disbursement/repayment catalogue: full Disbursement and Repayment report codes reconcile
   money, status, reference/date fields, totals where source-backed, filters, and scope.
4. Interest catalogue: Interest Invoice and Interest Accrual report codes reconcile to
   persisted finance truth and reject invalid filters.
5. Monitoring catalogue: CFO Quarterly MIS reconciles to the persisted MIS owner projection.
6. Cross-cutting acceptance: empty result, 401/403 and cross-scope nondisclosure, stable
   pagination, bounded query counts, registry completeness, and reverse-consumer read-only
   proof.

For each cycle: add one observable API behavior, run it RED with
`/Users/amitkallapa/LMS/.ralph/venv/bin/python`, implement the minimum selector/registry
change, then rerun GREEN before advancing.

## Contract and validation

- Add stable codes, filters, fields, totals, permissions, and owner reconciliation notes to
  `docs/working/API_CONTRACTS.md`.
- Run the focused report tests, relevant owner/reverse-consumer tests, Django `check`, and
  `makemigrations --check`. Do not run the complete backend suite or full coverage; the
  orchestrator owns the authoritative selective lane.
- Save a code-to-source/permission matrix, reconciliation examples, query-count evidence,
  risk assessment, final summary, and review packet. Finish only with review result exactly
  `Ready for independent validation`.
