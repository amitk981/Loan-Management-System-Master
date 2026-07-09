# Review Packet

Slice: `004J-bank-account-and-cancelled-cheque-profile-foundation`

## Implementation Summary
- Added `BankAccount` and `CancelledCheque` models plus migration `0008`.
- Added member-scoped endpoints:
  - `GET/POST /api/v1/members/{member_id}/bank-accounts/`
  - `GET/POST /api/v1/members/{member_id}/cancelled-cheques/`
- Added validation, masking, protected token/hash/last-four storage, permission gates, and metadata-only create audits.
- Updated `docs/working/API_CONTRACTS.md`, `docs/working/ASSUMPTIONS.md`, Epic 004 digest, 004J status, and sharpened 004K/005A.

## Traceability
- Source says `data-model.md` §12.3 defines `bank_accounts` with owner party, holder, protected account number, hash, last four, IFSC, bank/branch, verification, cancelled-cheque link, signature flag, and status.
  Code adds `BankAccount` with those fields in `sfpcl_credit/members/models.py`; tests verify create/list and protected storage in `test_member_bank_accounts_api.py`.
- Source says `data-model.md` §12.4 defines `cancelled_cheques` with member/document/account/IFSC/branch/verification/signature metadata.
  Code adds `CancelledCheque` and keeps `loan_application_id` nullable until real application persistence exists; tests verify member-scoped create/list.
- Source says §28/§29 require encrypted sensitive fields, hashes, and masking for account numbers.
  Code uses protected token + keyed hash + last four and serializes `{masked,last4,can_view_full:false}` only; tests assert full account numbers, token fields, and hashes are absent from responses/audit metadata.
- Source says `screen-spec.md` S11/S15 duplicate-bank and signature mismatch workflows are later workflow concerns.
  Code explicitly does not implement duplicate warnings, bank verification letters, disbursement blockers, or signature mismatch resolution; docs record the deferrals.
- Source has no exact bank-account metadata permission.
  A-034 records the assumption: list uses `members.member.read`, create uses `members.member.update`; tests assert read/create separation and no broad reveal reuse.

## Evidence
- RED: `evidence/terminal-logs/tdd-red-member-bank-accounts.log`
- GREEN: `evidence/terminal-logs/tdd-green-member-bank-accounts-final.log`
- Backend check: `evidence/terminal-logs/backend-check.log`
- Backend tests: `evidence/terminal-logs/backend-tests.log`
- Migration sync: `evidence/terminal-logs/backend-makemigrations-check.log`
- Coverage: `evidence/terminal-logs/backend-coverage.log`
- Frontend gates: `evidence/terminal-logs/frontend-lint.log`, `frontend-typecheck.log`, `frontend-tests.log`, `frontend-build.log`
- API examples: `api-response-examples.md`

## Reviewer Notes
- No frontend was changed; visual evidence is not applicable.
- `GET /api/v1/members/{member_id}/` remains unchanged and does not embed bank-account data or full bank values.
- The create endpoints accept full account numbers only as request input and never echo them back.
