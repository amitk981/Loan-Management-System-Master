# Architecture Review Evidence

Run: `2026-07-13_222951_architecture_review`

## Review Window

- Fixed point: `c843ea8f6de1aae50a7f665c35daf7f4b755f887`
- Merge base: `c843ea8f6de1aae50a7f665c35daf7f4b755f887`
- Head reviewed: `5ea122bbc49ac16d5aeaeb41cc528650ab3841f7`
- Commits: 007F2 (`14bb8d9`), CR-004 (`241ff25`), 007G2 (`9f98060`), 007H2
  (`5ea122b`).
- Production/test diff: 16 files, 1,721 insertions, 118 deletions. Ralph run artifacts and docs
  were inspected separately and are excluded from this code statistic.

## Independent Axes

The Standards pass checked documented module, permission, API, transaction, and test-interface
rules. The Spec pass checked every concrete requirement and acceptance item in the four slice/CR
files against code and retained evidence. Their findings are preserved in
`docs/working/REVIEW_FINDINGS.md` under separate Standards and Spec headings.

## Executable Defect Reproduction

Two diagnostic tests were injected in memory through Django's public `TestCase`/HTTP seam; no test
or production file was written.

1. Pending case probe:
   - `GET /api/v1/approval-cases/{case_id}/` returned 200.
   - Only the live appraisal snapshot's `policy_name` was changed and saved.
   - The case's persisted `routing_snapshot_is_coherent` remained true.
   - The expected unchanged second GET failed: actual `404 NOT_FOUND` instead of 200.
2. Terminal parity probe:
   - CFO + Director completed the case through public action endpoints.
   - Only the same live appraisal policy name was changed.
   - Actual result tuple was `(detail=404, sanction decision=200, register=200,
     register total_count=1)`; expected parity was `(200, 200, 200, 1)`.

Both probes failed for the reviewed defect exactly as expected and destroyed their isolated test
databases. They are diagnostic RED evidence, not configured gate failures. Corrective slice 007H3
owns the retained RED/GREEN implementation evidence.

## Traceability

- 007F2 requirement 4 says direct appraisal saves cannot change approval read authority and
  historical cycles use frozen facts. The diagnostic probes disprove that claim at the public seam.
- 007H2 requirement 5 says decision/register reads use the coherent case interface rather than the
  stored Boolean as authority. The terminal tuple proves detail and the two downstream readers
  currently disagree.
- Codebase-design §13.1 requires material change to create a new immutable cycle; §§26/42 require
  observable interface tests. 007H3 requires pending, returned/new-cycle, terminal, and malformed
  frozen-snapshot public matrices.
- M05-FR-003/006 exception routing, M05-FR-009 register generation/scoped reads, and M05-FR-012
  meeting evidence remain functionally substantive. The corrective issue is historical ownership
  and cross-endpoint authority consistency.

## Queue and Context

- New corrective slice: `007H3-frozen-case-provenance-and-read-scope-parity-closure` (`Not Started`,
  depends on 007H2).
- 007I now depends on 007H3 and contains frozen old/new-cycle UI acceptance.
- 007J was sharpened to keep borrower MP12 off the internal §25.8 permission boundary; A-089 owns
  the source-silent portal outcome decision.
- No slice is Blocked, so no stale block was reopened.
- `docs/working/CONTEXT.md` remains truthful and required no edit.
- No ADR was needed because existing source/slice rules already decide frozen cycle ownership.

## External Evidence Limitation

CR-004's local repair evidence is substantive, but its explicit hosted staging/PR-green criterion
is not retained in the repository. The sandbox has no network. Owner/orchestrator confirmation is
required before promotion; no product rule or code behavior was invented to substitute for it.
