# Migration State Manifest

Migration: `communications.0004_advice_outbox_and_receipt_owner`

## Retained receipt

- Canonical forward-state owner: `communications.DisbursementAdviceDeliveryReceipt`.
- Compatibility name: `disbursements.DisbursementAdviceDeliveryReceipt` is the same Python class,
  not a second registered model or persistence manager.
- Physical table: `disbursement_advice_delivery_receipts`.
- Primary key: `delivery_receipt_id`; a genuine delivered fixture's generated UUID is captured once
  and asserted equal after forward, reverse, and reapply.
- Unique facts retained: one-to-one `advice_intent`, `idempotency_key`, and `external_message_id`.
- Constraint retained: `advice_delivery_receipt_complete`.
- Database operations for owner transfer: none. `sqlmigrate` reports the custom state operation as
  non-SQL and contains no create, drop, rename, copy, update, or alter statement for the receipt
  table.

`CommunicationReceiptOwnerMigrationTests` begins at communications 0003/disbursements 0007, creates
a genuine public 009H2 sent receipt, records its columns/constraint names/id, and then proves:

| State | Receipt owner | Receipt signature/id | Outbox table count |
|---|---|---|---:|
| Pre-009H3A | disbursements | baseline | 0 |
| Forward | communications | identical | 1 |
| Reverse | disbursements | identical | 0 |
| Reapply | communications | identical | 1 |

## New outbox

Physical table: `communication_delivery_outboxes`.

It uniquely retains advice intent, communication identity, and idempotency key; channel; frozen
recipient address and SHA-256 digest; protected template relation plus code/version/checksum;
rendered subject/body; canonical payload digest; related entity type/id; pending/sent status; and
the all-or-none provider external id/status/accepted-at tuple. Database constraints are
`communication_outbox_complete` and `communication_outbox_provider_result_complete`; the related
entity lookup index is `communicati_related_0839f1_idx`.

Proof: `terminal-logs/green-migration.txt`, `migration-plan-and-sql.txt`, and
`migration-sync-final.txt`.
