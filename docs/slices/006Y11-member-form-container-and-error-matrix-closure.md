# Slice 006Y11: Member Form Container and Error Matrix Closure

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Deliver 006Y9's omitted mounted-container and negative interaction proof for complete member variants
and governed identity changes.

## Depends On
- 006Y9

## Runtime Capabilities
- `localhost-e2e-server`

## Source / Review References
- `docs/source/api-contracts.md` §6-§8, §13.2, and §44
- `docs/source/functional-spec.md` M02-FR-001 and M02-FR-012
- `docs/source/codebase-design.md` §23.3-§23.6, §26.3, and §42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/006Y9-member-form-real-session-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_203645_architecture_review`

## Scope

- Mount the production Member Directory -> registration -> Member Profile containers with mocked
  HTTP responses at the shared transport boundary, not mocked `createMember`/`updateMember` wrappers.
  Submit and assert every §13.2 common, address, individual, FPC, and Producer Institution field.
  Creation requires `members.member.create`; ordinary update and governed identity-change actions
  require `members.member.update`; detail/readback requires `members.member.read`.
- For create, ordinary PATCH, identity-change request, and approval, cover `400` field validation,
  `403` permission/object/maker-checker denial, and `409` stale/non-pending conflicts. Each action
  makes one mutation call, performs no retry/local merge/refetch on error, and preserves exact server
  field/reason facts; success performs exactly one canonical detail GET and renders masked identities.
- Extend the real-session scenario with a distinct Producer Institution registration, using
  collision-proof per-run folio/PAN/Aadhaar values and exact one-POST/one-detail-GET assertions.
  Retain the requester/checker approval flow and prove the approval POST is preceded by the
  Registry-projected enabled six-field action.
- Preserve the approved modal/action composition, masks, and screenshots; introduce no client-owned
  authority, data merge, retry, new styling, or plaintext identity logging.

## Trusted Browser Acceptance

- Spec: `e2e/member-governance-variants.e2e.spec.ts`
- Screenshot: `member-individual-complete-reloaded.png`
- Screenshot: `member-institution-complete-reloaded.png`
- Screenshot: `member-producer-institution-complete-reloaded.png`
- Screenshot: `member-identity-requester-denied.png`
- Screenshot: `member-identity-checker-approved.png`

## Trusted Browser Scenario

- Use real staff login/routing/API calls with no route interception, token injection, or mocked member
  responses. Create/reload individual, FPC, and Producer Institution variants, then request and
  separately approve one protected identity correction.
- Assert exact request bodies/counts and masked canonical readback before taking all five screenshots.

## Test Cases

- Mounted success matrix proves exact full-field bodies and one canonical refetch for all variants.
- Mounted negative matrix proves one-call `400/403/409`, no automatic retry/refetch/local merge, and
  exact displayed backend fields/reasons for create/update/request/approve.
- Browser collection discovers one deterministic scenario whose unique identities cannot collide
  across the two independent trusted runs.

## Evidence Required

Failing-first mounted/error logs, green request matrix, masked HTTP examples, browser collection,
two trusted runs with five screenshots, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- M02-FR-001's individual, FPC, and Producer Institution variants and M02-FR-012's approved change
  request are reachable through real sessions with canonical masked readback.
- All member mutation failures remain backend-authored, one-call, and free of client synthesis.
