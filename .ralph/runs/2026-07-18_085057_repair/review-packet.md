# Review Packet: 2026-07-18_085057_repair

## Result
Repair complete pending independent orchestrator revalidation

## Slice
009H3BA-communications-dispatcher-outbox-freeze

## Failure and Cause

Complete coverage failed only
`CommunicationReceiptOwnerMigrationTests.test_receipt_row_and_schema_survive_forward_reverse_and_reapply`
with a missing outbox table. The test had correctly reversed communications from `0004` to `0003`,
then incorrectly invoked the current public dispatcher to create historical receipt data. The
current dispatcher must query the `0004` outbox, so the failure was deterministic test-isolation
drift rather than a production migration defect.

## Repair

The test now seeds one deterministic receipt with the historical app-registry model after reversal.
It compares all eight retained receipt fields, the exact primary key, columns, constraints, and
outbox table count through forward migration, reverse, and reapply. No production or migration code
changed, and the dispatcher still fails closed if its required durable outbox schema is absent.

## Traceability

- 009H3A's retained schema/row-identity contract requires the receipt's exact physical table,
  constraints, id, relationship, and values to survive its state-only ownership transfer. The
  strengthened migration test verifies that exact contract at the historical model seam.
- 009H3BA requires the `0004` outbox before every provider call. Avoiding the current route in a
  deliberately pre-`0004` fixture preserves—not weakens—that durable-freeze requirement.
- The focused current public/dispatcher tests verify that successful advice still traverses the
  outbox and that no production behavior changed.

## Verification

- Exact failure: reproduced before repair; exact test passes after repair.
- 29 focused migration/communications/public tests: pass, with two expected 009H3BB PostgreSQL
  skips.
- Django check and migration sync: pass.
- Python compile, dependency direction, whitespace, protected paths, and diff scope: pass.
- Frontend gates and complete coverage: delegated to independent orchestrator revalidation because
  the repair has no frontend change and agents must not repeat complete backend coverage.

## Reviewer Focus

Confirm the historical fixture uses only the projected old receipt model and that the test finishes
at `communications.0004`, leaving current schema available to subsequent tests. Confirm no
production dispatcher/migration diff was introduced by repair.

## Recommended Next Action
Run authoritative independent revalidation and let the orchestrator commit. Then execute the
already-concrete 009H3BB, followed by 009G4 and 009I in dependency order.
