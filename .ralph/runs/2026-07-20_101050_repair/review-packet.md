# Review Packet: 2026-07-20_101050_repair

## Result
Ready for independent validation

## Slice
010H-interest-capitalisation-after-30-april

## Repair outcome

- Preserved the quarantined 010H implementation and changed only the failed PostgreSQL lock scope.
- Root cause: `capitalisation_evidence__isnull=True` creates a nullable reverse outer join, while
  unrestricted `select_for_update()` asks PostgreSQL to lock every joined table. PostgreSQL rejects
  `FOR UPDATE` on the nullable side before either concurrent request can complete.
- Correction: `InterestInvoice.objects.select_for_update(of=("self",))` retains the eligible
  invoice-row lock and avoids requesting a lock on the optional evidence join. The pre-existing
  account lock serializes requests for the same loan, and uniqueness remains the final safeguard.

## Source traceability

- The source requires eligible unpaid interest to be capitalised at most once after 30 April with
  atomic principal and ledger evidence (`product-requirements.md` §11.24; `user-flows.md`
  §§29.5–29.6; functional rules BR-061–063; `data-model.md` §35.3). The correction preserves both
  source-row and account locking; the exact two-caller PostgreSQL test proves one capitalisation and
  one ledger movement, with the other request rejected.
- No source, API, schema, calculation, communication, or borrower-intimation contract changed.

## Evidence

- RED, independent run 1:
  `.ralph/runs/2026-07-20_092159_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-1.txt`
  (one declared test; PostgreSQL `NotSupportedError`; non-zero result).
- RED, independent run 2:
  `.ralph/runs/2026-07-20_092159_normal_run/evidence/terminal-logs/postgresql-acceptance-validation-2.txt`
  (same deterministic failure).
- GREEN PostgreSQL regression:
  `evidence/terminal-logs/interest-capitalisation-postgresql-green.log` (one test passed; clean
  database teardown; explicit `EXIT_CODE=0`).
- GREEN focused gates:
  `evidence/terminal-logs/interest-capitalisation-repair-focused-gates.log` (7 API tests passed;
  Django check passed; migration sync reported no changes; every command exit `0`).

## Review focus

- Confirm generated PostgreSQL SQL locks only `interest_invoices` while retaining the nullable
  anti-join used to exclude already-capitalised invoices.
- Confirm both independent contention runs retain exactly one capitalisation and ledger movement.
- Confirm the candidate differs from the failed implementation only by the bounded lock correction
  plus current repair evidence/artifacts.

## Recommended Next Action
Run Ralph's independent full backend coverage, protected-path, migration, and twice-run PostgreSQL
acceptance gates. The orchestrator alone should commit, merge, update state, and transition status
after every gate passes.
