# Monitoring Default and Recovery Map

> [!summary] Purpose
> Connect DPD, reminders, portfolio monitoring, missed-payment handling, grace and extension decisions, recovery approval and controlled security invocation across all layers.

## Traceability

- **Source:** [[sfpcl_client_brief#15.7 Repayment Monitoring|Repayment monitoring]] · [[sfpcl_client_brief#16. Default Handling|Default handling]]
- **Product requirements:** [[product-requirements#11.25 Monitoring, DPD and MIS|Monitoring and MIS]] · [[product-requirements#11.26 Default and Extension|Default and extension]] · [[product-requirements#11.27 Recovery|Recovery]]
- **User flow:** [[user-flows#30. User Flow 22 — Repayment Monitoring, DPD and CFO MIS|Monitoring and MIS]] · [[user-flows#31. User Flow 23 — Missed Repayment, Grace Period and Extension|Grace and extension]] · [[user-flows#32. User Flow 24 — Recovery Action: Shares and Blank-Dated Cheque|Recovery action]]
- **Functional specification:** [[functional-spec#11.11 M11 — Monitoring and MIS|Monitoring and MIS]] · [[functional-spec#11.12 M12 — Default and Recovery|Default and Recovery]]
- **Domain model:** [[domain-model#14. Monitoring and Default Domain|Monitoring, default and recovery domain]]
- **Data model:** [[data-model#20. Monitoring Tables|Monitoring tables]] · [[data-model#21. Default and Recovery Tables|Default and recovery tables]]
- **Information architecture:** [[information-architecture#9.9 Monitoring & Collections Module|Monitoring and collections module]] · [[information-architecture#9.10 Default & Recovery Module|Default and recovery module]]
- **Screen specification:** [[screen-spec#S50 — Monitoring Dashboard|Monitoring dashboard]] · [[screen-spec#S51 — DPD / Portfolio at Risk Screen|DPD and risk]] · [[screen-spec#S52 — Reminder Management Screen|Reminders]] · [[screen-spec#S53 — Default Case Detail|Default case]] · [[screen-spec#S54 — Grace Period and Extension Screen|Grace and extension]] · [[screen-spec#S55 — Note for Non-Payment Screen|Non-Payment Note]] · [[screen-spec#S56 — Recovery Action Approval Screen|Recovery approval]] · [[screen-spec#S57 — Security Invocation Screen|Security invocation]]
- **Component specification:** [[component-spec#16. Monitoring Components|Monitoring components]] · [[component-spec#17. Default and Recovery Components|Default and recovery components]]
- **Content specification:** [[content-spec#S34 — DPD Monitoring Dashboard|DPD content]] · [[content-spec#S35 — Reminder Queue|Reminder content]] · [[content-spec#S36 — Extension Note|Extension content]] · [[content-spec#S37 — Non-Payment Note|Non-Payment content]] · [[content-spec#S38 — Recovery Approval|Recovery content]]
- **Design system:** [[design-system#33.7 Repayment and Monitoring Pattern|Monitoring pattern]] · [[design-system#33.8 Default and Recovery Pattern|Default and recovery pattern]]
- **API contracts:** [[api-contracts#34. Monitoring and Reminder APIs|Monitoring APIs]] · [[api-contracts#35. Default and Recovery APIs|Default and recovery APIs]]
- **Auth and permissions:** [[auth-permissions#12.10 Monitoring and Default Permissions|Monitoring and recovery permissions]]
- **Codebase design:** [[codebase-design#18. Monitoring, Default and Recovery Modules|Monitoring, default and recovery modules]]
- **Security and privacy:** [[security-privacy#23. Recovery and Legal Security|Recovery and legal security]]
- **Test plan:** [[test-plan#14.10 Repayment, Interest and Monitoring API Tests|Monitoring API tests]] · [[test-plan#13.17 Default Workflow Tests|Default tests]] · [[test-plan#13.18 Recovery Workflow Tests|Recovery tests]]
- **Implementation roadmap:** [[implementation-roadmap#15. Release R6 — Repayment, Interest and Monitoring|R6 monitoring]] · [[implementation-roadmap#16. Release R7 — Default, Recovery, Closure and Compliance|R7 recovery]]

## Key Decisions and Open Issues

- Derive DPD from schedules and ledger history while preserving both SOP and operational buckets.
- Missed principal starts a three-month grace period; approved non-intentional cases may receive a one-year extension.
- Security invocation requires an approved recovery decision, evidence, audit and fair-conduct controls.
- Define intentionality evidence, recovery authority, share-sale and cheque procedures, step-up authentication, DPD cadence, “not recoverable,” settlement and write-off. See [[Open Decisions Index#Default Classification and Recovery Authority|recovery decisions]].

## Related Maps

- [[Documentation and Security Map]]
- [[Repayment and Interest Map]]
- [[Closure and Compliance Map]]
- [[Platform Security and Operations Map]]

