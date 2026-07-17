# Execution Plan

Selected slice: 009H-disbursement-advice-and-communication

1. Preserve the exact 009G successful-transfer boundary and inventory its retained financial,
   audit, workflow, member-contact, and template evidence. Add no frontend work and no register,
   checklist, repayment, schedule, interest, or balance behavior.
2. RED→GREEN tracer: add one public API success test for
   `POST /api/v1/disbursements/{id}/send-advice/`, proving canonical borrower email, exact approved
   template merge, masked UTR, one accepted adapter call, one protected communication link, and one
   advice audit/workflow action with no financial side effects. Implement the smallest public
   `disbursement_advice` owner, adapter contract, workflow facade method, view, and route that passes.
3. RED→GREEN incrementally add public tests for exact zero-write/no-resend replay, changed replay,
   unknown fields/query parameters, wrong channel/email, missing or ambiguous template, inactive or
   unfunded/stale transfer evidence, role/grant/scope denial, and adapter rejection without false
   sent/link truth. Harden owner evidence reconciliation after each failing behavior.
4. RED→GREEN add a transaction/concurrency behavior proving only one accepted communication and
   one complete advice ledger can win. Add at most one migration only if existing relations cannot
   retain the immutable advice action identity and complete evidence safely.
5. Update the API contract, Epic 009 digest, slice checklist/status, Ralph state/progress/handoff,
   and self-contained run evidence. Sharpen the next one or two Not Started slices using only the
   already-open Epic 009 source/digest material.
6. Run focused backend tests with the mandated Ralph virtualenv, save RED/GREEN logs, then run the
   impacted disbursement/communication tests, Django check, migration-sync check, and Ruff. Do not
   run the full backend suite or coverage; the orchestrator owns those authoritative gates.
