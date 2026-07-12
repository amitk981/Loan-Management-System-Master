# Slice 006Y5: Member Registry Governance and Form Contract Closure

## Status
Complete

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

## Goal

Finish 006Y3's public Member Registry contract: internal object authority, duplicate-safe identity
approval, action/write maker-checker parity, and complete source §13.2 registration variants.

## Depends On
- 006Y3

## Source / Review References
- `docs/source/codebase-design.md` §10.1, §26.1-§26.3, and §42.2-§42.3
- `docs/source/api-contracts.md` §6-§8, §13.2, and §44
- `docs/source/auth-permissions.md` §34.2
- `docs/source/data-model.md` §10.1-§10.3, §29-§30, and §34
- `docs/source/functional-spec.md` M02-FR-001 and M02-FR-012
- `docs/slices/006Y3-member-registry-and-identity-change-approval-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-12_125256_architecture_review`

## Scope

- Make `MemberRegistry` the only public create/update/read/request/approve seam. It must perform
  exact permission and member object-access evaluation internally; HTTP views remain translation
  adapters and non-HTTP callers cannot bypass governance through public service functions.
- Validate proposed PAN/Aadhaar duplicates when requesting and again under the approval transaction.
  Translate the database unique-constraint race to standard field errors with no member/history/
  audit mutation; no `IntegrityError` may escape.
- Share the approval evaluation between projection and write. A requester holding the checker
  permission must see approval disabled with the same maker-checker reason returned by the write.
  Cover stale member/request, non-pending/repeated approval, object denial, and zero evidence.
- Complete the existing registration form and exact API payload for both §13.2 variants: individual
  middle name, gender, date of birth, occupation, cultivation area, primary crop, services flag,
  employment/service years; institution registration number, signatory PAN/Aadhaar, board-resolution
  flag, services flag, and produce-supply years.
- Preserve protected identity handling, masked history, canonical refetch, and the approved modal/
  action composition.

## Test Cases

- Direct module tests prove permission/object denial for every public method and no service bypass.
- PostgreSQL duplicate create and identity-approval races return one success and one standard
  duplicate response without a `500` or partial evidence.
- The approval projection/write matrix includes a requester who also owns approval permission.
- Mounted and real-session tests submit every field in both §13.2 variants and assert canonical
  refetch plus one-call `400`/`403`/`409` behavior.

## Evidence Required

Failing-first module/race/form logs, green public seam matrix, duplicate race log, exact HTTP
examples, masked evidence examples, browser screenshots for both variants and maker-checker denial,
and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Member governance cannot be bypassed outside HTTP and duplicate approval cannot become a `500`.
- Approval actions match writes for requester-checker separation, and both source registration
  variants are reachable end to end.
