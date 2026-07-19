# Failure Summary

- Run: 2026-07-19_161645_repair
- Mode: repair
- Slice: CR-012-epic-009-playwright-evidence-is-incomplete
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: first run screenshot evidence or manifest is incomplete.
e2e-results.md:- FAIL: second run screenshot evidence or manifest is incomplete.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- PASS: slice-specific trusted browser contract is valid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- SKIP: second trusted slice-specific browser run deferred because the first run failed.
- FAIL: first run screenshot evidence or manifest is incomplete.
- FAIL: second run screenshot evidence or manifest is incomplete.

Declared specs:
- e2e/epic-009-staff-disbursement-closure.e2e.spec.ts
Declared screenshots:
- loan-account-list.png
- loan-account-sanctioned-summary.png
- loan-account-active-summary.png
- sap-request-and-confirmation.png
- disbursement-readiness-blockers.png
- payment-initiation.png
- cfc-authorisation.png
- transfer-and-advice-success.png
- loan-account-safe-error.png
```

## Changed files (git status)

```
sfpcl-lms/e2e/README.md
sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts
sfpcl-lms/playwright.config.ts
sfpcl_credit/tests/test_seed_e2e_users.py
.ralph/runs/2026-07-19_154507_normal_run/
.ralph/runs/2026-07-19_161645_repair/
sfpcl_credit/identity/management/commands/seed_epic_009_e2e_fixture.py
```
