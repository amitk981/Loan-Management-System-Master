# Review Packet: 2026-07-19_233905_normal_run

## Result
Ready for independent validation

## Slice
010D-bank-statement-matching-unmatched-receipts

## Outcome

Implemented bounded manual CSV statement imports, retained document/checksum provenance,
deterministic statement lines, strict singular automatic matching, safe reconciliation queues,
authorized manual matching, and explicit exception decisions. The `tdd` skill shaped the work as
public HTTP RED→GREEN tracer bullets; each behavior is tested through authenticated API routes rather
than internal helpers.

Matching remains an evidence-only operation. Receipt allocation/SAP status, loan balances, schedule
paid amounts, and ledger rows are untouched. Exact and manual links are visible in safe receipt
evidence projections, while manual matches remain explicit exceptions for the later governed
allocation/reconciliation owner.

## Source Traceability

- User flows §§27.4/28.4 and functional M09-FR-007–008 require bank-statement verification,
  reconciliation, and unmatched routing. `BankStatementImport`/`BankStatementLine`, import/list/match/
  exception routes, and safe reason codes implement that contract; verified by all eight
  `BankStatementMatchingApiTests`.
- The slice and data model §19.5 require a statement-line owner link without financial allocation.
  the receipt UUID link, line one-to-one, receipt statement-match status, and database uniqueness
  provide singular ownership; verified by the manual-match test and the PostgreSQL race contract.
- Security §22.2 requires duplicate prevention, permission scope, and audit. Separate read/import/
  match permissions, role-and-permission checks, credit receipt scope, checksum/idempotency
  uniqueness, and safe audit actions are verified by the replay/permission/scope tests.
- The non-goal forbids fabricated matches without borrower/application narration. Automatic matching
  also requires account/application/member identity inside narration; verified by
  `test_exact_bank_facts_without_borrower_or_application_narration_remain_unmatched`.
- Test plan API-REP-006/007 and MOD-REP-010 are covered by upload/list/match/exception, malformed and
  mismatched candidate matrices, replay, permission, database, and reverse-consumer tests. 010C2
  retains ownership of M09-FR-009 financial allocation.

## Evidence

- RED/GREEN tracer: `evidence/terminal-logs/bank-statement-tracer-red.log` and
  `bank-statement-tracer-green.log`.
- RED/GREEN queue, manual match, exception, replay safety, and narration contracts: matching
  `bank-statement-*-red.log` / `bank-statement-*-green.log` files.
- Final focused run: `evidence/terminal-logs/bank-statement-focused-final.log` — 46 tests passed,
  including 010A–010C and permission-catalogue reverse consumers.
- Standard contract/check/migration gates: `evidence/terminal-logs/backend-final-gates.log` — 15 API
  harness tests passed; Django check and migration sync returned zero.
- Final post-review smoke: `evidence/terminal-logs/bank-statement-final-smoke.log` — all eight current
  slice API tests, Django check, and migration sync passed after the final audit-privacy tightening.
- PostgreSQL local collection: `evidence/terminal-logs/bank-statement-postgresql-local.log` — exactly
  one test collected and skipped because the local database is SQLite.
- Self-contained response, uniqueness, audit, and permission examples:
  `evidence/bank-statement-contract.md`.

## Review Focus

- Run the declared two-request manual-match race twice on PostgreSQL and verify statuses `[200,409]`,
  one line/receipt link, one manual-match audit, and unchanged allocation status.
- Confirm the single migration's one-to-one/unique/check constraints on PostgreSQL.
- Confirm A-140's narrow technical permission vocabulary and A-141's provenance-only collection
  account label remain acceptable until source governance supplies canonical names/registry.
- Inspect the existing storage adapter's orphan-object behavior on post-write database failure; it
  does not compromise database or financial truth but may require central lifecycle cleanup.

## Substantive Risks and Decisions

- High financial-integrity risk is bounded by evidence-only interfaces and retained reverse-consumer
  snapshots; no money owner is called from the matcher.
- Strict automatic matching deliberately prefers false negatives: all five exact/reference facts and
  narration identity are required. Manual review handles every lesser-confidence case.
- Manual reason text is retained for authorized evidence review but deliberately omitted from audits
  and ordinary projections; audits carry stable safe codes and identifiers.
- Repeated account/checksum imports reuse the retained import even under a different idempotency key;
  changed reuse of an existing key conflicts.

## Recommended Next Action
Run Ralph's independent complete backend coverage, migration, protected-path, diff-limit, and twice-
run PostgreSQL contention validation. The orchestrator may commit only if every gate passes.
