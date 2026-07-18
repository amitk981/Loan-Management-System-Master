# Ralph Handoff

## Last Run
2026-07-18_020218_repair

## Current Status
009H3A is complete. Communications now canonically owns the durable advice outbox and the retained
`DisbursementAdviceDeliveryReceipt` Django state. Migration `communications.0004` creates only the
outbox table and moves receipt state without receipt-table SQL, preserving the physical
`disbursement_advice_delivery_receipts` table, constraints, ids, relation, and historical rows
through forward, reverse, and reapply.

The outbox schema freezes one advice intent/communication/key plus channel, recipient/digest,
template/version/checksum provenance, rendered snapshots, canonical payload digest, related entity,
status, and complete provider-result tuple. Manual, Fake, and Future email adapters now derive one
logical provider identity solely from the stable key across changed payload and fresh instances;
rejection remains retryable. A policy-free disbursements model alias preserves existing imports.
All 24 focused foundation and retained 009H2 tests pass with two expected PostgreSQL-only skips;
Django check and migration sync pass. The public advice route, roles/scope, current truth, safe
audit, receipt/Communication behavior, and no-financial-side-effect contract are unchanged.

The combined 009H3B candidate passed its focused dispatcher/crash/template and twice-run
PostgreSQL evidence but was rejected at 2,118 changed lines against the 2,000-line limit. It is now
Superseded by dependency-ordered 009H3BA (dispatcher/outbox freeze) and 009H3BB (finalization/public/
race closure). Ralph's exact oversized-split semantics and queue-scope validators pass for the
corrected metadata-only rewrite; the original 009H3 parent remains unchanged.

Independent coverage initially failed five retained historical migration tests. The required
`communications.0004` dependency on `disbursements.0007` made communications a downstream leaf of
current application and credit state, so those tests' pre-migration app registries outran their
reversed physical schemas. The repair excludes communications from the two historical leaf
projections, matching their existing downstream-owner exclusions. The exact ordered repro is green,
all six implicated migration tests pass, and no production or migration file changed in repair.

## Next Run
Run 009H3BA, then 009H3BB. BA consumes the 009H3A schema without a second migration and owns the
dispatcher/template/render/outbox-freeze/provider boundary; BB completes communications-owned
finalization, the public matrix, both crash windows, and twice-run PostgreSQL five-caller proof.
Then run 009G4 and 009I in dependency order through terminal prerequisite 009H3BB. Both successors
are concrete and require another split before implementation if either forecast exceeds 1,350
changed lines.
