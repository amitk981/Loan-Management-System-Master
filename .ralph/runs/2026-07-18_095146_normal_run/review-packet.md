# Review Packet: 2026-07-18_095146_normal_run

## Result
Ready for independent validation

## Slice
009G4-legal-checklist-migration-ownership-anchor

## Outcome

One empty legal-documents migration anchors the exact checklist constraint state historically
introduced by disbursements 0005 and the current G3/H3B leaves. A static guard prevents a future
custom migration outside the legal app from mutating the same model state, except for the two exact
reviewed historical operation classes.

## Traceability

- Source codebase-design §§6-8 and 21 say `legal_documents` owns checklist persistence/workflow;
  §36 says disbursements may consume legal truth but the owner seam remains legal. The new migration
  is owned by `legal_documents` and every future legal descendant inherits the reviewed state.
- Source data-model §34 requires atomic, retained checklist/disbursement integrity. The migration
  emits no SQL/data operation, and
  `LegalChecklistConstraintOwnerMigrationTests.test_anchor_preserves_exact_state_schema_and_rows_through_reverse_reapply`
  proves exact ids, values, constraint names, and full physical schema survive every direction.
- Architecture review finding 4 requires an applied-history-preserving owner anchor and executable
  recurrence guard. Migration 0015 leaves disbursements 0005 untouched;
  `LegalChecklistMigrationOwnershipGuardTests` proves both the exact allowlist and synthetic denial.

## Changed implementation

- `legal_documents/migrations/0015_checklist_constraint_state_owner_anchor.py`: empty owner anchor.
- `shared/migration_state_guard.py`: narrow AST guard and exact historical allowlist.
- `tests/test_legal_checklist_migration_anchor.py`: retained-state/schema and guard proof; the older
  0013 test now uses projected graph state so it does not partially reverse beneath later leaves.

## Verification

- TDD red: missing guard module fails before implementation (`tdd-red.txt`).
- TDD green/refactor: 6 tests pass (`tdd-green-refactor.txt`).
- Adjacent migration isolation: communications/document-template 3 tests and SAP 4 tests pass.
- Django check, `makemigrations --check --dry-run`, compile, and `sqlmigrate` no-op pass.
- Node 20.19.6: typecheck, lint, 327 tests, and build pass. The existing Vite CJS and bundle-size
  warnings are unchanged and non-failing.
- Complete backend coverage is intentionally delegated to Ralph's independent validator.

## Review findings

- No destructive or behavioral migration operation exists.
- Dependency set includes all four named leaves and only one new migration was added.
- Test assertions inspect public migration graph/state and database schema/rows, not private runtime
  workflow helpers.
- No new assumption was needed. 009I and 009J were rechecked and already meet sharpening standards.
- Diff remains below configured file/line/dependency/migration limits.

## Recommended Next Action
Run independent Ralph validation and commit only if it passes. The architecture-review cadence is
due next; afterward run 009I, then 009J.
