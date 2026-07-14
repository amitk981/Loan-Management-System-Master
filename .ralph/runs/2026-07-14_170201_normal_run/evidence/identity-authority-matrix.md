# 008E2 Identity, Authority, and Error Matrix

| Interface | Case | Expected / verified result |
|---|---|---|
| Capture | Canonical application borrower id + legal name | 200; id/name and Compliance maker frozen |
| Capture | Selected nominee, application witness, active user | 200; canonical owner name frozen |
| Capture | Arbitrary/wrong/cross-application/null id | 400 `VALIDATION_ERROR`; zero signature evidence |
| Capture | Changed live name after first capture | Frozen-name replay 200/zero-write; refreshed name 400 |
| Capture | Same signer mismatch -> signed/pending | 409 `CONFLICT`; unresolved row, checklist blocker, and ledgers unchanged |
| Capture | Exact unresolved mismatch replay | 200; zero-write |
| Resolve | Distinct Compliance maker and Company Secretary checker | 200 §6.3 action response; one immutable workflow id |
| Resolve | Same user after role change | 400 `VALIDATION_ERROR`; zero resolution evidence |
| Resolve | Capture-only / resolve-only / inactive / permission-only actor | 403 before signature-owner scope |
| Resolve | Authorized unknown, wrong-stage, unrelated, non-current id | Identical 404 `NOT_FOUND` contract |
| Resolve | Exact retained resolution replay | Same §6.3 response and workflow id; zero-write |
| Resolve | Changed retained resolution replay | 409 `CONFLICT`; retained result unchanged |

Evidence: focused RED/GREEN logs in `terminal-logs/`, final 16-test focused run, and both PostgreSQL
race logs. The response contract asserted by the public test is exactly:

```json
{
  "entity_type": "signature_record",
  "entity_id": "<retained signature UUID>",
  "previous_status": "mismatch",
  "new_status": "resolved",
  "workflow_event_id": "<retained workflow UUID>",
  "available_actions": []
}
```
