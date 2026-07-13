# Review Packet: 2026-07-13_164911_architecture_review

## Result
Complete; findings recorded and all configured gates pass.

## Slice
architecture-review

## Review Window

`48ef331...e46ced6`: 007C3, 007D2, 007D3, and 007E.

## Standards

- Critical: conflict replacement can satisfy a two-Director rule with one duplicated Director.
- High: a successful alternate action is absent from canonical collection/detail/action history.
- High: the committee-wide helper index leaks `total_count` to an unused alternate.
- Medium judgment: ordinary `ApprovalCase.save()` hides engine evaluation and cross-table read-
  projection mutation. Corrective: 007E2 for all four.

## Spec

- Critical: 007E's no-authority-reduction rule fails for the two-Director exclusion edge.
- High: 007C3 does not scope an unused alternate out before counts/pagination.
- Medium: conflict-limited read can run before the base case object boundary.
- Medium: the §17.1 public enrichment/denial and non-assigned related-party flag matrices are
  incomplete. Corrective: 007E2.

## Traceability

- Auth §§16.2/27.1 and security §12 require distinct configured authority; the reproduced effective
  set has only two distinct users for three slots.
- API §25.4 and codebase-design §26 require caller-visible immutable action history; the reproduced
  approved alternate has no canonical history row.
- Auth §§32.1/37.3 and 007C3 require scope before pagination; the reproduced unused alternate gets
  empty data with `total_count: 1`.
- M05-FR-007/008/010 remain substantive; M05-FR-011 is unsafe until 007E2. M05-FR-009 stays with
  007H and M05-FR-012 evidence recording/gating stays with 007G after 007E2 fixes flag scope.

## Validation

Three dynamic isolated-Django probes retained the RED defects. Frontend build/typecheck/lint and
208 tests pass. Backend check/migration sync and 637 tests pass with 19 expected PostgreSQL-only
skips and 93% coverage. Queue/dependency lint, state JSON, diff whitespace, and blocked-slice checks
pass. No production, protected, or source file changed.

## Recommended Next Action
Run 007E2, then 007F and 007G in dependency order.
