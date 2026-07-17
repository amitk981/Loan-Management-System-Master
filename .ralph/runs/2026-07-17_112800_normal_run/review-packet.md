# Review Packet: 2026-07-17_112800_normal_run

## Result
Complete pending independent orchestrator validation

## Slice
009E3-disbursement-amount-and-source-bank-governance-closure

## Recommended Next Action
Run the authoritative backend coverage/protected-path/queue gates, then commit and merge through the
Ralph orchestrator. If green, execute 009F2 before 009G.

## Outcome

- Positive lesser 18,2 amounts within immutable terms/sanction reach CFC review and retain the exact
  amount across row, audit, workflow trace, task, and CFC terminal evidence.
- Initiation rejects changed/raw loan creation evidence and freezes the lifecycle status-history,
  audit, and workflow identities.
- Source-bank activation is a canonical unassigned Critical permission and an active row cannot be
  inserted without activation version/audit proof.
- Replacement retains original activation evidence, appends explicit predecessor/deactivation
  version/audit facts, closes the effective range, and resolves only a complete coherent chain.
- Twice-run PostgreSQL five-caller first/replacement and initiation races retain one winner with no
  orphan evidence.

## Traceability for non-developers

- The source says S38 permits the sanctioned amount or an approved lesser amount and S39 makes it
  editable within sanction limits. The workflow accepts positive values up to both terms/sanction;
  verified by `test_positive_lesser_amount_is_frozen_for_cfc_review` and
  `test_cfc_approves_exact_frozen_lesser_amount`.
- Auth CFG-003/004/005 says configuration is effective-dated, old decisions remain available, and
  activation creates audit. The source-bank owner now retains activation and deactivation versions,
  audits, predecessor, and closed range; verified by
  `test_source_bank_replacement_retains_exact_closed_history_and_fails_closed`.
- Codebase-design §§22/26 says financial/config activation uses transactions/concurrency control and
  tests cross module interfaces. Public workflow tests plus `SourceBankGovernanceRaceTests` prove
  the behavior twice on PostgreSQL without private source-shape assertions.
- Data-model §19.3 says amount is numeric 18,2 and cannot exceed sanction. The amount matrix proves
  zero/negative/precision/size/overage rejection and exact replay conflict.

## Verification

- Backend: 44 focused disbursement/loan tests, 49 documentation-owner tests, 16 catalogue tests.
- PostgreSQL: four tests covering two full source-bank first/replacement rounds and two genuine
  initiation rounds; all pass.
- Static/database: Django check, migration apply, migration sync, compileall, changed-scope Ruff.
- An exploratory whole-file Ruff pass also reported the retained documentation test file's existing
  24 `E702` and one `F841` baseline findings outside this slice's edits; the follow-up changed-scope
  pass with those known baseline codes excluded is green. Ruff is not a configured backend gate.
- Frontend configured gates: ESLint, TypeScript, production build, 327 Vitest tests.
- The complete backend coverage suite was intentionally not run locally; Ralph owns that single
  authoritative execution.

## Evidence index

- `evidence/amount-boundary-matrix.md`
- `evidence/source-bank-lifecycle-manifest.md`
- `evidence/genuine-loan-owner-initiation-trace.md`
- `evidence/terminal-logs/`
