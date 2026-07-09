# Execution Plan - 004H2 KYC Profile Duplicate Create Contract Hardening

## Scope
- Implement only `004H2-kyc-profile-duplicate-create-contract-hardening`.
- Harden duplicate `POST /api/v1/kyc-profiles/` requests for `party_type="member"` and an existing member KYC profile.
- Do not add re-KYC behavior, multiple-profile storage, new permissions, frontend design changes, or database migrations.

## Source Trace
- `docs/source/api-contracts.md` section 18.1-18.4 defines KYC profile read/create/update and document upload/verify endpoints.
- `docs/source/data-model.md` section 12.1 defines `kyc_profiles` fields and KYC business constraints.
- Epic 004 digest and architecture review finding require one profile per member party and a standard validation envelope for duplicates.

## TDD Plan
1. Add a backend API regression proving a second create for the same member-party returns `400 VALIDATION_ERROR`, leaves exactly one `KycProfile`, and creates only one `kyc.profile.created` audit row.
2. Run the focused test with `/Users/amitkallapa/LMS/.ralph/venv/bin/python` and save the failing output under `evidence/terminal-logs/`.
3. Implement the smallest service-layer pre-create check before `KycProfile.objects.create`.
4. Re-run the focused test and save green output.

## Implementation Plan
- Update `sfpcl_credit/tests/test_member_kyc_api.py` with the duplicate-create regression through the public API.
- Update `sfpcl_credit/members/services.py` to raise Django `ValidationError` when an active member-party profile already exists.
- Update `docs/working/API_CONTRACTS.md` with duplicate-create semantics.
- Run required backend and frontend gates, save logs, then update Ralph artifacts and slice status.

## Risk
- Medium. This changes an API error path only, keeps the existing unique database constraint, and should not affect successful KYC read/update/document flows.
