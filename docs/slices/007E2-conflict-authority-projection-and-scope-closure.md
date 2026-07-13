# Slice 007E2: Conflict Authority, Projection, and Scope Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007E

## Runtime Capabilities

none

## Goal

Close the independent-review defects in conflict replacement: preserve the exact number of
distinct CFO/Director authorities, expose every replacement action in canonical case history, and
keep unused committee candidates nondisclosed before list counts and pagination.

## Source / Review References

- `docs/source/auth-permissions.md` §§16.2, 17.1-17.3, 19.1, 27.1, 32.1, and 37.3
- `docs/source/api-contracts.md` §§25.3-25.8 and §44
- `docs/source/data-model.md` §§15.3-15.5, §30, and §34
- `docs/source/functional-spec.md` M05-FR-004..012
- `docs/source/security-privacy.md` §§12.1-12.3
- `docs/source/codebase-design.md` §§13.1-13.2, 26.1-26.3, 27.1, and 42.1-42.2
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_164911_architecture_review`

## Concrete Requirements

1. Resolve conflict replacements as distinct frozen authority slots. A user may occupy at most one
   effective slot; excluding either Director on a CFO + two-Director route cannot reuse the other
   Director twice. Authority is satisfiable only when the exact configured role counts are filled
   by distinct non-conflicted frozen candidates. Otherwise enrichment/abstention atomically closes
   the case as `blocked_by_conflict`, creates no sanction, and records the exact missing role.
2. Keep `required_approvers_json` immutable as route provenance, but make the one canonical
   collection/detail/action projection show the executable replacement mapping and every immutable
   action. An approved case cannot display an excluded original Director as undecided while hiding
   the alternate's approval. Document the response shape in `API_CONTRACTS.md`; collection, detail,
   action, returned history, and later cycles must agree byte-for-byte on authority/action facts.
3. Replace the read selector's over-broad committee-candidate index with an exact approval-owned
   read projection: original required/history actors plus currently effective replacements, never
   an unused committee alternate. Backfill existing rows deterministically. Ordinary list counts
   and pagination must be exact in SQL; an unused second Director with `approvals.case.read` gets an
   empty page with `total_count: 0` and direct `403 OBJECT_ACCESS_DENIED`.
4. Apply COI-005 only after the base case object boundary. A conflicted actor retains limited
   history read only if they were an original required actor, an effective replacement, or already
   acted in that cycle. Merely appearing in the frozen committee candidate pool or in a declaration
   cannot create read scope, queue membership, or action authority.
5. Preserve complete related-party detection independently from committee assignment: active
   borrower/Director-relative/Sanction-Committee-member declarations must set the immutable general-
   meeting flag even when the related Director is not a current case approver. Conflict exclusions
   still apply only to actual frozen authority candidates. Reject blank/whitespace declaration
   reasons before enrichment can produce an incoherent routed case.
6. Move coherence/read-index synchronization behind one explicit approval-owned projection updater
   invoked by case creation, enrichment, actions/abstention, appraisal-driven refresh, and migration.
   An ordinary model save must not hide cross-table workflow mutation or create a models-to-modules
   ownership cycle. Tests must prove every production writer refreshes the projection atomically.

## Test Cases

- Public enrichment and final-action paths for CFO + two Directors with Director 1 excluded,
  Director 2 excluded, both alternates unavailable, and self-abstention; assert distinct role/user
  sets and exact no-sanction blocked ledgers.
- One-Director replacement through collection, detail, approve response, final readback, and
  returned history; the alternate decision/acted-at/replacement attribution is visible everywhere
  while immutable route provenance is unchanged.
- Unused committee alternate with read permission, with a declaration, and after grant removal:
  ordinary/assigned counts remain zero and detail/action stay nondisclosing with zero writes.
- General-meeting flag matrix for Director borrower, Director relative, committee-member borrower,
  non-committee related Director, material interest only, and maker-checker only.
- Each §17.1 class crosses public enrichment -> queue/detail -> approve/reject/return denial with the
  exact §17.3 response and sole COI-006 audit exception; no manually injected exclusion may stand in
  for the class under test.
- Migration/backfill and query-count tests prove exact read projection, bounded SQL pagination, and
  unchanged immutable case/action/audit/workflow/communication history.

## Evidence Required

Retain RED output for the three architecture-review probes, GREEN public authority/projection/scope
matrices, migration proof, exact ledgers, focused API examples, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- A configured Director count can never be satisfied by duplicate user identity.
- Every actor visible in canonical approval history is attributable to immutable route, replacement,
  exclusion, or action evidence; unused candidates disclose neither rows nor counts.
- 007F/007G can consume one coherent conflict outcome without reimplementing authority or scope.
