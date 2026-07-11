# Slice 006X2: Credit Action Predicate and Container Closure

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Deliver the predicate-parity and mounted-container contract that 006H7 was marked complete without
implementing, so every advertised credit action agrees with its authoritative write and every
workbench mutation/error path is exercised through the default HTTP container.

## Depends On
- 006X

## Source / Review References
- `docs/source/api-contracts.md` §22-§24 and §44
- `docs/source/auth-permissions.md` §25.3 and §34.4
- `docs/source/codebase-design.md` §12.3, §23.3-§23.6, §26.3, §36.1, and §42.2-§42.3
- `docs/source/functional-spec.md` M04-FR-004 through M04-FR-011
- `docs/adr/ADR-0005-approval-case-module-owns-sanction-handoff.md`
- `docs/slices/006H7-credit-action-parity-and-container-proof.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-11_230238_architecture_review`

## Scope

- Replace eligibility and appraisal action heuristics with reusable transition evaluations consumed
  by both projection and the matching public write. Complete the existing loan-limit evaluator so
  permission, object scope, locked source facts, and concurrent re-checks cannot diverge between
  the action response and write boundary.
- Cover eligibility run; loan-limit calculate; appraisal create/update/revalidate/submit-review;
  reviewed/returned/rejected decisions; and sanction submission. Preserve ADR-0005: approvals owns
  sanction case/event creation and may call only credit's public handoff/evaluation seam.
- Each six-field action must expose the exact permission, required role, enabled fact, and stable
  disabled reason returned by the corresponding evaluation. The write remains authoritative and
  re-evaluates after its canonical locks; disabled writes create no success state/audit/workflow/
  rejection/case evidence.
- Replace the static child/source-string substitute with pinned Testing Library tests that mount
  the default `AppraisalWorkbench`, mock the authenticated HTTP boundary, select a real resource,
  click every named mutation, and observe the canonical four-read refresh.
- Preserve the exact appraisal PATCH allowlists, one-call `400`/`403`/`409` behavior, disabled-reason
  rendering, empty sanction route, and ADR-0005 dependency scan. Do not redesign the restored UI.

## Test Cases

- Backend matrix pairs every projected action with its public write across reference, completeness,
  eligibility, appraisal/sanction state, provenance, maker-checker, role, permission, object scope,
  immutable-history consistency, rejection-field, and concurrent-change cases.
- Mounted default-container tests click eligibility, limit, create/update/revalidate/submit,
  reviewed/returned/rejected decisions, and sanction; assert exact URL/body/count and exactly one
  eligibility/limit/appraisal/sanction-case read after each successful mutation.
- Container tests prove response-only fields never enter PATCH, absent/disabled actions cannot be
  invoked, field `400`, scope `403`, and stale `409` render without retry, optimistic synthesis, or
  automatic refresh.
- Existing PostgreSQL race tests and package-aware dependency scan remain unchanged and green.

## Evidence Required

Failing-first predicate/container logs, green backend parity matrix, green mounted interaction
matrix, exact HTTP examples, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every enabled action succeeds for the same actor/resource at its authoritative boundary, and
  every disabled action explains the same rejection without success evidence.
- The default production container proves every promised mutation, refresh, denial, validation,
  and stale path through mocked authenticated HTTP.
