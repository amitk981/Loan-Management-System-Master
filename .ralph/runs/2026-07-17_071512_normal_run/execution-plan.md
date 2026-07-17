# Execution Plan

Selected slice: 009E-payment-initiation-by-senior-manager-finance

1. Inspect the existing `disbursements`, loan-account, readiness, identity/permission, audit,
   workflow, and task public seams plus their focused test fixtures. Confirm the current 23-check
   order and the 009D3 canonical scope contract without importing lower-level owners.
2. Add one failing public-service tracer test for a Senior Manager Finance initiation from genuine
   passing readiness. Save RED output before implementing the schema or service.
3. Add the `disbursements` owner model/migration and the shallow public initiation module. In
   incremental RED/GREEN cycles, cover exact replay, changed replay, duplicate/stale/forged inputs,
   role/grant/scope denial, current bank/source evidence, exact ordered readiness digest, safe
   audit/workflow/CFC-task evidence, and zero transfer/account side effects.
4. Add the strict POST serializer/view/route and public API tests for the standard envelope,
   exact payload/header contract, stable errors, and nondisclosing inaccessible ids.
5. Add twice-run PostgreSQL concurrency acceptance proving one complete winner across five
   simultaneous attempts, with no partial loser artifacts. Save race output in the run evidence.
6. Run focused backend tests with the mandated interpreter, Django check, migration-sync check,
   and relevant frontend gates only if touched. Save GREEN, request/response, ledger, migration,
   and check evidence under this run folder.
7. Update the API contract ledger, Epic 009 digest, selected slice status/checklist, Ralph state,
   progress, handoff, changed-files, risk assessment, review packet, and final summary. Sharpen the
   next one or two Not Started slices only if the already-open Epic 009 sources add concrete detail
   beyond their present requirements.

Constraints: no frontend/product-screen work; no external bank call; no CFC authorisation, UTR,
funding, activation, register update, or borrower communication; no protected/source-file edits;
no git add/commit/push; at most one migration and the configured 30-file/2,000-line limits.
