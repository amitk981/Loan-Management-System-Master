# Risk Assessment

Slice: 005I-application-intake-frontend-wiring
Risk level: Medium

## Risk Factors
- Added backend read endpoints for staff application list and Loan Request Register, expanding API surface.
- Rewired high-traffic staff intake screens from mock data to backend APIs.
- Application detail now shows only API-backed checklist/deficiency data; audit rows remain empty until a dedicated audit UI wiring slice connects workflow/audit APIs.

## Controls
- Backend list/register endpoints require session-bound auth and `applications.loan_application.read`.
- Existing 005C2 application object-access evaluator is reused for list/register visibility.
- Staff screens use staff `/api/v1/loan-applications/` endpoints only; no portal application routes are consumed.
- Returned applications preserve `application_status = incomplete_returned` and display as borrower rectification work.
- Standard list pagination defaults and max page-size behavior are implemented and tested.

## Residual Risk
- Browser PNG screenshots could not be captured because Chromium launch is blocked by the macOS sandbox. Self-contained visual evidence HTML with built CSS is saved instead.
- New Application can save/submit source-backed draft facts but document upload remains metadata/checklist-only until a future upload UI slice.
- Rejection-note metadata is not surfaced in the detail UI because there is no staff read endpoint for existing rejection notes yet; no frontend-only rejected state was invented.

## Decision Policy Notes
- No business rule was invented. Eligibility, loan limit, appraisal, sanction, and rejection status transitions remain deferred to later source-backed slices.
