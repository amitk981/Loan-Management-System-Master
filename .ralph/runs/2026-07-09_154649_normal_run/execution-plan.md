# Execution Plan

Selected slice: 004J-bank-account-and-cancelled-cheque-profile-foundation

## Scope
- Implement member-owned bank account and cancelled-cheque metadata foundation only.
- Add backend models/migration, service validation/serialization, URL/view endpoints, and focused API tests.
- Do not add frontend UI in this slice; Member Profile rendering remains deferred unless later slices require it.
- Do not implement full bank-account reveal, payment initiation, disbursement gates, duplicate-active-borrower decisions, bank-verification letters, blank-cheque custody, or loan-application-specific cancelled-cheque behavior.

## Source Basis
- `docs/source/data-model.md` §12.3-§12.5 and §28/§29 require protected account-number storage, account hash/last-four support, bank-account status/verification fields, cancelled-cheque metadata, and masking.
- `docs/source/api-contracts.md` §31.2/§45 reserve bank-account IDs and idempotency for future disbursement endpoints; those are out of scope here.
- `docs/source/screen-spec.md` S11/S15 require duplicate-bank and signature-mismatch workflows later; this slice persists foundation facts without inventing those decisions.
- `docs/source/auth-permissions.md` has no exact bank-account metadata permission. Use the narrow current member-profile assumption: list with `members.member.read`, create with `members.member.update`; record A-034.

## TDD Plan
1. RED: Add focused backend API tests for creating/listing bank accounts and cancelled cheques with masked responses and protected storage assertions.
2. GREEN: Add models, migration, services, views, and URLs until the focused tests pass.
3. RED/GREEN increments: add permission/auth tests, missing/deleted member tests, validation tests, and metadata-only audit/no-workflow tests.
4. Update `docs/working/API_CONTRACTS.md`, Epic 004 digest, `ASSUMPTIONS.md`, and slice status.

## Validation Gates
- Backend focused tests for the new member bank API.
- `manage.py check`
- Full backend tests
- `makemigrations --check --dry-run`
- Backend coverage with the configured floor
- Frontend lint/typecheck/tests/build unchanged but still run as Ralph gates.
- Save red/green/gate logs under `evidence/terminal-logs/`, plus API examples.
