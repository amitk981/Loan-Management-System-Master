# Documentation and Security Map

> [!summary] Purpose
> Connect approved sanction to a signed, stamped, verified and auditable legal-document and security package, including PoA, SH-4, CDSL pledge, cheques, custody and checklist approval.

## Traceability

- **Source:** [[sfpcl_client_brief#13. Stage 4: Documentation and Stamping|Documentation and stamping]] · [[sfpcl_client_brief#13.7 Share Transfer Form SH-4|SH-4]] · [[sfpcl_client_brief#13.8 CDSL Share Pledge Process for Demat Shares|CDSL pledge]] · [[sfpcl_client_brief#13.14 Checklist|Checklist]] · [[sfpcl_client_brief#13.15 Final Approvals Before Disbursement|Final documentation approvals]]
- **Product requirements:** [[product-requirements#11.15 Legal Documentation|Legal documentation]] · [[product-requirements#11.16 Stamp Duty, Notarisation and Signatures|Stamping and signatures]] · [[product-requirements#11.17 Document Checklist|Checklist]] · [[product-requirements#11.18 Security Package|Security package]] · [[product-requirements#11.19 CDSL Pledge|CDSL pledge]]
- **User flow:** [[user-flows#17. User Flow 9 — Post-Sanction Document Collection|Document collection]] · [[user-flows#18. User Flow 10 — Legal Document Preparation and Stamping|Document preparation]] · [[user-flows#21. User Flow 13 — Security Handling for Physical Shares: SH-4|SH-4 flow]] · [[user-flows#22. User Flow 14 — Security Handling for Demat Shares: CDSL Pledge|CDSL flow]] · [[user-flows#24. User Flow 16 — Final Documentation Checklist and Approvals|Checklist approval]]
- **Functional specification:** [[functional-spec#11.6 M06 — Documentation and Security|Documentation and Security module]] · [[functional-spec#15. Document Generation Requirements|Document generation]]
- **Domain model:** [[domain-model#11. Documentation Domain|Documentation domain]] · [[domain-model#11.2 DocumentChecklist|DocumentChecklist]] · [[domain-model#12. Security Domain|Security domain]] · [[domain-model#12.1 SecurityPackage|SecurityPackage]] · [[domain-model#12.4 CDSLSharePledge|CDSLSharePledge]]
- **Data model:** [[data-model#16. Document and Checklist Tables|Document tables]] · [[data-model#16.3 `loan_documents`|Loan documents]] · [[data-model#16.4 `document_checklists`|Document checklists]] · [[data-model#17. Security Tables|Security tables]] · [[data-model#17.1 `security_packages`|Security packages]] · [[data-model#17.4 `cdsl_share_pledges`|CDSL pledges]] · [[data-model#17.6 `security_custody_events`|Custody events]]
- **Information architecture:** [[information-architecture#9.6 Documentation & Security Module|Documentation and security module]] · [[information-architecture#Document Checklist Page|Checklist page]] · [[information-architecture#Document Generation Page|Document generation]] · [[information-architecture#Security Register|Security Register]]
- **Screen specification:** [[screen-spec#S26 — Documentation Workspace|Documentation workspace]] · [[screen-spec#S27 — Document Checklist|Checklist]] · [[screen-spec#S28 — Power of Attorney Screen|PoA]] · [[screen-spec#S30 — SH-4 Physical Share Security Screen|SH-4]] · [[screen-spec#S31 — CDSL Pledge Screen|CDSL pledge]] · [[screen-spec#S34 — Bank Verification / Signature Mismatch Screen|Signature mismatch]] · [[screen-spec#S35 — Final Documentation Approval Screen|Final approval]]
- **Component specification:** [[component-spec#13. Documentation and Stamping Components|Documentation components]] · [[component-spec#13.2 Document Checklist Component|Checklist component]] · [[component-spec#13.3 Document Generator Component|Generator]] · [[component-spec#13.6 SH-4 Component|SH-4 component]] · [[component-spec#13.7 CDSL Pledge Component|CDSL component]] · [[component-spec#13.13 Final Documentation Approval Component|Final approval component]]
- **Content specification:** [[content-spec#S16 — Documentation Workbench|Documentation content]] · [[content-spec#S17 — Power of Attorney|PoA content]] · [[content-spec#S19 — SH-4 / CDSL Pledge|Security content]] · [[content-spec#S22 — Bank Verification|Verification content]] · [[content-spec#S23 — Document Checklist|Checklist content]]
- **Design system:** [[design-system#24. Document Checklist Component|Checklist design]] · [[design-system#33.5 Documentation Pattern|Documentation pattern]] · [[design-system#35. Generated Document Design Standards|Generated documents]] · [[design-system#39. Security and Privacy Design Standards|Security design]]
- **API contracts:** [[api-contracts#26. Document APIs|Document APIs]] · [[api-contracts#27. Document Checklist APIs|Checklist APIs]] · [[api-contracts#28. Security Package APIs|Security APIs]] · [[api-contracts#28.7 Security Custody Event|Custody event]]
- **Auth and permissions:** [[auth-permissions#12.7 Documentation Permissions|Documentation permissions]] · [[auth-permissions#12.8 Security Permissions|Security permissions]] · [[auth-permissions#16.4 Security Authority|Security authority]] · [[auth-permissions#25.5 Documentation Module|Documentation access]] · [[auth-permissions#25.6 Security Module|Security access]]
- **Codebase design:** [[codebase-design#14. Documentation Modules|Documentation modules]] · [[codebase-design#14.1 Document Generation Module|Generation module]] · [[codebase-design#14.2 Document Checklist Module|Checklist module]] · [[codebase-design#14.3 Signature Mismatch Module|Signature module]] · [[codebase-design#15. Security Instrument Modules|Security modules]] · [[technical-architecture#15. Document Architecture|Document architecture]]
- **Security and privacy:** [[security-privacy#20. Object Storage and Document Security|Document security]] · [[security-privacy#20.2 Restricted Document Types|Restricted documents]] · [[security-privacy#23.1 Security Instruments|Security instruments]] · [[security-privacy#24.1 Immutable Audit Logs|Audit logs]]
- **Test plan:** [[test-plan#13.10 Document Checklist Tests|Checklist tests]] · [[test-plan#13.11 Security Package Tests|Security-package tests]] · [[test-plan#14.8 Documentation and Security API Tests|Documentation API tests]] · [[test-plan#18. Security and Privacy Test Plan|Security tests]]
- **Implementation roadmap:** [[implementation-roadmap#13. Release R4 — Documentation and Security Package|R4 documentation]] · [[implementation-roadmap#Sprint 9 — Document Templates and Generation|Template sprint]] · [[implementation-roadmap#Sprint 11 — Security Package|Security-package sprint]]

## Key Decisions and Open Issues

- Confirm legal-document signer, wet-signature versus e-sign scope, optional NACH/guarantor records and CDSL integration mode.
- Resolve Annexure K before freezing template codes.
- Define custody and security-invocation authority, including re-authentication requirements.
- See [[Open Decisions Index#Template, Legal and Content Decisions|template and legal decisions]] and [[Monitoring Default and Recovery Map]].

## Related Maps

- [[Appraisal and Sanction Map]]
- [[SAP and Disbursement Map]]
- [[Monitoring Default and Recovery Map]]
- [[Closure and Compliance Map]]
- [[Platform Security and Operations Map]]

