# API response examples

GET own sanctioned application returns the standard success envelope with application identity,
`availability: available`, and checklist-ordered actions. Each action contains only code, label,
section, required/applicable, borrower-safe status/date/instruction, upload/re-upload flags, and a
nullable current Term Sheet/Loan Agreement action URL. Response scans found no storage key,
checklist/security identity, BO/bank/cheque value, or workflow/version evidence.

POST accepted upload returns `action_code`, `status: submitted`, and safe file id/name/MIME/size/
checksum/time. A second upload returns another document while retaining the first immutable ledger
row as `supersedes`; neither response reports internal completion.

GET current document action first returns a short-lived portal-scoped content URL. Authenticated
retrieval returns the checksum-verified bytes and records the separate download audit. Cross-member,
missing, internal-token, unsafe-action, and expired-link requests return nondisclosing errors.

Executable assertions: `evidence/terminal-logs/backend-post-review-focused.txt`.
