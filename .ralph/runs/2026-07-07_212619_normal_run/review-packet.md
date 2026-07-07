# Review Packet — 004A Member Directory API and UI

## Summary
Implemented the read-only member directory vertical slice:
- New `sfpcl_credit.members` app with a narrow `Member` model and migration for §13.1 directory fields.
- `GET /api/v1/members/` with standard list envelope, strict supported filters, pagination, auth, permission checks, and masked mobile output.
- Frontend `MemberDirectory` now fetches the backend API through `memberDirectoryApi` and no longer imports `mockData` on the wired path.
- API contracts, assumptions, prototype inventory/gap report, Epic 004 digest, and next slices 004B/004C were updated.

## Traceability
- Source says `api-contracts.md` §13.1 defines `GET /api/v1/members/?search=&member_type=&membership_status=&kyc_status=&default_status=&page=1&page_size=20` with member identifiers, status fields, masked `mobile_number`, `share_summary`, and `active_member_status`.
  Code does this in `sfpcl_credit/members/services.py` and `sfpcl_credit/members/views.py`.
  Verified by `MemberDirectoryApiTests.test_authenticated_user_can_list_members_with_paginated_masked_fields`.
- Source says standard list envelopes and validation errors come from `api-contracts.md` §6-7.
  Code uses `list_response`/`error_response`.
  Verified by pagination and validation tests in `sfpcl_credit/tests/test_member_directory_api.py`.
- Source says `auth-permissions.md` §12.2/§25.1 uses `members.member.read` for listing members.
  Code gates the endpoint with `MEMBER_READ_PERMISSION = "members.member.read"`.
  Verified by `test_member_directory_requires_authentication_and_member_read_permission`.
- Source says sensitive values must be masked and PAN/Aadhaar are sensitive.
  Code never serializes PAN/Aadhaar fields for the directory and masks mobile numbers.
  Verified by the PAN/Aadhaar absence assertion in the backend list-success test.
- Frontend rules require existing visual patterns and no mock fallback on API-backed screens.
  Code reuses the existing directory table/filter/card classes, adds an API client, and removes the `mockData` import.
  Verified by `sfpcl-lms/src/pages/members/MemberDirectory.test.tsx`.

## Evidence
- Backend red: `evidence/terminal-logs/backend-member-directory-red.log`.
- Backend green/focused: `backend-member-directory-green-1.log`, `backend-member-directory-green-2.log`, `backend-member-directory-green-3.log`.
- Frontend red/green: `frontend-member-directory-red.log`, `frontend-member-directory-green.log`.
- Gates: `backend-check.log`, `backend-tests.log`, `backend-makemigrations-check.log`, `backend-coverage.log`, `frontend-typecheck.log`, `frontend-lint.log`, `frontend-tests.log`, `frontend-build.log`, `git-diff-check.log`.
- API examples: `api-response-examples.md`.
- Visual artifacts: `evidence/screenshots/member-directory-html/{populated,empty,forbidden,unauthorized,api-error}.html`.

## Visual Evidence Note
Actual PNG screenshots could not be produced in this sandbox. Django/Vite local server binding returned `EPERM`, the in-app browser list was empty, and Playwright's Chromium binary is not installed locally. Static HTML state artifacts were generated from the real `MemberDirectoryView` with the built CSS so the visual states remain reviewable.
