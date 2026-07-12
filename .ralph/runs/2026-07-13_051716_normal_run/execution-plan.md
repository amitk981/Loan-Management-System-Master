# Execution Plan

Selected slice: `006Z12-portal-limit-denial-matrix-evidence-closure`

1. Inspect the existing public portal borrower-limit API matrix, its fixture setup, and every model
   category named by the slice. Confirm authentication occurs before each zero-write baseline.
2. Add independently selectable public API denial tests for stale authority, changed supply,
   missing profile, missing landholding, and contradictory profile/land facts while retaining and
   isolating the existing future, closed, manual, mismatched, service, duplicate-share, no-policy,
   and invalid-amount cases.
3. Build one complete immutable before/after ledger covering Member, ActiveMemberStatus,
   ProduceSupplyRecord, MemberServiceEvidence, Shareholding, LandHolding and profile,
   LoanLimitAssessment, LoanApplication, LoanPolicyConfig/version, AuditLog, and WorkflowEvent.
   Assert the exact redacted unavailable envelope or exact invalid-amount field error for every row.
4. Run the focused test first and retain red evidence. Change production behavior only if a public
   row exposes a defect; otherwise keep the slice test-only. Then run focused green tests and
   coverage plus dependency/static scans.
5. Run all configured frontend and backend gates, save terminal evidence, changed-files and risk/
   review/final artifacts, update slice/progress/state/handoff, and inspect the next two Not Started
   slices for concrete readiness using already-opened source material.
