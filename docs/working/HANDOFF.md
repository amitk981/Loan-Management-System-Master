# Ralph Handoff

## Last Run
2026-07-09_150108_normal_run

## Current Status
`004I-sensitive-masking-and-reveal-audit` completed successfully.

## What Completed
- Added `POST /api/v1/members/{member_id}/reveal-sensitive-field/` for member `pan` and `aadhaar`
  only.
- Reveal requires bearer auth, base `members.member.read`, and the exact field permission:
  `members.sensitive.reveal_pan` or `members.sensitive.reveal_aadhaar`.
- Request validation requires `field_name` in `pan|aadhaar` and a non-empty `reason`.
- Success returns the full value only in the immediate response with `expires_at`,
  `Cache-Control: no-store`, and `Pragma: no-cache`.
- `GET /api/v1/members/{member_id}/` remains masked; `can_view_full` now reflects only matching
  field-specific reveal permission.
- Successful reveals write `members.sensitive_field.revealed`; authenticated denied attempts write
  `members.sensitive_field.reveal_denied`. Audit metadata excludes full PAN/Aadhaar, encrypted
  token contents, hashes, and identifier-derived values. Reveal writes no workflow event.
- Member Profile overview now shows existing-pattern reveal controls only when `can_view_full` is
  true, requires a reason before calling the endpoint, clears the reason after success, and keeps
  full values only in temporary component state.
- Updated `docs/working/API_CONTRACTS.md` and Epic 004 digest. Sharpened 004J and 004K with the
  closed reveal boundary.

## Explicit Deferrals
- Nominee, witness, authorised-signatory, KYC document download, export reveal, generic sensitive
  reveal APIs, and bank-account full-number reveal remain deferred.
- Bank-account/cancelled-cheque metadata belongs to 004J. Do not reuse PAN/Aadhaar reveal
  permissions for normal bank metadata read/create.
- Borrower360/KYC panel reveal wiring outside the Member Profile overview belongs to 004K.
- 004E witness validation remains blocked until a real loan-application boundary exists.

## Evidence
See `.ralph/runs/2026-07-09_150108_normal_run/`.

Review artifacts: `execution-plan.md`, `review-packet.md`, `risk-assessment.md`,
`changed-files.txt`, `final-summary.md`, API examples, static visual HTML, and gate logs under
`evidence/terminal-logs/`.

Live PNG screenshot capture was unavailable: local Vite server binding failed with `EPERM`, and
the in-app browser backend list was empty. Static self-contained visual evidence was saved instead.

## Notes For Next Run
- Run `004J-bank-account-and-cancelled-cheque-profile-foundation` next.
- 004J should implement source-backed bank-account/cancelled-cheque metadata with protected
  account-number token/hash/last4 storage and masked/last-four responses only.
- 004J should record a permission assumption or split a permission-catalogue slice if no exact
  bank-account metadata permission exists. Do not use sensitive reveal, document download,
  disbursement, export, or KYC permissions for bank metadata.
- 004K is sharpened to compose the 004I reveal endpoint for remaining Borrower360/KYC panel UI
  wiring without redefining backend audit behavior.
