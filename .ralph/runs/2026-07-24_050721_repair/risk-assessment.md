# Risk Assessment

Risk level: Low repair within the selected slice's Medium-risk candidate.

- Selected slice: 012B-register-exports
- Mode: same-worktree repair
- Demonstrated validation domain: API permission-code contract harness
- Manual review required: independent Ralph validation before commit

## Scope

The current candidate was preserved. Product code changed only in
`sfpcl_credit/reports/modules/report_export.py`: two retired permission-code literals now reuse the
existing shared `FORBIDDEN` constant. Repair artifacts are confined to the current repair run.

No model, migration, URL, task, storage, report selector, source document, protected file, queue
status, state, or progress bookkeeping was changed by this repair.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Public and audit denial codes drift | Both sites now reuse the single canonical API constant; the exact AST contract harness is green. |
| Export denial or failure behavior regresses | All eight focused report-export API/service tests pass, including denial auditing and failure handling. |
| Repair causes schema/config drift | Django system check and `makemigrations --check --dry-run` pass. |
| Broader candidate has an undiscovered failure | The repair deliberately does not claim full-suite coverage; Ralph must rerun the authoritative independent lane before commit. |

## Residual Risk

Only the independently selected complete backend coverage lane can establish that the preserved
full candidate is globally green. No residual risk specific to the two-line permission-code repair
is known.
