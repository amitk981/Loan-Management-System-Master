# Returned Approval Cycle Proof

Slice: `007D3-returned-approval-cycle-and-resubmission-closure`

## Observable workflow

The retained tracer test executes the public module/API seams in this order:

1. Return enriched cycle 1 with a mandatory clarification reason.
2. Verify application returns to `appraisal_reviewed` and appraisal becomes editable `draft`.
3. Correct an appraisal value through `AppraisalWorkflow.create_or_update`.
4. Submit for review and record a fresh independent Credit Manager `reviewed` decision.
5. Resubmit through `SanctionHandoffModule.submit_reviewed_appraisal`; the new shell reports
   `cycle_number: 2` and links the new immutable review.
6. Enrich cycle 2 from current configuration and frozen corrected review facts.
7. Verify returned cycle 1 detail remains readable and every action is disabled, while
   `assigned_to_me=true` contains only pending cycle 2.
8. Record CFO partial approval and Director final approval in cycle 2; one application-unique
   sanction decision links to cycle 2.
9. Compare cycle 1 case/action/audit/workflow/communication ledgers exactly before and after the
   complete second cycle; they are unchanged.

Command/output: `terminal-logs/03-green-two-cycle-full-workflow.txt` and the consolidated proof in
`terminal-logs/11-green-single-migration-cycle-proof.txt`.

## Denial proof

A no-op appraisal PATCH records no changed fields. Even after a later Credit Manager review, the
sanction handoff rejects resubmission with: `A returned appraisal must be corrected before
resubmission.` The case/action/sanction/audit/workflow/communication/notification ledger is exact-
equal before and after the rejected handoff.

RED: `terminal-logs/08-red-noop-correction.txt`.

GREEN: `terminal-logs/09-green-noop-correction.txt`.

## Migration proof

Historical cases at approvals migration `0010` migrate to cycle 1 with positive revision, a matched
pre-submission immutable reviewed decision where available, and frozen review facts. The migration
test restores all migration leaf nodes and is cross-run with the pre-existing witness migration
suite to prove graph isolation.

Commands/output: `terminal-logs/04-green-cycle-migration.txt` and
`terminal-logs/14-green-migration-isolation-repair.txt`.

## Concurrency proof source

`SanctionSubmissionConcurrencyTests.test_concurrent_returned_cycle_resubmissions_create_one_cycle_two_ledger`
uses the established PostgreSQL application-lock coordination. It asserts one cycle-2 shell, one
new sanction-submission audit/workflow evidence set, and an unchanged cycle-1 case/action ledger.
The selected slice declares `postgresql-five-race-acceptance`. The sandbox's local attempt is
retained in `terminal-logs/17-postgresql-cycle-race-1.txt` and shows Unix-socket access denied by
the sandbox. Ralph therefore runs this class twice in its trusted PostgreSQL validation environment
before accepting the slice.
