# Slice 007M: Exception Supporting Evidence and Register Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007F2
- 007J

## Runtime Capabilities
- `localhost-e2e-server`

## Goal

Make the generated Exception Register carry and display the decision comments and immutable
supporting-document evidence required by S25.

## Source / Review References

- `docs/source/screen-spec.md` S25
- `docs/source/functional-spec.md` M05-FR-006 and BR-028
- `docs/source/api-contracts.md` §§25.2, 25.10, and 26
- `docs/source/auth-permissions.md` §§19.2-19.4 and 25.4-25.5
- `docs/source/data-model.md` §§15.7, 16.1, and §34
- `docs/source/codebase-design.md` §§13.1, 18.1, 23.5, 26.3, and 27.1
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_010536_architecture_review`

## Concrete Requirements

1. Extend the exception-enrichment boundary with an optional bounded list of supporting document
   ids. The documents owner must validate each id as publicly uploaded, attributable to the exact
   application/approval-case exception workflow, and referenceable by the actor under category,
   sensitivity, role, permission, and object scope. The approvals module must not query
   `DocumentFile` directly.
2. Freeze accepted references on the exact Exception Register entry/cycle. Exact enrichment replay
   includes the same ordered ids and is zero-write; changed ids after routing are a conflict, not a
   rewrite. Missing documents remain an honest empty list unless the source route requires one;
   do not invent per-exception-type mandatory-document rules.
3. Project only immutable metadata needed by S25. Register visibility grants no download. A
   download affordance appears only when the existing document resource separately returns an
   enabled action for that file.
4. Render the existing immutable `approval_actions` comments/acted-at facts and the new supporting
   evidence metadata in S25. Keep description and business reason distinct, use server pagination,
   and expose no mutation from the read-only register.
5. Add attributable audit/workflow evidence for initial document association inside the locked
   enrichment transaction; any reference denial is nondisclosing and zero-write.

## Trusted Browser Acceptance

- Spec: `e2e/exception-register-evidence.e2e.spec.ts`
- Screenshot: `exception-register-with-supporting-evidence.png`
- Screenshot: `exception-register-evidence-denied.png`

## Trusted Browser Scenario

- Open the routed S25 panel through an authenticated production app shell. Render a generated
  exception with distinct description/business reason, immutable approver comments/time, and
  supporting metadata; then prove an actor without document action authority sees metadata but no
  download control.

## Test Cases

- Valid same-application evidence, exact replay, cross-application/category/sensitivity/permission
  denials, duplicate ids, and changed-replay conflict with complete zero-write ledgers.
- S25 renders comments/time/evidence and never turns register permission or metadata into download.
- Both trusted screenshots are produced in two independent orchestrator runs.

## Risk Level
High

## Acceptance Criteria

- S25 contains its source-required immutable decision comments and supporting evidence.
- Documents remain owned and authorised by the document boundary.
- Backend TDD evidence, trusted screenshots, and all configured gates pass.
