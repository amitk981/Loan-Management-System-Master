# Review Packet: 2026-07-13_100911_architecture_review

## Result
Complete; findings recorded and all configured gates pass.

## Slice
architecture-review

## Review Window

`1752bcb...b37a349`: 006Z14, 007A5, 007B, and 007C.

## Standards

- High: `approvals.case.read` is treated as global object scope; an arbitrary unassigned reader can
  list/retrieve routed cases despite the source's explicit unassigned-Director denial. Corrective:
  `007C2-approval-case-read-scope-and-snapshot-contract-closure`.
- High: 006Z14's ten named public-action tests call only `evaluate_member_authority`, so they do not
  prove any public response or write. Corrective:
  `006Z15-member-public-action-authority-matrix-closure`.
- Medium: sanction handoff and approval-case engine expose divergent canonical serializers; §25.2
  success omits `current_status`. Corrective: 007C2.
- Low judgment: selected checklist facts are owner read-throughs rather than case snapshots. 007C2
  must prove no public post-routing mutation; final decision snapshotting remains 007D.

## Spec

- High: 006Z14 still lacks its required all-permissions/no-scope public action matrix, matching-
  scope successes, and action-linked scope/caller proof. Corrective: 006Z15.
- High: 007B exact replay ignores changed credit provenance and its configuration immutability test
  manually fills a shell rather than executing real enrichment. Corrective: 007C2.
- High: 007C's routed predicate accepts contradictory matrix/committee/required-approver JSON that
  can inject an actionable user. Corrective: 007C2.
- Medium: 007A5 proves one new version/audit row but not its exact winner content. Corrective:
  `007A6-approval-governance-winner-evidence-content-closure`.

Summary: Standards 2 High, 1 Medium, 1 Low/judgment; worst are global case reads and evaluator-only
action proof. Spec 3 High, 1 Medium; worst are the missing member public matrix and approval-case
routing/replay authority gaps.

## Traceability

- Auth §§15.9/24.1/32.1/37.3 requires assignment/object scope beyond action permission; 007C2 owns
  the missing case boundary.
- Codebase-design §§26.1-26.3/42.1 requires tests through caller interfaces; 006Z15 owns the real
  action matrix.
- Auth CFG-004..007 and data-model §§26/34 require attributable immutable configuration evidence;
  007A6 owns winner content.
- API §§3/25.2-25.4 and data-model §15.3 require coherent snapshots and response contracts; 007C2
  owns route/replay/status parity.
- M02-FR-004..006 and M05-FR-001..006 remain substantive but partially proven as recorded in
  `REVIEW_FINDINGS.md` and the Epic 006/007 digests.

## Validation

Frontend build/typecheck/lint and 208 tests pass. Backend check/migration sync and 566 tests pass
with 16 expected PostgreSQL-only skips and 93% coverage. Queue lint, state JSON, diff whitespace,
blocked-slice, protected-path, and diff-limit checks pass. See `evidence/terminal-logs/`.

## Recommended Next Action
Run 006Z15, then 007A6, then 007C2 before 007D.
