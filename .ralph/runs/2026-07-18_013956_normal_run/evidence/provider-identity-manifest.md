# Provider Identity Manifest

All adapters expose the same interface:

`send_email(EmailDeliveryPayload, idempotency_key) -> EmailDeliveryResult`

| Adapter | External behavior | Stable identity source | Network |
|---|---|---|---|
| Manual | deterministic accepted result | Manual namespace + idempotency key | none |
| Fake | deterministic accepted test result | Fake namespace + idempotency key | none |
| Future | delegates the exact payload/key contract | supplied transport contract | not introduced |

The shared contract mutates the email subject while retaining the key and constructs a fresh adapter
for every call. Each adapter returns the same logical external id and `sent` status for exact and
changed payloads under that key. Payload conflict remains the responsibility of 009H3B's durable
outbox dispatcher, not the provider-identity adapter.

A Future transport rejects its first attempt and accepts the second. The first call raises with no
fabricated `EmailDeliveryResult`; the same adapter/key remains retryable. Retained 009H2 rejection
tests separately prove no receipt, Communication, audit, workflow, or sent intent is created after
provider rejection.

Proof: `terminal-logs/red-adapters.txt`, `green-adapters.txt`, and `green-all-focused.txt`.
