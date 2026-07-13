# Ralph Handoff

## Last Run
2026-07-13_164911_architecture_review

## Current Status

The architecture review covered 007C3, 007D2, 007D3, and 007E from fixed point `48ef331`. 007C3's
source-reader grants, 007D2's guarded communication-backed actions/PostgreSQL races, and 007D3's
immutable correction/review cycles are otherwise substantive, but three executable probes exposed
one Critical authority flaw and two High public-boundary regressions.

On a CFO + two-Director route, excluding Director 1 can yield effective slots `(CFO, Director 2,
Director 2)` and the length-only check calls that satisfiable. On the lower one-Director route, a
real alternate can approve but is absent from canonical history. The selector's helper index also
contains the unused committee alternate, producing empty data with `total_count: 1` for a reader
who direct detail correctly denies. Conflict-limited access is evaluated before base object scope,
and the full §17.1 public enrichment/action matrix remains partial.

Corrective slice 007E2 now owns distinct role/user authority, replacement/action projection,
exact pre-pagination read projection/backfill, attributable COI-005 access, general-meeting flag
scope, and the explicit approval-owned projection update seam. 007F and 007G were sharpened to
consume that corrected outcome. No production code changed in this review.

## Validation

Independent Standards and Spec axes were retained in the run evidence. Dynamic isolated-Django
probes failed `1 != 0` for alternate count nondisclosure, `2 != 3` for distinct authority, and
`0 != 1` for alternate history visibility. These are review evidence, not implementation tests;
007E2 must turn them GREEN test-first.

Frontend build/typecheck/lint and all 208 tests pass. Backend check and migration sync pass; the
full 637-test suite passes with 19 expected PostgreSQL-only SQLite skips and 93% coverage. Slice
queue/dependency lint, state JSON, and diff whitespace checks pass. No Blocked slice exists, no
ADR was needed because source documents already decide the fixes, and CONTEXT.md remains truthful.

## Next Run

Run `007E2-conflict-authority-projection-and-scope-closure` next. It is the queue blocker for 007F
and must close the Critical duplicate-Director path before exception/register or general-meeting
work consumes approval outcomes. Then run 007F and 007G in dependency order.
