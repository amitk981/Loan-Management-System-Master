# Slice 007A6: Approval Governance Winner-Evidence Content Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007A5

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Finish 007A5's complete-ledger claim by proving the sole new version-history and business-audit rows
contain the exact winning proposal, maker/checker, reason, target, and before/after configuration
facts in every governed PostgreSQL race.

## Source / Review References

- `docs/source/auth-permissions.md` §§31.1-31.2, CFG-004..007, and §§30.1-30.3
- `docs/source/data-model.md` §§15.1-15.3, §§26.1-26.3, and §34
- `docs/source/codebase-design.md` §§22.3 and 26.1-26.3
- `docs/slices/007A5-approval-governance-complete-loser-ledger.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_100911_architecture_review`

## Concrete Requirements

1. In governed rule create/supersede and committee create/supersede races, snapshot the complete
   version-history and `config.changed` audit ledgers before approval. Continue proving every old
   row is byte-for-byte unchanged and exactly one winner row is added.
2. Assert the new `VersionHistory` row's entity type/id/version, author, distinct approver,
   approval timestamp/reference, source reason, and old/new payload identify the approved proposal
   and activated/superseded resource exactly. A cardinality assertion is insufficient.
3. Assert the new business audit row's actor, action, entity id/type, request/proposal provenance,
   and masked old/new values identify only the winning activation. It must not contain a losing
   proposal's reason/payload or claim writes that did not occur.
4. For supersession, prove the evidence names both the retained predecessor and exact new resource,
   including the predecessor's closed effective date. For creation, prove no fabricated predecessor
   appears.
5. Keep the unchanged pending loser, public loser detail, effective resources, open case, proposal,
   resolver, and winner-only row assertions from 007A5. Do not duplicate activation logic in tests
   to calculate the expected winner.
6. Run the same four exact governed race methods twice on PostgreSQL after migrations 0005-0007;
   preserve independently attributable rule/committee create/supersede failures.

## Test Cases

- Four PostgreSQL races with exact winner version/audit content and a byte-for-byte pending loser.
- Mutation/omission checks that fail when the new evidence row has the wrong actor, target, reason,
  old/new values, or proposal identity even if counts still pass.
- Register the rule-create, rule-supersede, committee-create, and committee-supersede methods as
  four independently resolvable test callables; the twice-run acceptance command must report four
  executed tests and zero skips on each invocation rather than selecting an aggregate wrapper.

## Evidence Required

Failing evidence-content assertions, two green four-race PostgreSQL runs, focused approval tests,
and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Complete-ledger acceptance proves what the winner wrote, not merely that one row was added.
- No losing proposal fact appears in winner history or audit evidence.
