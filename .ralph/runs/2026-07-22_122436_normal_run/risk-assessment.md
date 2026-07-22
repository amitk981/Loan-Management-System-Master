# Risk Assessment

Risk level: Medium

- Selected slice: 011C-extension-note-workflow
- Mode: normal_run
- Manual review required: independent Ralph validation required before commit.

## Risk analysis

- **Data integrity:** one `ExtensionNote` per `DefaultCase` is enforced by a one-to-one database constraint; the case pointer and transaction lock keep the retained current note coherent. Active effective dates reject model and queryset mutation.
- **Concurrency/idempotency:** exact replays return the retained note, changed replays conflict, and PostgreSQL five-way grant/expiry acceptance proves one note, audit, workflow transition, and review task.
- **Authority/object scope:** the mutation requires `defaults.extension.grant`, Credit Manager role, existing default read scope, and the defaults-owned object-scope query. Auditor and Credit Assessment access remains read-only.
- **Document isolation:** the stored foreign key must identify a generated `extension_note` `LoanDocument` belonging to the default case's exact loan application and backed by a document file. Existing download/object-permission regressions pass.
- **Financial/KYC isolation:** the workflow reads canonical principal/closure truth and never writes loan balances, ledger allocations, members, or KYC rows. Cure changes only the default workflow state and timestamp.
- **Scheduler/recovery separation:** expiry creates one existing-type `default_assessment` review task and never creates a Non-Payment Note or recovery decision.
- **Approval-policy gap:** source approval is conditional, but no extension-specific checker configuration/route exists. A-156 records the fail-safe no-route behavior: direct active grant with a null approver, with no inferred Sanction Committee authority.

## Residual risks and controls

- The orchestrator must rerun the declared PostgreSQL acceptance twice in isolated databases; local acceptance passed once with both expected tests.
- A future governed extension checker route must define its configuration owner and endpoint before draft/approved transitions are enabled. Existing active records and dates must remain immutable.
- No frontend was changed or required by this backend-only slice.
