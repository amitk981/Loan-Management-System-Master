# Architecture Review Evidence

## Pinned Window

- Fixed point: `23331d5` (previous successful architecture review)
- Reviewed head: `955cfc1`
- Commits: `6afd173` (006Z11), `46b47c0` (006Z12), `7359389` (007A2), and
  `955cfc1` (007A3)
- Diff command: `git diff 23331d5...955cfc1`

## Independent Axes

Standards review checked documented permission/object-scope boundaries, database integrity,
deep-module locality, API vocabulary, test assertions, and concurrency evidence. Spec review checked
each completed slice requirement and its cited source sections. Both identified the same High issue:
007A3 changed activation to a proposal decision but left `ApprovalMatrixConcurrencyTests` calling
the pre-governance immediate-activation interface.

## Discriminating Evidence

- Retained 007A2 PostgreSQL logs run four races successfully twice, but their migration list ends at
  approvals migration 0004 and therefore predates 007A3 proposal migration 0005.
- The current focused SQLite command applied migration 0005 and discovered the same four tests, but
  skipped all four as PostgreSQL-only. Static inspection shows both create contenders now return
  pending proposals, while tests still expect one create conflict and effective entity ids.
- Source API error vocabulary defines `APPROVAL_AUTHORITY_REQUIRED`; shipped 007A3 code/tests/docs
  use `APPROVER_AUTHORITY_REQUIRED`.
- 007A3's snapshot helper covers rules, committees, VersionHistory, and AuditLog, but no
  `ApprovalConfigurationProposal` or `ApprovalCase`; no test instantiates an open case.
- `MemberScopeAssignment.clean()` enforces scope shapes, while migration 0013 adds no equivalent
  database checks and nullable uniqueness does not deduplicate global/created-by rows.
- 006Z12's five independent denial tests assert the exact redacted envelope and compare member,
  authority, supply/service, share/land/profile, assessment, application, policy, audit, and workflow
  state before/after. This prior finding is closed.

## Disposition

- `006Z13` owns member-scope database constraints and the complete real public action/calculation
  authority matrix.
- `007A4` owns post-proposal PostgreSQL races, open-case/complete loser snapshots, the canonical
  authority code, proposal-detail access, and remaining committee/lifecycle matrices.
- `007B` now depends on 007A4.
- No ADR: existing source documents already decide these boundaries.
- `CONTEXT.md` remains accurate; no Blocked slice exists in state or slice files.

## Functional Requirements

- M04-FR-005..007: passing; 006Z12 closes the denial evidence matrix.
- BR-003..007 and M02-FR-004..006: substantive behavior, with complete authority proof queued in
  006Z13.
- M05-FR-003..006: sequential configuration behavior passes; remains partial until current governed
  concurrency passes in 007A4 and actual approval-case routing lands in 007B.

