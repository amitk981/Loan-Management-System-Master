# Ralph Handoff

## Last Run
2026-07-09_122959_normal_run

## Current Status
`004F-shareholding-and-share-certificate-records` completed successfully.

## What Completed
- Added `Shareholding` persistence in `sfpcl_credit.members` with source-backed fields:
  member FK, folio, share count, holding mode, nullable demat/valuation references, valuation
  snapshot fields, pledged count, available count, future-pledge flag, status, and timestamps.
- Added database constraints and service validation for non-negative `number_of_shares`,
  non-negative `pledged_share_count`, pledged shares not exceeding total shares, and maintained
  `available_share_count = number_of_shares - pledged_share_count`.
- Implemented `GET`/`POST /api/v1/members/{member_id}/shareholdings/` with standard envelopes,
  pagination, missing-member handling, `members.shareholding.read` for GET, and
  `members.shareholding.create` for POST.
- Successful shareholding create updates the member share summary from active shareholdings and
  writes `members.shareholding.created` audit metadata; no workflow event is written.
- Replaced Member Profile's Shareholding tab with API-backed loading/empty/error/list/validation/
  success/create states using existing UI patterns and no mock shareholding rows.
- Updated `docs/working/API_CONTRACTS.md` and the Epic 004 digest.
- Sharpened `004G-landholding-and-crop-plan-records` and `004H-kyc-upload-and-verification`.

## Explicit Deferrals
- `PATCH /api/v1/shareholdings/{shareholding_id}/` is not implemented.
- `share_certificates` are not implemented. Source `data-model.md` §11.2 fields are captured in
  the Epic 004 digest for a future small slice.
- Demat account management, CDSL integration, share valuation calculation, pledge eligibility, and
  loan-limit rules remain deferred.

## Evidence
See `.ralph/runs/2026-07-09_122959_normal_run/`.

Key logs under `evidence/terminal-logs/`:
- `backend-shareholdings-red.log` and `backend-shareholdings-green.log`
- `frontend-shareholdings-red.log` and `frontend-shareholdings-green.log`
- `backend-check.log`, `backend-tests.log`, `backend-makemigrations-check.log`,
  `backend-coverage.log`
- `frontend-typecheck.log`, `frontend-lint.log`, `frontend-tests.log`, `frontend-build.log`
- `git-diff-check.log`
- `frontend-screenshot-attempt.log`

Backend tests: 213 passed. Frontend tests: 69 passed. Coverage: 96%, above the 85% floor.

Visual evidence: `evidence/shareholding-tab.html` is self-contained. Live dev-server/browser PNG
capture was blocked by sandbox restrictions: Vite failed to bind localhost with `EPERM`, Playwright
Chromium failed Mach bootstrap permission, and `qlmanage` failed sandbox initialization.

## Current Blocker
`004E-witness-shareholder-validation` remains blocked until a real loan-application boundary exists.
Shareholding facts now exist, but witness records belong to application documentation and must not
be implemented as member-level witness APIs or boolean-only shareholder checks.

## Notes For Next Run
- Run `004G-landholding-and-crop-plan-records` next.
- `004G` is now sharpened to implement member land-holding and crop-plan list/create endpoints and
  Member Profile Land & Crop wiring if the APIs land in that slice.
- Land/crop-specific permission codes are not present in the source/catalogue. The next run must
  record an assumption if it uses an existing member permission, or split permission-catalogue work
  first if validation rejects that default.
- `004H` is sharpened with KYC profile/document fields and explicit KYC permission codes.
