# Critical UAT Trusted-Browser Repair Diagnosis

## Authoritative symptoms

Successive trusted-browser runs reached progressively later public boundaries and exposed stale
test assumptions rather than one production outage:

1. The DPD assertion expected the later repayment to reduce an earlier `2026-07-01` snapshot.
2. The report assertion read `pagination.total` instead of the standard `total_count` field.
3. The audit step used the CFC session for cross-module repayment, default, compliance, and export
   events, although the CFC audit selector is deliberately object-scoped.
4. The final negative test attempted to JSON-decode Django's valid empty HTTP 405 response.
5. One earlier transfer attempt submitted before the controlled inputs were observable, producing
   a 400 for a missing bank reference.

## Root causes and repairs

- DPD remains calculated from facts available at the requested cutoff. The E2E assertion now
  expects the full `400000.00` scheduled principal and explicitly checks that
  `principal_paid_as_of` is `0.00`. The existing canonical backend timing regression already
  proves this rule, so no duplicate business test was added.
- The report assertion now uses the repository-wide list-envelope contract,
  `pagination.total_count`.
- The guarded critical-UAT seed creates a deterministic Internal Auditor using the canonical
  `internal_auditor` role. The existing migration-owned active `audit_readonly` scope remains the
  authority; no permission was broadened. A red/green seed regression proves the user, password,
  role, active scope, and idempotent actor count. The browser switches to that actor only for
  UAT-025.
- The E2E fetch helper now accepts an empty response body and still asserts the actual HTTP status;
  it does not turn a denial into success.
- The transfer step waits for all three controlled values and captures the outgoing public request
  body before accepting the response, preventing a race from concealing an incomplete payload.

## Evidence

- RED auditor fixture: `terminal-logs/auditor-fixture-red.log`
- GREEN focused backend: `terminal-logs/focused-backend-final-green.log` — 3 tests passed
- GREEN frontend seed selection: `terminal-logs/frontend-seed-final-green.log` — 5 tests passed
- GREEN trusted browser run 1: `terminal-logs/trusted-browser-acceptance-green-1.log` — 1 passed
- GREEN trusted browser run 2: `terminal-logs/trusted-browser-acceptance-green-2.log` — 1 passed
- Static/build gates: `terminal-logs/frontend-typecheck-final.log`,
  `frontend-lint-final.log`, and `frontend-build-final.log`
- Django/migration checks: `terminal-logs/django-check-final.log` and
  `terminal-logs/migration-check-final.log`

Both browser runs deleted and migrated the isolated database before seeding. Each produced the
declared standard-loan and permission-negative screenshots plus the UAT matrix and seed manifest.

