# Slice 006Z12: Portal Limit Denial Matrix Evidence Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006Z10

## Runtime Capabilities

none

## Goal

Finish the 006Z10 public borrower-limit denial matrix with independently observable stale/supply/
missing-fact rows and complete zero-write snapshots, without changing the credit-owned calculation.

## Source / Review References

- `docs/source/functional-spec.md` M04-FR-005 through M04-FR-007
- `docs/source/api-contracts.md` §§6-8 and §§22-24
- `docs/source/codebase-design.md` §§22.1, 26.1-27.1, and §§42.1-42.3
- `docs/slices/006Z10-portal-limit-interaction-and-boundary-proof.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_044409_architecture_review`

## Concrete Requirements

1. Add independently selectable public projection rows for stale authority, changed qualifying
   supply provenance, missing profile, missing landholding, and missing/contradictory profile-land
   facts. Retain future/closed/manual/mismatched authority, changed service evidence, duplicate
   shareholding, no-policy, and invalid-amount rows.
2. Each denial compares complete before/after Member, ActiveMemberStatus, ProduceSupplyRecord,
   MemberServiceEvidence, Shareholding, LandHolding/profile, LoanLimitAssessment, LoanApplication,
   LoanPolicyConfig/version, AuditLog, and WorkflowEvent state. Do not mutate the expected snapshot
   to hide login audit differences; acquire authentication before the baseline.
3. Assert the complete stable redacted public envelope for every unavailable row and exact field
   error for invalid amounts; no authority/result/evidence/configuration identifiers may leak.
4. Keep all cases through the public credit projection/API boundary. Do not add raw source-string,
   private-helper, or fixture-name assertions and do not change production behavior unless a failing
   public row demonstrates a defect.

## Test Cases

- Changed supply evidence and changed service evidence independently stale the retained authority.
- Missing profile, missing landholding, and contradictory acreage are distinct selected rows with
  identical redacted unavailable contracts.
- Stale pointer/result/version facts are denied without any state change.
- Deleting any required snapshot category makes the test fail, proving the zero-write ledger is
  complete rather than a coverage-only assertion.

## Evidence Required

Failing public rows or false-completeness mutation proof, green complete matrix, focused coverage,
dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every blocked financial boundary named by 006Z10 is executed and proves complete zero-write state.
- M04-FR-005 through M04-FR-007 remain server-owned and redacted.

