# Sanitized Advice Contract Results

- Exact replay: same actor/channel/current recipient and coherent owner evidence returns the retained
  response with zero provider or local writes.
- Changed replay: changed recipient, channel, template provenance, render snapshots, provider tuple,
  transfer, register, intent, account, or retained ledger evidence returns a safe conflict.
- Provider rejection/malformed result: retains at most the pending frozen outbox; creates no receipt,
  Communication, action, audit, workflow, or sent intent.
- Post-acceptance recovery: both pre-receipt and pre-Communication-commit failures roll back the
  complete local transaction; exact fresh retry uses the one accepted provider identity.
- Permissions: CFC-only and out-of-scope roles remain denied; current Credit Manager and scoped
  Senior Manager Finance authority remain accepted; inaccessible ids remain nondisclosing.
- Secrecy: general audit/workflow evidence contains no raw recipient, rendered subject/body, full
  UTR, provider message id, protected bank content, or advice amount. Recipient/content/provider/
  amount use masks or SHA-256 digests.
- Side effects: advice send/replay changes no money, transfer, account balance/status, register,
  checklist, repayment, schedule, interest, default, closure, or portal state.
- PostgreSQL: four total executions (two declared methods in each of two final runs) each record one
  winner, four clean losers, one provider identity, and one complete local chain.
