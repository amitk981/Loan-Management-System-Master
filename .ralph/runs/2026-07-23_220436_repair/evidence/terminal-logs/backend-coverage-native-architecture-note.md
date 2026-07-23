# Backend coverage native-architecture retry

The first direct invocation of the exact coverage validator was stopped after macOS multiprocessing
repeatedly spawned x86_64 workers that could not load the pinned arm64 `coverage` and `cffi`
extensions. This was an execution-environment mismatch, not a product-test failure.

The unchanged validator was rerun with the established Ralph macOS handoff:

```text
PYTHONEXECUTABLE=/Users/amitkallapa/LMS/.ralph/venv/bin/python \
  /Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh \
  /Users/amitkallapa/LMS/.ralph/venv/bin/python \
  /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_210407_normal_run \
  sfpcl_credit 6 85
```

The successful complete output is retained in
`backend-coverage-exact-validator-green.log`.
