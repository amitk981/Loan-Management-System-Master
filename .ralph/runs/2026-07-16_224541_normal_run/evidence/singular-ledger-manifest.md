# Sanitized SAP Singular-Ledger Manifest

The public `SapCustomerCodeDecision` is emitted only when the newest completed request has exactly
one coherent tuple. No customer code, workbook bytes, capability, network secret, or internal row id
is included here.

| Ledger | Required current facts |
|---|---|
| Request | completed lifecycle; exact application/member/code; active assigned Senior Finance identity; exact send/completion digests and reuse flag |
| Annexure-I | restricted `.xlsx`; canonical MIME; original uploader; retained storage metadata; genuine XLSX package; decrypted-byte SHA-256 equals delivery SHA-256 |
| Send audit | one exact action; Credit Manager actor; role/team; request/application/member/sanction/assignee; draft-to-sent transition; communication/task/file/checksum/reference; request/network context; sealed complete safe body |
| Send workflow | one `SAPCustomerCodeSent`; exact request; draft-to-sent; same Credit Manager; exact trigger |
| Communication | one direct user email record; exact sender/recipient; canonical safe subject/body; delivered state; exact delivery reference |
| Task | one linked Finance task; exact communication/request/sender/recipient/action path and canonical safe content |
| Completion audit | one create or reuse action; assigned Senior Finance actor; role/team; exact request/application/member/code/document/digest/reuse; sent-to-completed transition; request/network context; sealed complete safe body |
| Completion workflow | one `SAPCustomerCodeCompleted`; exact request; sent-to-completed; same assignee; action matching create/reuse |
| Code | active, normalized, same member; original application belongs to that member; new-code creator/application exactly match the completing request |

Focused evidence: `terminal-logs/01-red-send-assignee.txt` through
`terminal-logs/22-focused-sap-tests-final-green.txt`.
