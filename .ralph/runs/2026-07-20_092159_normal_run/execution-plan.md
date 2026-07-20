# Execution Plan

Selected slice: 010H-interest-capitalisation-after-30-april

## Boundary

Implement only the backend/API capitalisation capability declared by slice 010H. No frontend,
invoice/accrual recalculation, new approval policy, provider call, or unrelated servicing change.

## Public behaviours to prove

1. A scoped finance caller can preview one loan/FY as of a supplied date; eligibility and unpaid
   amount come from retained issued invoices, and preview performs zero writes.
2. A final request after 30 April requires `finance.interest_capitalise`, loan scope, and a bounded
   `Idempotency-Key`; it locks source/account truth and rejects caller-supplied money.
3. Finalisation creates one immutable loan/FY capitalisation, raises principal/total outstanding by
   exactly eligible unpaid interest, records source snapshots, appends one immutable ledger row,
   queues one official email job, stores one hard-copy PDF artifact, and writes one audit record in
   the same transaction.
4. Exact replay returns the retained response; changed/cross-loan replay, cutoff/paid/zero/missing
   source/configuration, permission/scope denial, duplicate FY, and communication setup failure are
   zero-write failures.
5. Existing invoice/accrual snapshots remain unchanged, account/ledger reads expose the new
   principal movement, later interest calculations read the revised account principal, and a real
   PostgreSQL two-caller race retains one financial chain.

## TDD sequence

1. Add one public API test for preview zero-write and run it RED; implement the minimum preview path
   and run GREEN.
2. Add one public API test for successful finalisation/replay and run it RED; implement immutable
   models, migration, atomic service, views/routes, permission catalogue entry, document/email/audit
   evidence, and run GREEN.
3. Add cutoff, paid/zero, duplicate/changed replay, permission/scope, missing configuration,
   provider/job retry, reverse-consumer, and snapshot immutability tests one behavioural group at a
   time, keeping focused tests green.
4. Add the declared PostgreSQL contention test and run collection/local feedback; retain the exact
   test label for the orchestrator's authoritative twice-run PostgreSQL gate.

## Verification and evidence

- Save focused RED and GREEN outputs under `evidence/terminal-logs/`, including explicit exit codes.
- Run focused 010F/010G/010A/communications reverse-consumer tests, Django check, migration-sync,
  and relevant migration/contract tests with the mandated Ralph Python interpreter.
- Update `docs/working/API_CONTRACTS.md`, then complete risk assessment, review packet, and final
  summary. The orchestrator owns state, progress, changed-files, slice status, and mechanical handoff.
