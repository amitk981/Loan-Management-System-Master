# Slice 006Y: Member Create/Update and Identity Governance (Backend)

## Status
Not Started

## Parent Epic
Epic 004: Member, KYC, Nominee, Witness, and Profile Master
Epic file: `docs/epics/004-member-kyc-master.md`

Note: filename-scheduled after 006X deliberately (Checkpoint 1 of PRODUCTION_COMPLETION_BLUEPRINT.md closes tracer-critical debt first); the capability itself is Epic 004 scope debt — live member handlers are GET-only while the source requires create/update.

## Goal
Deliver the member create/update backend contract with change history, verified-identity-field locking, and maker-checker/reverification rules, closing the §6.3 "Member create/update and identity governance" gap.

## User Value
Staff can register and correct member records through governed APIs instead of relying on seed data; verified identity facts cannot be silently rewritten.

## Depends On
- 006X3

## Source References
- docs/source/api-contracts.md section 13 (member create/update endpoints and payloads)
- docs/source/data-model.md member tables and member change-history table
- docs/source/auth-permissions.md member/profile permission codes and maker-checker separation (§12 member permissions, §17.1 maker-checker)
- docs/source/functional-spec.md M01 member-master requirements
- docs/working/digests/epic-004-member-kyc-master.md

## Prototype Reference
- sfpcl-lms/src/pages/members/* (read-only reference; UI is 006Y2)

## Concrete Requirements
1. Implement `POST /api/v1/members/` and `PATCH /api/v1/members/{member_id}/` per the source §13 contracts, standard envelopes, and validation errors. Individual-farmer and FPC payload variants both supported.
2. Persist a member change-history record for every create/update: actor, timestamp, changed fields, old/new values (sensitive values stored masked/hashed, never plaintext).
3. Lock verified identity fields (PAN, Aadhaar, and any KYC-verified fact): once KYC verification (004H) has passed, direct PATCH of those fields is rejected with a contract error; changes require the reverification path, which resets the relevant KYC status and records the reason.
4. Maker-checker: the user who creates/edits a member record cannot be the sole verifier where the source requires separation; enforce with object-level checks, not UI hiding.
5. Use the narrowest source-backed create/update permission codes; classify anything not in the catalogue as approval-required and record the assumption. Test 401/403 on every mutation.
6. Audit events for create, update, locked-field rejection, and reverification trigger.
7. No plaintext PAN/Aadhaar in fixtures; synthetic encrypted/hash placeholders only.

## Test Cases
- Create and update happy paths for individual and FPC members with envelope/validation coverage.
- Locked-field PATCH after KYC verification is rejected; reverification path resets status and writes history + audit.
- Change-history rows record actor and field-level diff with masked sensitive values.
- Maker-checker separation and 401/403 negative tests.

## Out of Scope
Staff UI forms and witness capture surface (006Y2), sensitive reveal (004I owns), KYC document upload (004H owns), portal profile edits.

## Risk Level
High

## Acceptance Criteria
- Member create/update works only through the governed contract with history and locking enforced server-side.
- All gates pass; API request/response examples saved with synthetic data.

## Run-Ahead Sharpening Review (006X, 2026-07-11)

- Preserve the existing `GET /api/v1/members/` and `GET /api/v1/members/{member_id}/` envelopes
  while adding POST/PATCH; use the same canonical member UUID and object-scope projection across
  create, update, history, audit, and reverification responses.
- Tests must prove a denied verified-identity mutation writes neither member state nor change
  history, while the explicit reverification transition records actor, reason ownership, masked
  before/after identity facts, and the resulting KYC status atomically.

## Run-Ahead Sharpening Review (architecture review 2026-07-11_230238)

- Follow 006X2's action/write parity contract for member update and reverification: the member
  detail projection and authoritative mutation must consume the same permission, object-scope,
  identity-lock, KYC-state, maker-checker, and stale-version evaluation.
- Tests must pair every enabled/disabled six-field action with the matching write outcome and prove
  that denied/stale identity changes leave the member, masked history, KYC status, and audit counts
  unchanged. Do not use global `/auth/me` permissions as resource authority.

## Run-Ahead Sharpening Review (006X3, 2026-07-12)

- Seed/test identities must remain synthetic and guarded exactly like the Epic 006 browser fixture;
  no normal demo or production command may create governed member-change data.
- The create/update/history/reverification API test must assert one shared member UUID, masked
  sensitive history, exact six-field actions, and zero state/history/audit writes for 400/403/409.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
