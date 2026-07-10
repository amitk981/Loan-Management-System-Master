# Slice 006G3: Sanction Handoff Dependency and Evidence Ownership

## Status
Not Started

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Remove the credit/approvals dependency cycle and make the approvals-owned handoff atomically own
the pending case and its workflow-event identity as ADR-0005 requires.

## Depends On
- 004E2

## Source / Review References
- `docs/source/codebase-design.md` §12.3, §13.1, §22, §25, §26, and §36.2
- `docs/source/data-model.md` §15.3 and §34
- `docs/source/api-contracts.md` §24.5 and §25.2
- `docs/adr/ADR-0005-approval-case-module-owns-sanction-handoff.md`
- `docs/slices/006G2-sanction-handoff-module-and-read-contract.md`
- `docs/working/REVIEW_FINDINGS.md` entry for this review

## Scope

- Eliminate every production `credit -> approvals` import while retaining the documented
  `approvals -> credit/applications` direction. Move genuinely shared typed errors/access inputs to
  a lower shared seam only if both apps need them; approvals must not import credit-owned error or
  object-access implementations merely to satisfy its public interface.
- Compose the reviewed-appraisal handoff and approvals case creation through the owning module
  boundary/transaction described by ADR-0005. Views remain thin and may coordinate public results,
  but neither view nor credit may query/mutate `ApprovalCase` directly.
- Make the approvals handoff create and return the sanction-submission workflow event together with
  the unique pending case. Submission response and reload must expose that exact event UUID, not a
  later query for the newest event on the application.
- Preserve application -> appraisal -> review-history -> case lock order, canonical response,
  malformed-body behavior, duplicate-call `409`, rollback, and the five PostgreSQL race outcomes.

## Test Cases

- Static dependency tests reject all `credit -> approvals` imports and all approvals imports from
  private credit implementation/error modules; include aliased/package imports.
- Module/API tests assert one case and one exact workflow-event UUID on create/reload, and forced
  case/event/audit failures roll back every state/evidence write.
- Strengthen the five authoritative concurrency assertions to compare exact canonical workflow
  state/reason/decision identity rather than substring-only evidence. Run all five races twice on
  PostgreSQL with zero skips after the seam changes.

## Evidence Required

Dependency graph, red/green module/API output, exact event identity examples, two five-race
PostgreSQL logs, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- The app dependency graph follows §36.2 with no credit/approvals cycle.
- One approvals-owned atomic handoff produces the durable case and exact workflow event.

