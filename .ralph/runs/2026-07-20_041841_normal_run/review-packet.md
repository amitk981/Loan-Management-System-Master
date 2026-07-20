# Review Packet: 2026-07-20_041841_normal_run

## Result
Ready for independent validation

## Slice
010E2-effective-rate-versioning-and-borrower-notices

## Implementation Review

- One configuration-owned deep module exposes proposal/list, checker activation, exact-date
  resolution, and immutable consumption. Callers do not reproduce effective-period logic.
- One non-destructive migration owns effective rate versions, per-loan history, notice linkage, and
  invoice/accrual consumption snapshots.
- The existing communications dispatcher remains the only email/SMS snapshot, queue, provider,
  retry, and terminal-delivery owner.
- Section 41.4 paths use standard envelopes and exact configuration/communication authority.
- No frontend, protected path, source document, orchestrator state/progress, slice status, or
  mechanical handoff fact was edited.

## Traceability

- The source says M10-FR-001 stores floating-rate versions/effective dates; the code stores governed
  `InterestRateConfig` periods and resolves exactly one version, verified by
  `test_checker_activates_contiguous_versions_and_resolution_is_historical`.
- The source says M10-FR-002 and the communication matrix notify borrowers by SMS/email; activation
  creates one durable loan-level obligation linked to both channels through the existing dispatcher, verified
  by `test_activation_queues_honest_email_and_sms_obligations_for_active_loans`.
- Data-model §§18.5/25.3 require loan history, configuration metadata, communication linkage, and
  approver truth; the migration creates those relationships and the focused tests assert linkage,
  history, maker-checker, and immutable consumer behavior.
- API §41.4 names list/create/activate; the concrete envelope, validation, conflict, idempotency,
  period, permission, and notice-status contract is recorded in `docs/working/API_CONTRACTS.md`.

## Validation Evidence

- RED/GREEN and boundary/contract evidence is indexed in `evidence/evidence-summary.md`.
- Both real PostgreSQL runs executed and passed all three declared tests with zero skips; see
  `evidence/postgresql-acceptance.md`.
- Final focused regression: 51 tests green under SQLite, with only the three separately passed
  PostgreSQL tests skipped, then green system check and migration sync.
- Ralph still owns the authoritative complete backend coverage suite and independent repeated
  PostgreSQL gate.

## Risks and Review Focus

- Confirm the independent validator sees exactly one migration and the expected three-test label.
- Confirm future 010F/010G use `consume_effective_rate` rather than `LoanAccount.current_interest_rate`.
- Confirm deployment supplies approved effective rate-change email/SMS templates before activating a
  communication-required version for borrowers with valid channel addresses.
- Review A-145 before broadening active-loan population or implementing benchmark/reset formulas.

## Recommended Next Action
Run Ralph's independent full backend coverage, migration, protected-path, contract, and twice-run
PostgreSQL validation; commit only if all gates pass.
