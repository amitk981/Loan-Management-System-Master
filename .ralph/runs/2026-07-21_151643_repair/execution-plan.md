# Execution Plan

Selected slice: `CR-015-epic-010-terminal-servicing-owner-finalizer`

Repair domain: the independent complete-suite direct-repayment idempotency regression and the
missing PostgreSQL acceptance artifacts recorded in
`.ralph/runs/2026-07-21_150232_repair/failure-summary.md`.

1. Reproduce the exact failed Django test with the mandated Ralph virtual environment and retain
   the deterministic RED output in this repair run.
2. Inspect the direct-repayment command/posting seam and the existing permanent tests. Rank and
   probe only causes that explain why a same-key repeat now returns `200` where the established SAP
   posting endpoint contract requires `409`.
3. Keep the existing public regression as the TDD test and make the smallest owner-boundary change
   that preserves the composite command's exact replay while restoring the legacy SAP endpoint's
   duplicate-posting conflict contract.
4. Rerun the exact failed label to GREEN, then run the bounded direct-repayment API/command tests
   affected by the change. Do not run the complete backend suite or full coverage locally.
5. Run the declared five-test PostgreSQL acceptance class twice against PostgreSQL and retain the
   non-secret environment facts and both exact-count logs in this run folder.
6. Run Django system and migration-consistency checks. Update closure evidence, risk assessment,
   review packet, and final summary, then run the mandatory review-closure validator until `PASS`.

## Feedback loop

`/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_direct_repayment_posting_api.DirectRepaymentPostingApiTests.test_sap_posting_requires_permission_reference_and_records_safe_audit_truth --verbosity 2`

This is the exact independent failure, deterministic and seconds-scale, and it asserts the public
endpoint's duplicate SAP-posting response rather than merely checking that the request completes.
