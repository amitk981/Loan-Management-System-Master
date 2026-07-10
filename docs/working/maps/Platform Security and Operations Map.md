# Platform Security and Operations Map

> [!summary] Purpose
> Map cross-cutting authentication, authorisation, privacy, audit, jobs, deployment readiness, monitoring, backup, recovery and incident-response controls protecting every capability.

## Traceability

- **Source:** [[sfpcl_client_brief#23. Operational System Implications|Operational implications]] · [[sfpcl_client_brief#24. Key Controls That Must Not Be Bypassed|Non-bypassable controls]]
- **Product requirements:** [[product-requirements#12.1 Security and Privacy|Security NFRs]] · [[product-requirements#12.3 Availability and Operations|Operations NFRs]] · [[product-requirements#12.5 Audit and Retention|Audit and retention NFRs]]
- **User flow:** [[user-flows#41. Audit Trail Requirements|Audit and evidence flow]] · N/A — deployment, backup and incident-response journeys have no dedicated user-flow heading.
- **Functional specification:** [[functional-spec#11.18 M18 — Administration and Access Control|Administration and access]] · [[functional-spec#16.1 Security|Security requirements]] · [[functional-spec#16.3 Availability and Reliability|Availability and reliability]]
- **Domain model:** [[domain-model#18. Audit and Versioning Domain|Audit and versioning]] · [[domain-model#25. Privacy and Access Control Model|Privacy and access control]] · N/A — no dedicated operations aggregate.
- **Data model:** [[data-model#9. Identity, Access and Organisation Tables|Identity and access data]] · [[data-model#26. Audit, Workflow and Versioning Tables|Audit and workflow data]] · [[data-model#29. Security and Privacy Model|Security and privacy data]]
- **Information architecture:** [[information-architecture#12. Permission and Access Control Architecture|Access-control IA]] · [[information-architecture#18. Audit Trail and Record Retention Architecture|Audit and retention IA]] · N/A — no operations-console IA.
- **Screen specification:** [[screen-spec#S00 — Login / Access Landing|Login]] · [[screen-spec#S73 — User and Role Management|User and role management]] · [[screen-spec#S74 — Audit Log Explorer|Audit explorer]] · N/A — no deployment/job/incident screens.
- **Component specification:** [[component-spec#22.3 Role and Permission Management Component|Role and permission component]] · [[component-spec#26. Security and Privacy Requirements for Components|Component security]] · N/A — no operations-console component family.
- **Content specification:** [[content-spec#S00 — Login / Access Landing|Login content]] · [[content-spec#S47 — Admin Settings|Admin content]] · [[content-spec#19. Audit Trail Content Specification|Audit content]]
- **Design system:** [[design-system#39. Security and Privacy Design Standards|Security and privacy design]]
- **API contracts:** [[api-contracts#11. Authentication API|Authentication APIs]] · [[api-contracts#12. User, Role and Team APIs|Administration APIs]] · [[api-contracts#42. Audit and Workflow APIs|Audit APIs]] · N/A — health, job-run, incident and release endpoints are not specified.
- **Auth and permissions:** [[auth-permissions#3. Core Access-Control Philosophy|Access-control model]] · [[auth-permissions#35. Security Headers and API Hardening|API hardening]]
- **Codebase design:** [[codebase-design#9. Foundation Modules|Foundation modules]] · [[codebase-design#34. Scheduled Job Design|Scheduled jobs]] · [[codebase-design#39. Security Codebase Design|Security codebase]] · [[deployment-ops#11. CI/CD Pipeline|CI/CD]] · [[deployment-ops#17. Monitoring and Observability|Monitoring]]
- **Security and privacy:** [[security-privacy#30. Infrastructure and Deployment Security|Infrastructure security]] · [[security-privacy#38. Security Operations Runbooks|Security runbooks]] · [[security-privacy#40. Recommended MVP Security Baseline|MVP baseline]]
- **Test plan:** [[test-plan#18. Security and Privacy Test Plan|Security tests]] · [[test-plan#25. Operational Test Plan|Operational tests]]
- **Implementation roadmap:** [[implementation-roadmap#10. Release R1 — Core Platform Foundation|R1 foundation]] · [[implementation-roadmap#17. Release R8 — Reports, Hardening, UAT and Go-Live|R8 hardening]] · [[implementation-roadmap#24. Security Implementation Sequencing|Security sequence]]

## Key Decisions and Open Issues

- Backend enforcement combines role, team, object, workflow state, approval authority and sensitive-data rules.
- Critical approvals, audit events, custody movements and financial actions remain append-only and idempotent.
- Production requires separated environments, controlled secrets, monitored dependencies, tested backup/restore and incident runbooks.
- Decide JWT transport, token lifetimes, lockout and MFA; Aadhaar handling; hosting/providers; scanning/SIEM; measurable availability, RPO/RTO and support targets.
- Add missing canonical data/API/UI surfaces for sessions, job runs, incidents, releases, access reviews and support cases where needed.

## Related Maps

- [[Membership and KYC Map]]
- [[Application and Completeness Map]]
- [[SAP and Disbursement Map]]
- [[Repayment and Interest Map]]
- [[Monitoring Default and Recovery Map]]
- [[Closure and Compliance Map]]
