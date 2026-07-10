# Slice 002J2: Forbidden Permission Error Contract Alignment

## Status
Not Started

## Parent Epic
Epic 002: Platform Foundation and Authentication
Epic file: `docs/epics/002-platform-auth.md`

## Goal

Align authenticated missing-permission responses with the source-standard `403 FORBIDDEN` code
without collapsing object, sensitive-field, or approval-authority denials into the same error.

## Depends On
- 006H2

## Source / Review References
- `docs/source/api-contracts.md` §7.1
- `docs/source/codebase-design.md` §25.2-§25.4
- `docs/slices/002J-api-contract-test-harness.md`
- `docs/working/REVIEW_FINDINGS.md` entry for this review

## Scope

- Change the shared authenticated missing-permission contract from the locally accumulated
  `PERMISSION_DENIED` code to source-standard `FORBIDDEN` across staff APIs.
- Preserve `AUTH_REQUIRED`/token errors, `OBJECT_ACCESS_DENIED`,
  `SENSITIVE_FIELD_ACCESS_DENIED`, and `APPROVAL_AUTHORITY_REQUIRED` exactly; do not turn object
  existence or scope failures into permission-oracle responses.
- Centralise the translation so future modules return a typed permission denial and thin HTTP
  adapters do not choose competing codes. Update `docs/working/API_CONTRACTS.md` and affected
  frontend error handling only where it branches on the old code.
- Do not change permission grants, role assignments, object-access rules, status codes, or success
  payloads.

## Test Cases

- Extend the 002J contract harness with representative identity, member/application, credit,
  witness, audit, configuration, and portal/staff denial paths asserting `403 FORBIDDEN`.
- Assert object-scope, sensitive reveal, and approval-authority cases retain their distinct source
  codes and no write/audit/workflow side effect occurs on denial.
- Add a static regression rejecting new production literals of `PERMISSION_DENIED` outside an
  explicitly documented compatibility adapter; remove compatibility only after all callers/tests
  use `FORBIDDEN`.

## Evidence Required

Failing-first contract output, before/after denial examples, full configured gates, and a list of
every migrated endpoint family.

## Risk Level
Medium

## Acceptance Criteria

- Missing global permission consistently returns source-standard `403 FORBIDDEN`.
- Object/sensitive/approval denial semantics and all authorization decisions remain unchanged.

