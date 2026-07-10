# ADR-0003: Freeze Appraisal Prerequisite Projections

## Status
Accepted

## Context
`LoanLimitAssessment` and `EligibilityAssessment` are one-to-one current assessments. An explicit
successful rerun updates the existing row while preserving its UUID and records the replacement in
audit history. Slice 006E stored only those UUIDs on `LoanAppraisalNote` and accepted caller-written
eligibility/loan-limit summaries.

That is insufficient decision evidence. After a same-UUID rerun, the appraisal still names the same
assessment ID but cannot prove the eligibility, cultivated acreage, financial limits, policy
version, or exception flag used when its recommendation was prepared. This conflicts with the API
design principle that decision inputs are snapshotted and with the appraisal handoff requirement to
consume the stored 006B/006D facts without recalculation.

## Decision
At appraisal creation, the credit module must persist immutable, canonical, redacted copies of the
public eligibility and loan-limit projections used for that appraisal. The assessment UUIDs remain
as provenance identifiers, but they are not treated as immutable assessment content and are not
foreign-key navigation seams.

Draft PATCH, submit-for-review, Credit Manager review, sanction submission, reporting, and audit
metadata must use the appraisal-owned frozen projections. They must not reread a mutable current
assessment to reinterpret an existing appraisal. A later eligibility or loan-limit rerun does not
change the appraisal snapshots or its amount/exception decision boundary.

Legacy appraisal rows without frozen projections must not be silently backfilled as historical
truth when intervening assessment reruns make provenance uncertain. The corrective migration may
copy current projections only when evidence proves they are the original inputs; otherwise it must
mark the row as legacy/unverified and block downstream review until an explicit authorised,
audited revalidation pins the current projections.

## Consequences
- Slice `006E2-appraisal-source-contract-and-snapshot-hardening` owns the additive migration,
  legacy handling, API projection, and rerun-preservation tests.
- Existing assessment rerun semantics remain unchanged; this ADR freezes the decision boundary at
  the appraisal, not the current assessment table.
- Appraisal callers continue to depend only on `EligibilityAssessmentModule`,
  `LoanLimitCalculator`, and `AppraisalWorkflow`; concrete assessment models remain private.
- Snapshot JSON must contain only canonical public financial/eligibility facts and no PAN,
  Aadhaar, bank details, free-text risk notes, or mutable model handles.
