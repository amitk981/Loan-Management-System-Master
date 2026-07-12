# Slice 006Z7: Active-Member Relaxation, Authority, and Evidence-Race Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006Z6

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Goal

Make the source-defined recent-member relaxation reachable, make member authority one behavioral
policy, and prove active verification atomic against supply/service evidence mutations.

## Source / Review References

- `docs/source/functional-spec.md` BR-003 through BR-007 and M02-FR-004 through M02-FR-006
- `docs/source/data-model.md` §10.2-§11.6 and §34
- `docs/source/codebase-design.md` §22.1, §26.1-§27.1, and §42.2
- `docs/source/auth-permissions.md` §12.2, §25.1, and §34.2
- `docs/slices/006Z6-active-member-evidence-atomicity-and-history-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_004501_architecture_review`

## Concrete Requirements

1. Evaluate BR-003/BR-005 source-backed recent-member relaxation before rejecting a non-active
   membership status. One complete qualifying supply year plus distinct verified relaxation evidence
   can produce the documented relaxation route; reason text alone cannot.
2. Replace caller-controlled `globally_authorized` and embedded role-code switches with one
   member-owned authority policy. Registry and active-status public methods must return identical
   owner/global/permission/object results for equivalent inputs without evaluator mocks.
3. Lock the Member and exact evidence boundary in one consistent order for supply create/verify,
   service evidence mutation, and active verification. No path may bypass the boundary by writing an
   evidence row without advancing/invalidating current provenance.
4. Add real PostgreSQL verifier-vs-supply-create, supply-verify/update, service-create/update races.
   Each yields one coherent current result/record/pointer; the loser writes no status/history/audit
   evidence. Retain the two-verifier race and the five credit races twice.
5. Complete module/API rows for inactive and relaxation success, missing/future date, unknown/
   malformed payload, permission/object/maker-checker, stale member/result/evidence, repeat,
   unsupported decision, chronology, and zero failure evidence.
6. Remove the unreachable `_qualifying_service_evidence` implementation and any now-redundant
   authority compatibility code.

## Test Cases

- A recent non-active member with one qualifying year and persisted relaxation evidence qualifies;
  missing either fact does not.
- Registry and active-status authority matrices exercise production policy without patching it.
- Four evidence-vs-verifier PostgreSQL races prove coherent winner and current-pointer cardinality.
- Every losing module/API row preserves the complete member/status/history/audit snapshot.

## Evidence Required

Failing relaxation, authority-divergence, and evidence-race logs; green module/API matrices; two
authoritative PostgreSQL runs; dependency/dead-code scan; and all configured gates.

## Risk Level
High

## Acceptance Criteria

- BR-003..007 and M02-FR-004..006 resolve from one reviewable, source-backed, atomic authority.
- Concurrent evidence changes cannot make a stale snapshot current or leave partial evidence.

