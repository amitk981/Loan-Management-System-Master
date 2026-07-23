# Execution Plan

Selected slice: `012A3-default-compliance-and-audit-report-catalogue`

## Scope and permissions

- Extend only the backend report catalogue and the section-40 working API contract for
  Default, Recovery, Closure/NOC, Section 186, NBFC Test, KYC/Re-KYC, Stamp Duty,
  Money-Lending Review, Grievance, and the restricted Audit Log Export handoff.
- Reuse canonical persisted read interfaces owned by Epic 008/011 and the existing report
  registry. Do not add models, migrations, export jobs/files, audit-log query duplication,
  frontend work, or new compliance/default/recovery/closure calculations.
- Authorised edit paths checked against `.ralph/permissions.json`: `sfpcl_credit/**`,
  `docs/working/**`, and this run's `.ralph/runs/**` evidence are allowed. Protected
  configuration, scripts, source material, queue/state/progress, and mechanical handoff
  facts will remain unchanged.

## Public interface and module seam

Keep the existing deep reports module interface:

`GET /api/v1/reports/<stable-report-code>/?<documented filters and pagination>`

Each queryable report definition delegates to one source-owner-backed selector. Selectors
require the owning resource-read permission, preserve owner object scope, reject unknown or
malformed filters, return deterministic source rows, and use the standard list envelope.
The Audit Log Export definition is metadata-only: it names the future 012C/012D handoff and
cannot execute through the generic report read interface.

## TDD tracer bullets

Implement one observable behavior at a time, preserving RED and GREEN output under
`evidence/terminal-logs/`:

1. Default and Recovery codes reconcile scoped owner truth, stable order, filters,
   pagination/totals, and restricted recovery-field omission.
2. Closure/NOC reconciles canonical closure, NOC, security-return, and archive truth within
   owning account scope.
3. Section 186 and NBFC Test reconcile the persisted statutory-owner projections for exact
   financial-year/quarter and review-status filters.
4. KYC/Re-KYC reuses its canonical scoped summary, preserves default masking, and denies
   cross-scope access.
5. Stamp Duty reuses legal-document stamp/notary truth without exposing restricted evidence
   or document contents.
6. Money-Lending Review and Grievance reconcile owner records with documented filters,
   permissions, stable pagination, and nondisclosing scope.
7. Cross-cutting catalogue acceptance proves empty results, invalid filters, 401/403,
   deterministic ordering, bounded queries, complete code-to-owner mapping, reverse-consumer
   parity, and an Audit Log Export handoff that cannot query or download data.

For each cycle: add one API-level behavior test, run it RED with
`/Users/amitkallapa/LMS/.ralph/venv/bin/python`, implement only enough selector/registry code
to pass, then rerun GREEN before advancing.

## Contract and focused validation

- Complete `docs/working/API_CONTRACTS.md` with stable codes, fields, filters, totals,
  permissions, source-owner reconciliation, masking, and the restricted audit-export handoff.
- Run focused report tests and affected owner/reverse-consumer tests, Django `check`, and
  `makemigrations --check` with the mandated interpreter. Do not run the complete backend
  suite or full coverage; the High-risk authoritative complete lane belongs to the
  orchestrator.
- Save a complete 23-report plus two section-40 API matrix, reconciliation/masking/denial
  examples, audit-handoff proof, focused logs, risk assessment, final summary, and review
  packet. Finish only with review result exactly `Ready for independent validation`.
