# Review Packet: 2026-07-13_083408_architecture_review

## Result
Complete; findings recorded and all configured gates pass.

## Slice
architecture-review

## Review Window

`8b1af41...a58effa`: 006Z13, CR-002, CR-003, and 007A4, including both CR intake commits.

## Findings and Corrections

- 006Z13 delivered structural database constraints but not its demanded permission-versus-scope
  public matrix; its calculation caller proof uses raw source strings around an unused seam.
  Corrective slice: `006Z14-member-authority-action-and-calculation-proof-closure`.
- 007A4 restored real governed PostgreSQL races but does not compare the full loser/case ledger or
  execute the required conflicting open-case race. Corrective slice:
  `007A5-approval-governance-complete-loser-ledger`.
- 007B now depends on 007A5 and explicitly owns production population of the unrouted 006G shell;
  007C excludes empty shells and uses stored historical snapshots only.

## Traceability

- Auth §25.1/§32.1 and codebase-design §§26-27 require permission and object scope to be proved
  separately through public interfaces; 006Z14 owns the missing matrix.
- Auth CFG-007 and codebase-design §22.3 require approval configuration races to preserve existing
  cases and loser state; 007A5 owns complete PostgreSQL equality.
- Data-model §15.3 requires rule/amount/required-approver case snapshots; the existing shell remains
  explicitly unrouted until 007B atomically populates it through ADR-0005's approval-case seam.
- M02-FR-004..006 and M05-FR-003..006 remain substantive but partially proven as recorded above;
  M04-FR-005..007 remain passing.

## Validation

Frontend build/typecheck/lint and 208 tests pass. Backend check/migration sync and 535 tests pass
with 16 expected PostgreSQL-only skips and 93% coverage. Queue lint, state JSON, diff whitespace,
blocked-slice, and protected-path checks pass. See `evidence/terminal-logs/`.

## Recommended Next Action
Run 006Z14, then 007A5, before 007B.
