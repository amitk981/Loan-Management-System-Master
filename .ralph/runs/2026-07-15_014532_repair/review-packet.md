# Review Packet: 2026-07-15_014532_repair

## Result

Ready for full independent validation.

## Slice

`008I4-sensitive-field-encryption-and-cdsl-null-contract-closure`

## Failure and repair

- Three coverage errors came from non-canonical evidence document types in new test setup. They now
  use `cdsl_pledge_evidence` and assert the setup response before consuming the success envelope.
- Reveal denial rows were rolled back with their policy exceptions. The coordinator now commits the
  central denial ledger, exits the pledge-lock transaction, and then re-raises the unchanged domain
  exception to the HTTP adapter.
- Installing the pinned crypto dependency exposed a macOS subprocess architecture mismatch in an
  existing import-boundary test. It now launches the mandated virtualenv `bin/python` wrapper while
  retaining the same guarded-import probe.

## Traceability for a non-developer

- Auth §§6.5/12.8/19.4/21 requires denied sensitive access to be audited. The code now retains that
  denial when returning 400/403/429/409; `test_explicit_company_secretary_reveal_is_one_time_and_separately_audited`
  and `test_central_reveal_validates_reason_and_denies_lost_object_scope` verify it.
- Data model §17.4 requires exact current CDSL evidence when supplied and permits null only while
  pending. Canonical fixture correction preserves the production rejection of invented document
  types; the pending-null and terminal-null regressions remain green.
- Codebase design §§9.4/39.1-39.2 requires central encryption/reveal owners and the source dependency
  graph. The fresh-process guarded-import test and security boundary suite pass without relaxing any
  prohibited import.

## Validation evidence

- Original RED: `evidence/terminal-logs/focused-red.txt`
- Focused GREEN: `evidence/terminal-logs/focused-green.txt`
- Dependency RED/GREEN: `evidence/terminal-logs/dependency-direction-red.txt` and
  `evidence/terminal-logs/dependency-direction-green.txt`
- Backend: `evidence/terminal-logs/backend-coverage-tests-rerun.txt`,
  `backend-coverage-report.txt`, `backend-check.txt`, and `backend-migrations.txt`
- PostgreSQL twice: `evidence/terminal-logs/postgresql-races-run-1.txt` and
  `postgresql-races-run-2.txt`
- Frontend: lint/typecheck/tests/build logs under `evidence/terminal-logs/`

## Recommended next action

Let the orchestrator run full independent revalidation and commit only if it remains green. Then run
the already sharpened 008J, followed by sharpened 008K.
