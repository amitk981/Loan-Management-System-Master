# Execution Plan

Selected slice: `009B3B-sap-policy-adapter-and-dependency-closure`

## Outcome

Make `sap_workflow.modules.sap_customer_profile` the deep owner of SAP request creation,
Annexure-I rendering/encrypted retention, manual delivery, one-use download capabilities,
completion/reuse, safe reads, and Manual/Fake/Future adapter policy. Preserve the 009B2 HTTP,
storage, audit, workflow, idempotency, secrecy, and concurrency contracts without schema changes.

## Interface and seam

- Keep the existing public SAP functions/class as the caller and test interface.
- Keep the external-system seam in `sap_workflow.adapters`; exercise Manual and Fake adapters
  against one contract and retain the replaceable Future contract.
- Let Finance views and any legacy imports point one way into the public SAP owner only. Finance
  compatibility modules may forward names but may not query models, decide policy, store/read
  workbooks, issue capabilities, or invoke adapters.

## TDD tracer bullets

1. Add a dependency-graph/public-owner test that fails while executable `sap_workflow` imports
   Finance and proves behavior is reached through the SAP interface.
2. Move request creation and Annexure rendering/storage into the SAP owner; run the focused request
   tests green before proceeding.
3. Move send, delivery capability/read, completion/reuse, and member-code reads; run each focused
   public behavior group green as it moves.
4. Add/extend the shared Manual/Fake adapter contract and graph/downstream selector checks; make
   Finance compatibility imports one-way and policy-free.
5. Align touched stale/conflict responses to the standard taxonomy while preserving actionable
   details and route/status compatibility.

## Verification and evidence

- Save the initial failing dependency/public-interface output and incremental/final green output in
  `.ralph/runs/2026-07-16_201643_normal_run/evidence/terminal-logs/`.
- Run focused SAP request/repair, model-identity, loan selector, and disbursement selector tests with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run the declared SAP PostgreSQL race set twice with the repository PostgreSQL test settings.
- Run Django check and migration sync. Run impacted frontend tests/typecheck/lint/build only if the
  preserved HTTP contract requires frontend changes; no frontend change is currently expected.
- Record the final import graph, changed files, risk, traceability/review packet, final summary,
  state/progress/handoff, selected-slice completion, and sharpen the next two Not Started slices
  using already-open Epic 009 material.
