# Slice 006H4: Workbench Authoritative Actions and Container Tests

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Make resource-level backend actions authoritative in the real Appraisal Workbench and prove every
container action through its HTTP/state boundary.

## Depends On
- 006G3

## Sharpened Integration Anchor (2026-07-11)

- Treat the sanction-case `workflow_event_id` as the durable event identity returned by 006G3;
  container refresh tests must preserve that exact UUID and must not select or synthesize a newer
  application workflow event.

## Source / Review References
- `docs/source/codebase-design.md` §23.3-§23.6 and §26.3
- `docs/source/api-contracts.md` §24 and §44
- `docs/slices/006H2-workbench-action-contract-hardening.md`
- `docs/working/REVIEW_FINDINGS.md` entry for this review

## Scope

- Add an object/state-aware appraisal action projection to the backend read/action responses for
  eligibility run, loan-limit calculate, appraisal create/update, legacy revalidate, submit-review,
  review/return/reject, and sanction submit. Each item uses the standard §44 shape with action code,
  enabled flag, disabled reason, required permission, and required role where applicable.
- In React, treat the selected resource's `available_actions` as authority and intersect it with
  `/auth/me` permissions/roles only for usability. Never union global permission codes into the
  resource action set; an empty/missing resource action list exposes no controls.
- Ensure the real legacy-unverified appraisal response advertises the dedicated revalidation action
  to authorised update+risk users and that the real container renders/calls it.
- Preserve 006H2's writable projection, one-call stale behavior, field errors, four-way reload, and
  canonical case/status identity. Do not change visual composition; 006H3 owns fidelity.

## Test Cases

- Mount the default real `AppraisalWorkbench` container with Testing Library and mocked HTTP; select
  a real application and click every action. Assert exact URL/body, one request for stale `409`,
  subsequent refresh/state, and visible error/success/denied output.
- Cover Deputy Manager Finance, Credit Manager, zero permission, missing/disabled resource action,
  object denial, returned draft, legacy revalidation, conditional rejection fields, and sanction
  response/reload. Tests must fail if `/auth/me` grants a permission while the resource action list
  is empty.
- Keep exact top-level/nested PATCH allowlist assertions and prove response-only fields never enter
  container state sent to PATCH.

## Evidence Required

Failing-first container output demonstrating the current union/revalidation defects, green focused
interaction output, exact HTTP examples, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Resource actions can deny globally permissioned users, and legacy remediation is reachable only
  when the backend explicitly advertises it.
- Tests exercise the real container/action path, not only static markup or API wrappers.
