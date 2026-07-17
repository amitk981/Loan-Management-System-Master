# Import and Compatibility Graph

```text
disbursements.models
  -> communications.models.DisbursementAdviceDeliveryReceipt (shallow alias)

disbursements.modules.disbursement_advice
  -> communications.models.DisbursementAdviceDeliveryReceipt (canonical manager/query)
  -> communications.adapters (canonical Manual/Fake/Future seam)

communications.models
  -X-> disbursements Python imports
communications.adapters
  -X-> disbursements Python imports
```

The outbox and receipt use lazy Django relation strings to the disbursements-owned advice intent;
communications imports no disbursement model or policy module. Django's app registry contains the
receipt only under `communications`; the legacy disbursements name is the identical class and cannot
create a second table, manager, or query policy. Full template/render/dispatch/finalization policy
intentionally remains in the existing 009H2 module until 009H3B moves it.

Proof: `CommunicationAdvicePersistenceOwnershipTests` in
`terminal-logs/green-foundation-focused.txt` and `green-all-focused.txt`.
