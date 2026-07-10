# Application and Completeness Map

> [!summary] Purpose
> Connect assisted, offline and digital intake to draft handling, required documents, completeness review, deficiency resolution, reference-number generation and the Loan Request Register.

## Traceability

- **Source:** [[sfpcl_client_brief#8.2 Application Channel|Application channels]] · [[sfpcl_client_brief#8.3 Loan Application Form|Application form]] · [[sfpcl_client_brief#8.5 Application Completeness Check|Completeness check]] · [[sfpcl_client_brief#8.6 Application Numbering|Application numbering]] · [[sfpcl_client_brief#8.7 Incomplete Applications|Incomplete applications]]
- **Product requirements:** [[product-requirements#11.7 Loan Application Intake|Application intake]] · [[product-requirements#11.8 Application Completeness and Deficiencies|Completeness and deficiencies]]
- **User flow:** [[user-flows#10. User Flow 2 — Initial Loan Request and Application Submission|Application submission]] · [[user-flows#11. User Flow 3 — Application Completeness Check and Reference Number Generation|Completeness and reference generation]]
- **Functional specification:** [[functional-spec#8.1 Loan Application States|Application states]] · [[functional-spec#9.5 Loan Application|Application data]] · [[functional-spec#10.2 Application Rules|Application rules]] · [[functional-spec#11.3 M03 — Loan Origination|Loan Origination module]]
- **Domain model:** [[domain-model#8.1 LoanApplication|LoanApplication]] · [[domain-model#8.2 LoanRequestRegisterEntry|Loan Request Register entry]] · [[domain-model#8.3 ApplicationDocument|ApplicationDocument]] · [[domain-model#8.4 Deficiency and RejectionNote|Deficiency and rejection]] · [[domain-model#21.1 Loan Application Lifecycle|Application lifecycle]]
- **Data model:** [[data-model#13.1 `loan_applications`|Loan applications]] · [[data-model#13.2 `system_sequences`|Reference sequence]] · [[data-model#13.3 `loan_request_register_entries`|Loan Request Register]] · [[data-model#13.4 `application_documents`|Application documents]] · [[data-model#13.5 `deficiencies`|Deficiencies]] · [[data-model#13.6 `rejection_notes`|Rejection notes]]
- **Information architecture:** [[information-architecture#7.5 Loan Application|Loan Application object]] · [[information-architecture#8.2 Application Status Values|Application statuses]] · [[information-architecture#9.2 Applications Module|Applications module]] · [[information-architecture#Application Queue|Application queue]] · [[information-architecture#Loan Request Register|Loan Request Register]]
- **Screen specification:** [[screen-spec#S10 — New Loan Application|New application]] · [[screen-spec#S11 — Application Draft Review|Draft review]] · [[screen-spec#S12 — Application Completeness Check|Completeness check]] · [[screen-spec#S13 — Loan Request Register|Loan Request Register]] · [[screen-spec#S14 — Deficiency / Rejection Note Builder|Deficiency and rejection builder]]
- **Component specification:** [[component-spec#9.1 Loan Application Form Component|Application form]] · [[component-spec#9.2 Application Reference Number Component|Reference number]] · [[component-spec#9.3 Loan Request Register Component|Loan Request Register]] · [[component-spec#9.4 Completeness Check Component|Completeness check]] · [[component-spec#9.5 Deficiency Note Component|Deficiency note]] · [[component-spec#9.6 Rejection Note Component|Rejection note]]
- **Content specification:** [[content-spec#S08 — New Loan Application|New-application content]] · [[content-spec#S09 — Application Completeness Check|Completeness content]] · [[content-spec#S10 — Loan Request Register|Register content]] · [[content-spec#15.4 Loan Application Fields|Application labels]]
- **Design system:** [[design-system#15. Application Shell|Application shell]] · [[design-system#16.3 Application Status Labels|Application statuses]] · [[design-system#18.6 Autosave and Drafts|Autosave and drafts]] · [[design-system#33.1 Initial Loan Request Pattern|Initial-request pattern]] · [[design-system#33.2 Completeness Check Pattern|Completeness pattern]]
- **API contracts:** [[api-contracts#19. Loan Application APIs|Application APIs]] · [[api-contracts#20. Application Document APIs|Application-document APIs]] · [[api-contracts#21. Deficiency and Rejection APIs|Deficiency and rejection APIs]]
- **Auth and permissions:** [[auth-permissions#12.4 Loan Application Permissions|Application permissions]] · [[auth-permissions#19.2 Application Object Access|Application object access]] · [[auth-permissions#20.1 Loan Application Workflow Permissions|Application workflow permissions]] · [[auth-permissions#25.2 Application Module|Application access rules]]
- **Codebase design:** [[codebase-design#11.1 Loan Application Module|Loan Application module]] · [[codebase-design#11.2 Reference Number Module|Reference Number module]] · [[codebase-design#24.2 `features/applications`|Applications frontend feature]]
- **Security and privacy:** [[security-privacy#20.1 Document Storage Requirements|Document storage]] · [[security-privacy#20.3 File Upload Validation|Upload validation]] · [[security-privacy#24.1 Immutable Audit Logs|Application audit events]] · [[security-privacy#36.4 Workflow Security|Workflow security acceptance]]
- **Test plan:** [[test-plan#14.5 Loan Application API Tests|Application API tests]] · [[test-plan#16.4 E2E-004 — Incomplete Application Returned and Resubmitted|Incomplete-return E2E]] · [[test-plan#17.1 Origination Gates|Origination gate tests]]
- **Implementation roadmap:** [[implementation-roadmap#11. Release R2 — Loan Origination and Credit Assessment|R2 origination]] · [[implementation-roadmap#21.3 Origination and Credit Tables|Origination data sequence]] · [[implementation-roadmap#Sprint 4 — Application Intake|Application-intake sprint]]

## Key Decisions and Open Issues

- Drafts require a technical identifier; the business reference is generated atomically after the agreed completeness gate.
- References are immutable, unique, audited and never reused.
- Deficiencies remain individually resolvable with full history.
- Reconcile the draft/reference constraint in [[data-model#13.1 `loan_applications`|loan applications]] with the post-completeness numbering rule.
- Reconcile application-state vocabularies, deficiency versus Annexure L usage, screen IDs and whether direct member submission is MVP scope.

## Related Maps

- [[Membership and KYC Map]]
- [[Eligibility and Loan Limit Map]]
- [[Appraisal and Sanction Map]]
- [[Documentation and Security Map]]
- [[Platform Security and Operations Map]]

