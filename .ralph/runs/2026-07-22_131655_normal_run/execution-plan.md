# Execution Plan

Selected slice: 011D-non-payment-note-workflow

## Execution boundary

- Implement only the backend Non-Payment Note persistence, recovery-domain workflow, two POST APIs,
  approval handoff, permissions, audit, migration, and focused regressions declared by slice 011D.
- Do not add recovery decisions/actions, frontend work, canonical-ledger mutations, or edit protected,
  source, queue-status, state, progress, changed-files, or mechanical handoff files.
- Allowed edit roots were checked against `.ralph/permissions.json`: product work stays under
  `sfpcl_credit/**`; run evidence stays under this run directory; any API contract clarification may
  use `docs/working/**`. One database migration is permitted by `.ralph/config.yaml`.

## Public seam and behaviors

Use `recovery.modules.recovery_workflow` as the deep module interface. Views remain thin adapters,
and tests exercise the HTTP/domain interfaces rather than private helpers.

1. RED -> GREEN: an authorised Credit Assessment user creates the one draft only after an approved,
   expired, unpaid extension; the module derives current principal/interest and freezes case,
   due/grace/extension, assessment, evidence, narrative, recommendation, and preparer truth.
2. RED -> GREEN: reject absent/active extension, cured/closed/foreign cases, incomplete narrative,
   negative or caller-forged amounts, and foreign evidence; exact replay and concurrent creation
   converge on one note.
3. RED -> GREEN: an authorised Credit Manager submits the draft once, freezes decision inputs and
   submission time, and creates/reuses one approval case/task through the existing approval owner.
4. RED -> GREEN: reject unauthorised/foreign submission and post-submit mutation; exact replay and
   concurrent submission converge on one approval chain. Preserve returned-state semantics without
   inventing the later recovery-decision workflow.
5. Add the exact two-test PostgreSQL acceptance class declared by the slice and focused reverse
   regressions proving prior default/extension timelines remain immutable and note existence alone
   exposes no recovery action.

## Verification and evidence

- Save every focused failing and passing command under `evidence/terminal-logs/`, using only
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for backend commands.
- Run focused default/recovery/approval/API/permission tests, then `manage.py check` and
  `makemigrations --check`. Do not run the complete backend suite or coverage lane; Ralph owns it.
- Inspect diff stats and targeted hunks, complete `risk-assessment.md`, and perform a spec/standards
  self-review recorded in `review-packet.md` with source-to-code-to-test traceability.
- Finish only with the review packet Result exactly `Ready for independent validation`.

## Completion record

- Completed the create, submit, returned-correction, retained-document, object-scope, audit, and
  approval-handoff behaviors through incremental red/green tests.
- Completed focused reverse regressions for existing default, grace, extension, approval-routing,
  and catalogue behavior.
- Completed Django system and migration-drift checks. The exact two-test PostgreSQL class is
  locally discovered and intentionally skipped on SQLite; Ralph owns its authoritative PostgreSQL
  execution.
- Completed independent Standards and Spec reviews, repaired every blocking finding, and reran the
  impacted suites.
