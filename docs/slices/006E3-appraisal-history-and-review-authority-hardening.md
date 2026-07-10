# Slice 006E3: Appraisal History and Review Authority Hardening

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Close architecture review `2026-07-10_190455_architecture_review` by making legacy prerequisite
provenance genuinely evidence-backed, retaining every Credit Manager review reason, and enforcing
the source's Credit-Manager-only reviewer rule.

## Depends On
- 006F2

## Source / Review References
- `docs/source/api-contracts.md` §3, §24.4
- `docs/source/auth-permissions.md` §19.2, §25.3, §34.4
- `docs/source/functional-spec.md` §9.8 and M04-FR-010/M04-FR-011
- `docs/source/codebase-design.md` §12.3, §22.1, §26.1-§26.3
- `docs/source/data-model.md` §14.1-§14.4 and §34
- `docs/source/test-plan.md` MOD-APPRAISAL-004 through MOD-APPRAISAL-007
- `docs/adr/ADR-0003-freeze-appraisal-prerequisite-projections.md`
- `docs/adr/ADR-0004-append-only-appraisal-review-decisions.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_190455_architecture_review`

## Scope

- Add one immutable appraisal-review decision record per successful `reviewed`, `returned`, or
  `rejected` action. Store appraisal, decision, non-blank review comments, reviewer, decided time,
  and from/to states. Keep current fields on `LoanAppraisalNote` as the latest-decision projection.
- Create the history row inside `AppraisalWorkflow.review(...)` in the same transaction as the
  appraisal transition, optional rejection note, audit row, and workflow event. Audit/workflow JSON
  records the decision-record ID but never the free-text comments or detailed rejection reason.
- Require both `credit.appraisal.review` and actual `credit_manager` role membership. Permission
  assignment to another role, application ownership, or intake receipt must not confer reviewer
  authority. Preserve Credit Manager access to all applications in the credit-assessment domain and
  distinct `PERMISSION_DENIED` versus `OBJECT_ACCESS_DENIED` behavior.
- Correct legacy prerequisite proof with a forward data repair. A `verified` appraisal is safe only
  when both exact prerequisite IDs have their required success audit at or before `prepared_at`, no
  later success audit exists, both source timestamps are at or before preparation, and IDs belong to
  the same application. Any row lacking that positive chronology becomes `legacy_unverified` and is
  downstream-blocked until the existing scoped revalidation action succeeds. Preserve untrusted
  copied JSON for investigation, but never treat it as verified input.
- Backfill at most the latest known review decision for existing reviewed/returned/rejected rows and
  label it as legacy latest-only provenance. Do not invent missing earlier cycles.
- Update the stale top-level appraisal row in `docs/working/API_CONTRACTS.md` and the Epic 006 digest
  so summaries agree with the detailed implemented contract.

## Database / Migration Safety

- One additive migration may add the review-decision table and perform both conservative data
  repairs. It must be reversible where data semantics permit and must not rewrite assessment UUIDs,
  frozen projections, rejection notes, or current appraisal decision facts.
- Use indexed appraisal/decision-time access and source §30 naming conventions. Do not add sanction
  or approval tables.

## Test Cases

- Return, maker revision, resubmit, and final review leave two immutable decision rows; the original
  return reason/reviewer/time remain exact while the appraisal projects the latest review.
- Reviewed and rejected paths each create exactly one history row; rejection history, rejection
  note, appraisal, audit, and workflow writes roll back together on every forced failure.
- A non-Credit-Manager application owner holding `credit.appraisal.review` receives `403` and writes
  no decision/history/evidence; a scoped Credit Manager with the permission succeeds.
- Migration fixtures cover: both positive pre-appraisal audits, missing one/both audits, later rerun
  audit, source timestamp after preparation, mismatched application/ID, and existing legacy-
  unverified rows. Only positive proof remains `verified`.
- Generic audit/workflow evidence contains decision/history IDs and metadata but no review comments,
  return reason, detailed rejection reason, or frozen financial/risk free text.

## Evidence Required

TDD red/green logs, forward/reverse migration proof, before/after legacy provenance examples,
multi-review history API examples, authority matrix output, and all standard gates.

## Risk Level
High

## Acceptance Criteria

- No appraisal is called historically verified without positive audit chronology for both inputs.
- Credit Manager review cannot be exercised by another role through permission or ownership alone.
- Every review reason survives later review cycles outside generic audit JSON.
- The public appraisal module remains the only mutation seam.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing tests and red evidence saved first
- [ ] Additive migration and data repair implemented
- [ ] Review authority and append-only history implemented
- [ ] API contracts and Epic 006 digest updated
- [ ] Full gates passed
- [ ] Risk assessment and handoff updated
- [ ] State updated
- [ ] Commit delegated to orchestrator only after passing gates
