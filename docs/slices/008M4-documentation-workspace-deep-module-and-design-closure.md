# Slice 008M4: Documentation Workspace Deep-Module and Design Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package

## Depends On
- 008M3

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Restore a small S26-S35 projection interface over deep legal/security owners, bounded queue reads,
the shared frontend transport, and the approved prototype layout without changing business truth.

## Source / Review References

- `docs/source/codebase-design.md` §§6-7, 14-15, 23, 27, 36-37, and 42
- `docs/source/screen-spec.md` S26-S35
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/008M2-documentation-workspace-contract-and-visual-closure.md`
- `docs/slices/008M3-documentation-workspace-executable-action-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_072819_architecture_review`

## Concrete Requirements

1. Decompose the broad `staff_documentation_workspace` implementation behind one stable public read
   interface and narrow owner projections. Legal, security, bank, approval, template, and identity
   decisions remain in their existing deep modules; the workspace must not infer authority by
   exception-class name or query their tables to recreate policy.
2. Move queue filtering/counting/pagination into a bounded selector. Do not lock/serialize every
   checklist merely to return one page, do not serialize a full detail workspace per queue row, and
   add a query ceiling that remains stable as inaccessible/off-page rows grow.
3. Remove arbitrary `.first()` identity selection (including Company Secretary attorney choice).
   Consume a governed owner/configuration selector or return an honest blocker until one exists.
4. Reuse `authenticatedRequest`/`authenticatedPaginatedRequest` and the shared envelope/error/
   request-id handling in `authSession.ts`; documentation code owns DTO mapping only.
5. Remove the new four-column facts grid and any other 008M2 layout invention. Place required S26
   facts in the already-approved queue/card/table patterns without changing colours, typography,
   spacing, card, badge, table, or responsive layout vocabulary.
6. Preserve 008M3 action behavior, download capabilities, exact pagination, truthful states,
   redaction, and screenshots. This slice is structural/design correction, not new workflow scope.

## Trusted Browser Acceptance

- Spec: `e2e/staff-documentation-workspace.e2e.spec.ts`
- Screenshot: `documentation-checklist-blockers.png`
- Screenshot: `documentation-security-workflow.png`
- Screenshot: `documentation-restricted-state.png`
- Screenshot: `documentation-final-approval.png`
- Screenshot: `documentation-checklist-narrow.png`

## Test Cases

- Dependency/AST guards prove the coordinator calls owner interfaces and does not query forbidden
  owner models or catch authorisation by class-name string.
- Query-count tests cover large mixed-scope queues, off-page rows, exact final pages, and detail read.
- Frontend source tests prove use of the shared authenticated transport and absence of a local
  envelope/auth implementation.
- Trusted-browser screenshots preserve the existing prototype composition at desktop and narrow
  viewport; focused behavior tests remain unchanged.

## Evidence Required

Before/after dependency map, query-count results, focused backend/frontend tests, shared-client source
guard, twice-run trusted-browser screenshots, diff/readability report, and full configured gates.

## Risk Level
High

## Acceptance Criteria

- The workspace is a bounded shallow composition over deep owners, not a second policy owner.
- Queue cost is page-bounded, identities are governed, and frontend transport/layout follow existing
  shared seams and prototype patterns.
- 008M3 behavior and all configured gates remain green.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
