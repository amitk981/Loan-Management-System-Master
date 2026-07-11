# Slice 006H6: Workbench Action Projection and Interaction Proof

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Finish 006H4's unimplemented contract: derive authoritative resource actions behind the credit
module boundary from the real transition gates, preserve the full action objects in React, and
prove every default-container action through mocked HTTP and refreshed state.

## Depends On
- 006H4
- 006G4

## Source / Review References
- `docs/source/codebase-design.md` §6.3, §23.3-§23.6, §26.3, §36.1, and §42.2-§42.3
- `docs/source/api-contracts.md` §24 and §44
- `docs/slices/006H4-workbench-authoritative-actions-and-container-tests.md`
- `docs/working/REVIEW_FINDINGS.md` entry for architecture review `2026-07-11_135129_architecture_review`

## Scope

- Remove credit workflow/action decisions from `applications.views._credit_action_snapshot`.
  Public credit/approvals module results must attach the six-field §44 projection using the same
  application/resource/role/permission predicates as the action they describe, not a second
  key-name heuristic in the HTTP adapter.
- Disabled actions remain present with their exact `disabled_reason`, `required_permission`, and
  `required_role`; React retains typed `AvailableAction` objects through rendering and does not
  flatten them to enabled strings or recreate state/role rules.
- Eligibility and loan-limit rerun actions must be disabled after their service preconditions stop
  applying (including incomplete/wrong-stage/no-reference and later appraisal/sanction states).
  Appraisal create/update/revalidate/submit/review/reject/return/sanction actions must match the
  corresponding backend service outcomes for draft, legacy, pending, reviewed, rejected, returned,
  and submitted resources.
- After every successful mutation, the default container performs the canonical four-way reload
  (eligibility, loan limit, appraisal, sanction case) and renders returned IDs/status/action facts.
  A stale `409` performs exactly one mutation request and no automatic retry.
- Preserve 006H2's writable allowlist and field errors plus 006G3's exact case, review-decision,
  and workflow-event identities. Do not change visual composition; 006H3 owns fidelity.

## Test Cases

- Mount the default exported `AppraisalWorkbench` with Testing Library and a mocked authenticated
  HTTP interface; select an application and click eligibility, limit, create/update, legacy
  revalidate, submit-review, reviewed/returned/rejected decisions, and sanction.
- Assert every exact URL/body, mutation count, four-read refresh, visible success/error, and
  refreshed canonical state. Assert response-only appraisal fields never enter PATCH.
- Cover Deputy Manager Finance, Credit Manager, zero permission, out-of-scope `403`, missing and
  disabled resource actions, returned draft, legacy repair, conditional rejection fields, and
  stale `409` with no retry.
- Backend matrix compares every projected enabled/disabled result with the corresponding public
  service acceptance/rejection across the source states.

## Evidence Required

Failing-first real-container output, backend action/service parity matrix, green interaction log,
exact HTTP examples, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- No HTTP view or React page owns a competing workflow/action matrix.
- Every workbench action is proven through the real container and mocked HTTP boundary, including
  refresh, denial, validation, and one-call stale behavior.

## Run-Ahead Sharpening Review (006G4, 2026-07-11)

- Keep the public dependency direction proven by 006G4: approvals may consume only the documented
  appraisal-workflow handoff; action projection work must not add a credit-to-approvals import or a
  second approvals-to-private-credit edge.
- The backend parity matrix and mounted-container HTTP tests are both mandatory and distinct; keep
  the exact four-read refresh and single-request stale-write assertions already specified.
