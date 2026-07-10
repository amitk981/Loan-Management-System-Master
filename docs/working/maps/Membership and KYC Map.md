# Membership and KYC Map

> [!summary] Purpose
> Connect member identity, member type, active-status evidence, nominees, witnesses, onboarding KYC and periodic re-KYC from source policy through delivery and testing.

## Traceability

- **Source:** [[sfpcl_client_brief#8.1 Who Can Apply|Who can apply]] · [[sfpcl_client_brief#8.4 KYC and Supporting Documents|KYC and supporting documents]] · [[sfpcl_client_brief#11. Active and Inactive Member Status|Active-member status]] · [[sfpcl_client_brief#17.4 KYC / AML|KYC and AML obligations]]
- **Product requirements:** [[product-requirements#11.3 Member and Borrower Master|Member and borrower master]] · [[product-requirements#11.4 Nominee and Witness|Nominee and witness]] · [[product-requirements#11.5 KYC and Re-KYC|KYC and re-KYC]]
- **User flow:** [[user-flows#9. User Flow 1 — Borrower Identification and Member Validation|Member validation]] · [[user-flows#34. User Flow 26 — Borrower Compliance and Re-KYC|Borrower compliance and re-KYC]]
- **Functional specification:** [[functional-spec#9.2 Member / Borrower Master|Member and borrower data]] · [[functional-spec#9.6 KYC Record|KYC record]] · [[functional-spec#11.2 M02 — Member and Borrower Master|Member and borrower module]]
- **Domain model:** [[domain-model#7.1 Member|Member]] · [[domain-model#7.2 IndividualMemberProfile|Individual profile]] · [[domain-model#7.3 ProducerInstitutionProfile|Producer Institution profile]] · [[domain-model#7.4 Nominee|Nominee]] · [[domain-model#7.5 Witness|Witness]] · [[domain-model#16.4 KYCReview|KYC review]]
- **Data model:** [[data-model#10.1 `members`|Members]] · [[data-model#10.2 `individual_member_profiles`|Individual profiles]] · [[data-model#10.3 `producer_institution_profiles`|Producer Institution profiles]] · [[data-model#10.4 `nominees`|Nominees]] · [[data-model#10.5 `witnesses`|Witnesses]] · [[data-model#12.1 `kyc_profiles`|KYC profiles]] · [[data-model#12.2 `kyc_documents`|KYC documents]] · [[data-model#23.6 `kyc_reviews`|KYC reviews]]
- **Information architecture:** [[information-architecture#7.1 Member|Member object]] · [[information-architecture#7.3 Nominee|Nominee object]] · [[information-architecture#7.4 Witness|Witness object]] · [[information-architecture#7.6 KYC Record|KYC object]] · [[information-architecture#9.3 Members & Borrowers Module|Members and borrowers module]]
- **Screen specification:** [[screen-spec#S05 — Member Directory|Member directory]] · [[screen-spec#S06 — Member Profile|Member profile]] · [[screen-spec#S08 — Nominee Detail Panel|Nominee detail]] · [[screen-spec#S09 — Witness Detail Panel|Witness detail]] · [[screen-spec#S16 — Active Member Verification|Active-member verification]] · [[screen-spec#S17 — KYC Verification|KYC verification]] · [[screen-spec#S65 — KYC / AML and Re-KYC Tracker|KYC and re-KYC tracker]]
- **Component specification:** [[component-spec#8.1 Member Search and Selector|Member search]] · [[component-spec#8.3 Member Profile Component|Member profile]] · [[component-spec#8.4 Active Member Assessment Component|Active-member assessment]] · [[component-spec#8.6 Nominee Details Component|Nominee details]] · [[component-spec#8.8 KYC Document Status Component|KYC document status]] · [[component-spec#19.3 KYC / Re-KYC Compliance Component|KYC compliance]]
- **Content specification:** [[content-spec#S05 — Member Directory|Member-directory content]] · [[content-spec#S06 — Member Profile|Member-profile content]] · [[content-spec#S43 — KYC / Re-KYC Tracker|KYC tracker content]] · [[content-spec#15.1 Borrower and Member Fields|Member field labels]]
- **Design system:** [[design-system#18.7 Sensitive Data Display|Sensitive-data display]] · [[design-system#30.1 File Upload Rules|File uploads]] · [[design-system#36.1 Borrower / Member View|Member view]] · [[design-system#39.2 Sensitive Document UX|Sensitive-document UX]]
- **API contracts:** [[api-contracts#13. Member APIs|Member APIs]] · [[api-contracts#14. Nominee APIs|Nominee APIs]] · [[api-contracts#16.1 Calculate Active Member Status|Active-member calculation]] · [[api-contracts#18. KYC APIs|KYC APIs]]
- **Auth and permissions:** [[auth-permissions#12.2 Member Permissions|Member permissions]] · [[auth-permissions#12.3 KYC Permissions|KYC permissions]] · [[auth-permissions#25.1 Member Module|Member access rules]] · [[auth-permissions#34.2 Members|Member endpoint permissions]]
- **Codebase design:** [[codebase-design#10.1 Member Registry Module|Member Registry module]] · [[codebase-design#10.2 Active Member Module|Active Member module]] · [[codebase-design#10.3 KYC Module|KYC module]] · [[codebase-design#24.1 `features/members`|Members frontend feature]]
- **Security and privacy:** [[security-privacy#7.1 Borrower / Member Personal Data|Member personal data]] · [[security-privacy#7.2 Nominee Personal Data|Nominee data]] · [[security-privacy#7.3 Witness Personal Data|Witness data]] · [[security-privacy#14.3 Masking Rules|Masking rules]] · [[security-privacy#20.1 Document Storage Requirements|Document controls]]
- **Test plan:** [[test-plan#13.5 Active Member Status Tests|Active-member tests]] · [[test-plan#14.4 Member and KYC API Tests|Member and KYC API tests]] · [[test-plan#16.17 E2E-017 — KYC/Re-KYC Cycle|KYC cycle E2E]] · [[test-plan#21.4 KYC and AML Controls|KYC control tests]]
- **Implementation roadmap:** [[implementation-roadmap#21.2 Business Master Tables|Business-master sequence]] · [[implementation-roadmap#Sprint 3 — Member and KYC|Member and KYC sprint]]

## Key Decisions and Open Issues

- Only a verified SFPCL member may proceed; active-member evidence and any relaxation must be preserved.
- KYC covers borrowers, nominees, witnesses and institutional authorized signatories.
- Sensitive identifiers and documents require encryption, masking, restricted download and audit.
- Confirm full-Aadhaar policy, KYC download roles, watermarking, bulk export, consent and final retention. See [[Open Decisions Index#Identity, Privacy and Access Decisions|identity and privacy decisions]].
- CKYC and credit-bureau processes remain future or configurable until confirmed.

## Related Maps

- [[Application and Completeness Map]]
- [[Eligibility and Loan Limit Map]]
- [[Documentation and Security Map]]
- [[Closure and Compliance Map]]
- [[Platform Security and Operations Map]]

