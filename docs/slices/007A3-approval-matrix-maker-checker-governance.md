# Slice 007A3: Approval Matrix Maker-Checker Governance

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007A2

## Runtime Capabilities

none

## Goal

Replace unilateral activation of Critical approval-matrix configuration with the source-required
Admin plus CFO/Company Secretary maker-checker decision and mandatory change reason.

## Source / Review References

- `docs/source/auth-permissions.md` §§31.1-31.2 (CFG-001, CFG-003-005, CFG-007)
- `docs/source/data-model.md` §§15.1-15.2 and §34
- `docs/source/api-contracts.md` §25.1
- `docs/source/codebase-design.md` §27.1 and versioned-configuration module guidance
- `docs/slices/007A-approval-matrix-configuration.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_044409_architecture_review`

## Concrete Requirements

1. Creating or superseding an approval rule/committee must capture a non-empty reason and persist a
   pending immutable configuration proposal; it must not become resolvable/effective in the maker's
   request.
2. Require one authenticated maker with `approvals.matrix.manage` and a distinct active approver
   carrying persisted CFO or Company Secretary approval authority. The maker cannot approve their
   own proposal, and action permission, role display text, or `Role.is_system_role` is not a
   substitute for approval authority.
3. Expose explicit approve/reject actions using the repository's standard transition envelope,
   stale version/idempotency handling, required rejection reason, and resource-level
   `available_actions`. Record the exact paths and error contracts in `API_CONTRACTS.md`.
4. Approval activates/supersedes the proposed effective-dated row atomically with coherent version
   history and `config.changed` audit evidence naming separate author/approver and the reason.
   Rejection leaves the current effective configuration unchanged.
5. Re-run full-history overlap and committee-authority validation while holding the configuration
   boundary at approval time; a proposal that became stale/conflicting returns a stable conflict and
   writes no partial activation evidence.
6. Existing open approval-case snapshots remain unchanged across proposal, rejection, activation,
   and later reads, satisfying CFG-007.

## Test Cases

- Admin maker + distinct CFO/CS approver activates once; maker self-approval, ordinary manager,
  inactive approver, and wrong authority are denied.
- Missing reason, rejection without reason, stale proposal, double approval/rejection, and a race
  with another activation produce stable errors and complete zero-write loser snapshots.
- Before approval the resolver returns the prior rule/committee; after approval it returns the new
  version only within its effective range; referenced cases retain old snapshots.
- VersionHistory author and approver are distinct and audit facts include reason/request metadata
  without sensitive values.

## Evidence Required

Failing unilateral-activation/self-approval tests, green public transition matrix, exact API
examples, configuration/case snapshot proof, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Critical approval configuration cannot be activated by one actor.
- Every activation has a reason, distinct authorised business approver, immutable history, and audit.
