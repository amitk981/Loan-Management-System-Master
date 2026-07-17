# Execution Plan

Selected slice: 009E3-disbursement-amount-and-source-bank-governance-closure

## Scope and source contract

- Change only the 009E3 backend/business slice: positive lesser disbursement amounts, genuine
  loan-lifecycle evidence, source-bank permission/catalogue and versioned governance integrity,
  public-boundary tests, and the declared PostgreSQL races.
- Preserve the existing typed readiness decision, API idempotency/error contract, redaction, exact
  frozen initiation evidence, and absence of CFC/transfer/funding side effects.
- Apply screen-spec S38-S39, integrations 9.1-9.5, codebase-design 6.5/16.3-16.4/22/26/38/42,
  auth-permissions 15.6/26.5/30.2/31.2, and data-model 19.3/29-30/34.

## TDD tracer bullets

1. RED: add public initiation tests for two lesser positive 18,2 amounts and amount-boundary/
   overage failures; GREEN: relax only the exact-equality guard while retaining unfunded, terms,
   sanction, replay, and frozen-evidence checks.
2. RED: add database/public-governance tests requiring complete activation evidence and a canonical
   unassigned Critical permission; GREEN: add the catalogue row and one migration-backed invariant,
   restructuring activation so an active row is never transiently incomplete.
3. RED: expand replacement tests to require explicit predecessor linkage, activation/deactivation
   versions and audits, closed effective range, immutable original activation proof, and fail-closed
   current resolution after one-field mutations; GREEN: implement the append-only lifecycle.
4. RED: exercise initiation with a loan created by `loans.modules.loan_account_lifecycle` and reject
   raw or corrupted creation evidence with zero writes; GREEN: expose/consume a narrow canonical
   loan-owner decision at the disbursement workflow boundary.
5. RED: replace private source-shape assertions with public `DisbursementWorkflow` behavior and an
   executable dependency-boundary test; GREEN/refactor: keep one public owner and remove brittle
   implementation coupling.
6. RED/GREEN: add five-caller first-activation and replacement races, run twice on PostgreSQL, and
   normalize unique/concurrent losers to the stable domain conflict without orphan evidence.

## Verification and retained artifacts

- Save every focused failing-first and passing run under `evidence/terminal-logs/`, including the
  amount matrix, governance lifecycle, genuine owner trace, and twice-run PostgreSQL races.
- Run focused backend tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, then Django check
  and `makemigrations --check`; do not run the complete backend suite or coverage locally.
- Run relevant static dependency tests and any impacted frontend gates only if frontend files are
  touched (none are expected).
- Review the diff against the slice and limits; write changed-files, risk assessment, review packet,
  and final summary; update assumptions only if source silence is encountered.
- Sharpen the next one or two Not Started slices using only already-open Epic 009 source material,
  then update progress, state, handoff, and mark only 009E3 Complete.
