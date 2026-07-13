# Review Packet: 2026-07-13_131622_architecture_review

## Result
Complete; findings recorded and all configured gates pass.

## Slice
architecture-review

## Review Window

`26cc7a8...d0f2fbe`: 006Z15, 007A6, 007C2, and 007D. Protected-doc maintenance commit `25212f3`
was excluded from product findings.

## Standards

- High: 007C2 denies source-required Credit Manager, Company Secretary, and Auditor read-only
  sanction-package scope while correctly denying arbitrary permission holders. Corrective: 007C3.
- High: a returned one-to-one ApprovalCase cannot be resubmitted, contrary to source cardinality
  and the new-cycle invariant. Corrective: 007D3.
- Medium judgment: approval lists materialize the broad ledger before Python scope filtering and
  pagination. Corrective: 007C3 selector work.
- 006Z15 and 007A6 close their prior public-action and winner-evidence findings with no new material
  standard violation.

## Spec

- High: collection returns raw approver snapshots after actions while detail/action include
  decision history. Corrective: 007D2.
- High: the mandatory final-action PostgreSQL race and exact loser ledger are absent. Corrective:
  007D2.
- Medium: terminal workflow notifications bypass the required communication adapter. Corrective:
  007D2.
- Medium: application/appraisal guards and the promised closed/excluded/contradictory/per-action
  denial matrix are incomplete. Corrective: 007D2.

Summary: Standards 2 High and 1 Medium/judgment; worst are missing source read scopes and the return
dead end. Spec 2 High and 2 Medium; worst are false serializer parity and absent PostgreSQL races.

## Traceability

- Auth §§14.1/19.1/26.3 requires read-only sanction-package scopes distinct from approver action
  scope; 007C3 owns the persisted predicate and bounded selector.
- Data-model approval cardinality and codebase-design §13.1 require a fresh immutable cycle after a
  returned/materially changed case; 007D3 owns it.
- API §§25.3-25.8/§44 and codebase-design §§22.3/26 require read/write parity and authoritative
  concurrency proof; 007D2 owns both twice-run PostgreSQL races.
- M02-FR-004..006 are substantive. M05-FR-001..006 are substantive; 007/008 remain partial on the
  recorded action gaps, 009 remains 007H, and 010 remains partial until 007D2.

## Validation

Frontend build/typecheck/lint and 208 tests pass. Backend check/migration sync and 592 tests pass
with 16 expected PostgreSQL-only skips and 93% coverage. Queue lint, state JSON, diff whitespace,
blocked-slice, and dependency checks pass. See `evidence/terminal-logs/`.

## Recommended Next Action

Run 007C3, then 007D2 and 007D3 before 007E.
