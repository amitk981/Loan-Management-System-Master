# Slice 006G2: Sanction Handoff Module and Read Contract

## Status
Complete

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Move pending sanction-case ownership behind the approvals module interface and provide one
reload-safe backend contract for the canonical case and submitted statuses.

## Depends On
- 006F4

## Source / Review References
- `docs/source/codebase-design.md` §12.3, §13.1, §22, §25, §26, and §36.2
- `docs/source/api-contracts.md` §3, §6-§8, §24.5, and §25.2
- `docs/source/data-model.md` §15.3, §30, and §34
- `docs/adr/ADR-0005-approval-case-module-owns-sanction-handoff.md`
- `docs/working/ASSUMPTIONS.md` A-059/A-060
- `docs/working/REVIEW_FINDINGS.md` entry for this review

## Scope

- Add one deep approvals module interface that owns pending-case create/get, unique application and
  appraisal linkage, serialization, and the later 007B enrichment seam. Remove the credit module's
  concrete `approvals.ApprovalCase` import and preserve the existing public HTTP action and atomic
  application -> appraisal -> history -> case lock order.
- Return backend-owned `application_status`, `appraisal_status`, `submission_status`, case UUID,
  latest review-decision UUID, workflow-event UUID, actor/time, exception flag, and applicable
  `available_actions` from a successful submission. Do not expose remarks or frozen free text.
- Provide an authenticated, object-scoped subsequent read—either an approvals-owned pending-case
  summary composed into the appraisal read or a dedicated §25.2-style read—returning the same case
  UUID and canonical statuses after reload. Missing case is a standard `404`; denied scope is the
  existing `403` envelope.
- Catch malformed/non-object JSON at the submit adapter and return the standard `400
  VALIDATION_ERROR` envelope. Preserve exact `{ remarks }`, no automatic retry, and duplicate-call
  `409` behavior.
- Keep matrix evaluation, approver assignment/actions, exception decisions, and registers in Epic
  007; 007B enriches this same row through the new module interface.

## Test Cases

- Module/API tests prove create/read return identical IDs/statuses, malformed JSON is enveloped,
  response metadata contains the state transition and workflow event, and free text is absent.
- Permission, Credit-Manager role, object scope, missing case, repeated submission, and forced
  case/audit/workflow failures have precise codes and no partial writes.
- Static dependency test rejects `credit -> approvals.models` imports; transaction tests call the
  module interface and retain the PostgreSQL duplicate-submission proof from 006F4.

## Sharpened Contract Details

- The submit adapter remains `POST /api/v1/loan-applications/{id}/submit-to-sanction-committee/`
  with exactly one trimmed, non-blank `remarks` field; malformed JSON, arrays, and unknown keys are
  `400 VALIDATION_ERROR` and create no case, audit, or workflow row.
- Both submit and reload projections return the same `approval_case_id`, `loan_application_id`,
  `loan_appraisal_note_id`, latest review-decision UUID,
  `application_status = submitted_to_sanction_committee`,
  `appraisal_status = submitted_to_sanction_committee`, and pending case status.
- The approvals module owns case create/get/serialization and returns the created workflow-event
  UUID; credit may consume that interface but must not import `approvals.models`.
- After the approvals-module extraction, rerun the exact 006F4 five-race PostgreSQL command twice;
  SQLite skips or collection without execution do not preserve the concurrency acceptance.

## Evidence Required

TDD red/green output, API examples for POST/read/error paths, dependency graph/static check, and all
configured gates.

## Risk Level
High

## Acceptance Criteria

- Approval-case complexity disappears behind one approvals-owned interface.
- A reload can recover the exact pending case and statuses without client synthesis.
