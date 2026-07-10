# Review Packet

Slice: 005I-application-intake-frontend-wiring

## Traceability
- Source `api-contracts.md` §8 and §19.1 require list pagination/filtering/sorting/search for `GET /api/v1/loan-applications/`; code now implements `list_applications_for_staff(...)` and `loan_application_collection` GET, verified by `test_list_applications_supports_staff_pagination_filtering_search_and_ordering`.
- Source S13 requires a digital Loan Request Register with generated `LO...` references and borrower/status columns; code now implements `GET /api/v1/loan-request-register/`, verified by `test_loan_request_register_list_returns_generated_reference_rows`.
- Slice 005I requires staff screens to use staff APIs and avoid mock application rows; `ApplicationList.tsx`, `NewApplication.tsx`, and `ApplicationDetail.tsx` no longer import `mockData.ts` and use `applicationIntakeApi.ts` / `memberDirectoryApi.ts`.
- Prior slice facts require `incomplete_returned` to be distinct from plain submitted; frontend status vocabulary and Application List display now show it as returned/rectification work.

## What To Review
- `sfpcl_credit/applications/services.py`: list/register filtering, object-access filtering, pagination helpers, and metadata-only serializers.
- `sfpcl_credit/applications/views.py` and `sfpcl_credit/config/urls.py`: GET collection/register routes and permission checks.
- `sfpcl-lms/src/services/applicationIntakeApi.ts`: staff API client and error-envelope handling.
- `sfpcl-lms/src/pages/applications/*`: API-backed list/new/detail wiring while preserving existing visual classes.
- `docs/working/API_CONTRACTS.md` and Epic 006 digest/slice sharpening.

## Evidence
- Backend RED: `evidence/terminal-logs/backend-list-register-red.log`.
- Backend GREEN: `evidence/terminal-logs/backend-list-register-green.log`.
- Frontend API RED/GREEN: `evidence/terminal-logs/frontend-application-api-red.log`, `frontend-application-api-green.log`.
- Focused frontend: `evidence/terminal-logs/frontend-application-focused.log`.
- Full gates: `backend-test-results.md`, `backend-coverage-results.md`, `lint-results.md`, `typecheck-results.md`, `test-results.md`, `build-results.md`, `backend-check-results.md`, `backend-migrations-results.md`.
- Visual evidence: `evidence/005I-visual-evidence.html`.

## Known Follow-Up
- Real audit/workflow timeline UI wiring should connect existing audit/workflow APIs in a later slice.
- Rejection-note display needs a read/list contract before the detail UI can show existing rejection-note metadata.
