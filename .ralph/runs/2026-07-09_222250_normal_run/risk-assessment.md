# Risk Assessment

Run: 2026-07-09_222250_normal_run  
Slice: 005FA-member-portal-authentication  
Risk level: High

## Why High
- This slice changes authentication, password reset, session revocation, token claims, and borrower/member access boundaries.
- A mistake could grant staff workflow powers to borrowers or expose cross-member data in later portal screens.

## Controls Applied
- High-risk standing approval checked in `docs/working/HIGH_RISK_APPROVALS.md`; no veto exists.
- Backend TDD added before implementation for activation, duplicate/unknown activation rejection, member-scoped token claims, staff API denial, single-use password reset, session revocation, password change, and audit rows.
- Borrower portal tokens include `member_id`, `portal_account_id`, and `portal_role = borrower_member`.
- Borrower current-user payload exposes only portal own-data permission codes, not staff `applications.loan_application.complete_check`, reference-generation, or deficiency-return permissions.
- OTP values are not returned by production API responses and only OTP hashes are persisted.
- Password reset revokes active sessions; password change revokes other sessions and keeps the current session active.
- Sensitive values are not serialized in portal auth responses.

## Assumptions / Residual Risk
- A-042 records that OTP delivery is currently represented by the existing communication-shell row, with no real SMS/email provider call.
- A-042 also records that PAN/Aadhaar last-four verification compares against current stored placeholder encrypted values until a proper sensitive-value verification adapter exists.
- MP00 OTP-login mode is intentionally blocked in the UI until a source-backed OTP preference/login flow is implemented.
- Visual PNG screenshots could not be captured in this sandbox: Vite server bind failed with `EPERM`, the in-app browser was unavailable, Playwright Chromium launch failed with macOS Mach-port permission denial, and Quick Look rendering failed. A self-contained visual evidence HTML file and failure logs are saved under `evidence/`.

## Gate Result
- Backend check, full backend tests, migration check, backend coverage, frontend lint/typecheck/tests/build, `git diff --check`, and protected-path scan passed.
