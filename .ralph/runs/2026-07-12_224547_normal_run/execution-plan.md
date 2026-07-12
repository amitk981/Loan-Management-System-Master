# Execution Plan

Selected slice: 006Y13-member-mutation-success-interaction-closure

1. Add failing mounted interaction tests that drive the production `App` Member Directory registration
   route into Member Profile and prove successful create, ordinary PATCH, protected-identity request,
   and checker approval each use an exact single mutation followed by one canonical detail GET.
2. Seed deliberately conflicting mutation/canonical response display values and assert only the masked,
   canonical server response renders; retain the existing 400/403/409 matrices unchanged.
3. Extend `e2e/member-governance-variants.e2e.spec.ts` request instrumentation to record and assert exact
   method, URL, body, ordering, and canonical reads for create/update/request/approval, including the
   backend-projected enabled six-field checker action before approval.
4. Make the smallest production-container correction required by the failing tests, without changing
   the approved visual composition or adding client-side authority/state calculations.
5. Run focused red/green tests, browser collection, and all configured frontend/backend gates; save
   terminal evidence and the request-ledger artifact. Trusted browser execution and five screenshots
   remain the orchestrator's declared localhost acceptance gate.
6. Complete the Ralph evidence packet, changed-file/risk/review/final artifacts, update the selected
   slice/state/progress/handoff, and sharpen the next one or two eligible Not Started slices using only
   the epic digest/source material already opened.
