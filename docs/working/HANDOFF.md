# Ralph Handoff

## Last Run
2026-07-17_124432_normal_run

## Current Status
009F2 is complete pending independent orchestrator validation and commit. CFC scope and terminal
authorisation now consume one typed current-disbursement decision. It reconciles the exact genuine
loan-creation history/audit/workflow identities, application-owned borrower-bank decision manifest,
complete governed source-bank lifecycle, initiation audit/workflow/task, unfunded account, and the
absence of transfer/advice/register truth. Changed beneficiary-bank facts deny both scope and
approve/reject with zero writes.

Initiation freezes the beneficiary bank, cancelled cheque, file/checksum, verifier, request, audit,
workflow, version, and source-governance request/facts identities. Database constraints reject
partial pending/terminal authorisation tuples, invalid checker role/comment evidence, same maker and
checker, and any transfer/reference/time/advice/register truth before approval. The §31.3 response,
safe comment digest, exact terminal replay, and single `DisbursementWorkflow` mutation owner remain
unchanged.

The focused authorisation/initiation set passes 33 tests; Django check, migration sync, and Ruff are
green. The PostgreSQL five-caller approve/reject class passed twice, and each class run contains the
two independent race rounds required by the slice. No frontend or external API contract changed.

## Next Run
Run 009G. It is sharpened to call
`current_disbursement_evidence.resolve_current_disbursement_evidence` for approved state and extend
that typed result with exact terminal-authorisation plus transfer-evidence reconciliation before
creating a unique UTR, funding balances, or activating the loan. Then run 009H for advice only after
the exact successful transfer.
