# Slice 006Y15: Witness Authority Matrix Behavioral Closure

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master

## Depends On
- 006Y14

## Runtime Capabilities

none

## Goal

Finish the witness correction matrix through observable public behavior, including the missing
unknown-field and in-scope missing-parent cases, without internal authority mocks.

## Source / Review References

- `docs/source/screen-spec.md` S09
- `docs/source/api-contracts.md` §6-§8 and §44
- `docs/source/auth-permissions.md` §3-§3.1, §18-§19, and §24
- `docs/source/codebase-design.md` §26.1-§27.1 and §42.2-§42.3
- `docs/slices/006Y14-witness-parent-nondisclosure-and-matrix-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_004501_architecture_review`

## Concrete Requirements

1. Return the normal `404 NOT_FOUND` for a genuinely missing parent when the actor has in-scope
   authority, while existing and random out-of-scope parent IDs remain identical `403
   OBJECT_ACCESS_DENIED` responses before child lookup.
2. Build independently selectable contact and identity cases for missing permission, parent object
   denial, child non-disclosure, applicable maker-checker, stale version, malformed/non-object JSON,
   unknown field, immutable field, and success.
3. Every applicable authority case projects the exact six-field action and invokes one public PATCH;
   denial reason/category must match and the complete witness/history/audit/workflow snapshot must
   remain unchanged. Payload-only validation cases must explicitly document why no action state
   exists for malformed request content.
4. Remove internal `evaluate_member_authority`/application-authority patches from behavioral
   coverage. Exercise owners, globally authorised users, permission denials, and object denials
   through public module/API results.

## Test Cases

- In-scope random parent is `404`; existing/random out-of-scope parents are indistinguishable `403`.
- Unknown and immutable fields execute separately for both correction kinds with zero evidence.
- Each contact/identity authority row passes alone and asserts its exact projection/write pair.
- No test passes by mocking the authority evaluator or asserting internal call counts.

## Evidence Required

Failing in-scope-parent and unknown-field tests, green independently selected matrices, dependency
scan, focused API contract results, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Parent/child non-disclosure and normal in-scope absence semantics are both preserved.
- The two correction kinds have complete observable authority/payload matrices with zero loser evidence.

## Execution Notes

- Exercise `PATCH /api/v1/loan-applications/{loan_application_id}/witnesses/{witness_id}/` for
  both `contact` and `identity` correction payload families; do not add a parallel endpoint.
- Treat `expected_version`, parent application UUID, witness UUID, correction kind, and changed
  fields as the row identity. Snapshot Witness, correction history, AuditLog, and WorkflowEvent
  before every denied write.
