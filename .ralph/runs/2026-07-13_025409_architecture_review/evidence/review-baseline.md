# Architecture Review Baseline

- Fixed point: `c31ac790d510a4e5bf06e2cdcbf311ec71d66fca`
- Diff: `git diff c31ac79...HEAD`
- Commits reviewed:
  - `40cea5e` — 006X10 credit object-scope executable rows
  - `81884ed` — 006Y15 witness authority matrix
  - `a2c857c` — 006Z7 active-member authority/evidence races
  - `53420e7` — 006Z8 portal limit provenance/interaction, including repairs
- Independent axes: Standards and Specification reviews were run separately and reconciled only
  after each report completed.
- Product code changes by this review: none.

## Evidence inspected

- Four product/test diffs and their slice contracts.
- 006X10 independently selected row/omission logs.
- 006Y15 public witness API red/green and matrix logs.
- 006Z7 two-run PostgreSQL active-member and credit race logs.
- 006Z8 repair chain, two final trusted-browser runs, and four final screenshots.
- Epic 004/006 digests and cited auth/API/data-model/codebase/functional sections.

## Functional disposition

- Substantive: BR-004, BR-006, BR-007, M02-FR-004, M02-FR-006, M04-FR-005,
  M04-FR-006, and M04-FR-007 calculation behavior.
- Partial: BR-003, BR-005, and M02-FR-005 pending 006Z9; portal acceptance for
  M04-FR-005..007 pending 006Z10.
