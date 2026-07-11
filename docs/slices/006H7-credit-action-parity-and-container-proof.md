# Slice 006H7: Credit Action Parity and Container Proof

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Finish 006H6's unimplemented contract by deriving every credit resource action from the exact
public write predicate and proving the default workbench's complete HTTP interaction matrix.

## Depends On
- 006H6
- 006G5

## Source / Review References
- `docs/source/codebase-design.md` §12.3, §23.3-§23.6, §26.3, §36.1, and §42.2-§42.3
- `docs/source/api-contracts.md` §22-§24 and §44
- `docs/source/auth-permissions.md` §25.3 and §34.4
- `docs/source/functional-spec.md` M04-FR-004 through M04-FR-011
- `docs/adr/ADR-0005-approval-case-module-owns-sanction-handoff.md`
- `docs/slices/006H6-workbench-action-projection-and-interaction-proof.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-11_212738_architecture_review`

## Scope

- Give eligibility, loan-limit, and appraisal modules one reusable transition-evaluation result per
  public mutation; both action projection and write execution must consume it. Do not maintain a
  second state/permission heuristic merely because it sits inside the same module.
- Eligibility and loan-limit projections must match formal-reference, complete-documentation,
  credit-stage, object-scope, stored eligible prerequisite, appraisal-started, and permission
  gates. Appraisal create/update/revalidate/submit/review/reject/return/sanction projections must
  match risk authority, provenance, maker-checker, Credit Manager role, object scope, immutable
  history consistency, rejection facts, and exact state gates used by the writes.
- Preserve full six-field actions and exact disabled reasons. Add a backend state/role/object matrix
  that invokes the public write corresponding to each projection and proves enabled succeeds while
  disabled fails without success evidence.
- Add the standard pinned Testing Library packages if absent, then mount the default exported
  `AppraisalWorkbench` with mocked authenticated HTTP. Do not substitute server-rendered child
  markup, raw-source assertions, or a hand-projected view for the required container boundary.
- Remove React's parallel `canEdit`/`canSubmit`/`canRevalidate`/`canReview`/`canSanction` workflow
  matrix. Controls consume the matching backend action's `enabled` fact and intersect its declared
  permission/role with `/auth/me` only as a usability guard; status/provenance must not independently
  re-decide whether a mutation is available.
- Preserve the canonical four-read reload, one-call stale behavior, writable appraisal allowlist,
  response-only field exclusion, ADR-0005 dependency direction, and the empty sanction route.

## Test Cases

- Backend parity covers missing/wrong reference/stage/completeness, absent/ineligible eligibility,
  later appraisal/sanction state, draft/legacy/review-pending/reviewed/returned/rejected states,
  maker-checker self-review, wrong role, missing permission, out-of-scope object, inconsistent
  history, and conditional rejection fields.
- Mounted default-container tests select an application and click eligibility, limit, appraisal
  create/update/revalidate/submit, reviewed/returned/rejected decisions, and sanction; assert exact
  URL/body/count plus one eligibility/limit/appraisal/sanction-case reload after each success.
- Assert refreshed IDs/status/action reasons render, response-only fields never enter PATCH,
  field-level `400`, out-of-scope `403`, absent/disabled actions, and one-call `409` with no retry or
  automatic refresh.
- Existing full backend/frontend gates and the relative-import repository scan remain green.

## Evidence Required

Failing-first service-parity and mounted-container output, green backend matrix, green Testing
Library interaction matrix, exact HTTP examples, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every advertised enabled action is accepted by the corresponding public service for the same
  actor/resource, and every disabled projection explains the matching rejection.
- The production container—not a child or source-text proxy—proves every mutation, refresh,
  denial, validation, and stale path.

## Run-Ahead Sharpening Review (005E4, 2026-07-11)

- Apply codebase-design §§23.3-23.5 and API §44 exactly as proven by 005E4: every default-container
  control must retain the full backend action object, and `/auth/me` permission/role intersection is
  usability only. A disabled or absent backend action must remain non-invokable even when the actor
  has a matching global permission.
- The mounted interaction matrix must count the mutation and each canonical post-success read; a
  `403`, `400`, or `409` response is evidence only when it traverses the real API client/container
  error boundary and proves no retry or optimistic workflow synthesis.
