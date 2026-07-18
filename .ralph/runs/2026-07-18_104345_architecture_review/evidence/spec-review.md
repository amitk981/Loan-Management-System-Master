# Spec Review

## Findings

1. **High — legacy/terminal redispatch:** preserved delivered rows have no migrated outbox; an
   absent outbox re-enters the provider path and commits new accepted outbox truth before conflict.
2. **High — mutable provider acceptance:** a different valid provider id/time in a sent pre-receipt
   outbox is trusted and becomes receipt/Communication/audit/workflow truth.
3. **Medium — partial provenance freeze:** the outbox retains a mutable template FK plus checksum,
   not every named original template provenance value required by 009H3BA.
4. **Medium — partial migration guard:** 009G4's future-owner prevention misses module constants and
   other indirection.
5. **High — no communication job/retry lifecycle:** the Epic 009 communication job and integrations
   queued/sending/failed/retrying/backoff contract remain absent.

Thirty-four retained tests pass; three review probes fail and directly reproduce findings 1, 2,
and 4. No material unrelated scope creep was found. BR-054/M08-FR-010 and INT-COMM-001-003 remain
partial until 009H4/009H5; 009G4's source-independent guard acceptance remains partial until 009G5.

Worst severity: High. Three High and two Medium findings.
