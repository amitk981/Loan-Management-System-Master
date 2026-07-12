# Review Packet: 2026-07-13_044409_architecture_review

## Result
Success

## Slice
architecture-review

## Review Window

`git diff 190eb5c...HEAD`: 006Y16, 006Z9, 006Z10, and 007A.

## Outcome

No production code changed. The review accepted 006Y16's witness nondisclosure contract, 006Z9's
decision-route agreement, 006Z10's real mounted/browser submit lifecycle, and 007A's sequential
exact/above/exception matrix facts. It created four corrective boundaries:

- 006Z11: separate action permission from member scope and retain every service-evidence maker.
- 006Z12: complete stale/supply/missing-fact borrower-limit rows and the full zero-write ledger.
- 007A2: protect full configuration history, validate committee authority, paginate lists, and run
  the approval PostgreSQL races directly twice.
- 007A3: require reason plus distinct Admin/CFO-or-CS maker-checker activation.

007B now depends on 007A3 and consumes the corrected historical rule/committee resolvers.

## Traceability

- Auth §§19.1/25.1 separate object scope from action permission; current code grants every
  `members.member.read` holder global detail access. 006Z11 owns the final assignment projection.
- 006Z10 explicitly named stale authority, changed supply, missing facts, and complete assessment
  snapshots; the retained matrix omits those rows/categories. 006Z12 owns proof closure.
- Auth §§31.1-31.2 requires Approval Matrix reason plus Admin + CFO/CS approval; current create/
  supersede activates immediately with one author/approver. 007A3 owns governance.
- Data-model §§15.1-15.2 and CFG-004 require retained effective history. Current validation ignores
  superseded rows while the resolver reads them, allowing an ambiguous historical backfill. 007A2
  owns lifecycle/non-overlap and committee authority.
- Full standards/spec findings and functional-ID disposition are in
  `docs/working/REVIEW_FINDINGS.md`.

## Validation

- Slice queue lint and `git diff --check`: pass; no protected/source diff.
- Frontend: build, typecheck, lint, and 207/207 tests pass.
- Backend: check and migration sync pass; 512 tests pass with 14 PostgreSQL-only skips; coverage is
  93% against the 85% floor.
- This review does not claim 007A approval-race PostgreSQL acceptance: retained evidence selected
  five older tests and omitted `ApprovalMatrixConcurrencyTests`.

## Recommended Next Action
Run 006Z11, 006Z12, 007A2, and 007A3 before 007B; separately correct the protected PostgreSQL
validator discovery so declared slice-specific races cannot be reported as passing when omitted.
