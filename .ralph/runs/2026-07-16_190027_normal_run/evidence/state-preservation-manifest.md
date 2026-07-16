# SAP State Preservation Manifest

The focused migration-executor test created one synthetic completed SAP request and one synthetic
active SAP code in the exact pre-009B3A Finance migration state, then migrated forward to
`sap_workflow.0001_sap_model_owner_state` and backward to no SAP migration.

## Exact identities compared in both directions

| Category | Preserved values |
|---|---|
| Physical schema | `sap_customer_profile_requests`, `sap_customer_codes` |
| Counts and keys | request/code row counts and both UUID primary keys |
| Source relations | application, member, requester, assignee, workbook, communication, task, and customer-code foreign keys |
| Retained secrets | synthetic Aadhaar ciphertext token and PAN ciphertext token (compared exactly; plaintext was not materialised) |
| File/delivery truth | workbook checksum, delivery checksum, delivery reference, workbook snapshot id, and assignee snapshot id |
| Completion truth | supplied/omitted-aware completion digest, status, send timestamp, completion timestamp, reuse flag, customer/vendor code identity |
| Evidence | audit entity/action/actor and workflow entity/name/state/actor |
| Downstream state | `LoanAccount.sap_customer_code` resolves to `sap_workflow` forward and `finance` backward while retaining the same physical target table |

Every comparison passed. The migration produced no data or schema SQL; `state-only-sql-proof.log`
contains Django's SQL rendering proof. `green-migration-preservation.log` contains the executor
result, and `migration-graph.log` contains the fresh migration plan.

## Database operation manifest

- Table creates: 0
- Table deletes: 0
- Table renames: 0
- Column/index/constraint changes: 0
- Row copies/deletes/updates: 0
- Decryption/re-encryption/checksum rewrites: 0
- Django state owner changes: 2 models and the existing relation references to those models
