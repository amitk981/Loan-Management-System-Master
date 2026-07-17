# 009E2 Dependency Graph

```text
POST /loan-accounts/{id}/disbursements/initiate
  -> DisbursementWorkflow (only public mutation owner)
     -> private _initiate engine
        -> typed DisbursementReadinessModule.evaluate_for_initiation
           -> loan-account owner
           -> approval owner
           -> legal/signature owner
           -> security owner
           -> SAP owner
           -> borrower-bank verification owner
           -> source-bank governance owner
        -> lock and reconcile amount/account/bank identities
        -> freeze Disbursement + AuditLog + WorkflowEvent + CFC Notification

Later readiness/CFC projection
  -> has_cfc_scope
     -> exactly one pending instruction
     -> exact row/audit/workflow/task identity and state
     -> exact maker, amount, bank, readiness and idempotency evidence
     -> exact request-id trace and normalized-comment SHA-256
```

Duplicate keys are resolved after payload validation and maker authorization but before current
readiness/bank evaluation. An identical payload returns the retained original response without writes;
a changed payload returns `CONFLICT`.
