# Execution Plan

Selected slice: `009H4-communications-advice-evidence-and-legacy-replay-closure`

## Scope and seam

- Keep the public mutation interface at `DisbursementWorkflow.send_advice`; deepen the existing
  communications `CommunicationDispatcher` implementation so callers do not learn provider,
  provenance, legacy-replay, or reconciliation details.
- Add exactly one communications migration and no frontend/API-shape changes. Preserve physical
  receipt/outbox/history identifiers while replacing cross-app foreign keys with primitive UUID
  identities and adding communications-owned immutable provider acceptance plus full template
  provenance.
- Do not implement the asynchronous dispatcher/job/retry lifecycle reserved for `009H5`.

## TDD tracer bullets

1. Copy the two architecture-review probes into the public advice test surface. Save a focused RED
   run proving terminal missing-outbox replay currently calls the provider and a changed valid
   accepted tuple currently finalizes.
2. Add one public-interface test at a time for immutable provider acceptance, complete provenance,
   protected terminal-chain reconciliation, legacy/non-current nondispatch, and the real
   immediately-before-commit rollback window. Implement the minimum owner behavior after each RED
   result and retain RED/GREEN logs.
3. Add migration fixtures for coherent pre-outbox delivery, accepted-not-finalized, pending,
   malformed/ambiguous, and no-advice rows. Assert exact model/physical schema manifests and exact
   rows across forward, reverse to the declared safe boundary, and reapply; then implement the one
   reversible communications migration.
4. Extend the public mutation matrix for missing/extra/duplicate/changed/cross-linked outbox,
   provider, provenance, receipt, Communication, audit, workflow, and disbursement action facts.
   Preserve role/scope/current-contact/template/masking/no-financial-write behavior.

## Verification and evidence

- Run focused communications/advice/migration tests with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, plus the declared PostgreSQL five-caller tests
  twice when the local capability is available.
- Run Django check, migration sync, impacted backend tests, Python compilation, and relevant
  dependency/static guards. Do not run the complete backend suite or coverage; the orchestrator owns
  those authoritative gates.
- Run frontend typecheck, lint, tests, and build because Ralph validates every slice, even though no
  frontend change is planned.
- Save self-contained terminal evidence, changed-files, risk assessment, review packet, and final
  summary. Update the Epic 009 digest, assumptions only if needed, Ralph state/progress/handoff, and
  mark only `009H4` Complete. Recheck and sharpen the next one or two Not Started slices only if the
  source material already opened reveals a concrete gap.
