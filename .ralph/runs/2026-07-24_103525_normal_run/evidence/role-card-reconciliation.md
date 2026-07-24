# Role/Card Reconciliation

Source: `docs/source/information-architecture.md` §9.1 and
`docs/source/api-contracts.md` §43.

| Effective role | API context | Stable card families | Canonical count scope |
|---|---|---|---|
| Credit Manager | `credit_manager` | completeness, deficiencies, appraisal TAT/review, rejection, outstanding/DPD/reminders/default assessment | Application creator/receiver or Credit Assessment stage; canonical scoped loan-account candidates |
| CFO / Director | `sanction_committee` | pending/returned sanction cases and exceptions; CFO also portfolio/DPD/statutory/recovery | Approval-case and exception selectors; scoped loan-account candidates; statutory and recovery report selectors |
| Compliance | `compliance` | document generation/signature, custody, due tasks | Post-sanction checklist selector; security-custody report selector; tasks assigned to/reviewed by actor |
| Company Secretary | `compliance` | Compliance cards plus board approvals, grievances, archive | Same checklist/task scope plus grievance selector and canonical compliance-team archive-requirement scope |
| Internal Auditor | `compliance` | document, assigned task, Section 186, NBFC cards; no direct custody total | Persisted audit/checklist scope and explicit statutory read role; global custody card intentionally omitted |
| Treasury / CFC | `treasury` | SAP drafts/sent requests, disbursement readiness/authorisation, repayment allocation, invoices | Assigned SAP requests and canonical scoped loan-account candidates |
| Accounts | `treasury` | repayment posting, invoice, accrual, reconciliation breaks | Canonical scoped loan-account candidates and actor-imported bank statements |
| Management Viewer | `management` | none in 012E | Legacy context remains reachable, but global totals are omitted until a canonical object-scoped selector exists |

Reconciliation proof:

- `test_credit_manager_pending_completeness_card_reconciles_to_scoped_application_list`
  creates one owned submitted application, asserts card count `1`, and proves the corresponding
  `/api/v1/loan-applications/?status=submitted&current_stage=initial_loan_request` list reports the
  same total.
- `test_accounts_and_company_secretary_receive_role_specific_source_cards` proves the role-specific
  catalogue rather than reusing Treasury or generic Compliance cards.
- Cards are filtered by their owning read permission before selectors run; a missing permission
  or unavailable archive object scope omits the card rather than returning a fake zero.
- Dedicated-route and unknown-role tests prove callers cannot select or fall back into another role.
- Frontend role-family navigation tests assert exact backend URLs are preserved for sanction,
  grievance, SAP, Accounts posting, archive, and statutory-report destinations. The application
  reverse-consumer test additionally proves `status/current_stage` are consumed by its target list.
- `tasks` is asserted as `[]`; population remains owned by 012EA/012EB.
