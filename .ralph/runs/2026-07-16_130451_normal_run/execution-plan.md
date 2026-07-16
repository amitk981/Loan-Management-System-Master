# Execution Plan

Selected slice: 009D-disbursement-readiness-service

1. Freeze the source contract and inventory the existing loan, SAP, approval, legal-checklist,
   security-instrument, verified-bank, configuration, authentication, and object-scope owner seams.
   Keep the public interface to `evaluate(actor, loan_account_id)` and the exact source §31.1 GET.
2. RED→GREEN tracer bullet: add one authenticated API test for a sanctioned account whose source
   facts are deliberately incomplete. Assert the standard envelope, complete stable check order,
   safe blocker reasons, aggregate false, and zero writes; save the focused RED and GREEN logs.
3. RED→GREEN incrementally add source-owner projections and tests for the fully-ready path, every
   independently flipped mandatory/conditional blocker, SAP/account relationship incoherence,
   configured-source-bank fail-closed behavior, and amount-within-sanction.
4. RED→GREEN add permission and nondisclosure coverage for active persisted Senior Manager Finance
   and CFC actors, exact application/account object scope, missing permission/wrong role/inactive and
   inaccessible ids, plus unknown-query rejection and secret-free responses.
5. Add regression proof that evaluation calls bounded public owner seams, remains read-only across
   retries, and does not create or mutate audit/workflow/account/payment/task/communication/checklist
   truth. Update the API contract ledger and durable Epic 009 digest if implementation clarifies it.
6. Run focused tests after each vertical cycle, then Django check, migration drift, full backend
   coverage, and all frontend build/typecheck/lint/test gates. Save reviewable ready/all-blocked API
   examples, per-check traceability, query/owner-seam evidence, changed-files, risk assessment,
   review packet, and final summary in this run folder.
7. Sharpen the next one or two eligible Not Started Epic 009 slices only from source material already
   opened, then mark only 009D Complete and update Ralph state, progress, and handoff.
