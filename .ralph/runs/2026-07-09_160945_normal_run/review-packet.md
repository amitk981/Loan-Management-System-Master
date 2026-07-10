# Review Packet

Slice: `004K-borrower-360-kyc-panel-and-masking-ui-wiring`

## What Changed
- `Borrower360.tsx` now loads real Epic 004 member-master data through frontend API clients:
  member detail, shareholdings, land holdings, crop plans, nominees, KYC profile/documents, bank
  accounts, and cancelled cheques.
- `memberProfileApi.ts` now exposes `fetchMemberBankAccounts` and
  `fetchMemberCancelledCheques`, normalizing account-number DTOs to masked/last-four metadata with
  `can_view_full: false`.
- Added `Borrower360.test.tsx` covering the bank metadata client methods and the API-backed
  Borrower 360 view states.
- Updated prototype tracking docs, Epic 004 digest, 004K status, handoff/progress/state, and
  sharpened 005A/005B.

## Source Trace
- Source says Borrower 360 S07 must consolidate borrower profile, KYC, documents, loans, defaults,
  communications, and audit. Code now consolidates implemented Epic 004 facts and explicitly shows
  empty states for modules without backend APIs yet.
- Source/API facts say sensitive values must be masked unless returned by the audited reveal
  endpoint. Code uses masked PAN/Aadhaar by default and calls only
  `POST /api/v1/members/{member_id}/reveal-sensitive-field/` when the backend sets the matching
  `can_view_full` flag.
- Prior 004J facts say bank/cancelled-cheque responses expose only masked account metadata and no
  bank full-number reveal exists. Code normalizes bank account DTOs to masked-only values and the UI
  has no bank reveal, duplicate-warning, signature-mismatch workflow, payment-initiation, or
  disbursement-readiness controls.
- Screen S17 requires borrower KYC profile, CKYC consent, re-KYC status, document list, and verify
  action surface. Code renders profile/document metadata from 004H APIs; mutation controls remain in
  the existing Member Profile KYC panel where 004H wired them.

## Verification
- TDD red: `evidence/terminal-logs/borrower360-red.log`
- TDD green: `evidence/terminal-logs/borrower360-green.log`
- Frontend tests: `npm test` -> 80/80 passing
- Frontend typecheck: `npm run typecheck` passing
- Frontend lint: `npm run lint` passing
- Frontend build: `npm run build` passing
- Backend check: `manage.py check` passing
- Backend tests: 238/238 passing
- Backend migration sync: `makemigrations --check --dry-run` passing
- Backend coverage: 96%, above 85% floor
- Diff whitespace check: `git diff --check` passing

## Visual Evidence
- Self-contained HTML: `evidence/visual/borrower360-evidence.html`
- Browser PNG capture was attempted but blocked by sandbox/browser launch restrictions. Failure log:
  `evidence/terminal-logs/visual-screenshot-desktop.log`.

## Reviewer Notes
- No backend schema or API contract changed in this slice.
- The new active-tab prop on `Borrower360View` is only for deterministic view testing; the page
  runtime continues using internal tab state.
- Optional subresource failures render warnings while keeping the core member profile visible.
