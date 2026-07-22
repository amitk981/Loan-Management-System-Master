# Execution Plan

Selected slice: `011F-recovery-action-execution-shell`

## Boundary and permissions

- Implement only the prepared 011F recovery-action execution shell. Do not broaden S53-S56/S58+
  frontend wiring or automate external DP, bank, share-sale, SAP, or grievance-resolution work.
- Product edits are limited to `sfpcl_credit/**` and `sfpcl-lms/src/**`; acceptance coverage may edit
  the slice-owned `e2e/recovery-action-execution.e2e.spec.ts` if that path is already part of the
  frontend harness. Run evidence is limited to this run directory.
- `.ralph/permissions.json` permits the backend, frontend, working-doc, and run-evidence paths. The
  protected/forbidden paths from the prompt and decision policy remain untouched.

## Public behaviors, developed vertically

1. Through the recovery workflow public interface, an authorised Company Secretary/recovery user
   can initiate exactly the action named by an approved recovery decision, only with matching usable
   security and evidence; replay is idempotent and all denial/success outcomes are audited.
2. Each approved SH-4, CDSL, or cheque route delegates to its existing security-module owner without
   duplicating custody or invocation policy; owner failure rolls back the recovery action.
3. An initiated action can complete once with a non-negative amount no greater than the outstanding
   loan balance, evidence, timestamps, remarks, and fair-conduct interaction evidence. Completion and
   the canonical recovery-proceeds loan-ledger movement commit atomically; replay/stale losers never
   post twice or partially mutate state.
4. POST initiate/complete APIs expose standard envelopes and authoritative `available_actions`,
   enforce object scope and Critical permissions, and remain read-only/blocked for Credit,
   Committee, Auditor, foreign-security, mismatched, and unapproved cases.
5. The existing S57 area in `DefaultRecoveryHub.tsx` displays the approved action, masked instrument
   status, evidence/checklist, initiate/complete controls, interaction log, grievance route, and
   truthful blocked/success/error/loading states using only existing visual patterns.

## TDD and implementation sequence

- Inspect the existing 011A-011E recovery module, security-owner facades, 010A ledger owner, API
  contracts/routes, frontend hub/client/tests, and existing PostgreSQL/browser acceptance patterns.
- RED→GREEN one externally observable behavior at a time: initiation; each owner route and rollback;
  completion plus ledger atomicity; replay/concurrency; API permission/scope; frontend blocked and
  approved execution paths. Save every focused red/green command output under
  `evidence/terminal-logs/`.
- Add the single schema migration allowed by the run when the model contract requires it. Keep SAP
  explicitly pending unless an existing governed adapter records real acceptance.
- Refactor only while green, preserving existing module/public-interface conventions.

## Focused verification

- Backend: focused recovery orchestration/API/permission/reverse-owner tests, Django system check,
  and migration consistency with `/Users/amitkallapa/LMS/.ralph/venv/bin/python` only.
- PostgreSQL: run the declared three-test label when the configured local database is available;
  otherwise retain the exact test implementation and let trusted validation own execution.
- Frontend: focused Vitest coverage, typecheck, lint, and build; implement and run the declared
  Playwright spec/screenshots when Chromium is available without fabricating evidence.
- Do not run the complete backend suite or global coverage; independent Ralph validation owns the
  authoritative High-risk lane.

## Completion evidence

- Save focused terminal logs, browser screenshots when runnable, `risk-assessment.md`, and a
  source-to-code-to-test traceability review packet.
- Set the review packet Result exactly to `Ready for independent validation` only after focused
  gates are green. Leave state, progress, slice status, changed-files, and mechanical handoff to the
  orchestrator.
