# Execution Plan

Selected slice: `009B3C-sap-current-evidence-and-adapter-contract-closure`

## Scope and interface

- Keep `sap_workflow.modules.sap_customer_profile.get_customer_code_for_member()` as the sole
  downstream interface returning the immutable `SapCustomerCodeDecision`.
- Deepen the canonical SAP owner so that decision creation reconciles exactly one send audit,
  send workflow, communication, task, completion audit, and completion workflow against the
  retained request, workbook, assignee, member, application, code, action, transition, role/team,
  and replay facts.
- Keep Manual, Fake, and Future behind the existing `SapAdapter` seam. Centralize workbook,
  checksum, reference, result, and idempotency validation so no adapter can weaken the file-first
  contract.
- Preserve all routes, response envelopes, error codes, redaction, capability behavior, model
  ownership/table identity, and schema. Do not touch frontend or protected/source files.

## TDD tracer bullets

1. RED: add a public-decision probe that mutates the retained send assignee audit fact and proves
   the existing decision incorrectly remains present. GREEN: reconcile the complete send tuple in
   the SAP owner and save red/green terminal output.
2. RED/GREEN incrementally extend the same public-interface matrix across every retained safe
   send/completion field and each singular linked ledger, including duplicate or cross-linked
   communication/task/workflow rows. Verify genuine create/send/download/complete/reuse decisions
   remain current and invalid evidence exposes no decision fields.
3. RED: replace the happy-only adapter test with one shared Manual/Fake/Future contract covering
   exact replay, malformed checksum, non-XLSX bytes, changed request/file/assignee/key facts,
   malformed references/results, and a rejecting/bypass-attempt Future transport. GREEN: add the
   minimal centralized validation and in-adapter replay ledger; prove denials are zero-write and do
   not invoke a Future transport twice.
4. Run the focused SAP request/repair tests with the mandated Ralph Python interpreter, then Django
   check and migration-sync. Run frontend lint, typecheck, tests, and build because they remain
   configured repository gates, while leaving the authoritative full backend coverage run to the
   orchestrator.

## Evidence and closeout

- Save red/green and focused-gate logs under `evidence/terminal-logs/`, plus a sanitized singular
  ledger manifest, adapter contract summary, public flow/denial summary, and dependency graph.
- Review the final diff for secrecy, exact error taxonomy, imports, schema drift, and configured
  limits. Write `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and
  `final-summary.md`.
- Update the Epic 009 digest, assumptions only if needed, Ralph progress/state/handoff, the selected
  slice status/checklist, and sharpen the next one or two eligible Not Started slices using only
  source material already opened.
