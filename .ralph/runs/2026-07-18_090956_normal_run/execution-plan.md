# Execution Plan

Selected slice: 009H3BB-communications-finalization-and-race-closure

## Scope and constraints

- Implement only accepted advice finalization and race closure; consume the existing 009H3BA
  frozen outbox/provider decision and the 009H3A receipt schema without adding a migration.
- Keep disbursements responsible for authority, locked financial context, and its immutable action.
  Make `communications.modules.communication_dispatcher` the deep module whose interface returns an
  immutable ordinary delivery decision and whose implementation owns receipt, protected
  Communication, delivery/audit/workflow evidence, finalization, and reconciliation.
- Preserve the public send-advice endpoint, all 009H2 role/object/current-truth rules, masking, exact
  replay, and zero financial/downstream side effects. Do not touch frontend or protected/source
  files.
- Keep the product diff below the slice's 1,350-line forecast stop threshold and introduce no new
  dependency or database migration.

## Test-first implementation

1. Inspect the dispatcher, transitional disbursement advice module, models/migrations, and focused
   public/owner tests; map the existing retained chain and dependency direction.
2. RED -> GREEN: add one public-interface crash test for provider acceptance followed by failure
   before receipt retention. Save the failing output, minimally move receipt/finalization recovery
   behind the communications interface, and save matching green output.
3. RED -> GREEN: add one public-interface crash test for failure before protected Communication
   commit. Save the failing output, minimally complete atomic communications-owned finalization and
   disbursement decision consumption, and save matching green output.
4. Incrementally extend the focused matrix for exact fresh-adapter replay, changed frozen facts,
   rejection/malformed results, redacted audit/workflow evidence, complete ledger identity, role and
   scope denials, and zero financial writes. Reduce the legacy disbursement module to a shallow
   context/authority consumer with no duplicate finalization policy.
5. Add/complete two independently declared PostgreSQL five-caller race methods and run both methods
   twice, preserving every adapter result and asserting one winner plus four clean losers.

## Verification and evidence

- Run the complete focused communications/advice/public suite with the mandated backend interpreter;
  save `green-advice-owner-suite-final.txt` and sanitized contract evidence.
- Run both PostgreSQL race methods in two separate commands and save
  `postgresql-final-five-race-run-1.txt` and `postgresql-final-five-race-run-2.txt`.
- Run Django check, migration sync, Python compile, dependency-cycle/owner checks, retained 009H3A
  regressions, protected-path check, whitespace/diff checks, and focused relevant tests only (the
  orchestrator owns the complete backend coverage gate).
- Record changed files, honest high-risk assessment, traceable review packet, final summary, state,
  progress, handoff, digest, selected-slice completion, and sharpen/recheck the next one or two
  already-open Not Started slices using only requirements already loaded.
