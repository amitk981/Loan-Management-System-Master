# Execution Plan

Selected slice: 009G-utr-capture-and-transfer-success

## Scope and source contract

- Extend the existing `DisbursementWorkflow` public owner with the exact API-contract §31.4
  transfer-success action; do not introduce another public workflow owner or any frontend work.
- Consume the locked 009F2 current-disbursement decision in approved state, then reconcile its
  terminal authorisation tuple and a current restricted application/account-scoped evidence file.
- Persist one normalized globally unique manual bank transfer and one immutable success evidence
  tuple, fund the exact approved amount, activate the sanctioned loan, and append one status
  history atomically. Preserve all initiation/CFC facts and leave advice, register, checklist,
  repayment, schedule, interest, and communication truth absent.

## TDD tracer bullets

1. Add one public API success test that starts from the genuine 009F2 owner-backed approved fixture
   and proves the response, bank transfer, funded active account, history, safe audit/workflow, and
   absence of later-slice side effects. Run it first and save RED output.
2. Add the smallest model/migration, workflow action, view, and route needed to make that tracer
   green; save GREEN output.
3. Add public behavior tests incrementally for exact replay/changed replay, duplicate normalized
   UTR, malformed input/time/evidence, permission and operational scope, stale authorisation/owner
   evidence, already-funded state, and database aggregate constraints. Keep every rejected path
   zero-write.
4. Add the declared PostgreSQL five-caller race test using the same public owner path; run the race
   class twice and retain one complete winner with no loser artifacts.

## Planned files and limits

- Backend only: disbursement models/migration, current evidence/workflow modules, view/URL, and one
  focused transfer-success test module, plus the API contract working document if required.
- At most one migration; stay below the configured 30-file/2,000-line limits and add no dependency.
- Only permitted paths in `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`,
  `.ralph/progress.md`, and this run folder will be edited. Protected/source paths remain untouched.

## Verification and handoff

- Run focused transfer API/state/permission tests with the mandated Ralph virtualenv interpreter,
  Django check, migration sync, Ruff/lint for changed backend files, and the PostgreSQL race twice.
  Do not run the complete backend suite or coverage; the orchestrator owns those gates.
- Save sanitized success/replay/conflict examples and terminal logs, then complete changed-files,
  risk assessment, review packet, final summary, slice status, state, progress, handoff, digest, and
  sharpen the next one or two eligible Not Started slices from already-opened source material.
