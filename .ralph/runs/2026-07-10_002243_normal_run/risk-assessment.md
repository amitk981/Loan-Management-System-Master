# Risk Assessment

Run ID: 2026-07-10_002243_normal_run
Slice: 005G-member-portal-application-start-status
Risk level: Medium

## Scope Risk
- Full-stack change: backend portal application APIs plus MP05/MP09/MP10 frontend wiring.
- No database migration was added. Existing `loan_applications` and `deficiencies` models are reused.
- No new dependencies were added.

## Permission And Data Risk
- Portal application authority is derived only from active `PortalAccount.member_id`.
- Client-supplied `member_id` cannot broaden scope. Cross-member attempts return
  `403 OBJECT_ACCESS_DENIED`.
- Staff/non-portal tokens receive `403 PERMISSION_DENIED` on portal application endpoints.
- Responses intentionally omit staff-only actions, PAN, Aadhaar, full bank account values,
  encrypted values, token hashes, raw document contents, and staff document internals.

## Side-Effect Risk
- Draft create/update/submit reuse existing application services, metadata-only audit rows, and
  workflow events.
- Read-only list/status endpoints create no audit rows.
- Cross-member denied create/read/update/submit attempts create no application, audit row,
  workflow event, register row, reference, or visible sequence side effect.
- Submit does not generate `LO...` reference numbers; completeness pass remains the reference
  generation boundary.

## Validation Risk
- Backend focused portal tests cover own create/update/submit/list/status, staff denial,
  cross-member denial, submitted-without-reference, and returned-incomplete borrower status.
- Frontend API tests cover create/update/submit/list/detail request mapping and bearer-token usage.
- Frontend view tests cover MP09 loading, empty, error, and returned-incomplete states.
- Live screenshot capture was blocked by sandbox network binding (`listen EPERM 127.0.0.1:5173`);
  static self-contained visual evidence was saved instead.

## Gate Results
- Backend check: passed.
- Backend full tests: 265 passed.
- Backend migrations check: passed, no changes detected.
- Backend coverage: 95%, above 85% floor.
- Frontend tests: 90 passed.
- Frontend typecheck: passed.
- Frontend lint: passed.
- Frontend build: passed.
