# Risk Assessment

Risk level: High (inherited 009G3 slice); Low incremental repair risk

- Selected slice: 009G3-post-transfer-aggregate-and-checklist-integrity-closure
- Mode: repair
- Manual review required: yes; independent Ralph validation is required before commit.

## Demonstrated failure and repair scope

- Complete coverage exposed one obsolete legacy test that attempted to delete a register now
  protected by the 009G3 aggregate owner relation. Django's parallel runner then obscured that
  `ProtectedError` with a traceback-pickling failure.
- The repair changes only that regression test. It explicitly asserts deletion protection, then
  tampers the retained register checksum to preserve the test's 409 current-evidence assertion.
- No production model, migration, service, permission, API, frontend, dependency, or source
  document was changed during this repair.

## Underlying slice risk retained

- 009G3 remains High risk because it changes financial-success aggregate integrity, protected Loan
  Register evidence, Stage-5 Senior Finance authority, immutable replay reconciliation, a data
  migration, and concurrency-sensitive behavior.
- Complete backend coverage and twice-run PostgreSQL acceptance remain mandatory independent gates.

## Residual risk

- The focused 61-test set proves the intended register protection and documentation replay path,
  but only the orchestrator's full parallel coverage run can prove no other legacy test has the
  same stale deletion assumption.
- A supplemental local parallel attempt ran zero tests because spawned workers had an x86_64 versus
  arm64 `_cffi_backend` mismatch. It was stopped and is not presented as gate evidence.
