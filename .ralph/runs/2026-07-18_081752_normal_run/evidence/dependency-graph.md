# One-way Advice Dependency Graph

```text
public disbursement route
  -> DisbursementWorkflow.send_advice
    -> disbursements.modules.disbursement_advice
       - authenticates and locks current financial/upstream facts
       - builds frozen DisbursementAdviceContext primitives
       - consumes immutable AdviceDeliveryDecision
       - retains transitional final ledgers (removed by 009H3BB)
      -> communications.modules.communication_dispatcher
         - resolves/validates approved effective template
         - validates exact merge variables and protected values
         - renders subject/body
         - commits/reconciles CommunicationDeliveryOutbox
         - invokes Manual/Fake/Future adapter
         - validates and retains provider result
```

Static AST proof: `communication_dispatcher`, communications models, and communications adapters
contain no executable `sfpcl_credit.disbursements` import. The existing outbox model's lazy string
relation is schema metadata from 009H3A, not an executable policy dependency. No new migration was
introduced. The transitional receipt/Communication/audit finalization remains explicitly allocated
to 009H3BB.

