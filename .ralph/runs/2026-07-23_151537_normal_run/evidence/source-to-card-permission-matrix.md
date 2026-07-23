# Source-to-Card and Permission Matrix

| Canonical owner | Safe search fields | S02 title / identifier | Status, risk, amount | Scope and action |
|---|---|---|---|---|
| 011K `ComplianceControl` | code, name, area | control name / control code | control status; no restricted risk narrative or amount | `control.read`; owner/reviewer unless manager or Internal Auditor; `Open` only with `task.read` |
| 011K `ComplianceTask` | parent code/name, period | control-name task / code + period | task status; no remarks | `task.read`; assignee/reviewer or Internal Auditor; `Open` |
| 011K `ComplianceEvidence` | parent code/name/period only | control-name evidence / code + period | review status only | submitter/assignee, reviewer, or Internal Auditor; no file action |
| 011K `MoneyLendingLawReview` | financial year, state, applicability | Money-lending law review / FY + state | applicability; no legal opinion, Board note, remarks, or amount | reviewer/assigned task owner or Internal Auditor; `Open` only with `task.read` |
| 011L `Section186Tracker` | FY and quarter | Section 186 quarterly limit / FY + quarter | review status, within-limit/special-resolution risk, applicable limit amount | exact `section186.read`; `Open` only with `task.read` |
| 011L `NbfcPrincipalBusinessTest` | FY and quarter | NBFC principal-business test / FY + quarter | review status and clear/warning/registration-triggered risk; no amount | exact `nbfc_test.read`; `Open` only with `task.read` |
| 011M `KYCReview` | scoped member name/number or authorised member root | member KYC/re-KYC review / type + member number | tracker status and summary risk rating; no KYC value | `kyc_review.manage` member scope or assigned/reviewer `task.read`; `Open` only with `task.read` |

Actual control/task/KYC `last_updated_by` comes from canonical audit events; a legacy/direct row
without an event emits no actor rather than inventing one. Statutory, evidence, and money-lending
projections use their retained preparer/reviewer timestamps and actors.

Verification:

- `GlobalSearchComplianceTests.test_compliance_cfo_cs_and_auditor_permission_matrix`
- `GlobalSearchComplianceTests.test_rekyc_review_uses_member_scope_without_exposing_kyc_values`
- `GlobalSearchComplianceTests.test_cross_scope_guesses_and_provider_failures_leak_no_match_existence`
- `GlobalSearchComplianceTests.test_governed_evidence_and_money_lending_review_are_minimised`
- `backend-compliance-matrix-post-review.log`
