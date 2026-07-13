# Failure Summary

- Run: 2026-07-12_103055_repair
- Mode: repair
- Slice: 006Y3-member-registry-and-identity-change-approval-closure
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
- member-create-submitted.png
- member-update-refetched.png
- member-identity-change-requested.png
- member-identity-change-approved.png
- member-governance-denied.png
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/006Y3-member-registry-and-identity-change-approval-closure.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/HANDOFF.md
sfpcl-lms/e2e/member-governance-closure.e2e.spec.ts
sfpcl-lms/src/pages/members/MemberGovernanceForm.test.tsx
sfpcl-lms/src/pages/members/MemberGovernanceForm.tsx
sfpcl-lms/src/pages/members/MemberProfile.test.tsx
sfpcl-lms/src/pages/members/MemberProfile.tsx
sfpcl-lms/src/services/memberProfileApi.ts
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/identity/management/commands/seed_e2e_users.py
sfpcl_credit/members/models.py
sfpcl_credit/members/services.py
sfpcl_credit/members/views.py
sfpcl_credit/tests/test_member_governance_api.py
sfpcl_credit/tests/test_member_profile_api.py
sfpcl_credit/tests/test_seed_e2e_users.py
.ralph/runs/2026-07-12_094433_normal_run/
.ralph/runs/2026-07-12_095521_repair/
.ralph/runs/2026-07-12_100436_repair/
.ralph/runs/2026-07-12_103055_repair/
sfpcl_credit/members/migrations/0010_member_identity_change_request.py
sfpcl_credit/members/modules/
```
