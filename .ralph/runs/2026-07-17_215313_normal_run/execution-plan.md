# Execution Plan

Selected slice: 009G3-post-transfer-aggregate-and-checklist-integrity-closure

## Scope and interface

- Keep `DisbursementWorkflow.mark_transfer_successful` and the existing public post-transfer
  checklist action as the only mutation interfaces; deepen their implementation rather than add a
  parallel workflow.
- Add one disbursements-owned protected aggregate relation from a successful disbursement to its
  exact `LoanRegisterUpdate`, with database constraints that forbid success without that relation
  and forbid pending/failed rows from carrying it.
- Preserve the existing API response shape and transfer/checklist transaction boundaries unless a
  source-required field is demonstrably missing.

## TDD tracer bullets

1. Add one public transfer-success test proving the returned success retains a protected register
   owner relation and cannot lose/reparent it. Run it RED, save the output, implement the minimum
   model/workflow/migration change, then run it GREEN and save the output.
2. Add public replay/tamper tests for missing, changed, cross-object, and duplicate register
   evidence. Extend the current-evidence reconciliation only enough to make each behavior pass.
3. Add public checklist-scope tests proving both the original initiator and a distinct current
   Stage-5 Senior Manager Finance assignee can sign, while stale, permission-only, role-only,
   inactive, cross-loan, and CFC-only actors remain denied.
4. Add public checklist replay tests that independently mutate or duplicate the completion action,
   audit, workflow, and version tuple. Reconcile exact meaning, comment, actor/role/team,
   request/network, states, relation ids, action ids, timestamps, and current transfer/register/
   advice facts, preserving zero writes on conflict.
5. Extend the declared PostgreSQL acceptance tests so transfer and checklist five-caller races run
   twice and retain one coherent winner with clean loser conflicts.

## Implementation and migration

- Inspect the existing 009G2 models, transfer owner, checklist coordinator, canonical Stage-5 scope
  selector, migrations, and focused tests before selecting exact field/constraint names.
- Create at most one disbursements migration. Preserve ids and backfill only singular coherent
  register rows; ambiguous legacy state must remain fail-closed rather than receive fabricated
  evidence.
- Keep disbursements as owner, use row locks for financial/current-evidence checks, and avoid new
  dependencies or frontend changes.

## Verification and handoff

- Save focused RED/GREEN terminal logs under `evidence/terminal-logs/` using the mandated Ralph
  Python interpreter.
- Run impacted backend tests, both PostgreSQL race methods when the local socket permits, Django
  check, and migration sync. Do not run the complete backend suite or coverage.
- Review the diff for protected paths, migration count, aggregate invariants, exact replay, object
  nondisclosure, and slice-only scope.
- Save changed-files, risk assessment, review packet, final summary, and evidence; update the Epic
  009 digest, assumptions only if needed, state, progress, handoff, and this slice status. Recheck
  and sharpen the next one or two Not Started slices using only already-opened source material.
