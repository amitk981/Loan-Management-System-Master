# Execution Plan

Selected slice: 006E2-appraisal-source-contract-and-snapshot-hardening

1. Extend the public appraisal contract tests one behavior at a time: required repayment-capacity
   notes and exact redacted prerequisite projections at create; save the initial failure as red
   evidence before implementing.
2. Add one additive credit migration for appraisal-owned eligibility/loan-limit projection JSON,
   provenance verification state, repayment-capacity notes, and submission remarks. Its data step
   copies current historical facts only when audit chronology proves no later successful rerun;
   otherwise it marks the appraisal `legacy_unverified` without claiming mutable current facts.
3. Deepen `AppraisalWorkflow` behind its existing interface: create pins only the public
   `EligibilityAssessmentModule` and `LoanLimitCalculator` projections; GET, PATCH amount checks,
   submit, and future consumers use only the frozen appraisal fields. Add a draft-only authorised
   revalidation action requiring appraisal-update and risk-management scope, preserving all
   caller-authored recommendation/risk fields and emitting metadata-only audit/workflow evidence.
4. Add incremental public-interface regressions for same-UUID prerequisite reruns, blank input and
   no-write paths, persisted-but-redacted submit remarks, legacy safe/ambiguous migration paths,
   revalidation permissions/state/rollback, and create/PATCH/submit rollback. Strengthen the AST
   contract to positively require both public prerequisite modules and reject concrete model seams.
5. Update the local API contract/digest, generate immutable before/after and migration evidence,
   run backend focused tests after each red/green cycle, then run all configured backend/frontend
   quality gates with the mandated virtualenv interpreter.
6. Review the final diff against the High-risk limits, sharpen the next two Not Started slices from
   already-opened Epic 006 sources, and finish the Ralph changed-files, risk, review, summary,
   progress, handoff, state, and selected-slice artifacts. Git commit/push remains delegated to the
   orchestrator.

Risk controls: one additive migration only; no protected/source/frontend changes; no free text in
audit JSON; no concrete eligibility/loan-limit model navigation; no weakening of PostgreSQL
calculator concurrency or static import regressions.
