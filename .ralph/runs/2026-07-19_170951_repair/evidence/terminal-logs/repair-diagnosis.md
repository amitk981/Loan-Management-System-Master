# Repair Diagnosis

## Red-capable feedback loop

Retained independent command from run `2026-07-19_165226_repair`:

`RALPH_EVIDENCE_DIR=<run-1> E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`

The real staff login succeeded, `/api/v1/loan-accounts/?page=1&page_size=20` returned HTTP 200, and
Playwright deterministically timed out on `getByText('LN-REAL-OWNER-001', { exact: true })` before
the first screenshot.

## Root cause

The guarded fixture creates a sanctioned account assigned to its Senior Finance SAP owner. The
canonical loan-account read owner intentionally scopes Credit Managers only to active-or-later
accounts. The test logged in as Credit Manager for the sanctioned list/summary, so a truthful real
Django response omitted the row. This was an evidence actor-selection defect, not missing fixture
data, frontend pagination, or a product permission defect.

## Repair

Senior Finance now captures the sanctioned list and summary. After real initiation, CFC
authorisation, and transfer success, Credit Manager captures the active summary. Senior Finance then
returns through the real login form for the genuine inaccessible-account error. No production scope
or UI behavior changed.
