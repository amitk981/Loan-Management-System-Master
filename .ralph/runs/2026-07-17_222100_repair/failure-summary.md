# Failure Summary

- Run: 2026-07-17_222100_repair
- Mode: repair
- Slice: 009G3-post-transfer-aggregate-and-checklist-integrity-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
(none in check files)
```

## Last 50 lines: backend-coverage-results.md

```
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_215313_normal_run/sfpcl_credit/manage.py", line 13, in main
    execute_from_command_line(sys.argv)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/__init__.py", line 442, in execute_from_command_line
    utility.execute()
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/__init__.py", line 436, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/commands/test.py", line 24, in run_from_argv
    super().run_from_argv(argv)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 413, in run_from_argv
    self.execute(*args, **cmd_options)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 459, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/commands/test.py", line 68, in handle
    failures = test_runner.run_tests(test_labels)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 1068, in run_tests
    result = self.run_suite(suite)
             ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 995, in run_suite
    return runner.run(suite)
           ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/runner.py", line 217, in run
    test(result)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/suite.py", line 84, in __call__
    return self.run(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 541, in run
    subsuite_index, events = test_results.next(timeout=0.1)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/multiprocessing/pool.py", line 873, in next
    raise value
TypeError: cannot pickle 'traceback' object
Exception ignored in: <function Pool.__del__ at 0x104363240>
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/multiprocessing/pool.py", line 271, in __del__
    self._change_notifier.put(None)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/multiprocessing/queues.py", line 377, in put
    self._writer.send_bytes(obj)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/multiprocessing/connection.py", line 199, in send_bytes
    self._send_bytes(m[offset:offset + size])
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/multiprocessing/connection.py", line 410, in _send_bytes
    self._send(header + buf)
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/multiprocessing/connection.py", line 367, in _send
    n = write(self._handle, buf)
        ^^^^^^^^^^^^^^^^^^^^^^^^
OSError: [Errno 9] Bad file descriptor

Duration milliseconds: 68681
Exit code: 1
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/009G3-post-transfer-aggregate-and-checklist-integrity-closure.md
docs/working/HANDOFF.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/disbursements/models.py
sfpcl_credit/disbursements/modules/disbursement_transfer_success.py
sfpcl_credit/disbursements/modules/post_transfer_evidence.py
sfpcl_credit/tests/test_disbursement_transfer_success_api.py
.ralph/runs/2026-07-17_215313_normal_run/
.ralph/runs/2026-07-17_220014_repair/
.ralph/runs/2026-07-17_220706_repair/
.ralph/runs/2026-07-17_221920_repair/
.ralph/runs/2026-07-17_222100_repair/
sfpcl_credit/disbursements/migrations/0007_remove_disbursement_disb_success_evidence_complete_and_more.py
```
