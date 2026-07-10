# Slice 006E2: Appraisal Source Contract and Snapshot Hardening

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Close architecture review `2026-07-10_173305_architecture_review`: make the appraisal preserve the
exact eligibility/loan-limit decision facts it used, capture source-required repayment-capacity
notes, and retain the required submit-for-review reason before Credit Manager review begins.

## Depends On
- 006E
- 006D2C

## 006D2C Handoff Contract
- `LoanLimitCalculator.calculate_for_application(...)` serializes competing reruns through its
  locked application boundary on PostgreSQL. Do not weaken or bypass that public seam while adding
  appraisal-owned snapshots; the PostgreSQL valid/valid and valid/invalid transaction regressions
  must remain green.
- The canonical loan-limit public projection is internally consistent with the final persisted row
  and final `loan_limit.calculated` audit projection after serialization. Copy that projection at
  appraisal creation; do not rebuild the listed §14.2 fields from concrete models.
- Static boundaries resolve `ast.Import` and `ast.ImportFrom` aliases/package imports, reject
  concrete assessment/policy/private-helper access, and positively require the calculator and
  appraisal public imports. Extend required-method checks by subset only; additional harmless
  public workflow methods must remain allowed.

## Source / Review References
- `docs/source/api-contracts.md` §3 and §24.1-§24.4
- `docs/source/functional-spec.md` §9.8 and M04-FR-008/M04-FR-009
- `docs/source/codebase-design.md` §§12.2-12.3, §26, and §§42.1-42.2
- `docs/source/data-model.md` §14.2-§14.4 and §34
- `docs/adr/ADR-0003-freeze-appraisal-prerequisite-projections.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_173305_architecture_review`

## Backend / API Scope
- At create, persist canonical redacted eligibility and loan-limit projection snapshots owned by
  the appraisal. Retain the two assessment UUIDs as provenance, but never treat a UUID as snapshot
  content or expose a concrete model/FK navigation seam.
- The frozen loan-limit projection must include at least cultivated acreage, share/land/final
  limits, requested amount, within-limit/exception flags, calculation rule version, policy source,
  calculated actor, and calculated time. The eligibility projection must include every named check,
  overall result, assessed actor, and assessed time.
- PATCH, submit, review, and sanction consumers use only these frozen appraisal projections for
  amount/exception and prerequisite decisions. A later successful assessment rerun with the same
  UUID must not change appraisal GET, validation, or downstream behavior.
- Add required non-blank `repayment_capacity_notes`, using the exact functional-spec §9.8 term.
  Preserve recommended amount, tenure, interest/rate basis, and security as the implemented
  M04-FR-008 repayment-term facts; do not invent a second undocumented repayment formula.
- Persist the non-blank §24.3 submit `remarks` on the appraisal (or an appraisal-owned append-only
  submission record) so the compliance-first reason is retained. Audit JSON remains metadata-only:
  record that a reason exists and its owning record ID, not the free text itself.
- Preserve 006D2C's strengthened static boundary regression and positively require appraisal to
  call the public eligibility and loan-limit interfaces; do not reintroduce concrete model access.
- Keep `config.postgres_test_settings` and the PostgreSQL concurrency command documented in the
  review packet whenever this slice changes calculator/appraisal imports or assessment snapshots.

## Database / Migration Safety
- One additive migration may add immutable projection JSON, repayment-capacity, submission-reason,
  and provenance fields/records. No assessment table, UUID, or existing appraisal/risk link changes.
- Existing rows may copy current assessment projections only when audit chronology proves no
  successful rerun occurred after appraisal creation. Otherwise mark provenance
  `legacy_unverified` and block review/sanction until an explicit authorised revalidation pins the
  current public projections with metadata-only audit/workflow evidence.
- Never silently label a current mutable assessment as the historical input of an older appraisal.

## Validation And Permissions
- Create requires non-blank repayment-capacity notes in addition to the existing strict payload.
- Snapshot pin/revalidation, if needed for legacy rows, requires appraisal update plus risk/credit
  scope, is draft-only, and must not change caller-authored recommendation/risk facts.
- Submit still requires `credit.appraisal.submit_review`, a non-blank reason, and draft state.
  Denied/invalid paths leave appraisal, frozen snapshots, submission reason, audit, and workflow
  counts unchanged.

## Test Cases
- Create stores exact public prerequisite projections and returns the new required field without
  sensitive data or mutable model handles.
- After create, successfully rerun eligibility/loan limit under the same UUID with changed facts;
  appraisal GET and amount/exception validation remain tied to the frozen original projection.
- Missing/blank repayment-capacity notes and submit remarks fail with no state/evidence writes;
  successful submit persists the reason outside metadata-only audit JSON.
- Legacy safe-copy and ambiguous-rerun paths are both tested; ambiguous history cannot proceed to
  review until explicit audited revalidation.
- Static import tests remain green and fail if either public projection call is removed.
- Forced audit/workflow failure rolls back create, PATCH/revalidation, and submit writes.

## Evidence Required
TDD red/green logs, immutable-before/after API examples, legacy migration proof, boundary-test
fixtures, and all standard gates.

## Risk Level
High

## Acceptance Criteria
- An appraisal permanently identifies the exact eligibility and financial decision facts it used.
- M04-FR-009 repayment-capacity notes and §24.3 submission reason are persisted and tested.
- No concrete assessment-model coupling or free-text audit leakage is introduced.
- 006F can review only a source-complete appraisal with verified frozen prerequisite projections.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing tests and red evidence saved first
- [ ] Additive migration and implementation completed
- [ ] API contracts updated
- [ ] Legacy provenance paths tested
- [ ] Full gates passed
- [ ] Risk assessment and handoff updated
- [ ] State updated
- [ ] Commit delegated to orchestrator only after passing gates
