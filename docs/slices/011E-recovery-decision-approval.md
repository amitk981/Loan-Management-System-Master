# Slice 011E: Recovery Decision Approval

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Bind a submitted Non-Payment Note to the configured approval matrix and record one terminal recovery
decision whose permitted action exactly matches approved authority evidence.

## User Value
No security can be invoked from an unapproved or ambiguous recovery recommendation.

## Depends On
- 011D

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.RecoveryDecisionPostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/api-contracts.md` §35.8
- `docs/source/data-model.md` §§15.2-15.4, 21.5
- `docs/source/product-requirements.md` §11.27
- `docs/source/screen-spec.md` S56
- `docs/source/auth-permissions.md` §§16-18, 20.3, 25.8, 40.3
- `docs/source/security-privacy.md` §23.2
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011E

## Scope
- Extend the existing approval owner with recovery approval type/routing as configured; do not build
  a second voting or matrix engine in the recovery app.
- Add one `RecoveryDecision` per case and POST
  `/api/v1/default-cases/{id}/recovery-decision/` accepting approval case, decision, and mandatory reason.
- Require the approval case to belong to the same submitted/frozen Non-Payment Note/default, be
  terminal-approved by its required distinct authority, and approve the exact selected action.
- Support source actions (SH-4/share action, CDSL, cheque, continue/no action, configured other) only
  when the approval evidence/configuration permits them; expose no executable action for rejection.
- Freeze decision, reason, approval evidence, authority, and time; replay returns retained truth.

## Permissions and Audit
- `recovery.decision.create` is Critical and limited to the configured Sanction Committee/Board
  decision path. Maker-checker/conflict exclusions from the approval owner remain binding.
- Approval and recovery audit chains cross-reference each other without copying mutable role truth.

## Acceptance and Negative Tests
- Approved matching case creates one decision and exposes only the approved next action.
- Reject missing/pending/rejected/returned/foreign/stale approval; mismatched action; self/conflicted or
  insufficient authority; missing reason; changed replay; second decision; and client-forged status.
- Concurrent decision requests yield one retained record/event chain.
- Reverse consumers: all existing sanction/approval matrix, quorum, conflict, and object-scope tests
  remain green; 011D note remains immutable; 011F cannot execute a rejected/no-action decision.

## Non-Goals
Executing recovery (011F), defining open policy for sale/write-off/settlement, changing generic
approval semantics, or staff frontend beyond API evidence.

## Evidence
RED/GREEN approval-composition/API/permission tests; migration/race proof; authority/conflict and
frozen-link probes; audit trace; full backend gate and response examples.

## Risk Level
High

## Acceptance Criteria
- `REC-AC-001/003`, `MOD-REC-003/004/010`, and the approval gate in `API-REC-003` pass.
- No decision exists without one matching, source-authorised, terminal approval chain.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Recovery decision and approval-owner composition completed
- [ ] Authority, conflict, mismatch, race, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
