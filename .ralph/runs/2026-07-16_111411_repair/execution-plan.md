# Execution Plan

Selected slice: 009B2-sap-delivery-replay-audit-and-owner-seam-closure

## Repair diagnosis

- The newest available `failure-summary.md` is the older 008M3 browser failure and is not a
  009B2 gate result. This worktree is otherwise clean, so this run repairs the two executable SAP
  contract failures retained by the 2026-07-16 architecture review.
- Feedback loop: the retained delivery probe currently proves a `sent` request gives its frozen
  assignee no workbook read path; the retained replay probe currently proves optional fields can
  be added to a reused-code completion and still receive HTTP 200.

## Implementation sequence

1. Copy the two review probes into focused 009B2 regression tests, add adapter/capability/audit and
   dependency-guard assertions, run them with the required Ralph Python interpreter, and save the
   failing output under `evidence/terminal-logs/`.
2. Add one Finance compatibility migration for immutable delivery identity/checksum/capability
   state and the canonical completion-input digest while preserving the applied SAP tables/data.
3. Establish `sap_workflow.modules.sap_customer_profile` as the public policy seam plus a manual
   `SapAdapter` implementation. Route the existing HTTP endpoints through that owner and leave the
   existing Finance modules as compatibility forwards only where required by older callers/tests.
4. Make send verify/decrypt the retained Annexure-I, require adapter acceptance, persist delivery
   identity, and expose an assignee-only short-lived one-use/replacement capability and audited
   checksum-verified workbook read. Keep the manual task body free of file ids, secrets, and tokens.
5. Persist and compare the canonical completion digest for both create and reuse, align new-code
   audit vocabulary to `sap.customer_code_created`, emit explicit reuse/read/denial truth with
   frozen role/team/request/network context, and keep all loser paths zero-write.
6. Run focused tests to green and save output, then run Django check, migration drift, full backend
   coverage, and the configured frontend build/typecheck/lint/test gates.
7. Update API contracts, Epic 009 digest/traceability, assumptions only if needed, slice status,
   state/progress/handoff, and all Ralph review/evidence artifacts. Sharpen the next one or two
   `Not Started` slices only from source material already opened, then verify diff limits and
   protected paths before handoff to the orchestrator.
