# Execution Plan

Selected slice: 007D-approval-action-api-approve-reject-return

## Scope and public interface

- Add the three source-defined action routes under
  `/api/v1/approval-cases/{approval_case_id}/`: `approve/`, `reject/`, and
  `return-for-clarification/`.
- Accept only the caller's optimistic `version` plus optional `comments`; require non-blank
  comments for reject/return.
- Route every action through one approval-owned transaction boundary. Lock application,
  appraisal, and case in the established order, then re-run the canonical routability,
  object-scope, and pending-actor predicates before writing.
- Persist immutable per-approver action evidence. Partial approvals remain pending; final joint
  approval closes the case and application and creates one source-shaped sanction decision.
  Reject/return close the case in their respective states; return restores the reviewed
  pre-committee application/appraisal state through transition guards.
- Create attributable audit/workflow evidence for the executed action and completion, and notify
  the Credit Assessment Team through the existing notification persistence adapter.
- Return the action identifiers/completion flags together with the canonical approval-case detail
  projection so read and write authority/status/action projections stay identical.

## TDD tracer bullets

1. RED -> GREEN: an assigned, permitted approver records one approval; the immutable action and
   canonical response appear while the joint case stays pending.
2. RED -> GREEN: the final required approval atomically closes the case/application, creates one
   sanction decision from frozen appraisal facts, and records exact audit/workflow/notification
   evidence.
3. RED -> GREEN: reject and return require comments and perform their guarded terminal/clarification
   transitions with no sanction decision.
4. RED -> GREEN: missing permission, object-scope mismatch, excluded/acted/closed state,
   contradictory routing, duplicate action, and stale version all return the canonical error and
   preserve exact action/case/sanction/audit/workflow/notification ledgers.
5. Add the PostgreSQL concurrency acceptance row for simultaneous final approvals, with one
   sanction decision and an exact zero-write loser ledger where the database capability is
   available.

## Schema and documentation

- Extend the existing approval models only where source §15.3/§15.5 fields are absent; add a
  migration with the source unique/index constraints.
- Update `docs/working/API_CONTRACTS.md`, the Epic 007 digest, and record any source-silent mapping
  assumption without changing `docs/source/`.
- Before completion, sharpen the next one or two eligible Not Started slice files using only the
  already-open Epic 007 material.

## Verification and evidence

- Save each focused failing and passing backend command under
  `evidence/terminal-logs/` using `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run focused approval action/routing tests, Django check, migration sync, full backend coverage,
  and the frontend build/typecheck/lint/test gates.
- Save changed-files, risk assessment, review packet, final summary, and update Ralph state,
  progress, handoff, digest, API contract, and selected slice status only after gates pass.
