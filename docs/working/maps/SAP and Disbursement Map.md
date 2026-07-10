# SAP and Disbursement Map

> [!summary] Purpose
> Connect a documentation-ready sanctioned loan to SAP customer-code confirmation, loan-account creation, readiness validation, controlled payment initiation, CFC authorisation, bank evidence and disbursement advice.

## Traceability

- **Source:** [[sfpcl_client_brief#14. Stage 5: Loan Disbursement|Loan disbursement]] · [[sfpcl_client_brief#14.1 SAP Customer / Vendor Code Creation|SAP code]] · [[sfpcl_client_brief#14.2 Customer Code Creation Process|Code process]] · [[sfpcl_client_brief#14.3 Disbursement Process|Disbursement process]]
- **Product requirements:** [[product-requirements#11.20 SAP Customer Code Workflow|SAP workflow]] · [[product-requirements#11.21 Loan Account Creation|Loan-account creation]] · [[product-requirements#11.22 Disbursement Readiness and Payment|Readiness and payment]]
- **User flow:** [[user-flows#25. User Flow 17 — SAP Customer / Vendor Code Creation|SAP code flow]] · [[user-flows#26. User Flow 18 — Loan Disbursement|Disbursement flow]]
- **Functional specification:** [[functional-spec#11.7 M07 — SAP and Finance Setup|SAP and Finance Setup]] · [[functional-spec#11.8 M08 — Loan Disbursement|Loan Disbursement]] · [[functional-spec#13.1 SAP Integration|SAP integration]]
- **Domain model:** [[domain-model#13.1 LoanAccount|LoanAccount]] · [[domain-model#13.2 SAPCustomerProfileRequest and SAPCustomerCode|SAP request and code]] · [[domain-model#13.3 Disbursement|Disbursement]]
- **Data model:** [[data-model#18. Loan Account and Terms Tables|Loan-account tables]] · [[data-model#18.1 `loan_accounts`|Loan accounts]] · [[data-model#19. Finance, SAP, Disbursement and Repayment Tables|Finance tables]] · [[data-model#19.1 `sap_customer_profile_requests`|SAP requests]] · [[data-model#19.2 `sap_customer_codes`|SAP codes]] · [[data-model#19.3 `disbursements`|Disbursements]] · [[data-model#19.4 `bank_transfers`|Bank transfers]]
- **Information architecture:** [[information-architecture#9.7 Disbursement Module|Disbursement module]] · [[information-architecture#Disbursement Readiness Queue|Readiness queue]] · [[information-architecture#SAP Customer Code Queue|SAP queue]] · [[information-architecture#Payment Initiation Page|Payment page]]
- **Screen specification:** [[screen-spec#S36 — SAP Customer Code Request|SAP request]] · [[screen-spec#S37 — SAP Customer Code Confirmation|SAP confirmation]] · [[screen-spec#S38 — Disbursement Readiness Review|Readiness review]] · [[screen-spec#S39 — Payment Initiation Screen|Payment initiation]] · [[screen-spec#S40 — CFC Payment Authorisation Screen|CFC authorisation]] · [[screen-spec#S41 — Disbursement Advice Screen|Advice]] · [[screen-spec#S42 — Loan Account 360|Loan Account 360]]
- **Component specification:** [[component-spec#14. SAP and Disbursement Components|SAP and disbursement components]] · [[component-spec#14.1 SAP Customer Code Request Component|SAP request component]] · [[component-spec#14.3 Disbursement Readiness Gate Component|Readiness component]] · [[component-spec#14.4 Payment Initiation Component|Payment component]] · [[component-spec#14.5 Chief Financial Controller Authorisation Component|CFC component]]
- **Content specification:** [[content-spec#S24 — SAP Customer Code Request|SAP content]] · [[content-spec#S25 — Disbursement Queue|Queue content]] · [[content-spec#S26 — Disbursement Initiation|Initiation content]] · [[content-spec#S27 — Bank Transfer Approval|Approval content]] · [[content-spec#S28 — Disbursement Advice|Advice content]]
- **Design system:** [[design-system#33.6 SAP and Disbursement Pattern|SAP and disbursement pattern]]
- **API contracts:** [[api-contracts#29. SAP Customer Code APIs|SAP APIs]] · [[api-contracts#30. Loan Account APIs|Loan-account APIs]] · [[api-contracts#30.1 Create Loan Account from Sanction|Create account]] · [[api-contracts#31. Disbursement APIs|Disbursement APIs]] · [[api-contracts#31.1 Disbursement Readiness Check|Readiness API]] · [[api-contracts#31.3 CFC Authorise Disbursement|CFC API]] · [[api-contracts#31.4 Mark Bank Transfer Successful|Transfer success]]
- **Auth and permissions:** [[auth-permissions#12.9 SAP and Finance Permissions|SAP and finance permissions]] · [[auth-permissions#16.3 Disbursement Authority|Disbursement authority]] · [[auth-permissions#25.7 Finance Module|Finance access]] · [[auth-permissions#26.5 Stage 5 — Loan Disbursement|Stage permission matrix]]
- **Codebase design:** [[codebase-design#16. SAP and Disbursement Modules|SAP and disbursement modules]] · [[codebase-design#16.1 SAP Customer Profile Module|SAP module]] · [[codebase-design#16.2 Loan Account Module|Loan-account module]] · [[codebase-design#16.3 Disbursement Readiness Module|Readiness module]] · [[codebase-design#16.4 Disbursement Workflow Module|Workflow module]] · [[technical-architecture#19.2 SAP Integration|SAP architecture]] · [[integrations#8. SAP Integration|SAP integration]] · [[integrations#9. Bank / RBL Bank Integration|Bank integration]]
- **Security and privacy:** [[security-privacy#21.2 SAP Security|SAP security]] · [[security-privacy#21.3 Bank Security|Bank security]] · [[security-privacy#22.1 Disbursement Controls|Disbursement controls]] · [[security-privacy#24.1 Immutable Audit Logs|Audit logs]]
- **Test plan:** [[test-plan#13.12 SAP Customer Profile Tests|SAP tests]] · [[test-plan#13.13 Disbursement Readiness Tests|Readiness tests]] · [[test-plan#13.14 Disbursement Workflow Tests|Workflow tests]] · [[test-plan#14.9 Disbursement API Tests|API tests]]
- **Implementation roadmap:** [[implementation-roadmap#14. Release R5 — SAP and Disbursement|R5 disbursement]] · [[implementation-roadmap#Sprint 12 — SAP and Loan Account|SAP and account sprint]]

## Key Decisions and Open Issues

- Select SAP and bank MVP modes and their workflow owners.
- No payment may proceed before documentation, security, confirmed SAP code, bank details and approvals pass readiness.
- Payment initiation and CFC authorisation remain segregated, audited and idempotent.
- Resolve the “SAP code confirmed” versus “in process” inconsistency in [[Open Decisions Index#SAP Code and Disbursement Gate|the disbursement decision]].

## Related Maps

- [[Documentation and Security Map]]
- [[Repayment and Interest Map]]
- [[Monitoring Default and Recovery Map]]
- [[Platform Security and Operations Map]]

