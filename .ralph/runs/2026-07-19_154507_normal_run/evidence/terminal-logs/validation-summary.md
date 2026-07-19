# Focused Validation Summary

## Backend TDD

- RED: `backend-red.log` — two new seed tests failed because
  `seed_epic_009_e2e_fixture` did not exist.
- GREEN: `backend-green.log` — both guarded-seed regressions pass, including refusal without both
  guards, idempotent reseed/advance behavior, real Loan Account/workspace reads, the named source-
  bank blocker, ready-state action projection, CFC governance, and immutable transfer-upload
  provenance.
- Django system check: pass, zero issues.
- Migration sync: pass, no changes detected.

## Frontend and Browser Contract

- Focused Vitest: 4 files, 15 tests passed for Loan Account 360, Disbursement Hub, Payment
  Authorisation Hub, and the disbursement transport.
- Typecheck: pass (`tsc --noEmit`).
- ESLint: pass for `src`, and a direct lint of the changed Playwright spec/config also passed.
- Production build: pass (1,882 modules transformed).
- Playwright collection: `playwright-collection.log` lists exactly one test from the declared spec.
- Local browser attempt: `playwright-local-attempt-2.log` proves the fresh database migrated, the
  guarded Epic 009 fixture seeded, and Django reached its ready endpoint. Chromium then aborted
  with `SIGABRT` under the sandbox's macOS service restrictions before creating a page. No
  screenshots were fabricated; Ralph's declared outside-sandbox two-run gate is authoritative.

## Static Boundary Audit

- The changed spec contains no `page.route`, `route.fulfill`, `addInitScript`, or auth-session
  `localStorage.setItem` call.
- All nine declared screenshot basenames occur in the spec, including the new
  `loan-account-list.png`.
- The spec deletes stale declared files at test start and asserts nine unique SHA-256 values before
  writing the sorted filename-to-hash manifest.
