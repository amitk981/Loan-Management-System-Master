# Appraisal and Sanction Map

> [!summary] Purpose
> Connect completed credit assessment to a controlled and auditable appraisal, approval-matrix route, Sanction Committee decision, conflict handling and sanction registers.

## Traceability

- **Source:** [[sfpcl_client_brief#12. Stage 3: Credit Scrutiny and Approval|Credit scrutiny and approval]] · [[sfpcl_client_brief#12.1 Sanction Committee Review|Committee review]] · [[sfpcl_client_brief#12.3 Approval Matrix|Approval matrix]] · [[sfpcl_client_brief#12.4 Special Cases: Director, Sanction Committee Member or Relative as Borrower|Special cases]]
- **Product requirements:** [[product-requirements#11.12 Appraisal and Credit Review|Appraisal and credit review]] · [[product-requirements#11.13 Sanction Approval|Sanction approval]] · [[product-requirements#11.14 Conflict and Related-Party Approval|Conflict approval]]
- **User flow:** [[user-flows#14. User Flow 6 — Credit Manager Review and Rejection|Credit Manager review]] · [[user-flows#15. User Flow 7 — Sanction Committee Scrutiny and Approval|Committee approval]] · [[user-flows#16. User Flow 8 — Special Case Approval: Director / Sanction Committee Member / Relative as Borrower|Special-case approval]]
- **Functional specification:** [[functional-spec#11.4 M04 — Eligibility and Appraisal|Eligibility and Appraisal]] · [[functional-spec#11.5 M05 — Sanction and Approval|Sanction and Approval]]
- **Domain model:** [[domain-model#9.3 LoanAppraisalNote|LoanAppraisalNote]] · [[domain-model#10. Approval Domain|Approval domain]] · [[domain-model#10.3 ApprovalCase and ApprovalAction|Approval case and action]] · [[domain-model#10.4 SanctionDecision, CreditSanctionRegister and ExceptionRegister|Sanction and registers]]
- **Data model:** [[data-model#14.4 `loan_appraisal_notes`|Appraisal notes]] · [[data-model#15. Approval and Sanction Tables|Approval tables]] · [[data-model#15.3 `approval_cases`|Approval cases]] · [[data-model#15.5 `sanction_decisions`|Sanction decisions]] · [[data-model#15.6 `credit_sanction_register_entries`|Sanction register]]
- **Information architecture:** [[information-architecture#9.5 Appraisal & Sanction Module|Appraisal and sanction module]] · [[information-architecture#Sanction Committee Queue|Committee queue]]
- **Screen specification:** [[screen-spec#S19 — Loan Appraisal Note|Appraisal note]] · [[screen-spec#S20 — Credit Manager Review|Credit Manager review]] · [[screen-spec#S21 — Sanction Committee Workbench|Committee workbench]] · [[screen-spec#S22 — Sanction Case Detail|Case detail]] · [[screen-spec#S23 — Credit Sanction Register|Sanction register]] · [[screen-spec#S24 — Special Case Approval|Special-case approval]]
- **Component specification:** [[component-spec#11.1 Loan Appraisal Note Component|Appraisal component]] · [[component-spec#12.1 Sanction Committee Review Component|Committee review]] · [[component-spec#12.2 Approval Matrix Engine|Approval Matrix Engine]] · [[component-spec#12.4 Credit Sanction Register Component|Sanction register]] · [[component-spec#12.6 Conflict-of-Interest Component|Conflict component]]
- **Content specification:** [[content-spec#S11 — Loan Appraisal Note|Appraisal content]] · [[content-spec#S13 — Credit Review and Rejection|Review content]] · [[content-spec#S14 — Sanction Committee Review|Committee content]] · [[content-spec#S15 — Special Case Approval|Special-case content]]
- **Design system:** [[design-system#33.3 Appraisal Pattern|Appraisal pattern]] · [[design-system#33.4 Sanction Pattern|Sanction pattern]]
- **API contracts:** [[api-contracts#24. Loan Appraisal APIs|Appraisal APIs]] · [[api-contracts#24.5 Submit to Sanction Committee|Committee submission]] · [[api-contracts#25. Approval and Sanction APIs|Approval APIs]] · [[api-contracts#25.8 Sanction Decision|Sanction decision]] · [[api-contracts#25.9 Credit Sanction Register|Sanction register]]
- **Auth and permissions:** [[auth-permissions#12.5 Credit Assessment Permissions|Credit permissions]] · [[auth-permissions#12.6 Approval Permissions|Approval permissions]] · [[auth-permissions#16.2 Loan Sanction Authority|Sanction authority]] · [[auth-permissions#17.2 Conflict Rules|Conflict rules]] · [[auth-permissions#25.4 Approval Module|Approval access rules]]
- **Codebase design:** [[codebase-design#12.3 Appraisal Module|Appraisal module]] · [[codebase-design#13.1 Approval Case Engine|Approval Case Engine]] · [[codebase-design#13.2 Conflict of Interest Module|Conflict module]] · [[technical-architecture#13.3 Transaction Boundary Example: Sanction Approval|Sanction transaction boundary]]
- **Security and privacy:** [[security-privacy#12. Segregation of Duties|Segregation of duties]] · [[security-privacy#12.2 Conflict-of-Interest Controls|Conflict controls]] · [[security-privacy#24.1 Immutable Audit Logs|Immutable audit]]
- **Test plan:** [[test-plan#13.8 Appraisal Workflow Tests|Appraisal tests]] · [[test-plan#13.9 Approval Case Engine Tests|Approval-engine tests]] · [[test-plan#14.7 Approval API Tests|Approval API tests]]
- **Implementation roadmap:** [[implementation-roadmap#12. Release R3 — Sanction and Approval Workflow|R3 sanction]] · [[implementation-roadmap#Sprint 7 — Approval Matrix and Cases|Approval sprint]] · [[implementation-roadmap#Sprint 8 — Sanction, Exceptions and Special Cases|Sanction sprint]]

## Key Decisions and Open Issues

- Approval matrix and conflict rules are backend-configured authority, not UI logic.
- Confirm the operative limit formula, exactly ₹5,00,000 treatment, document signer and general-meeting evidence.
- Resolve Annexure K before fixing the Credit Sanction Register template code.
- See [[Open Decisions Index#Approval Threshold and Signing Authority|approval decisions]] and [[Open Decisions Index#Annexure K|Annexure K]].

## Related Maps

- [[Application and Completeness Map]]
- [[Eligibility and Loan Limit Map]]
- [[Documentation and Security Map]]
- [[Platform Security and Operations Map]]

