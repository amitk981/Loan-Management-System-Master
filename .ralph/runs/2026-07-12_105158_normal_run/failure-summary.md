# Failure Summary

- Run: 2026-07-12_105158_normal_run
- Mode: normal_run
- Slice: 006Y4-witness-correction-and-resource-action-closure
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
- e2e/member-governance-closure.e2e.spec.ts
Declared screenshots:
- witness-capture-refetched.png
- witness-correction-refetched.png
- witness-correction-stale.png
- witness-resource-denied.png
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/006Y4-witness-correction-and-resource-action-closure.md
docs/slices/006Z-produce-supply-history-persistence.md
docs/slices/006Z2-portal-application-limit-display-authority.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/HANDOFF.md
sfpcl-lms/e2e/member-governance-closure.e2e.spec.ts
sfpcl-lms/src/App.tsx
sfpcl-lms/src/pages/applications/ApplicationDetail.test.tsx
sfpcl-lms/src/pages/applications/ApplicationDetail.tsx
sfpcl-lms/src/services/applicationIntakeApi.test.ts
sfpcl-lms/src/services/applicationIntakeApi.ts
sfpcl_credit/api.py
sfpcl_credit/applications/models.py
sfpcl_credit/applications/services.py
sfpcl_credit/applications/views.py
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/identity/management/commands/seed_e2e_users.py
sfpcl_credit/tests/test_witness_api.py
.ralph/runs/2026-07-12_105158_normal_run/
sfpcl-lms/src/pages/applications/WitnessPanel.container.test.tsx
sfpcl_credit/applications/migrations/0013_witness_correction.py
sfpcl_credit/applications/modules/witness_corrections.py
```
