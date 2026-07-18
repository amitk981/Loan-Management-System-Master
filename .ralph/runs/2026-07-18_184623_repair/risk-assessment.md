# Risk Assessment

Risk level: High (inherited slice); Low repair-delta risk.

- Selected slice: `009H7-communications-dispatcher-interface-and-idempotency-closure`
- Mode: repair
- Demonstrated failure: one retained notification API integration test expected HTTP 200 while
  omitting the explicit `Idempotency-Key` that H7 intentionally requires.
- Repair: add one stable key to that test request. No production, migration, provider, financial,
  permission, frontend, or external-service behavior changed.
- Principal regression risk: weakening the endpoint to satisfy the old test would reintroduce
  implicit duplicate identity and could duplicate communication delivery. This repair avoids that
  risk by preserving the fail-closed endpoint and updating the stale caller contract.
- Verification: exact RED/GREEN reproduction, 14 focused API tests, Django check, migration sync,
  and focused compilation pass. Full backend coverage remains the independent acceptance gate.
- External effects: none. No real provider, network, deployment, data deletion, or git mutation was
  invoked.
- Protected/source paths: no protected file or `docs/source/**` path was modified.
