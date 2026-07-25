# Authoritative impacted-backend red excerpt

Source: orchestrator-owned failure summary for the immediately preceding same-worktree repair.

```text
FAIL: test_authenticated_user_without_tracer_permission_cannot_write_domain_rows
(sfpcl_credit.tests.test_tracer_api.TracerApiTests.test_authenticated_user_without_tracer_permission_cannot_write_domain_rows)

File "sfpcl_credit/tests/test_tracer_api.py", line 273
    self.assertEqual(response.status_code, 403)

AssertionError: 404 != 403

Ran 1401 tests in 76.065s
FAILED (failures=1, skipped=4)
Exit code: 1
```

This is the red half of the repair loop. The full current-run green half is
`backend-impacted-green.log`.
