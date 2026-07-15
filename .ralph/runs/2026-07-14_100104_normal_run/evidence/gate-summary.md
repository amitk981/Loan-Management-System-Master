# Gate Summary

- Frontend build: PASS (`frontend-build.log`).
- Frontend typecheck: PASS (`frontend-typecheck.log`).
- Frontend lint: PASS (`frontend-lint.log`).
- Frontend tests: PASS, 293 tests in 33 files (`frontend-test.log`).
- Django check: PASS (`backend-check.log`).
- Migration sync: PASS, no changes detected (`backend-migrations.log`).
- Backend full suite: PASS, 722 tests with 22 expected skips (`backend-coverage-tests.log`).
- Backend coverage: PASS, 93% against 85% floor (`backend-coverage-report.log`).
- Exact backend legacy register contract: PASS (`backend-legacy-contract.log`).
- Trusted browser collection: PASS, two specs (`trusted-browser-collection.log`).
- Local trusted browser execution: environment-blocked before test execution by Chromium macOS
  Mach-port permission denial (`trusted-browser-local.log`); no screenshot fabricated, independent
  orchestrator execution required by the declared `localhost-e2e-server` capability.
