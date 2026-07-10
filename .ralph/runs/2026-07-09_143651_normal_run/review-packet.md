# Review Packet - 004H2 KYC Profile Duplicate Create Contract Hardening

## Summary
This slice hardens duplicate KYC profile creation for member parties. A second
`POST /api/v1/kyc-profiles/` for the same member now returns a standard validation envelope with
`field_errors.party_id = "A KYC profile already exists for this member."` instead of surfacing the
database uniqueness message.

## Traceability
- Source says KYC profile create/read endpoints are `POST /api/v1/kyc-profiles/` and
  `GET /api/v1/kyc-profiles/?party_type=member&party_id={member_id}` (`docs/source/api-contracts.md`
  section 18.1-18.2).
- Source says `kyc_profiles` are party-scoped records with `party_type`, `party_id`, KYC status,
  CKYC consent, and risk rating (`docs/source/data-model.md` section 12.1).
- Epic 004 digest and architecture review say one profile is allowed per member party and duplicate
  creates must return a standard validation envelope before the database constraint raises.
- Code does this in `sfpcl_credit/members/services.py` by checking for an existing member-party
  `KycProfile` before `KycProfile.objects.create`.
- Test verifies this through the public API in
  `sfpcl_credit/tests/test_member_kyc_api.py::MemberKycApiTests.test_duplicate_kyc_profile_create_returns_validation_error_without_extra_rows`.

## Behavioral Checks
- Duplicate create returns `400 VALIDATION_ERROR`.
- Duplicate create response has the stable `party_id` field error.
- Duplicate create leaves exactly one member-party `KycProfile`.
- Duplicate create leaves exactly one `kyc.profile.created` audit row.
- Existing KYC create/read/update/document upload/document verify tests still pass.

## Gates
- Backend duplicate red/green logs saved under `evidence/terminal-logs/`.
- Backend KYC tests: passed.
- Backend check/tests/migration sync/coverage: passed; coverage 96%, floor 85%.
- Frontend lint/typecheck/tests/build: passed.
- `git diff --check`: passed.

## Scope Boundaries
- No migration.
- No new permission codes.
- No frontend design change.
- No KYC re-review, deficiency, document download, sensitive reveal, bank account, application
  blocker, or re-KYC task behavior.
