# Review-only RED probes

Backend interpreter: `/Users/amitkallapa/LMS/.ralph/venv/bin/python`

## Stable provider key / changed payload

Command: run `review_probe_adapter_idempotency.py` through `manage.py shell`.

```text
REPRODUCED: one stable idempotency key can identify two provider messages when acceptance precedes durable receipt retention.
idempotency_key=disbursement-advice:eddf42df-078f-49fd-9a9a-9c41ef03028b
first_external_message_id=manual:eed670f9-0619-58ee-8212-99c7a416b721
retry_external_message_id=manual:0904352c-c3a6-59b3-8899-78c5d446132c
same_logical_provider_identity=False
```

Exit status: `1` (expected review reproduction).

## Source-bank rationale redaction

Command: run `review_probe_source_bank_reason.py` through `manage.py shell`.

```text
REPRODUCED: formatted bank numbers and unrelated field-encryption tokens pass the rationale validator and can enter audit/version evidence.
unsafe_reason_count=2
accepted_unsafe_reasons=['Move treasury funds to account 1234-5678-9012.', 'Investigate unrelated field:v2:k9:secret-ciphertext-token.']
```

Exit status: `1` (expected review reproduction).

These probes diagnose reviewed production behavior only. No product code was changed and no GREEN
claim is made; corrective slices own the fixes.
