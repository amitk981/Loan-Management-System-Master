# Slice 007A4: Approval Governance Concurrency and Case Snapshot Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007A3

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Restore authoritative concurrency proof through the governed proposal-approval seam, align the
public error/permission contract, and prove that configuration decisions cannot alter an existing
approval-case snapshot.

## Source / Review References

- `docs/working/digests/epic-007-sanction-approval-workflow.md`
- `docs/source/auth-permissions.md` §§18.2, 31.1-31.2, and §34
- `docs/source/api-contracts.md` §§3, 6-8, 25.1, and error code §7.1
- `docs/source/data-model.md` §§15.1-15.3 and §34
- `docs/source/codebase-design.md` §§22.3, 26.1-26.3, and §27.1
- `docs/slices/007A2-approval-configuration-history-and-committee-authority-closure.md`
- `docs/slices/007A3-approval-matrix-maker-checker-governance.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_055322_architecture_review`

## Concrete Requirements

1. Replace the stale PostgreSQL helpers that call rule/committee create/supersede as if those calls
   activate immediately. Create two valid pending proposals first, then race distinct authorised
   checkers through `decide_proposal` (or the public approve endpoint) while holding the real
   configuration boundary. Cover overlapping rule create, rule supersede, committee create, and
   committee supersede; exactly one effective activation wins and the loser proposal and all
   effective/history/audit/case state remain at their pre-decision values.
2. Run the governed `ApprovalMatrixConcurrencyTests` directly under
   `sfpcl_credit.config.postgres_test_settings` twice and retain exact test names and output. The
   migration creating `ApprovalConfigurationProposal` must be present in both runs; pre-007A3 logs
   are not acceptance evidence.
3. Add a real open `ApprovalCase` fixture carrying immutable rule/committee/approver snapshots.
   Propose, reject, activate, race a conflicting activation, and read again; every case field and
   version remains byte-for-byte unchanged, satisfying CFG-007. Include proposals and cases in all
   complete loser snapshots rather than asserting only rules/committees/version/audit counts.
4. Finish the 007A2/007A3 public matrix for both resource kinds: inactive/duplicate/swapped
   committee authority, historical/current committee resolution and backfill conflict, inactive
   rule/committee non-resolution, malformed/unknown/non-finite zero-write inputs, proposal stale/
   replay/reject parity, and approval-time authority revalidation.
5. Emit the source-standard `403 APPROVAL_AUTHORITY_REQUIRED` code. Remove the noncanonical
   `APPROVER_AUTHORITY_REQUIRED` variant from production, tests, and `API_CONTRACTS.md`.
6. Protect proposal detail with the existing approval-matrix read boundary or the narrower
   source-backed participant/eligible-checker scope; an arbitrary authenticated user must not read
   Critical configuration reasons, actor ids, or action eligibility. Document and test the exact
   401/403/200 contract without adding role-name inference.
7. Keep activation atomic and approval-owned. Do not move range/authority logic into views or tests,
   and do not query current-only rows when validating retained history.

## Test Cases

- Two overlapping create proposals approved concurrently: one active row and one approved proposal;
  the loser remains pending with unchanged version/decision fields and no loser history/audit/case
  writes. Repeat for rule supersede and committee create/supersede.
- A case snapshotted to version 1 is identical after proposal, rejection, version-2 approval,
  conflicting loser, resolver calls, and proposal-detail reads.
- Ordinary/inactive/wrong-authority/self checkers receive the canonical 403 codes; stale/replayed
  proposals receive their stable 409 codes with complete state equality.
- Rule and committee malformed/lifecycle/history rows are independently selected through public
  APIs and resolvers, not compressed into coverage-only loops.
- Unauthenticated and unrelated authenticated proposal-detail requests are denied; maker,
  authorised checker, and configured reader behavior matches the documented contract.

## Evidence Required

Failing stale PostgreSQL tests and canonical-error/case-snapshot rows, green sequential and public
matrices, two post-007A3 PostgreSQL runs, migration list showing proposal migration, dependency
scan, focused coverage, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Governed activation has current, authoritative PostgreSQL one-winner proof.
- Critical configuration decisions preserve open cases and use one canonical permission contract.

