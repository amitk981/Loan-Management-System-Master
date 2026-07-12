# Slice 006Y7: Member Registry Race and Action-Scope Closure

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Close the unexecuted 006Y5 concurrency contract and ensure identity-approval actions apply the same
member object scope as the approval write.

## Depends On
- 006Y5

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Source / Review References
- `docs/source/codebase-design.md` §10.1, §26.1-§26.3, and §42.2
- `docs/source/api-contracts.md` §6-§8, §13.2, and §44
- `docs/source/auth-permissions.md` §34.2
- `docs/source/data-model.md` §10.1, §29-§30, and §34
- `docs/source/functional-spec.md` M02-FR-001 and M02-FR-012
- `docs/slices/006Y5-member-registry-governance-and-form-contract-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_141135_architecture_review`

## Scope

- Make identity-approval projection and write consume one evaluation covering exact permission,
  member object scope, requester-checker separation, pending state, member/request version, and KYC
  state. An out-of-scope checker must see the same disabled reason/category returned by the write.
  The projected approval row must contain exactly §44's `action_code`, `label`, `enabled`,
  `disabled_reason`, `required_permission`, and `required_role` fields; no serializer-local
  authority inference may supplement them.
- Add direct public-module tests for create, update, read, request, and approve so view checks or
  patched evaluators cannot substitute for the Registry's own permission/object authority.
- Add real PostgreSQL duplicate-create and duplicate-identity-approval races. Each race must return
  one success and one standard field-level duplicate result, never an escaping `IntegrityError` or
  `500`, with exact member/request/history/audit cardinality.
- Remove the circular action-evaluation ownership between the generic member service and Registry:
  the public module owns the complete predicate/projection; serializers may translate its result.
- Preserve the complete §13.2 forms, protected identifiers, masked history, and canonical refetch.

## Test Cases

- A permissioned but object-denied checker has disabled approval projection and matching write
  denial with zero evidence.
- Requester-checker, stale member/request, non-pending/repeated approval, and duplicate approval all
  assert projection/write parity and cardinality.
- PostgreSQL duplicate create and approval races run twice without skips and expose standard
  `VALIDATION_ERROR` field errors rather than database exceptions.
- Every public Registry method denies a direct non-HTTP caller lacking its exact authority.

## Evidence Required

Failing-first object/race logs, green public Registry matrix, two PostgreSQL race logs, exact HTTP
examples, masked evidence examples, dependency scan, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- No caller can observe an enabled identity approval that the same actor/resource write rejects for
  object scope.
- Concurrent duplicate create or approval is atomic, duplicate-safe, and standard-envelope compatible.
