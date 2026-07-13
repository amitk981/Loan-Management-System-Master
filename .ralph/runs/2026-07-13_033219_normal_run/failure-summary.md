# Failure Summary

- Run: 2026-07-13_033219_normal_run
- Mode: normal_run
- Slice: 006Z10-portal-limit-interaction-and-boundary-proof
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: second trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: one or more declared browser screenshots are missing or empty.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- PASS: slice-specific trusted browser contract is valid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- FAIL: second trusted slice-specific browser run did not pass.
- FAIL: one or more declared browser screenshots are missing or empty.

Declared specs:
- e2e/portal-application-limit-authority.e2e.spec.ts
Declared screenshots:
- portal-limit-available.png
- portal-limit-unavailable.png
- portal-limit-over-limit-advisory.png
- portal-limit-review-maximum.png
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/006Z10-portal-limit-interaction-and-boundary-proof.md
docs/slices/007A-approval-matrix-configuration.md
docs/slices/007B-approval-case-creation-from-appraisal.md
docs/working/HANDOFF.md
docs/working/digests/epic-006-eligibility-loan-limit-appraisal.md
sfpcl-lms/e2e/portal-application-limit-authority.e2e.spec.ts
sfpcl-lms/src/pages/borrower/portal/applications/MP05_NewApplication.test.tsx
sfpcl_credit/credit/modules/borrower_limit_projection.py
sfpcl_credit/tests/test_portal_member_api.py
.ralph/runs/2026-07-13_033219_normal_run/
```
