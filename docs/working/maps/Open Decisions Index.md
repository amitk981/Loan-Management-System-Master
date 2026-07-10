# Open Decisions Index

This index consolidates unresolved decisions that appear across the specification set. Repetition across derived notes does not make a decision settled. Each item requires an authoritative owner, decision evidence and an effective date before implementation is frozen.

## Primary Decision Registers

- [[sfpcl_client_brief#25. Open Issues and Client Clarifications Required|Client and SOP clarifications]]
- [[product-requirements#17. Open Questions and Clarifications|Product open questions]]
- [[domain-model#28. Open Domain Questions|Domain questions]]
- [[data-model#36. Open Data Model Questions|Data-model questions]]
- [[technical-architecture#37. Open Technical Decisions|Technical decisions]]
- [[implementation-roadmap#8. Key Decision Gates|Roadmap decision gates]]

## Policy and Lending Rules

### Loan-Limit Formula

Status: **Open — Board-approved operative rule required.**

- [[sfpcl_client_brief#25.1 Loan Limit Contradiction|Source contradiction]]
- [[domain-model#Important Policy Ambiguity|Domain ambiguity]]
- [[data-model#36.1 Loan Limit Rule|Data-model response]]
- [[content-spec#26.1 Loan Limit Formula Contradiction|Content impact]]
- [[design-system#44. Open Design Decisions and Client Confirmations Required|Design impact]]
- [[Eligibility and Loan Limit Map]]

### Approval Threshold and Signing Authority

Status: **Open — exactly ₹5,00,000 and document-signing authority require confirmation.**

- [[product-requirements#17.1 Policy and Legal|Product policy questions]]
- [[auth-permissions#40. Open Questions Requiring Client Confirmation|Permission and authority questions]]
- [[Appraisal and Sanction Map]]
- [[Documentation and Security Map]]

### Annexure K

Status: **Open — Credit Sanction Register versus Grievance Form.**

- [[sfpcl_client_brief#25.2 Annexure Numbering Inconsistency|Source inconsistency]]
- [[data-model#36.2 Annexure K Conflict|Data-model response]]
- [[content-spec#26.2 Annexure Numbering Conflict|Content impact]]
- [[Open Decisions Index#Template, Legal and Content Decisions|Related decisions]]

### Interest, Penal Charges and Fees

Status: **Open — benchmark, spread, reset cadence, calculation convention, ownership and charges require approval.**

- [[sfpcl_client_brief#25.3 Interest Rate Not Specified|Interest policy gap]]
- [[sfpcl_client_brief#25.4 Penal Charges and Fees|Charges gap]]
- [[domain-model#Important Ownership Clarification|Interest-invoice ownership conflict]]
- [[functional-spec#Open Accounting Configuration|Accounting configuration]]
- [[Repayment and Interest Map]]

### NACH, Guarantors and Credit Bureau

Status: **Open — optional requirements must not be made mandatory without confirmation.**

- [[sfpcl_client_brief#25.5 NACH / ECS Mandate|NACH/ECS]]
- [[sfpcl_client_brief#25.6 Guarantor Requirement|Guarantors]]
- [[sfpcl_client_brief#25.7 Credit Bureau Enquiry|Credit bureau]]
- [[content-spec#26.5 NACH / ECS Ambiguity|NACH content impact]]
- [[content-spec#26.6 Guarantor Ambiguity|Guarantor content impact]]

## Workflow and State Decisions

### Application Reference Timing

Status: **Open — draft creation versus post-completeness registration.**

- [[Application and Completeness Map]]
- [[product-requirements#11.7 Loan Application Intake|Product requirement]]
- [[data-model#13.1 `loan_applications`|Application persistence]]

### SAP Code and Disbursement Gate

Status: **Open — SAP code “confirmed” versus “in process” must be canonical.**

- [[SAP and Disbursement Map]]
- [[product-requirements#11.22 Disbursement Readiness and Payment|Product readiness rule]]
- [[user-flows#26. User Flow 18 — Loan Disbursement|Operational flow]]

### Waivable Versus Non-Waivable Gates

Status: **Open — formal whitelist required.**

- [[functional-spec#20. Open Clarifications and Implementation Risks|Functional risks]]
- [[information-architecture#20. Open Issues and Configuration Risks|IA risks]]
- [[security-privacy#39. Open Security and Privacy Questions|Security questions]]

### Default Classification and Recovery Authority

Status: **Open — intentionality criteria, non-recoverable classification, approval route and invocation authority require definition.**

- [[sfpcl_client_brief#16.5 Sanction Committee Decision on Recovery Action|Source recovery decision]]
- [[domain-model#14.4 DefaultAssessment, ExtensionNote, NonPaymentNote and RecoveryDecision|Domain model]]
- [[auth-permissions#40.3 Recovery Approval Authority|Permission question]]
- [[Monitoring Default and Recovery Map]]

### Closure Sequencing

Status: **Open — financial settlement, NOC, security return, closed and archived states need one canonical order.**

- [[data-model#36. Open Data Model Questions|Data-model questions]]
- [[api-contracts#36. Closure APIs|API closure flow]]
- [[Closure and Compliance Map]]

## Identity, Privacy and Access Decisions

### Aadhaar, OVD and Masking

Status: **Open — mandatory fields, permitted transmission and masking format require privacy/legal confirmation.**

- [[security-privacy#39. Open Security and Privacy Questions|Security and privacy questions]]
- [[data-model#10. Party and Member Tables|Member data model]]
- [[Membership and KYC Map]]

### KYC Retention and Destruction

Status: **Open — KYC-specific retention must not be inferred from the generic eight-year loan-file rule.**

- [[security-privacy#26. Data Retention and Archival|Retention controls]]
- [[technical-architecture#31. Data Retention and Archival Architecture|Architecture retention]]
- [[Membership and KYC Map]]

### MFA and JWT Transport

Status: **Open — privileged MFA and access/refresh-token transport must be finalised.**

- [[auth-permissions#40.2 MFA|MFA question]]
- [[security-privacy#39. Open Security and Privacy Questions|Security questions]]
- [[Platform Security and Operations Map]]

## Scope, Integration and Operations Decisions

### Member Portal Scope

Status: **Open — PRD and roadmap defer the portal, while a complete portal screen specification exists.**

- [[screen-spec-member-portal#15. Out of Scope / Configuration Decisions|Portal decisions]]
- [[product-requirements#9.2 Future / Non-MVP Scope|PRD scope]]
- [[implementation-roadmap#5.2 Non-MVP / Future Scope|Roadmap scope]]

### Integration Providers and Automation Level

Status: **Open — SAP, bank, messaging, storage, CKYC, bureau, e-sign and CDSL provider modes require confirmation.**

- [[integrations#32. Open Integration Questions|Integration questions]]
- [[implementation-roadmap#8.2 Integration Decisions|Roadmap integration gates]]
- [[SAP and Disbursement Map]]
- [[Platform Security and Operations Map]]

### Hosting, SLO, RPO/RTO and Support

Status: **Open — deployment model and measurable service targets require owner approval.**

- [[deployment-ops#46. Open Deployment and Operations Questions|Operations questions]]
- [[technical-architecture#37. Open Technical Decisions|Technical decisions]]
- [[Platform Security and Operations Map]]

## Template, Legal and Content Decisions

- [[content-spec#26. Open Content and Policy Issues|Content and policy issues]]
- [[component-spec#30. Open Component Design Questions|Component questions]]
- [[design-system#44. Open Design Decisions and Client Confirmations Required|Design questions]]
- [[screen-spec#11. Open Issues to Reflect in UI|Screen-level issues]]

## Governance

When an item is resolved:

1. Record the authoritative decision and owner.
2. Link the Board, legal, policy or product evidence.
3. Record the effective date and affected versions.
4. Update every linked capability map.
5. Update [[domain-model|Domain Model]] and [[data-model|Data Model]] before freezing APIs or implementation.
6. Run `python3 validate_vault_links.py`.

## Related

- [[LMS Index]]
- [[LMS Traceability Matrix]]
- [[implementation-roadmap#29.2 Decision Log|Implementation decision log]]
