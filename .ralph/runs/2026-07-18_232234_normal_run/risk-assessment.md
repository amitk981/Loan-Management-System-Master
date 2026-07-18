# Risk Assessment

Risk level: High

- Selected slice: 009H9C-communication-channel-interface-and-provider-evidence-closure
- Mode: normal_run
- Standing approval: confirmed; no owner veto exists for this slice.
- Manual review required: orchestrator/owner should review the migration and provider-evidence
  contract before promotion from `staging` to `main`.

## Material risks and controls

- **Duplicate external delivery:** provider acceptance is frozen once per job before mutable sent
  projections. Exact worker replay reconciles the immutable evidence and bypasses provider entry.
  PostgreSQL five-worker races passed for Email and SMS twice.
- **Wrong-channel or sensitive SMS:** channel/template coherence and recipient validation execute
  before any Communication/job/audit write. SMS has a separate adapter/payload and rejects PAN,
  Aadhaar, bank/account, cheque, IFSC, and ciphertext variables/rendered values. Static tests reject
  provider calls outside the dispatcher.
- **Idempotency response drift:** replay classification now comes from the dispatcher while holding
  its idempotency lock, not from an unlocked pre-query. PostgreSQL five-caller races retain one
  ordinary original response and four source §45.2 replay wrappers for both channels.
- **Migration/history:** migration 0012 adds one generic evidence table and backfills accepted
  pre-migration generic jobs with explicit `legacy:retained-generic-acceptance` identity. It does not
  rewrite advice attempts/outboxes. Migration sync and focused forward migration tests pass.
- **Provider identifier collision:** provider message identifiers are not globally unique across
  adapters; singularity is enforced by the evidence-to-job one-to-one relationship. The evidence
  digest also binds adapter identity and all accepted facts.
- **Residual limitation:** phone/courier return stable unsupported-channel validation because this
  generic endpoint has no source-owned manual-task workflow. No provider or sent claim is made.

No frontend, dependency, source-document, protected-file, or external-provider changes were made.
