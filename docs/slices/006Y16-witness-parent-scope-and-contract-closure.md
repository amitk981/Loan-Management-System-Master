# Slice 006Y16: Witness Parent Scope and Contract Closure

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master

## Depends On
- 006Y15

## Runtime Capabilities

none

## Goal

Remove the artificial absent-parent credit-manager bypass, make existing and missing application
scope use one documented authority predicate, and record the resulting witness `403`/`404`
contract without reintroducing a parent or child existence oracle.

## Source / Review References

- `docs/source/auth-permissions.md` §§3-3.1 and §§19.1-19.2
- `docs/source/api-contracts.md` §§6-8 and §44
- `docs/source/codebase-design.md` §§26.1-27.1 and §§42.1-42.3
- `docs/slices/006Y15-witness-authority-matrix-behavioral-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_025409_architecture_review`

## Concrete Requirements

1. `resolve_application_access` must not infer all-stage global application scope from the
   `credit_manager` role when the parent row is absent. Use the same source-backed application
   scope vocabulary for an existing parent and an unresolved identifier.
2. Preserve `404 NOT_FOUND` only when the actor has documented application-wide scope independent
   of facts stored on the missing row. Otherwise existing and random denied parent identifiers must
   remain identical `403 OBJECT_ACCESS_DENIED` responses before witness lookup.
3. Exercise a Credit Manager against an existing application both inside and outside the Credit
   Assessment domain plus random parent identifiers; no role/stage combination may reveal existence.
4. Retain the independently selected contact/identity payload matrices and complete unchanged
   witness/history/audit/workflow snapshots for every denied request.
5. Update `docs/working/API_CONTRACTS.md` with the canonical parent-absence/scope ordering and exact
   `403`/`404` envelopes after the policy is fixed.

## Test Cases

- Credit Manager + permission: in-domain existing scope follows §19.2; out-of-domain existing and
  random parents are indistinguishable unless a separate documented global scope applies.
- Ordinary owner/assigned/global/denied actors execute public PATCH behavior without authority mocks.
- Missing child lookup occurs only after parent authority succeeds; all denied paths write zero evidence.

## Evidence Required

Failing cross-stage parent-oracle test, green public contact/identity matrix, API contract diff,
focused dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Witness PATCH cannot reveal an application by combining an absent-id shortcut with stage-limited authority.
- The durable API contract describes the implemented authority-first `403`/`404` behavior exactly.
