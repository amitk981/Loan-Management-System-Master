# Slice 010N7: Global Search Canonical Input Owner Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010N6

## Runtime Capabilities

none

## Goal
Make sensitive global-search inputs consume the same canonical permission, role, object-scope, and
identifier decisions as their owning domains before any related member or group can be disclosed.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-SEARCH-001 | ROOT-010-GLOBAL-SEARCH-SENSITIVE-AUTHORITY | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/global-search-owner-scope.log | AC-E10-S5, AC-E10-S6, AC-E10-S7 |

## Source References
- `docs/slices/010N4-global-search-sensitive-authority-closure.md` requirements 1–5
- `docs/source/screen-spec.md` S02
- `docs/source/api-contracts.md` §§8.1 and 8.4
- `docs/source/auth-permissions.md` §§12.8, 21, and 22.1
- `docs/source/codebase-design.md` §§26 and 42
- `docs/working/API_CONTRACTS.md` “Global search aggregate (010N)”

## Concrete Requirements
1. Replace raw security-instrument table matching with one domain-owned search decision that applies
   the canonical package/instrument permission, effective role, Stage-4 evidence, and object scope
   before returning an opaque member id. Package-read and manage permissions alone are not global
   object scope.
2. Route every supported SAP customer code, cheque number, CDSL pledge sequence, and SH-4 reference
   by canonical field validation rather than invented `SAP-`/`CDSL-` prefixes. A sensitive-looking
   value must not fall through to unrelated generic matches when its owner denies it.
3. Apply the same owner contract to bank suffix and identity inputs: exact hashed/last-four lookup,
   source-specific authority, member/object scope, and nondisclosing denial precede group scope,
   cap, count, pagination, and actions.
4. Remove the coordinator's cross-domain compatibility model alias. Permanent public API matrices
   must use real in-scope and out-of-scope owner records, arbitrary valid identifier formats, denied
   collisions, and all six delivered groups rather than testing `paginate_group` in isolation.

## Acceptance Criteria
- [AC-E10-S5] A real cheque/CDSL/SH-4 record outside canonical Stage-4/object scope contributes no
  owner, group, count, action, or match-existence signal despite an otherwise matching permission.
- [AC-E10-S6] Valid prefixed and unprefixed owner identifiers reach the correct facade, while denied
  sensitive collisions cannot fall through to generic member/application/account results.
- [AC-E10-S7] Bank/identity/SAP/security permission-object matrices and real 1/20/21/100/101 group
  paths pass with the current review reproducer green and raw sensitive values absent from outputs.

## Risk Level
High
