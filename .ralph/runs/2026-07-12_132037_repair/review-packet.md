# Review Packet: 2026-07-12_132037_repair

## Result
Ready for independent validation

## Slice
006X5-credit-public-action-write-matrix-closure

## Recommended Next Action
Run full independent repair validation, then commit the preserved 006X5 implementation.

## Failure and Repair

- Exact failure: protected PostgreSQL acceptance expected `Found 5`/`Ran 5`; the preserved slice
  produced a fully green but rejected six-test log.
- Root cause: the new stale-enabled projection race was added as a sixth discovered method even
  though the orchestrator's declared capability contract fixes the three acceptance classes at
  five tests.
- Repair: capture the sanction action projection inside the existing duplicate-submission race,
  then retain its concurrent winner, exact stale loser denial, and zero loser evidence assertions.

## Traceability

- API contracts §44 requires backend enforcement after action projection. The merged sanction race
  projects `credit.appraisal.submit_sanction` as enabled, then proves the competing stale write is
  denied by the public handoff after the winner changes state.
- Codebase design §26.3 requires a real concurrency test. PostgreSQL logs show all five declared
  races executing twice without skips, including the merged sanction projection/write proof.
- The red and green predicate logs provide the exact validator feedback loop; both fresh acceptance
  logs and non-secret environment facts are self-contained under `evidence/`.

## Review Notes

- No production, frontend, migration, dependency, API contract, source, or protected file changed
  during repair.
- The next Not Started slices 006Y5 and 006Y6 were rechecked and remain concrete with fields,
  authorities, validation rules, endpoints/interactions, and acceptance tests.
