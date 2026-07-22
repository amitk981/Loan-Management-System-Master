# Review Packet: 2026-07-22_143202_repair

## Result
Ready for independent validation

## Slice
011D-non-payment-note-workflow

## Repair outcome

The bounded repair fixes the exact failed PostgreSQL acceptance domain without changing the 011D
contract. Non-Payment Note create and submit now retain the required workflow and canonical loan row
locks while excluding nullable relations from the locking query. This clears PostgreSQL's outer-join
lock error and prevents stale nullable approval caches during concurrent replay.

The diagnosing-bugs feedback loop materially shaped the repair: each newly exposed error was rerun
through the same exact two-test validator, and the final implementation was accepted only after the
original create and submit scenarios both passed together.

## Validation

| Check | Result | Evidence |
| --- | --- | --- |
| Exact PostgreSQL acceptance class | 2/2 passed; exit 0 | `evidence/terminal-logs/postgresql-acceptance-repair-4-final.log` |
| PostgreSQL environment | vendor PostgreSQL; version 14.20; exit 0 | `evidence/terminal-logs/postgresql-environment.log` |
| Focused Non-Payment Note API workflow | 6/6 passed; exit 0 | `evidence/terminal-logs/focused-repair-checks.log` |
| Django system check | passed | `evidence/terminal-logs/focused-repair-checks.log` |
| Migration drift | no changes detected | `evidence/terminal-logs/focused-repair-checks.log` |

## Traceability

| Source requirement | Repair behavior | Verification |
| --- | --- | --- |
| `api-contracts.md` §§35.6-35.7: create one note and submit it to committee | Create/submit serialize on their owning rows and canonical loan balance row | Both exact five-worker tests pass |
| `data-model.md` §21.4: one note per default case | Concurrent exact creates converge on one note | PostgreSQL create acceptance test |
| `functional-spec.md` M12-FR-010-011: formal note and committee routing | Concurrent exact submits converge on one approval chain | PostgreSQL submit acceptance test |

## Review findings

- Spec: no change to eligibility, amounts, authority, approval routing, or response behavior.
- Standards: atomic row locking remains explicit; nullable joins are not lock targets; no debug
  instrumentation or throwaway harness remains.
- Scope: only `sfpcl_credit/recovery/modules/recovery_workflow.py` changed in product code during the
  repair. Existing candidate files and prior-run evidence were preserved.
- Open blocking findings: none.

## Recommended Next Action
Run Ralph's full independent validation, including its two fresh PostgreSQL acceptance executions.
Commit only if that independent validation passes.
