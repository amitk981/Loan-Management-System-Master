# Provider Acceptance Rollback / Retry Trace

1. 009G2 has already retained a pending advice UUID.
2. A fresh Fake adapter accepts a canonical payload keyed by that UUID.
3. Audit creation is forced to raise after acceptance; the database transaction rolls back.
4. No communication/link/audit/workflow survives and the advice intent remains `pending`.
5. A newly constructed Fake adapter receives the same UUID, created time, recipient, rendered
   subject/body, and related disbursement facts.
6. It returns the exact same provider message id, status, and accepted time.
7. Retry persists one communication using the original pending UUID and marks that intent `sent`.

Verified by
`test_fresh_adapter_retry_reuses_provider_receipt_after_post_acceptance_rollback`; RED and GREEN
outputs are retained in `terminal-logs/delivery-rollback-red.log` and
`terminal-logs/delivery-rollback-green.log`.

