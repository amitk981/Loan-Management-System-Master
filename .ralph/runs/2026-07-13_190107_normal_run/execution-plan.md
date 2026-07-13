# Execution Plan

Selected slice: 007H-credit-sanction-register

## Scope and source contract

- Implement only the immutable Credit Sanction Register and the two read endpoints in slice 007H.
- Preserve the existing approval-action transaction as the sole terminal-decision seam. Generate one
  register row for an approved or rejected case in that transaction, alongside the action, case,
  sanction decision (approved only), workflow event, audit evidence, and existing notification.
- Project the functional specification's 15 fields from frozen application, appraisal, case,
  action, 007E conflict/abstention, 007F exception, and 007G general-meeting records. Do not resolve
  exception or meeting evidence by latest application record.
- Keep Annexure K/template code absent pending OC-002; expose no mutation interface.

## TDD tracer bullets

1. RED/GREEN: final approval creates exactly one immutable register row and the sanction-decision
   read endpoint returns the source §25.8 contract.
2. RED/GREEN: rejection creates a register row without inventing a sanction decision; replayed or
   stale terminal actions cannot duplicate it.
3. RED/GREEN: the register endpoint returns all 15 fields, including same-case exception,
   conflict/abstention, and frozen general-meeting references.
4. RED/GREEN: validate April-March financial-year and decision filters, bounded pagination,
   authentication/permission negatives, 404-before-decision behavior, and absent mutation routes.
5. Verify register creation audit/workflow linkage and database uniqueness/immutability guards.

Each cycle uses the public HTTP/action interface, runs the focused test, and saves failing and
passing terminal output under `evidence/terminal-logs/`.

## Implementation shape

- Add one approval-owned register model/migration with frozen projection columns, a one-to-one case
  key, nullable sanction-decision link for rejected outcomes, indexes for decision/date filtering,
  and model/database immutability protections consistent with existing generated registers.
- Add one deep `sanction_register` module whose small interface owns terminal generation,
  serialization, filters, pagination, and sanction-decision serialization.
- Call generation from `approval_actions` only after the terminal case/action facts exist and before
  the surrounding atomic transaction commits.
- Add GET-only view/URL adapters and permission checks for
  `approvals.sanction_register.read` and `approvals.sanction.read`.
- Update API contract/source traceability docs, the Epic 007 digest, and the unresolved Annexure K
  assumption without changing source material.

## Verification and closeout

- Run focused tests after every RED/GREEN cycle, then backend check, migration sync, full backend
  coverage, frontend build/typecheck/lint/tests, and slice-queue/protected-path checks available to
  the agent.
- Review the final diff separately for documented standards and slice fidelity; repair findings.
- Save API examples/logs, changed-files, risk assessment, review packet, final summary, and update
  progress, handoff, state, selected-slice status, plus sharpen the next one or two Not Started
  slices using already-opened Epic 007 material.
