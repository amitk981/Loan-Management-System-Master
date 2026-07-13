# Epic 006 Functional-ID Spot Check

| Requirement | Review result | Evidence / owner |
|---|---|---|
| M04-FR-001 | Explicitly deferred | A-053; 012EA owns idempotent appraisal-task creation after application number generation. |
| M04-FR-002 | Explicitly deferred | A-053; 012EA owns Deputy Manager Finance task assignment. |
| M04-FR-003 | Implemented with explicit assumption | A-054 uses application `created_at` as the receipt-time proxy until governance resolves receipt vs completeness confirmation. |
| M04-FR-004 | Implemented | Eligibility checklist/result API and substantive pass/fail/manual-evidence tests; frontend fidelity remains 006H3. |
| M04-FR-005 | Implemented | Stored shareholding-based limit with boundary/configuration tests. |
| M04-FR-006 | Implemented | Stored land-based limit with cultivated-acreage consistency tests. |
| M04-FR-007 | Implemented | Backend lower-of-two calculation and below/equal/above tests. |
| M04-FR-008 | Implemented | Appraisal recommendation amount/tenure/security/repayment facts; 006H2 must repair the existing-draft PATCH path. |
| M04-FR-009 | Implemented | Required repayment-capacity and linked risk facts with rollback/redaction tests. |
| M04-FR-010 | Behavior implemented; assurance open | Credit Manager review gates sanction, but 006E4/006F4/006G2 must close legacy repair, PostgreSQL outcomes, and the case handoff/read contract. |
| M04-FR-011 | Behavior implemented; assurance open | Credit Manager rejection creates an unsent rejection note and immutable history; 006E4/006F4 must close legacy-history and race assurance. |

Epic 006 must not be marked complete before 006E4, 006F4, 006G2, 006H2, 006H3, and 006X. No
requirement ID is silently omitted: M04-FR-001/002/003 remain explicitly owned by A-053/A-054.
