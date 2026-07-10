# Slice 006H2: Workbench Action Contract Hardening

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Make every Appraisal Workbench action executable through the real container, send only writable
request fields, and consume canonical server state/case identity without local workflow synthesis.

## Depends On
- 006G2

## Source / Review References
- `docs/source/codebase-design.md` §23.3-§23.6 and §26.3
- `docs/source/api-contracts.md` §22-§25
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/006H-eligibility-appraisal-frontend-integration.md`
- `docs/working/REVIEW_FINDINGS.md` entry for this review

## Scope

- Introduce one explicit response-to-draft projection that includes only writable appraisal and
  nested risk fields. Never place response-only IDs, frozen snapshots, status, reviewer, history,
  TAT, or rejection/case summaries in the PATCH body. Returned and ordinary draft edits must save.
- Load the 006G2 pending-case summary on navigation/reload and consume returned
  application/appraisal statuses exactly. Remove hard-coded post-submit status mutations and retain
  the case UUID for Epic 007 navigation.
- Render actions from backend `available_actions` plus `/auth/me` usability checks. Correct the
  revalidation gate to require the backend-provided legacy-unverified action; do not reuse the
  submit-review permission. Eligibility, limit, create/edit, review/return/reject, revalidate, and
  sanction controls must disappear or be disabled when the server says unavailable.
- Reuse existing shared authenticated request/envelope behavior rather than adding another shallow
  fetch implementation; preserve one-call stale `409` behavior and field-level errors.

## Test Cases

- UI behavior tests mount the real container with mocked HTTP, click every action, and assert exact
  URL/body plus state refresh. Include returned PATCH, rejection conditional fields, revalidation
  authority, sanction response/read reload, malformed/error envelopes, and no retry after `409`.
- Permission/available-action matrix covers Deputy Manager Finance, Credit Manager, zero
  permission, object denial, and stale state.
- Regression asserts writable projection keys exactly and rejects response-only fields.
- Static no-mock/no-formula checks remain, but do not substitute for interaction tests.

## Sharpened UI Contract Details

- The writable appraisal projection is an allowlist of borrower/eligibility/loan-limit/security
  summaries, recommendation terms, repayment-capacity notes, recommendation, and nested risk
  ratings/mitigation only. IDs, prerequisite snapshots/provenance, status, TAT, reviewer/comments,
  history, rejection summary, pending case, and `available_actions` are never PATCHed.
- The real workbench container must cover loading, error, unauthorized/object-denied, validation,
  stale `409`, success, returned-draft, and sanction-reload states using only existing alert,
  checklist, calculator, panel, badge, and page patterns from the binding frontend rules.
- On sanction success and reload, display/navigate with the exact 006G2 case UUID and server statuses;
  do not derive a status from the clicked action or retain a client-only case identifier.

## Evidence Required

TDD red/green interaction output, exact request examples, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Existing and returned draft edits succeed with strict backend validation.
- No workflow status or pending case identity is synthesized or lost in React.
- Tests execute the real container/action path rather than only static markup.
