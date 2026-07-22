# Execution Plan

Selected slice: 011E-recovery-decision-approval

## Boundary

Implement only the backend recovery-decision approval composition described by slice 011E. Reuse
the existing approvals owner and the submitted Non-Payment Note/default workflow. Do not execute a
recovery action, add frontend work, define unresolved recovery policy, or change generic approval
semantics.

## Planned TDD Behaviours

1. Add one public/API behaviour test showing that a matching terminal-approved recovery approval
   creates one frozen decision and exposes only its approved next action; retain RED and GREEN logs.
2. Add one negative behaviour at a time for approval/note/default mismatch, non-terminal or
   rejected/returned approval, changed action, missing reason, forged status, conflict/maker-checker
   or insufficient authority, changed replay, and duplicate decision; minimally implement each
   behaviour before proceeding.
3. Add the declared PostgreSQL concurrency acceptance proving simultaneous requests retain one
   decision and event chain.
4. Add the migration and recovery permission catalog entry needed by the public endpoint, preserving
   the existing standard response/error envelopes and immutable cross-referenced audit evidence.

## Verification and Evidence

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Save each focused RED/GREEN result under `evidence/terminal-logs/`.
- Run focused recovery/default and reverse approval-owner tests, Django check, and migration-sync.
  Do not run the complete backend suite or coverage; independent validation owns that High-risk lane.
- Save representative API responses and schema/race evidence, then complete `risk-assessment.md`,
  `review-packet.md`, and `final-summary.md`. Set the review result exactly to
  `Ready for independent validation`.

## Permissions

The required candidate paths are expected under `sfpcl_credit/**`, `docs/working/**`, and this run's
`.ralph/runs/**`, all listed as writable without approval in `.ralph/permissions.json`. Protected and
forbidden paths, including `docs/source/**`, scripts, Ralph configuration/permissions, and Git
metadata, will not be modified. Exact candidate paths will be rechecked after code discovery and
before the first product edit.
