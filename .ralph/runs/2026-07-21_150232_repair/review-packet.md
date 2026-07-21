# Review Packet: 2026-07-21_150232_repair

## Result
Ready for independent validation

## Slice

`CR-015-epic-010-terminal-servicing-owner-finalizer`

## Failure Reproduced

The quarantined complete-suite run failed
`CommunicationWorkerQueueTests.test_final_accepted_crash_closes_exception_without_redispatch`
because a post-provider crash left `provider_external_message_id` empty. The exact selector failed
again locally. The adjacent non-final accepted-crash recovery test also failed in isolation, proving
the complete-suite fail-fast had exposed one symptom of the same transaction defect.

## Root Cause and Repair

`CommunicationDispatcher.execute_generic_job` had an encompassing `@transaction.atomic` added
around a workflow that intentionally consists of separate durable phases. A failure after the
external provider accepted the message rolled back the job claim and immutable accepted-provider
evidence, although the provider effect could not be rolled back.

The repair removes only that encompassing decorator. Existing explicit atomic owners remain:

- `start_job` owns and commits the worker claim;
- reminder serviceability owns its source locks while crossing the provider seam;
- provider-evidence reconciliation owns the accepted identity write;
- communication finalisation and `complete_job` retain their own locks and checks.

Thus a later local crash cannot erase irreversible provider truth, and recovery reuses the retained
identity without redispatch.

## Standards Review

- The change preserves the deep communications module interface and does not move business policy
  into callers.
- No schema, API, dependency, configuration, frontend, source-document, or protected-file change was
  introduced by the repair.
- The existing public worker tests exercise real database state and adapter calls rather than a
  private helper.
- `git diff --check`, Django system check, and migration consistency are clean.

## Spec Review and Traceability

The Epic 010 shared invariant requires exact replay to retain one result and one external effect;
CR-015 AC-E10-F-1 requires retry and competing-worker reminder paths to retain at most one justified
effect. The code now commits accepted provider identity before fallible post-provider finalisation,
verified by the exact final and non-final crash tests and the 36-test worker runtime module.

The original CR-015 finding/acceptance evidence was retained in this repair run and the exact closure
validator reports: `PASS: validated semantic closure for 3 finding(s) and 5 acceptance id(s).`

## Validation Evidence

- RED exact failure: `evidence/terminal-logs/communication-final-accepted-red.log`
- RED companion: `evidence/terminal-logs/communication-nonfinal-accepted-probe.log`
- GREEN exact selector: `evidence/terminal-logs/communication-final-accepted-green.log`
- GREEN companion: `evidence/terminal-logs/communication-nonfinal-accepted-green.log`
- GREEN module: `evidence/terminal-logs/communication-worker-runtime-green.log` — 36 tests, 6
  PostgreSQL-only skips, exit 0
- Django check: `evidence/terminal-logs/django-check.log` — exit 0
- Migration check: `evidence/terminal-logs/migration-check.log` — exit 0
- Closure contract: `evidence/terminal-logs/review-closure-validator.log` — PASS, exit 0

## Substantive Next-Run Risk

The orchestrator must rerun complete-suite coverage and the slice's trusted PostgreSQL acceptance.
Those authoritative gates were deliberately not duplicated in the coding sandbox.

## Recommended Next Action

Run independent Ralph validation and commit only if every configured gate passes.
