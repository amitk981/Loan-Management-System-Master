# Review Packet: 2026-07-20_221716_repair

## Result
Ready for independent validation

## Slice
CR-014-rate-current-date-terminal-finalizer

## Repair Outcome

The production candidate was preserved. The only demonstrated failure was an invalid PostgreSQL
acceptance fixture expectation: `clone_servicing_account` provides a distinct financial owner for
bounded rate races, but it intentionally does not clone the application-owned current SAP and
disbursement evidence required to become a second Loan Account 360 collection identity. The test
also discarded the clone and later referenced undefined `other`.

The repaired test now proves the intended contract at both seams: both distinct accounts are
returned by competing bounded owner runs and retain exactly two decisions, while the one canonical
read-valid stale account remains visible and converges. The clone's stored scalar is checked through
the financial owner seam without falsely widening collection identity.

## Traceability

- The slice requires PostgreSQL races with a stale starting projection and an account that remains
  visible (AC-RATE-F-4). The repaired race uses the public owner callable, asserts both financial
  account IDs, and then verifies the owner-valid stale account in Loan Account 360 count and rows.
- The slice requires canonical collection count/rows and current projection agreement
  (AC-RATE-F-2). The collection correctly counts one canonical identity, and its row plus both
  underlying financial scalars show `9.7500`.
- The source keeps rate publication effective-dated and current projection owner-controlled
  (`functional-spec.md` M10-FR-001–002, BR-064–065; `data-model.md` §§18.1, 18.5, 34–35). No
  production calculation, mutation, or retained evidence behavior changed in repair.

## Verification

- RED: exact PostgreSQL failing selector reproduced `total_count` 1 versus invalid expectation 2.
- GREEN: the same selector passed after the fixture/assertion correction.
- Trusted PostgreSQL contract: exact declared class, 5 tests, passed twice on PostgreSQL 14.20.
- Focused current-date and reverse-consumer checks: 12 tests passed.
- Django system check and migration sync: passed.
- Runtime-capability and trusted PostgreSQL declaration validators: passed.
- Machine-readable review closure: 1 finding and 5 acceptance IDs passed.
- No `[DEBUG-...]` instrumentation remains.

## Independent Validation Boundary

The orchestrator must still run the authoritative full backend suite under coverage and all
candidate integrity gates. No commit, merge, or push was attempted by the agent.

## Recommended Next Action
Run full independent validation and commit only if every configured gate passes.
