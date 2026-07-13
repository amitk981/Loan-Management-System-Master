# Slice 007A5: Approval Governance Complete Loser Ledger

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007A4

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Turn 007A4's one-winner PostgreSQL races into complete zero-write loser and open-case immutability
proof, and finish the independently selected committee-history matrix before case enrichment.

## Source / Review References

- `docs/source/auth-permissions.md` §§31.1-31.2, CFG-004..007, and §34.5
- `docs/source/api-contracts.md` §§3, 6-8, and 25.1
- `docs/source/data-model.md` §§15.1-15.3 and §34
- `docs/source/codebase-design.md` §§22.3 and 26.1-26.3
- `docs/slices/007A4-approval-governance-concurrency-and-case-snapshot-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_083408_architecture_review`

## Concrete Requirements

1. For governed rule create/supersede and committee create/supersede races, snapshot complete
   proposals, effective resources, retained history, version history, business audit, and approval-
   case state before the decisions. After the winner commits, prove the loser changed none of those
   facts beyond the winner's exact expected writes; row counts alone are insufficient.
2. Read the losing proposal through the public proposal-detail boundary after each race and prove
   its reason, maker, payload/target, status, version, null decision fields, and action projection
   remain consistent with an unchanged pending loser.
3. Put a real open case with the full stored rule/committee/required-approver/decision-date/version/
   workflow snapshot into the same PostgreSQL race fixture. Cover rejection, a winning activation,
   a conflicting losing activation, resolver reads, and proposal-detail reads; the case must remain
   byte-for-byte identical throughout, satisfying CFG-007.
4. Run the four governed races directly twice on PostgreSQL after migrations 0005 and 0006, with
   exact test names retained. Include discriminating case facts so omitting cases from the ledger
   makes the test fail.
5. Add independent public/resolver rows for historical and current committee resolution plus a
   conflicting committee backfill. Keep inactive/duplicate/swapped authority and malformed/unknown
   rule/committee rows independently attributable; do not compress acceptance into an opaque tuple
   loop.
6. Keep activation logic behind `decide_proposal` and the configuration lock. Do not duplicate
   range, lifecycle, or authority rules in tests or views.

## Test Cases

- Four competing approval races: one winner, one byte-for-byte pending loser, exact winner-only
  resource/history/audit writes, and an unchanged open case.
- Rejection then conflicting activation race preserves the same open case across public reads.
- Historical/current committee dates resolve uniquely; a backfill conflict returns the stable
  configuration error with the complete ledger unchanged.

## Evidence Required

Failing complete-ledger and conflicting-case-race rows, green independent lifecycle matrix, two
PostgreSQL runs after both proposal and case-snapshot migrations, focused coverage, and all gates.

## Risk Level
High

## Acceptance Criteria

- Governed races prove complete winner-only writes, not only cardinality.
- CFG-007 is exercised inside a real conflicting PostgreSQL activation race.

## Run-Ahead Sharpening Review (006Z14, 2026-07-13)

- Keep every committee-history and race row independently addressable by its Django test method;
  completeness metadata must resolve and execute those methods, not compare advertised strings.
- Assert public proposal-detail and resolver outputs plus persisted ledgers. Do not add a
  filename/source-text whitelist as a substitute for the observable loser and open-case behavior.
