# Compatibility and Owner Proof

- `SapCustomerCode` and `SapCustomerProfileRequest` report `sap_workflow` as their runtime app
  label and retain their Finance-era physical table and constraint names.
- `finance.models` contains only the compatibility import, its export list, and documentation. It
  defines no class, function, manager, query, action, storage, adapter, or decision policy.
- Both legacy exported names are object-identical to the canonical `sap_workflow.models` classes.
- The public SAP module imports its model state directly from `sap_workflow`; existing Finance route
  and orchestration policy remains unchanged for the explicitly dependent 009B3B slice.
- `loans.LoanAccount.sap_customer_code` resolves directly to the canonical class.

Verified by `SapRuntimeModelOwnershipTests` and the 101-test impacted backend run recorded in
`evidence/terminal-logs/impacted-backend-tests.log`.
