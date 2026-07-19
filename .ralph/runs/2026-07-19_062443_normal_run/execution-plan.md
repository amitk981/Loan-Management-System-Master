# Execution Plan

Selected slice: `009L-epic-009-staff-workflow-and-sap-posting-closure`

## Scope and interfaces

- Preserve the existing SAP customer-profile, loan-account, disbursement-workflow, and communications
  module interfaces as the mutation authorities. Deepen their public read/facade seams so the staff
  workspace composes canonical decisions instead of importing persistence models or rebuilding rules.
- Add a canonical Credit Manager S36 candidate/assignment projection and route its action descriptors
  to the retained create/send endpoints with fixed application facts and safe assignee choices.
- Add one disbursements-owned, singular initial-loan-payment SAP posting obligation created atomically
  by successful transfer. It remains `pending`; confirmation is unavailable until an explicit source-
  backed grant/adapter is defined, which will be recorded as an assumption rather than invented.
- Keep Epic 010 servicing state out of the Loan Account 360 UI while extending current list filters and
  bounded database pagination for the source-supported Epic 009 fields.

## TDD tracer bullets

1. RED/GREEN: retain the architecture-review probes proving an admitted Senior Finance workspace read
   does not return 500 and incoherent current disbursement evidence projects no actionable row.
2. RED/GREEN: prove current effective CFC/Senior Finance/Credit Manager authority, dependent permissions,
   safe SAP projection/action parity, assignee scoping, optional completion fields, and no sensitive ids.
3. RED/GREEN: prove a successful transfer creates exactly one pending SAP posting obligation containing
   immutable transfer/register/application/account/amount/time evidence; exact replay stays singular and
   conflicts/cross-object failures create none.
4. RED/GREEN: prove loan-account search/status/member filters, explicit `dpd_bucket` Epic 010 deferral,
   database pagination, and populated query ceilings for both staff collections.
5. RED/GREEN: prove frontend transport converts `datetime-local` to an aware ISO-8601 instant, sends exact
   fixed bytes and stable idempotency keys, exposes 400/403/409 errors, selects the intended MP14 record
   independent of list order, and cannot combine real account identity with mock servicing history.

## Implementation and verification

- Add at most one migration and update API contracts, the Epic 009 digest, and ASSUMPTIONS only for new
  durable contract/governance facts.
- Extend the existing Disbursement/Payment Authorisation/Loan Account/MP14 pages using only established
  prototype patterns; add the declared Playwright contract and eight exact screenshot names.
- Run each focused backend test with `/Users/amitkallapa/LMS/.ralph/venv/bin/python` and retain RED/GREEN
  logs. Run focused frontend Vitest tests, then frontend typecheck, lint, tests, and build; run Django
  check and migration-sync, but leave the complete backend suite/coverage to the orchestrator.
- Inspect targeted diffs and reverse consumers, then complete risk-assessment.md, review-packet.md, and
  final-summary.md with honest browser limitations and traceability.
