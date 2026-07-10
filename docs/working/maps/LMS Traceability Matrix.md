# LMS Traceability Matrix

This matrix is the audit-oriented entry point for capability coverage. Each row links to a capability map containing the full 17-layer chain from source policy through implementation and testing.

## Coverage Rule

Every capability map must cover:

```text
Source → Product Requirements → User Flow → Functional Specification
→ Domain Model → Data Model → Information Architecture → Screen Specification
→ Component Specification → Content Specification → Design System
→ API Contracts → Authentication and Permissions → Codebase Design
→ Security and Privacy → Test Plan → Implementation Roadmap
```

The [[domain-model|Domain Model]] and [[data-model|Data Model]] are mandatory. A genuinely absent layer must be marked `N/A — reason`; it must never be silently omitted.

## Capability Matrix

| Capability | Detailed map | Product requirement | Domain model | Data model | Principal UI | API | Tests | Delivery |
|---|---|---|---|---|---|---|---|---|
| Membership and KYC | [[Membership and KYC Map]] | [[product-requirements#11.5 KYC and Re-KYC|KYC and re-KYC]] | [[domain-model#7.1 Member|Member]] | [[data-model#12.1 `kyc_profiles`|KYC profiles]] | [[screen-spec#S17 — KYC Verification|KYC verification]] | [[api-contracts#18. KYC APIs|KYC APIs]] | [[test-plan#14.4 Member and KYC API Tests|Member/KYC tests]] | [[implementation-roadmap#Sprint 3 — Member and KYC|Sprint 3]] |
| Application and completeness | [[Application and Completeness Map]] | [[product-requirements#11.8 Application Completeness and Deficiencies|Completeness]] | [[domain-model#8.1 LoanApplication|LoanApplication]] | [[data-model#13.1 `loan_applications`|Loan applications]] | [[screen-spec#S12 — Application Completeness Check|Completeness screen]] | [[api-contracts#19. Loan Application APIs|Application APIs]] | [[test-plan#16.4 E2E-004 — Incomplete Application Returned and Resubmitted|Resubmission E2E]] | [[implementation-roadmap#Sprint 4 — Application Intake|Sprint 4]] |
| Eligibility and loan limit | [[Eligibility and Loan Limit Map]] | [[product-requirements#11.11 Loan Limit Calculator|Loan limit]] | [[domain-model#9.2 LoanLimitAssessment|LoanLimitAssessment]] | [[data-model#14.2 `loan_limit_assessments`|Loan-limit assessments]] | [[screen-spec#S18 — Loan Limit Calculator|Calculator]] | [[api-contracts#23.1 Calculate Loan Limit|Calculation API]] | [[test-plan#13.7 Loan Limit Calculator Tests|Calculator tests]] | [[implementation-roadmap#Sprint 5 — Eligibility and Loan Limit|Sprint 5]] |
| Appraisal and sanction | [[Appraisal and Sanction Map]] | [[product-requirements#11.13 Sanction Approval|Sanction approval]] | [[domain-model#10.3 ApprovalCase and ApprovalAction|ApprovalCase]] | [[data-model#15.3 `approval_cases`|Approval cases]] | [[screen-spec#S21 — Sanction Committee Workbench|Committee workbench]] | [[api-contracts#25. Approval and Sanction APIs|Approval APIs]] | [[test-plan#13.9 Approval Case Engine Tests|Approval tests]] | [[implementation-roadmap#12. Release R3 — Sanction and Approval Workflow|R3]] |
| Documentation and security | [[Documentation and Security Map]] | [[product-requirements#11.18 Security Package|Security package]] | [[domain-model#12.1 SecurityPackage|SecurityPackage]] | [[data-model#17.1 `security_packages`|Security packages]] | [[screen-spec#S27 — Document Checklist|Checklist]] | [[api-contracts#28. Security Package APIs|Security APIs]] | [[test-plan#13.11 Security Package Tests|Security tests]] | [[implementation-roadmap#13. Release R4 — Documentation and Security Package|R4]] |
| SAP and disbursement | [[SAP and Disbursement Map]] | [[product-requirements#11.22 Disbursement Readiness and Payment|Disbursement]] | [[domain-model#13.3 Disbursement|Disbursement]] | [[data-model#19.3 `disbursements`|Disbursements]] | [[screen-spec#S38 — Disbursement Readiness Review|Readiness review]] | [[api-contracts#31. Disbursement APIs|Disbursement APIs]] | [[test-plan#13.14 Disbursement Workflow Tests|Workflow tests]] | [[implementation-roadmap#14. Release R5 — SAP and Disbursement|R5]] |
| Repayment and interest | [[Repayment and Interest Map]] | [[product-requirements#11.24 Interest, Accrual and Capitalisation|Interest lifecycle]] | [[domain-model#13.4 Repayment and Allocation|Repayment]] | [[data-model#19. Finance, SAP, Disbursement and Repayment Tables|Finance tables]] | [[screen-spec#S46 — Loan Ledger|Loan ledger]] | [[api-contracts#32. Repayment APIs|Repayment APIs]] | [[test-plan#13.16 Interest Engine Tests|Interest tests]] | [[implementation-roadmap#15. Release R6 — Repayment, Interest and Monitoring|R6]] |
| Monitoring, default and recovery | [[Monitoring Default and Recovery Map]] | [[product-requirements#11.27 Recovery|Recovery]] | [[domain-model#14. Monitoring and Default Domain|Default domain]] | [[data-model#21. Default and Recovery Tables|Default/recovery tables]] | [[screen-spec#S56 — Recovery Action Approval Screen|Recovery approval]] | [[api-contracts#35. Default and Recovery APIs|Recovery APIs]] | [[test-plan#13.18 Recovery Workflow Tests|Recovery tests]] | [[implementation-roadmap#16. Release R7 — Default, Recovery, Closure and Compliance|R7]] |
| Closure and compliance | [[Closure and Compliance Map]] | [[product-requirements#11.29 Compliance|Compliance]] | [[domain-model#15. Closure Domain|Closure domain]] | [[data-model#22. Closure Tables|Closure tables]] | [[screen-spec#S62 — Compliance Dashboard|Compliance dashboard]] | [[api-contracts#36. Closure APIs|Closure APIs]] | [[test-plan#13.20 Compliance Module Tests|Compliance tests]] | [[implementation-roadmap#16. Release R7 — Default, Recovery, Closure and Compliance|R7]] |
| Platform security and operations | [[Platform Security and Operations Map]] | [[product-requirements#12.1 Security and Privacy|Security NFRs]] | [[domain-model#18. Audit and Versioning Domain|Audit domain]] | [[data-model#26. Audit, Workflow and Versioning Tables|Audit data]] | [[screen-spec#S74 — Audit Log Explorer|Audit explorer]] | [[api-contracts#42. Audit and Workflow APIs|Audit APIs]] | [[test-plan#25. Operational Test Plan|Operational tests]] | [[implementation-roadmap#17. Release R8 — Reports, Hardening, UAT and Go-Live|R8]] |

## Cross-Cutting Review

- Open policy and legal questions: [[Open Decisions Index]]
- Authority and document hierarchy: [[LMS Index#Authority Rules|Authority rules]]
- Curated visual map: [[LMS Architecture.canvas|LMS Architecture Canvas]]
- Link validation: run `python3 validate_vault_links.py`

## Governance

When a specification section changes:

1. Update its capability map.
2. Confirm both domain and data-model effects.
3. Update the matrix if the primary section changed.
4. Review affected open decisions.
5. Run the validator before accepting the change.

## Related

- [[LMS Index]]
- [[Open Decisions Index]]
- [[test-plan|Test Plan]]
- [[implementation-roadmap|Implementation Roadmap]]

