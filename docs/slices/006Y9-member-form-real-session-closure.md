# Slice 006Y9: Member Form Real-Session Closure

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Prove the complete source §13.2 individual and institution registration variants through the real
routed staff/auth/API boundary that 006Y5 required but replaced with mocked wrapper tests.

## Depends On
- 006Y7

## Runtime Capabilities
- `localhost-e2e-server`

## Source / Review References
- `docs/source/api-contracts.md` §6-§8, §13.2, and §44
- `docs/source/codebase-design.md` §23.3-§23.6, §26.3, and §42.3
- `docs/source/functional-spec.md` M02-FR-001 and M02-FR-012
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/006Y5-member-registry-governance-and-form-contract-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_141135_architecture_review`

## Scope

- Mount the production Member Directory/profile containers through authenticated HTTP and submit
  every §13.2 field for individual and institution variants; mocked API wrappers and static markup
  do not satisfy the contract.
- Assert exact request bodies, one canonical refetch, masked protected identities after refetch, and
  one-call `400`/`403`/`409` behavior without local merge/retry.
- Run real staff sessions through create, ordinary correction, identity-change request, separate-
  checker approval, and canonical reload while preserving the approved modal/action composition;
  assert the checker consumes the Registry-projected six-field approval action before POST.
- Keep synthetic identities out of screenshots/logs except visibly masked values; do not change the
  visual system or add client-side business authority.

## Trusted Browser Acceptance

- Spec: `sfpcl-lms/e2e/member-governance-variants.e2e.spec.ts`
- Start from the real staff login boundary; no route interception, direct token injection, or mocked
  member response is allowed.
- Create and reload one complete individual and one complete institution, then request and approve a
  protected identity correction with distinct actors.
- Required screenshots:
  - `evidence/screenshots/member-individual-complete-reloaded.png`
  - `evidence/screenshots/member-institution-complete-reloaded.png`
  - `evidence/screenshots/member-identity-requester-denied.png`
  - `evidence/screenshots/member-identity-checker-approved.png`

## Test Cases

- Mounted tests submit every exact field/type for both variants and assert canonical masked refetch.
- Validation, object denial, stale write, and requester-checker denial each make one call and retain
  server field/reason facts.
- Trusted browser collection discovers the named flows and all four screenshots are produced in two
  independent orchestrator runs.

## Evidence Required

Failing-first mounted/browser collection logs, green interaction tests, exact HTTP examples, four
trusted screenshots, masked response/audit examples, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Both source registration variants and approved identity correction are reachable through real
  routed sessions with canonical masked readback and backend-owned authority.
