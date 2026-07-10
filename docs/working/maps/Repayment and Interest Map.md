# Repayment and Interest Map

> [!summary] Purpose
> Connect repayment capture, allocation, reconciliation, interest accrual, invoicing and capitalisation across business policy, data, interfaces, security, tests and delivery.

## Traceability

- **Source:** [[sfpcl_client_brief#15. Stage 6: Monitoring and Repayment|Monitoring and repayment]]
- **Product requirements:** [[product-requirements#11.23 Repayment|Repayment requirements]] · [[product-requirements#11.24 Interest, Accrual and Capitalisation|Interest requirements]]
- **User flow:** [[user-flows#27. User Flow 19 — Direct Repayment by Farmer|Direct repayment]] · [[user-flows#28. User Flow 20 — Repayment Through Subsidiary Deduction|Subsidiary deduction]] · [[user-flows#29. User Flow 21 — Interest Invoicing, Accrual and Capitalisation|Interest lifecycle]]
- **Functional specification:** [[functional-spec#11.9 M09 — Repayment and Receipting|Repayment and Receipting]] · [[functional-spec#11.10 M10 — Interest and Accounting|Interest and Accounting]]
- **Domain model:** [[domain-model#13.4 Repayment and Allocation|Repayment and allocation]] · [[domain-model#13.5 InterestInvoice, AccrualEntry and InterestCapitalisation|Interest domain]]
- **Data model:** [[data-model#18. Loan Account and Terms Tables|Schedules and rate histories]] · [[data-model#19. Finance, SAP, Disbursement and Repayment Tables|Repayment and interest records]]
- **Information architecture:** [[information-architecture#9.8 Repayments & Accounting Module|Repayments and accounting module]]
- **Screen specification:** [[screen-spec#S43 — Repayment Schedule Screen|Repayment schedule]] · [[screen-spec#S44 — Direct Repayment Entry|Direct repayment]] · [[screen-spec#S45 — Subsidiary Deduction Reconciliation|Subsidiary reconciliation]] · [[screen-spec#S46 — Loan Ledger|Loan ledger]] · [[screen-spec#S47 — Interest Accrual Screen|Interest accrual]] · [[screen-spec#S48 — Yearly Interest Invoice Screen|Interest invoice]] · [[screen-spec#S49 — Interest Capitalisation Screen|Capitalisation]]
- **Component specification:** [[component-spec#15. Repayment Components|Repayment and interest components]]
- **Content specification:** [[content-spec#S30 — Direct Repayment Posting|Direct repayment content]] · [[content-spec#S31 — Subsidiary Deduction Posting|Subsidiary content]] · [[content-spec#S32 — Interest Invoice|Invoice content]] · [[content-spec#S33 — Monthly Accrual Entry|Accrual content]] · [[content-spec#16.9 Interest Capitalisation Message|Capitalisation message]]
- **Design system:** [[design-system#33.7 Repayment and Monitoring Pattern|Repayment and monitoring pattern]]
- **API contracts:** [[api-contracts#32. Repayment APIs|Repayment APIs]] · [[api-contracts#33. Interest APIs|Interest APIs]]
- **Auth and permissions:** [[auth-permissions#12.9 SAP and Finance Permissions|Finance, repayment and interest permissions]]
- **Codebase design:** [[codebase-design#17. Repayment and Interest Modules|Repayment and interest modules]]
- **Security and privacy:** [[security-privacy#22.2 Repayment Controls|Repayment controls]] · [[security-privacy#22.3 Interest Controls|Interest controls]]
- **Test plan:** [[test-plan#13.15 Repayment Capture and Allocation Tests|Repayment tests]] · [[test-plan#13.16 Interest Engine Tests|Interest tests]]
- **Implementation roadmap:** [[implementation-roadmap#15. Release R6 — Repayment, Interest and Monitoring|R6 servicing]]

## Key Decisions and Open Issues

- Support direct and subsidiary receipts with unique references, evidence, matching and reconciliation.
- Allocate partial repayment principal-first and update ledger/outstanding atomically.
- Preserve rate snapshots, unique monthly accruals and once-per-year capitalisation after 30 April.
- Confirm benchmark, spread, reset cadence, day count, penal rate, fees, tax, invoice owner, charge waterfall, excess repayment and NACH scope. See [[Open Decisions Index#Interest, Penal Charges and Fees|interest decisions]].

## Related Maps

- [[SAP and Disbursement Map]]
- [[Monitoring Default and Recovery Map]]
- [[Closure and Compliance Map]]
- [[Platform Security and Operations Map]]

