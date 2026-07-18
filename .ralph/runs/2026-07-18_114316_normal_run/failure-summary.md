# Failure Summary

- Run: 2026-07-18_114316_normal_run
- Mode: normal_run
- Slice: 009H4-communications-advice-evidence-and-legacy-replay-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_receipt_row_and_schema_survive_forward_reverse_and_reapply (sfpcl_credit.tests.test_communication_receipt_owner_migration.CommunicationReceiptOwnerMigrationTests.test_receipt_row_and_schema_survive_forward_reverse_and_reapply)
backend-coverage-results.md:FAILED (failures=1, skipped=62)
```

## Last 50 lines: backend-coverage-results.md

```
FAIL: test_receipt_row_and_schema_survive_forward_reverse_and_reapply (sfpcl_credit.tests.test_communication_receipt_owner_migration.CommunicationReceiptOwnerMigrationTests.test_receipt_row_and_schema_survive_forward_reverse_and_reapply)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 623, in run
    self._callTestMethod(testMethod)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 579, in _callTestMethod
    if method() is not None:
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_114316_normal_run/sfpcl_credit/tests/test_communication_receipt_owner_migration.py", line 93, in test_receipt_row_and_schema_survive_forward_reverse_and_reapply
    self.assertEqual(self._receipt_signature(), before)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 873, in assertEqual
    assertion_func(first, second, msg=msg)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 1172, in assertDictEqual
    self.fail(self._formatMessage(msg, standardMsg))
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 703, in fail
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: {'tab[54 chars]': ('advice_intent_id', 'delivery_receipt_id',[264 chars]_0')} != {'tab[54 chars]': ('delivery_receipt_id', 'idempotency_key', [264 chars]_0')}
Diff is 716 characters long. Set self.maxDiff to None to see it.

----------------------------------------------------------------------
Ran 1152 tests in 390.812s

FAILED (failures=1, skipped=62)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 28.494s
  Creating 'default' took 28.424s
  Cloning 'default' took 0.010s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.013s
  Cloning 'default' took 0.012s
  Cloning 'default' took 0.011s
  Cloning 'default' took 0.012s
Total database teardown took 0.016s
Total run took 419.820s

Duration milliseconds: 420341
Exit code: 1
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/009H4-communications-advice-evidence-and-legacy-replay-closure.md
docs/working/CONTEXT.md
docs/working/HANDOFF.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/communications/models.py
sfpcl_credit/communications/modules/communication_dispatcher.py
sfpcl_credit/disbursements/models.py
sfpcl_credit/tests/test_communication_advice_persistence.py
sfpcl_credit/tests/test_communication_receipt_owner_migration.py
sfpcl_credit/tests/test_disbursement_advice_api.py
.ralph/runs/2026-07-18_114316_normal_run/
changed-files.txt
sfpcl_credit/communications/migrations/0005_advice_evidence_and_legacy_replay_closure.py
sfpcl_credit/processes/advice_evidence_migration.py
```
