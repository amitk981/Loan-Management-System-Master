# Slice 006X10: Credit Object-Scope Executable Row Closure

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006X9

## Runtime Capabilities

none

## Goal

Replace 006X9's static test-name inventory and paired helpers with eight genuinely independent,
executable object-scope cases whose completeness fails when any named case is absent or stale.

## Source / Review References

- `docs/source/codebase-design.md` §26.1-§26.3 and §42.2
- `docs/source/api-contracts.md` §22-§24 and §44
- `docs/slices/006X9-credit-object-scope-isolated-execution-matrix.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_004501_architecture_review`

## Concrete Requirements

1. Represent the eight public action codes as executable parameter cases, not strings naming other
   tests. Collection must fail for a missing, duplicate, or unresolvable case.
2. Each selected test identifier executes only its own persisted arrangement, exact disabled
   six-field projection, matching public write, `OBJECT_ACCESS_DENIED`, and complete before/after
   evidence comparison. Create must not execute update; revalidate must not execute submit-review.
3. The omission proof must remove each real phase from an executable case and fail locally. It may
   not satisfy completeness with synthetic `SimpleNamespace` exceptions or metadata alone.
4. Preserve all production credit behavior, HTTP `403` non-disclosure, state/provenance/
   maker-checker coverage, and PostgreSQL race contracts.

## Test Cases

- Select each of the eight case IDs alone and observe exactly one substantive action row.
- Run all cases in normal, reverse, and independently spawned processes with the same eight results.
- Delete or misname one case and obtain a focused collection/completeness failure.
- Omit projection, write, category, or evidence in turn and obtain a focused row failure.

## Evidence Required

Failing paired-row/static-name proof, green eight individual selections, normal/reverse/process
runs, omission failures, focused HTTP denials, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every advertised credit object-scope row is independently executable and self-proving.
- Static names, sibling execution, test order, sharding, and process state cannot claim closure.
