# Closure and Compliance Map

> [!summary] Purpose
> Connect financial settlement, NOC, security return, unpledging, archival and recurring statutory-control evidence across the product and engineering specification.

## Traceability

- **Source:** [[sfpcl_client_brief#15.4 Full Repayment and Closure|Full repayment and closure]] · [[sfpcl_client_brief#17. Statutory Compliance Required by SFPCL|Statutory compliance]]
- **Product requirements:** [[product-requirements#11.28 Closure, NOC, Security Return and Archive|Closure requirements]] · [[product-requirements#11.29 Compliance|Compliance requirements]]
- **User flow:** [[user-flows#33. User Flow 25 — Full Repayment, Closure, NOC and Security Return|Closure flow]] · [[user-flows#34. User Flow 26 — Borrower Compliance and Re-KYC|Borrower compliance]] · [[user-flows#35. User Flow 27 — Company Statutory Compliance Monitoring|Company compliance]]
- **Functional specification:** [[functional-spec#11.13 M13 — Closure and Archival|Closure and Archival]] · [[functional-spec#11.14 M14 — Compliance and Audit|Compliance and Audit]]
- **Domain model:** [[domain-model#15. Closure Domain|Closure domain]] · [[domain-model#16. Compliance Domain|Compliance domain]]
- **Data model:** [[data-model#22. Closure Tables|Closure tables]] · [[data-model#23. Compliance Tables|Compliance tables]]
- **Information architecture:** [[information-architecture#9.11 Closure & NOC Module|Closure and NOC module]] · [[information-architecture#9.12 Compliance Module|Compliance module]]
- **Screen specification:** [[screen-spec#S58 — Loan Closure Screen|Loan closure]] · [[screen-spec#S59 — NOC Generation Screen|NOC]] · [[screen-spec#S60 — Security Return / Unpledge Screen|Security return]] · [[screen-spec#S61 — Archive Screen|Archive]] · [[screen-spec#S62 — Compliance Dashboard|Compliance dashboard]]
- **Component specification:** [[component-spec#18. Closure Components|Closure components]] · [[component-spec#19. Compliance Components|Compliance components]]
- **Content specification:** [[content-spec#S39 — Loan Closure|Closure content]] · [[content-spec#S40 — Compliance Dashboard|Compliance content]]
- **Design system:** [[design-system#33.9 Closure Pattern|Closure pattern]] · [[design-system#36.6 Auditor View|Auditor view]]
- **API contracts:** [[api-contracts#36. Closure APIs|Closure APIs]] · [[api-contracts#37. Compliance APIs|Compliance APIs]]
- **Auth and permissions:** [[auth-permissions#12.11 Closure Permissions|Closure permissions]] · [[auth-permissions#12.12 Compliance Permissions|Compliance permissions]]
- **Codebase design:** [[codebase-design#19. Closure and Compliance Modules|Closure and compliance modules]]
- **Security and privacy:** [[security-privacy#26. Data Retention and Archival|Retention and archival]] · [[security-privacy#34. Compliance Security Controls|Compliance security]]
- **Test plan:** [[test-plan#13.19 Closure Module Tests|Closure tests]] · [[test-plan#13.20 Compliance Module Tests|Compliance tests]]
- **Implementation roadmap:** [[implementation-roadmap#16. Release R7 — Default, Recovery, Closure and Compliance|R7 closure and compliance]]

## Key Decisions and Open Issues

- Settlement requires principal, interest and applicable charges; NOC and security release must be evidenced and archived.
- Closed records remain read-only and loan files are retained for at least eight years.
- Compliance tasks require frequency, owner, due date, evidence, reviewer, status and audit.
- Resolve whether NOC/security return precede final closure or follow it; use explicit settlement, closure-in-progress, closed and archived states. See [[Open Decisions Index#Closure Sequencing|closure decision]].
- Confirm KYC retention, money-lending jurisdiction, write-off/settlement treatment, signers and archive locations.

## Related Maps

- [[Repayment and Interest Map]]
- [[Monitoring Default and Recovery Map]]
- [[Membership and KYC Map]]
- [[Platform Security and Operations Map]]

