# Slice 010N4: Global Search Sensitive Authority Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010N3

## Runtime Capabilities

none

## Goal
Route every sensitive and cross-domain global-search input through its canonical read authority so
denied match existence, counts, and actions cannot leak across module boundaries.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-SEARCH-001 | ROOT-010-GLOBAL-SEARCH-SENSITIVE-AUTHORITY | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/global-search-sensitive-authority.log | AC-E10-S1, AC-E10-S2, AC-E10-S3, AC-E10-S4 |

## Source References
- `docs/slices/010N-global-search-api-and-ui.md`
- `docs/source/screen-spec.md` S02 and §§4.4, 5.1
- `docs/source/api-contracts.md` §§8.1, 8.4
- `docs/source/auth-permissions.md` §§12.8, 21, 22.1
- `docs/source/codebase-design.md` module-owner and coordinator sections

## Concrete Requirements
1. Replace direct cross-domain model queries in the aggregate with public search facades for member,
   application, account, document, repayment, audit, SAP, bank, and security-instrument owners.
   Each input facade must enforce its exact permission, role/object scope, sensitive matching policy,
   and nondisclosing denial before returning stable ids/cards.
2. Blank-cheque, SH-4, CDSL, bank-suffix, PAN/Aadhaar, and SAP inputs must disclose neither owner nor
   match existence to an actor who lacks that input owner's authority, even when ordinary member read
   is global. Denied groups/actions remain absent with no count side channel.
3. Apply object scope before cap, count, ordering, and pagination. Independently authorised
   application/account groups must search their own permitted borrower/reference inputs without
   borrowing member-group authority, and 100 newer denied candidates cannot hide an older authorised
   result.
4. Keep sensitive values out of responses, logs, audit payloads, URLs, persisted client storage, and
   post-request React state. Clear transient submitted values after completion while preserving
   explicit safe pagination behavior through a server-owned opaque continuation or another bounded
   design that does not retain raw sensitive text.
5. Add a real permission/object matrix for every S02 input and six delivered groups, including CFO
   blank-cheque denial, security-authorised positive matches, independent group permissions,
   action suppression, 1/20/21/100/101 boundaries, wildcard/injection errors, and representative
   indexed plans. Do not mock the restricted domain query as positive acceptance.

## Acceptance Criteria
- [AC-E10-S1] Every sensitive input is resolved only by its canonical domain facade and unauthorized
  actors receive no item, group count, action, or match-existence signal.
- [AC-E10-S2] Scope precedes cap/count/page for every group, and independently authorised groups find
  their permitted records without depending on member-read authority.
- [AC-E10-S3] Raw sensitive queries are absent from every returned, logged, audited, URL, persisted,
  and post-request client surface while safe multi-page search remains functional.
- [AC-E10-S4] The full input/group/action and pagination matrix passes, the current failing probe is
  a permanent GREEN regression, representative plans use maintained indexes, and all gates pass.

## Risk Level
High

