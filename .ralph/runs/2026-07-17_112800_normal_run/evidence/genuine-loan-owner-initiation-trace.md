# Genuine Loan-Owner Initiation Trace

The retained full-path fixture crosses these public owners in order:

1. Terminal documentation/checklist/security owners.
2. SAP request/send/completion owner.
3. `POST /create-loan-account/` backed by `loans.modules.loan_account_lifecycle`.
4. Disbursement readiness and governed source-bank activation.
5. `POST /disbursements/initiate/` backed by `DisbursementWorkflow`.

Initiation calls the loan lifecycle's narrow decision and reconciles one account/terms tuple, one
creation status history, one `finance.loan_account.created` audit, and one `LoanAccountCreated`
workflow event. Their three identities are frozen into initiation evidence. Changing the creation
audit's terms identity returns `409 INVALID_STATE_TRANSITION` with zero disbursement writes.

Evidence: `08-loan-owner-evidence-red.txt`, `09-loan-owner-evidence-green.txt`,
`11-genuine-loan-owner-trace.txt`, `15-owner-drift-regression-green.txt`, and
`18-final-documentation-fixture-green.txt`.
