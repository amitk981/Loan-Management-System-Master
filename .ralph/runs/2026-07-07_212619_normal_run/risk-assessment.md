# Risk Assessment — 004A Member Directory API and UI

Risk level: Medium.

## Why
- Adds a new backend Django app/model/migration for member directory data.
- Adds a protected API endpoint and frontend API wiring for a staff-facing member screen.
- Touches sensitive-member context, but does not expose PAN/Aadhaar or implement reveal/export.

## Controls
- Backend permission gate uses source-backed `members.member.read`; no dashboard/report/document/import permissions are reused.
- Missing auth returns `401`; authenticated users without member read permission return `403`.
- Directory response excludes PAN/Aadhaar fields and masks mobile numbers to last four digits.
- Unknown query parameters and unsupported enum filters return standard `400 VALIDATION_ERROR`.
- Read-only list access creates no audit/workflow event and no mutation endpoint was added.
- Frontend removes `mockData` dependency on the backend-wired directory path and removes mock-only exposure/supply/Borrower 360 fields.

## Residual Risk
- A-029 records that the source docs do not yet provide a complete canonical enum catalogue for member/KYC/default statuses; 004A uses source examples/S05 labels only.
- Object-level member scoping beyond the broad `members.member.read` permission is not implemented because the source rule is not specific enough for this directory slice.
- Browser screenshots could not be captured in this sandbox because local server binding is denied and no browser backend/Playwright browser binary is available. Static HTML visual state artifacts were generated with the built CSS under `evidence/screenshots/member-directory-html/`.
