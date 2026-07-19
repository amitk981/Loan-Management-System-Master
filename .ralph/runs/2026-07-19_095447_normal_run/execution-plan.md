# Execution Plan

Selected slice: 009L3-epic-009-authority-evidence-and-pagination-closure

## Delivery boundary

- Work only in the existing SAP, loan-account, disbursement-workspace, initial-payment-posting,
  Loan Account 360, and MP14 seams named by the selected slice.
- Preserve the public mutation owners as authority: workspace selectors/actions will call or share
  their exact role, permission, governed-authority, assignment, and current-evidence predicates.
- Preserve Epic 010 ownership: servicing tabs remain visible but explicitly unavailable, with no
  repayment, interest, monitoring, default, or closure fixtures/calculations.
- Do not add SAP posting confirmation governance, an actor, adapter, provider evidence, or a new
  frontend visual pattern. Initial-payment posting remains pending-only under A-135.

## TDD tracer bullets

1. Convert the three retained architecture-review probes into product regressions, one at a time:
   Credit Manager SAP candidate reachability, governed CFC action parity, and canonical SAP
   completion-evidence rejection. Save each focused RED and GREEN command output.
2. Add public owner-level pagination regressions around denied/incoherent rows at 1, 21, and 101
   rows, covering totals, stable page contents, navigation, out-of-range behavior, nondisclosure,
   and bounded query ceilings. Implement scope/evidence-first selectors before database slicing.
3. Add pending-only posting model/service/serializer regressions, then constrain the database and
   remove acceptance of evidence-free `posted`; extend transfer replay/race assertions to exactly
   one pending posting and no duplicate aggregate.
4. Add the remaining action/evidence drift and frontend interaction matrix incrementally through
   public HTTP/UI seams, including exact create/send/complete/transfer payloads, 400/403/409
   handling, and MP14 explicit-id selection in opposite input orders.
5. Restore the established Loan Account 360 tabs with existing components/classes and unavailable
   Epic 010 bodies; add a focused frontend regression before changing the page.

## Verification and evidence

- Run focused backend tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, plus Django check
  and migration-sync; do not run the complete backend suite or local full coverage.
- Run impacted Vitest files, frontend typecheck, lint, and build. Collect the declared Playwright
  spec when local Chromium is unavailable; the orchestrator owns the twice-run trusted browser
  and PostgreSQL decisions.
- Save red/green and focused gate logs under `evidence/terminal-logs/`, then complete an honest High
  risk assessment, self-review packet with exact `## Result\nPASS`, and final summary. Do not edit
  orchestrator-owned state/progress/status/changed-files or invoke git add/commit/push.
