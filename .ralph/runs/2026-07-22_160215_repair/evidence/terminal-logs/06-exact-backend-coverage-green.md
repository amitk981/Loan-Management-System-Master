# Exact backend coverage validator — GREEN

Command from the worktree root (with the approved venv wrapper retained for spawned workers):

```text
PYTHONEXECUTABLE=/Users/amitkallapa/LMS/.ralph/venv/bin/python /Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh /Users/amitkallapa/LMS/.ralph/venv/bin/python /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-22_151342_normal_run sfpcl_credit 6 85
```

Final output:

```text
Ran 1619 tests in 1452.412s
OK (skipped=160)
Total database setup took 62.390s
Total database teardown took 0.010s
Total run took 1515.368s
Combined 7 files
TOTAL 66246 statements, 6607 missed, 90% coverage
Exit code: 0
```

This is the same six-worker, 85%-floor validator named in the failed run. It passed after both
historical migration projections excluded the new downstream `recovery` leaf.
