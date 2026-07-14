# Source-field traceability

| Screen fact | Frozen owner / implementation | Verification |
|---|---|---|
| S23 entry number | `CreditSanctionRegisterEntry.entry_number`, assigned once by the register model | Backend register API tests assert the `CSR-` value and immutability |
| S23 folio, loan type, purpose, risk | Approval review package copied into `source_review_facts_json` before terminal routing | Backend test mutates member, application, and appraisal owners and re-reads unchanged values |
| S23 approver decision/comment/time | Terminal approval actions copied into `approver_decisions_json` | Backend and UI tests assert comments and non-null/displayed action times |
| S23 rejection reason and conditions | Terminal case/decision values copied into `terminal_facts_json` | Approved, rejected, and null behavior covered; the test mutates the live sanction decision after creation |
| S23 communication status/date | Terminal communication copied into `communication_json` in the same transaction | Backend test mutates live delivery status/time and proves the register stays pending/unsent |
| S25 borrower, financial impact, requester | Exception creation copies routed review facts and actor identity into `source_facts_json` | Backend test mutates member/requester owners and proves unchanged output |
| S25 decision date | Closed approval-case timestamp, serialized only after closure | Backend test compares the returned date with the frozen case closure date |
| S25 supporting evidence | Frozen document metadata only | UI and browser specs assert metadata and prove no inferred download control |

Sources: screen specification S23/S25; functional specification M05-FR-006/M05-FR-009; API
contracts §§6–8, 25.9, 25.10. Public contract detail is recorded in
`docs/working/API_CONTRACTS.md`.
