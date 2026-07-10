# ADR-0005: Approval-Case Module Owns the Sanction Handoff

## Status
Accepted

## Context

Slice 006G added the first pending sanction `ApprovalCase`, but
`credit.modules.appraisal_workflow` imports and persists the concrete `approvals.ApprovalCase`
model. That creates the reverse of the documented dependency direction (`approvals -> credit`) and
places approval-case uniqueness, persistence, and future read/enrichment behavior inside the credit
module. Epic 007 must add matrix selection, approver snapshots, actions, decisions, and registers;
leaving the concrete import in credit would spread approval invariants across both apps.

The frontend also needs one durable read of the pending case after reload. A POST-only response is
not a sufficient interface for Epic 007 navigation, and the client must not reconstruct application
or appraisal status locally.

## Decision

The approval-case module owns pending sanction-case creation, uniqueness, persistence, and case
summary reads. Its small interface accepts a reviewed-appraisal handoff from the credit module and
returns the canonical case/application/appraisal statuses and IDs. Later Epic 007 enrichment must
extend the same module and the same unique row.

The credit module continues to own appraisal validation, frozen facts, review-history consistency,
and the application -> appraisal -> review-history lock order. It exposes those behaviors through
its module interface; it does not import or mutate a concrete approvals model. The approvals module
may depend on the credit interface, consistent with `docs/source/codebase-design.md` §36.2.

HTTP views remain thin adapters. They may compose the two module interfaces inside the owning
transaction, but they do not query either concrete model or reproduce workflow rules. A subsequent
read returns the same pending case UUID and backend-owned statuses that the submission returned.

## Consequences

- Corrective slice `006G2-sanction-handoff-module-and-read-contract` removes the concrete reverse
  dependency, preserves the established lock order, and adds the reload-safe case summary.
- Slice 007B enriches the existing case through the approval-case module; it must not introduce a
  second create path or duplicate row.
- Frontend code consumes returned/read statuses and `available_actions`; it does not synthesize
  approval, application, or appraisal state.
- Transaction and PostgreSQL race tests use the module interface as their test surface.
