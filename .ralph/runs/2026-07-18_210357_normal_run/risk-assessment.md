# Risk Assessment

Risk level: High

- Selected slice: 009H9A-queued-advice-migration-provenance-closure
- Mode: normal_run
- Manual review required: independent orchestrator validation before commit.

## Risk

The slice changes an already-committed pre-release data migration. A false positive could bless
reconstructed legacy template facts; a false negative could make migration 0009 reject a valid H5
queued job and block deployment.

## Controls

- Corrected migration 0008 in place, before the 0009 operation that otherwise aborts; no unreachable
  later repair migration was added.
- Verification requires exact outbox/job/advice/payload relationships, complete actor/request facts,
  pristine queued/zero-attempt state, no provider/receipt/final evidence, and an internally
  recomputed frozen-template checksum.
- Missing and one-field-drifted evidence remains fail-closed as legacy-partial and has its untrusted
  snapshot cleared.
- Exact before/after manifests prove old and current fields across forward, current leaves, safe
  reverse, and reapply.
- Retained public tests prove legacy rows remain nondispatching, operator-blocked, and excluded from
  borrower portal current/download truth.

## Non-impact

No schema, current model, API, frontend, provider call, receipt, Communication, action, audit,
workflow, financial, or borrower state changed. Tests use only synthetic identities and addresses.
