# Review Packet: 2026-07-20_022525_normal_run

## Result
Ready for independent validation

## Slice
010D2-statement-evidence-owner-and-scope-closure

## Recommended Next Action
Run the declared four-test PostgreSQL class twice, then the normal independent complete backend
coverage, migration, frontend, protected-path, and slice-contract gates.

## Implementation Review

- `BankStatementLine.matched_repayment` is now the sole persisted relationship owner; receipt fields
  are derived projections and direct capture must claim an existing exact line.
- Import, auto/manual matching, line lists/counts, direct claims, and operator exceptions share
  permission and loan-object-scope decisions.
- Subsidiary auto-match requires both borrower name and application number; direct evidence remains
  an explicitly separate exact rule.
- Collection account input is the opaque centrally governed bank-account UUID and is never echoed;
  unmappable legacy labels are encrypted.
- Migration evidence retains orphan/incomplete/contradictory UUIDs without fabricating counterparts
  and supports a tested ownership-safe rollback.

## Traceability

- The source says subsidiary statement narration must identify borrower and loan application
  (`functional-spec.md` M09-FR-007; `user-flows.md` §§28.3–28.4); the matcher requires both, verified
  by `test_subsidiary_auto_match_requires_borrower_and_application_facts`.
- The source models `bank_statement_line_id` as a relationship (`data-model.md` §19.5) and requires
  atomic integrity (§34); the line now solely owns the one-to-one relationship, verified by the
  owner-interface and migration-executor tests.
- The source requires backend permission/object filtering (`auth-permissions.md` §§19.3, 26.6,
  32.1); automatic/manual/list paths filter through the same loan scope, verified by the public
  scope and nondisclosure tests.
- The source classifies bank accounts/statements as restricted and requires masking/encryption and
  log minimisation (`security-privacy.md` §§3–7, 25); the central governed UUID replaces raw account
  labels, responses omit private facts, and legacy labels are encrypted.

## Evidence Reviewed

- RED/GREEN: `evidence/terminal-logs/statement-owner-red.log` and
  `evidence/terminal-logs/statement-owner-green.log`.
- Acceptance matrix and migration: `evidence/terminal-logs/acceptance-matrix-green.log` and
  `evidence/terminal-logs/statement-migration-green.log`.
- Reverse consumers: `evidence/terminal-logs/reverse-consumers-green.log` (34 tests, 4 expected
  PostgreSQL skips, exit 0).
- PostgreSQL collection: `evidence/terminal-logs/postgresql-acceptance-collection.log` (4 tests
  discovered; local SQLite skips explicitly recorded).
- Static/frontend gates: `evidence/terminal-logs/backend-static-gates.log` and
  `evidence/terminal-logs/frontend-gates.log`.

## Substantive Independent-Validation Risk

The local sandbox did not execute PostgreSQL races or the complete backend coverage suite, by Ralph
contract. Independent validation must fail closed if either differs from the focused evidence.
