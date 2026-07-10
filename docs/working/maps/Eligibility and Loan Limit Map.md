# Eligibility and Loan Limit Map

> [!summary] Purpose
> Connect active-member, default, document and purpose gates to shareholding-based and land-based limits, exceptions, approved configuration and immutable calculation snapshots.

## Traceability

- **Source:** [[sfpcl_client_brief#9.3 Eligibility Criteria|Eligibility criteria]] · [[sfpcl_client_brief#10. Loan Limit Determination|Loan-limit determination]] · [[sfpcl_client_brief#10.5 Percentage Ambiguity Requiring Client Confirmation|Percentage ambiguity]] · [[sfpcl_client_brief#23.3 Eligibility Engine|Eligibility engine]] · [[sfpcl_client_brief#23.4 Loan Limit Engine|Loan-limit engine]]
- **Product requirements:** [[product-requirements#11.9 Eligibility Assessment|Eligibility assessment]] · [[product-requirements#11.10 Active Member Assessment|Active-member assessment]] · [[product-requirements#11.11 Loan Limit Calculator|Loan-limit calculator]]
- **User flow:** [[user-flows#12. User Flow 4 — Loan Appraisal and Eligibility Assessment|Eligibility assessment]] · [[user-flows#13. User Flow 5 — Loan Limit Calculation|Loan-limit calculation]]
- **Functional specification:** [[functional-spec#10.1 Member and Borrower Rules|Member rules]] · [[functional-spec#10.3 Loan Limit Rules|Loan-limit rules]] · [[functional-spec#11.4 M04 — Eligibility and Appraisal|Eligibility and Appraisal module]]
- **Domain model:** [[domain-model#7.6 Shareholding|Shareholding]] · [[domain-model#7.7 ShareValuation|Share valuation]] · [[domain-model#7.8 LandHolding|Landholding]] · [[domain-model#9.1 EligibilityAssessment|EligibilityAssessment]] · [[domain-model#9.2 LoanLimitAssessment|LoanLimitAssessment]]
- **Data model:** [[data-model#11.1 `shareholdings`|Shareholdings]] · [[data-model#11.4 `share_valuations`|Share valuations]] · [[data-model#11.7 `land_holdings`|Land holdings]] · [[data-model#14.1 `eligibility_assessments`|Eligibility assessments]] · [[data-model#14.2 `loan_limit_assessments`|Loan-limit assessments]] · [[data-model#25.1 `loan_policy_configs`|Loan policy]] · [[data-model#35.1 Loan Limit|Calculation rule]] · [[data-model#36.1 Loan Limit Rule|Open data-model decision]]
- **Information architecture:** [[information-architecture#7.9 Loan Limit Calculation|Loan-limit object]] · [[information-architecture#Eligibility & Loan Limit Tab|Eligibility and loan-limit tab]] · [[information-architecture#Loan Limit Calculator|Calculator page]] · [[information-architecture#15.3 Share Valuation Master|Share valuation]] · [[information-architecture#15.4 Scale of Finance Master|Scale of finance]]
- **Screen specification:** [[screen-spec#S15 — Eligibility Assessment|Eligibility assessment]] · [[screen-spec#S16 — Active Member Verification|Active-member verification]] · [[screen-spec#S17 — KYC Verification|KYC gate]] · [[screen-spec#S18 — Loan Limit Calculator|Loan-limit calculator]] · [[screen-spec#9.2 Eligibility Rules|Eligibility rules]] · [[screen-spec#9.3 Loan Limit Rules|Loan-limit rules]]
- **Component specification:** [[component-spec#10.1 Eligibility Checklist Component|Eligibility checklist]] · [[component-spec#10.2 Existing Default Check Component|Default check]] · [[component-spec#10.3 Loan Purpose Validator Component|Purpose validator]] · [[component-spec#10.4 Shareholding-Based Limit Calculator|Shareholding calculator]] · [[component-spec#10.5 Agricultural Land-Based Limit Calculator|Land calculator]] · [[component-spec#10.6 Final Eligible Loan Amount Component|Final eligible amount]]
- **Content specification:** [[content-spec#Eligibility Labels|Eligibility labels]] · [[content-spec#S12 — Loan Limit Calculator|Calculator content]] · [[content-spec#15.5 Loan Limit Fields|Loan-limit labels]] · [[content-spec#26.1 Loan Limit Formula Contradiction|Content issue]]
- **Design system:** [[design-system#22. Loan Limit Calculator Component|Calculator design]] · [[design-system#23. Eligibility Checklist Component|Eligibility design]] · [[design-system#26. Exception Component|Exception design]]
- **API contracts:** [[api-contracts#16.1 Calculate Active Member Status|Active-member calculation]] · [[api-contracts#22. Eligibility Assessment APIs|Eligibility APIs]] · [[api-contracts#23.1 Calculate Loan Limit|Loan-limit API]]
- **Auth and permissions:** [[auth-permissions#12.5 Credit Assessment Permissions|Credit permissions]] · [[auth-permissions#25.3 Credit Module|Credit access rules]] · [[auth-permissions#34.4 Credit|Credit endpoint permissions]]
- **Codebase design:** [[codebase-design#10.2 Active Member Module|Active Member module]] · [[codebase-design#12.1 Eligibility Assessment Module|Eligibility module]] · [[codebase-design#12.2 Loan Limit Module|Loan Limit module]] · [[codebase-design#24.3 `features/credit`|Credit frontend feature]]
- **Security and privacy:** [[security-privacy#16.2 High-Risk Endpoints|Override security]] · [[security-privacy#18.3 Service Layer Security|Server enforcement]] · [[security-privacy#24.1 Immutable Audit Logs|Audit events]]
- **Test plan:** [[test-plan#13.5 Active Member Status Tests|Active-member tests]] · [[test-plan#13.6 Eligibility Assessment Tests|Eligibility tests]] · [[test-plan#13.7 Loan Limit Calculator Tests|Loan-limit tests]] · [[test-plan#16.7 E2E-007 — Loan Exceeding Eligible Limit|Above-limit E2E]]
- **Implementation roadmap:** [[implementation-roadmap#11. Release R2 — Loan Origination and Credit Assessment|R2 origination]] · [[implementation-roadmap#21.3 Origination and Credit Tables|Credit data sequence]] · [[implementation-roadmap#Sprint 5 — Eligibility and Loan Limit|Eligibility and loan-limit sprint]]

## Key Decisions and Open Issues

- The final eligible amount is the lower of independently calculated shareholding and land-based limits.
- Requests above that amount require an exception route; all inputs and policy versions are snapshotted.
- Policy must be Board-approved and versioned, never hard-coded in UI or services.
- The operative 30% versus 10% versus ₹200-per-share rule remains unresolved. Production calculation must remain blocked until approved configuration exists. See [[Open Decisions Index#Loan-Limit Formula|loan-limit decision]].
- Confirm scale-of-finance value/effective date and precise override authority.

## Related Maps

- [[Membership and KYC Map]]
- [[Application and Completeness Map]]
- [[Appraisal and Sanction Map]]
- [[Documentation and Security Map]]
- [[Platform Security and Operations Map]]

