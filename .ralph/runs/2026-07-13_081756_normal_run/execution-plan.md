# Execution Plan

Selected slice: `007A4-approval-governance-concurrency-and-case-snapshot-closure`

## Scope and constraints

- Work only in the approval-configuration backend/API seam, its tests/contracts, Ralph evidence,
  and required run/state/handoff/slice records. No frontend change is required.
- Preserve proposal-based maker-checker activation and retained historical resolution. Activation
  remains atomic behind `ApprovalConfigurationLock` and `decide_proposal`.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every Django/test/coverage command.
- Do not modify protected files, `docs/source/`, scripts, or git metadata.

## Behavior-first TDD sequence

1. Add a public proposal-detail/API authority test proving 401 for unauthenticated, 403 for an
   unrelated authenticated user, and 200 for maker, eligible checker, and matrix reader. Run it
   red, then implement the narrow participant/checker/read-permission boundary and canonical
   `APPROVAL_AUTHORITY_REQUIRED` mapping; rerun green.
2. Add independent public validation/lifecycle/history rows for both rule and committee resources,
   including inactive/duplicate/swapped authority, malformed/unknown/non-finite zero-write input,
   stale/replay/reject parity, backfill overlap, retained historical/current resolution, and
   approval-time authority revalidation. Advance one focused behavior at a time and retain red/green
   output where production changes are needed.
3. Add a real open `ApprovalCase` fixture and a complete stored-state ledger. Prove proposal,
   rejection, successful activation, conflicting loser, resolver calls, and detail reads preserve
   the case snapshot byte-for-byte. Add only the persistence needed for the immutable rule,
   committee, required-approver, decision-date, case-version, and workflow-event projection, with a
   synchronized migration if those fields are absent.
4. Replace all four stale PostgreSQL races with two pending proposals approved by distinct eligible
   checkers through `decide_proposal`. Assert exactly one effective activation and a complete loser
   proposal/effective/history/audit/case ledger for rule create, rule supersede, committee create,
   and committee supersede.

## Verification and evidence

- Save focused RED and GREEN terminal logs under
  `.ralph/runs/2026-07-13_081756_normal_run/evidence/terminal-logs/`.
- Run the governed `ApprovalMatrixConcurrencyTests` twice with
  `sfpcl_credit.config.postgres_test_settings`, retaining exact names/output and migration `0005`.
- Run dependency/module-boundary scans, focused coverage, Django check, migration sync, full backend
  coverage suite, and all configured frontend build/typecheck/lint/test gates.
- Update `docs/working/API_CONTRACTS.md`, the epic digest if distilled source facts need expansion,
  and sharpen the next one or two Not Started slices using already-open sources.
- Produce `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, then update
  `.ralph/state.json`, `.ralph/progress.md`, `docs/working/HANDOFF.md`, and mark only this slice Complete.
