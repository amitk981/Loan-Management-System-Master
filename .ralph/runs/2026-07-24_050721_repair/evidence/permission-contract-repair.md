# Permission Contract Repair Evidence

## Demonstrated Failure

Independent validation failed
`ApiContractHarnessUnitTests.test_production_code_does_not_use_legacy_permission_denied_literal`.
The retained failure named `reports/modules/report_export.py` as the only offender.

The same exact test was rerun before the repair and failed with:

```text
AssertionError: Lists differ: ['reports/modules/report_export.py'] != []
FAILED (failures=1)
```

Retained output:
`terminal-logs/01-api-contract-harness-red.txt`.

## Root Cause and Repair

The report export module introduced two retired `PERMISSION_DENIED` production constants: one in
the denied-request audit metadata and one in worker failure-code classification. The public API
boundary already defines `FORBIDDEN` as the canonical permission denial code.

The repair imports and reuses `sfpcl_credit.api.FORBIDDEN` at both sites. It changes no request,
selector, storage, task, lifecycle, or database behavior.

## GREEN Evidence

The exact formerly failing test passed:

```text
Ran 1 test in 0.770s
OK
```

Retained output:
`terminal-logs/02-api-contract-harness-green.txt`.

The full focused report-export module remained green:

```text
Ran 8 tests in 0.146s
OK
```

This includes denial audit sanitisation, lifecycle/status, idempotent replay, task registration,
failure classification, retention/expiry, download grants, and all four export formats.

Retained output:
`terminal-logs/03-report-exports-focused.txt`.

Cheap backend gates also passed:

- Django system check: no issues (`terminal-logs/04-django-check.txt`).
- Migration consistency: no changes detected (`terminal-logs/05-migrations-check.txt`).
- No retired literal or debug instrumentation remains in the repaired module, and
  `git diff --check` passed (`terminal-logs/06-scope-and-cleanup-check.txt`).

The complete backend coverage lane was not rerun by the repair agent; Ralph independent validation
owns that authoritative lane.
