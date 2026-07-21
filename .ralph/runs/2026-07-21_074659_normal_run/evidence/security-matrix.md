# Permission, Masking, Download, and Audit Matrix

| Control | Evidence | Result |
|---|---|---|
| Staff authority | Loan read remains canonical; `reports.export` additionally required | Pass |
| Borrower scope | Active portal account + `portal.loan_account.read_own` + exact member loan | Pass |
| Cross-user job | Second authorised portfolio reader receives nondisclosing 404 | Pass |
| Masking | CSV omits raw bank reference and retains masked last four | Pass |
| Signed download | Token binds actor/job/loan/document/checksum/current issue version and expires after 15 minutes | Pass |
| Revocation | A later status issue changes the version, superseding the older capability | Pass |
| Audit minimisation | Request/generation/accepted/denied events omit rows, URLs, storage keys, and raw bank data | Pass |
