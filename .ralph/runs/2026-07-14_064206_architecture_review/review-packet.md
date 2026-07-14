# Review Packet: 2026-07-14_064206_architecture_review

## Result
Success

## Slice
architecture-review

## Review Range

`git diff 4b5b4b1...15b8d02`, covering 007O, 007P, 007Q, and 008A.

## Standards

The independent Standards pass found the new S23/S25 four-column grouped table violates the fixed
no-new-layout/table rule, template file references bypass the documents-owned provenance decision,
query/transport concerns drift into modules, and several tests use implementation or impossible
states. API §3 also expects sensitive-change reasons while §26.3 supplies no rationale field; A-098
records that source gap instead of inventing a contract. 007S and 008A2 own the implementable
corrections.

## Spec

The independent Spec pass found two Critical legacy regressions: the expanded frozen package reused
the `approval-review-v2` label and invalidates earlier cases, while older register rows with empty
source JSON can raise instead of returning nulls. It also found mutable approver names, stale/
under-filled pagination acceptance, a first-version approved-template overlap race, unsafe file
reference authority, and unresolved FPC/FPO vocabulary. 007R, 007S, and 008A2 are concrete,
dependency-valid corrective slices; 008B now depends on 008A2.

## Traceability

- 007O says historical cycles stay immutable and missing terminal facts fail closed; current code
  instead invalidates the whole earlier v2 read boundary. 007R tests exact legacy JSON through public
  reads/actions and remediates only through return/correct/review/new cycle.
- 007Q/digest say unavailable legacy fields are null; current register serialization directly
  indexes empty JSON. 007R adds migrated-row null-safe tests with no live reconstruction.
- 007P says collection replacement is atomic and malformed pagination fails; current client accepts
  an under-filled last page and S21 lacks stale-response protection. 007S adds exact remainder and
  out-of-order promise matrices.
- 008A says approved effective ranges cannot overlap and files use the existing permissioned
  document boundary; current first-row race has nothing to lock and reference checks use only row
  existence plus download permission. 008A2 adds identity locking and provenance-aware resolution.

## Validation

Frontend build/typecheck/lint and 269 tests pass. Django check/migration sync and 700 tests pass with
20 expected skips at 93% coverage. Queue lint, state JSON, and diff checks pass. The reviewed 007Q
screenshots are visibly complete and uncorrupted.

## Recommended Next Action
Run 007R, then 007S, then 008A2. Only then run sharpened 008B.
