# Execution Plan

Selected slice: 004D-nominee-validation-and-ui

## Source and Boundary
- Implement only member-level nominees for `004D-nominee-validation-and-ui`.
- Source-backed behavior: `GET` and `POST /api/v1/members/{member_id}/nominees/`, `members.nominee.read` for list, `members.nominee.create` for create, required/format validation for PAN and Aadhaar, minor rejection, masked response values, and audit metadata on creation without full PAN/Aadhaar.
- Defer loan-application nominee snapshots, nominee update/delete, KYC document upload/verification, nominee count rules, relationship rules, and source-undefined object-scope narrowing.

## Planned File Areas
- Backend: `sfpcl_credit/members/`, `sfpcl_credit/config/urls.py`, focused backend tests, and one members migration.
- Frontend: `sfpcl-lms/src/pages/members/MemberProfile.tsx`, `sfpcl-lms/src/services/memberProfileApi.ts`, and the existing member profile tests.
- Documentation/evidence: API contract working file, Epic 004 digest, next-slice sharpening, run evidence, risk/review/final artifacts, state/progress/handoff.

## TDD Cycles
1. Backend red: add a focused nominee API test for masked list/create success and permission separation.
2. Backend green: add `Nominee` persistence, service validation/serialization, URL/view handlers, and migration.
3. Backend red/green: add tests for missing member/auth, required and invalid PAN/Aadhaar, minor rejection, and no plaintext leakage in response/audit.
4. Frontend red: add member-profile API/view tests for nominee list, empty/error/validation states, create payload, and no mock nominee rows.
5. Frontend green: extend the member-profile API client and replace the deferred Nominee tab using existing card, empty, alert, and form/modal-style patterns.

## Verification
- Save red/green logs under `evidence/terminal-logs/`.
- Run backend `manage.py check`, backend tests, `makemigrations --check --dry-run`, backend coverage using `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run frontend `npm run typecheck`, `npm run lint`, `npm test`, and `npm run build`.
- Save API response examples and static visual evidence for the nominee tab states.
- Run `git diff --check`, protected-path review, changed-files capture, and diff-size review before final artifacts.
