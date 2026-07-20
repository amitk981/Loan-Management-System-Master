# Interest Invoice Evidence

## Calculation and immutable draft

`InterestInvoiceApiTests.test_generation_uses_server_owned_fy_truth_and_leaves_balances_unchanged`
proves FY2026-27 resolves 1 April–31 March, ₹400,000.00 principal, the approved 9.2500% rate,
₹37,000.00 gross/due, immutable rate/configuration versions, one audit/rate consumption, and no
account or ledger change.

## Duplicate, scope, and configuration controls

- Exact generation replay returns retained truth; another key for the same loan/period is `409`.
- Client-supplied `interest_amount` is `400`; missing accounting configuration is zero-write `409`.
- Create permission without canonical loan scope is safe zero-write `403` without borrower email.
- Queryset bulk update of a retained invoice raises `ValidationError`.

## Issuance evidence

`InterestInvoiceApiTests.test_issue_binds_one_document_communication_job_and_audit_chain` proves one
new `DocumentFile`, `Communication`, and `CommunicationDeliveryJob`, one issuance audit, recipient-safe
`queued` status, exact replay, and an `issued` rather than `paid` invoice.

## Contention contract

The exact declared selector
`sfpcl_credit.tests.test_servicing_postgresql_acceptance.InterestInvoicePostgreSQLAcceptanceTests`
contains one test. It races two same-period requests and requires statuses `[200, 409]`, one invoice,
one rate-consumption snapshot, and one generation audit. Local SQLite collection skipped it by its
explicit PostgreSQL guard; independent Ralph validation executes it twice on PostgreSQL.
