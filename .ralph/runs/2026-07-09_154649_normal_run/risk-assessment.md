# Risk Assessment

Slice: `004J-bank-account-and-cancelled-cheque-profile-foundation`

Risk level: High

## Why High
- The slice introduces financial/bank-account metadata tables and APIs.
- Account numbers are sensitive fields; storage, serialization, and audit metadata must not leak full values, protected token contents, or hashes.
- The source catalogue has no exact bank-account metadata permissions, so A-034 records a temporary member-profile permission assumption.

## Controls Applied
- TDD first: RED evidence in `evidence/terminal-logs/tdd-red-member-bank-accounts.log`; GREEN evidence in `evidence/terminal-logs/tdd-green-member-bank-accounts-final.log`.
- Account numbers are normalized to digits, stored as protected token plus keyed hash plus last four, and serialized only as masked/last-four objects.
- Create audit metadata includes member/entity IDs, masked account last four, IFSC, verification status, and signature flags only.
- `members.member.read` gates metadata lists; `members.member.update` gates creates under A-034.
- No frontend state or UI was changed, so no browser/local-storage sensitive-data risk was introduced.

## Explicit Deferrals
- Bank-account full-number reveal.
- Duplicate-active-borrower warning.
- Bank verification letters and signature mismatch resolution.
- Blank-dated cheque custody.
- Payment initiation, disbursement readiness gates, idempotency, and transfer workflows.
- Loan-application-specific cancelled-cheque behavior beyond nullable placeholder storage.

## Gate Results
- Backend focused tests: passed, 7 tests.
- `manage.py check`: passed.
- Full backend tests: passed, 238 tests.
- `makemigrations --check --dry-run`: passed.
- Backend coverage: 95%, floor 85%.
- Frontend lint/typecheck/tests/build: passed.
- `git diff --check`: passed.
