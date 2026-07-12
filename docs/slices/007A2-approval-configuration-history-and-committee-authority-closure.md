# Slice 007A2: Approval Configuration History and Committee Authority Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007A

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make effective-dated approval rules and sanction committees unambiguous across their full retained
history, and reject committee membership that does not carry the persisted CFO/director authority
required by the source.

## Source / Review References

- `docs/working/digests/epic-007-sanction-approval-workflow.md`
- `docs/source/data-model.md` §§15.1-15.2, §30, and §34
- `docs/source/api-contracts.md` §25.1
- `docs/source/auth-permissions.md` §12.6, §§15.8-15.9, §16.2, and §30
- `docs/source/functional-spec.md` M05-FR-003 through M05-FR-006
- `docs/slices/007A-approval-matrix-configuration.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_044409_architecture_review`

## Concrete Requirements

1. Enforce non-overlapping effective-date plus inclusive-amount intervals across every resolvable
   rule row, including superseded historical rows. A later POST/PATCH must not backfill an interval
   that makes a previously unique historical decision date ambiguous.
2. Define and enforce the rule lifecycle explicitly: active/current and superseded/historical rows
   resolve only inside their stored effective interval; inactive/invalid lifecycle values never
   resolve. Add database constraints/indexes where they can prevent invalid dates, statuses, or
   duplicate version identities without replacing transactional overlap checks.
3. Apply equivalent full-history non-overlap and lifecycle rules to sanction committees. Expose one
   approval-owned `resolve_sanction_committee(decision_date)` projection returning committee
   id/version and the CFO/two Director user ids, with stable absent/ambiguous errors for 007B.
4. On committee create/supersede, require three distinct active users whose persisted
   `approval_authority_type` values are exactly CFO, Director, Director. Role display names or field
   position alone are not authority. Denials leave committee, rule, version, and audit evidence
   unchanged.
5. Keep version/audit evidence coherent when superseding: retained history must show the closed old
   interval and new interval without rewriting an approval case's stored rule/committee projection.
6. Cover authenticated 403 manage denials and malformed/unknown/non-finite payload zero-write
   matrices separately for both rule and committee resources; retain standard envelopes.
7. Make both collection APIs use the standard paginated list envelope with bounded `page`/
   `page_size`, deterministic ordering, and unknown-parameter rejection; no endpoint may materialize
   an unbounded configuration table.

## Test Cases

- Supersede a rule, then attempt a historical-range POST overlapping the superseded row: conflict,
  zero writes, and the original date still resolves exactly one original rule.
- Adjacent inclusive amount/date boundaries remain legal; equal endpoints overlap and are rejected.
- Historical/current committee resolution returns the correct version; backfill overlap is rejected.
- Ordinary users in CFO/director-shaped fields, inactive authority users, duplicate members, and
  swapped authority types are rejected with complete zero evidence.
- PostgreSQL concurrent historical backfill/create and supersede races each have one winner and a
  zero-write loser across rule/committee/version/audit state.
- Run `ApprovalMatrixConcurrencyTests` directly under
  `sfpcl_credit.config.postgres_test_settings` twice and retain both command/test-name logs; the
  fixed Ralph five-race harness did not discover 007A's new test class.

## Evidence Required

Failing historical-ambiguity and authority-type tests, green resolver/API matrices, migration
constraint proof, PostgreSQL five-race output, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every decision date resolves at most one immutable rule and one correctly authorised committee.
- Historical configuration cannot be made ambiguous by a later mutation.

