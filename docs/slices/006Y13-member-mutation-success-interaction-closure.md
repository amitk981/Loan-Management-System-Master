# Slice 006Y13: Member Mutation Success Interaction Closure

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Complete 006Y11's omitted successful ordinary-update, identity-request, and approval interaction
proof through the production containers and real browser request stream.

## Depends On
- 006Y11

## Runtime Capabilities
- `localhost-e2e-server`

## Source / Review References
- `docs/source/api-contracts.md` §6-§8, §13.2, and §44
- `docs/source/functional-spec.md` M02-FR-001 and M02-FR-012
- `docs/source/codebase-design.md` §23.3-§23.6, §26.3, and §42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/006Y11-member-form-container-and-error-matrix-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_220748_architecture_review`

## Scope

- Mount the actual Member Directory registration route/container and Member Profile container at the
  shared authenticated HTTP transport. Do not substitute a test-only `RegistrationJourney` for the
  routed Directory-to-Profile transition.
- Preserve the completed individual/FPC/Producer Institution create bodies, then add successful
  ordinary PATCH, protected-identity request, and separate checker approval. For every mutation,
  assert exact URL/method/body, exactly one mutation, exactly one canonical member-detail GET, masked
  readback, and no client-side merge or authority inference.
- Extend the real-session request instrumentation to assert exact ordinary-update, identity-request,
  approval bodies/counts and their canonical GETs, not only the three creates. Approval must be
  preceded by the backend-projected enabled six-field action.
- Keep existing `400`/`403`/`409` error matrices, collision-safe identities, five screenshots,
  existing components/classes, and backend-authored messages unchanged.

## Trusted Browser Acceptance

- Spec: `e2e/member-governance-variants.e2e.spec.ts`
- Screenshot: `member-individual-complete-reloaded.png`
- Screenshot: `member-institution-complete-reloaded.png`
- Screenshot: `member-producer-institution-complete-reloaded.png`
- Screenshot: `member-identity-requester-denied.png`
- Screenshot: `member-identity-checker-approved.png`

## Test Cases

- Routed mounted create matrix retains exact complete bodies and one canonical read for all three
  member types.
- Ordinary update, identity request, and approval each make one exact mutation plus one canonical
  GET, render masked server state, and never merge the mutation response locally.
- Seed conflicting display values in the mutation and canonical GET responses and assert only the
  subsequent masked detail response renders, so a hidden local merge cannot satisfy the test.
- Browser request ledger contains the exact create/update/request/approve sequence in both trusted
  runs with no duplicate writes or missing canonical reads.

## Evidence Required

Failing-first routed-container and success-ledger logs, green mounted matrix, exact browser request
table, collection, two trusted runs with five screenshots, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Every member mutation named by 006Y11 is proven through the production interaction boundary on
  success and failure, with canonical masked readback and backend authority.
