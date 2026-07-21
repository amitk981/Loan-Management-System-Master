# Execution Plan

Selected slice: `CR-015-epic-010-terminal-servicing-owner-finalizer`

Repair domain: the complete-suite regression
`CommunicationWorkerQueueTests.test_final_accepted_crash_closes_exception_without_redispatch`
recorded in the quarantined run's `backend-coverage-results.md`.

1. Reproduce the failure with the exact Django dotted test label using the mandated Ralph virtual
   environment and retain the focused RED output in this repair run.
2. Compare the final-attempt path with the already-passing non-final accepted-crash recovery path,
   rank falsifiable causes, and identify the smallest transaction/exception boundary that explains
   why accepted provider evidence is rolled back only on the final attempt.
3. Keep the existing permanent regression as the TDD test. Make the smallest communications-worker
   change that persists accepted provider identity before final-attempt exception bookkeeping while
   preserving zero redispatch and manual exception resolution semantics.
4. Rerun the exact failing label to GREEN, then run the communication worker runtime module as the
   bounded regression validator. Do not run the complete backend suite or coverage locally; the
   orchestrator owns that independent revalidation.
5. Run Django system and migration consistency checks if the repair changes product code. Save all
   command output under `evidence/terminal-logs/` with explicit commands and exit codes.
6. Update repair risk, review, closure, and final-summary artifacts, then run the mandatory review
   closure validator until it prints `PASS`.

## Feedback loop

`/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_communication_worker_runtime.CommunicationWorkerQueueTests.test_final_accepted_crash_closes_exception_without_redispatch --verbosity 2`

This public worker regression is deterministic, seconds-scale, agent-runnable, and asserts the exact
missing accepted-provider identity plus the no-redispatch/final-exception behavior.
