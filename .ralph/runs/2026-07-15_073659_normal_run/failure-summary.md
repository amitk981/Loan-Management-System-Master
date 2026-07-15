# Failure Summary

- Run: 2026-07-15_073659_normal_run
- Mode: normal_run
- Slice: 008L2-member-portal-deficiency-response-and-resubmission
- Failed checks: 3

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
artifact-quality-check.md:- FAIL: risk-assessment.md is still the unfilled template.
backend-coverage-results.md:FAIL: test_borrower_reads_open_deficiencies_without_internal_staff_notes (sfpcl_credit.tests.test_portal_deficiency_response_api.PortalDeficiencyResponseApiTests.test_borrower_reads_open_deficiencies_without_internal_staff_notes)
backend-coverage-results.md:FAIL: test_borrower_saves_response_draft_and_downloads_borrower_safe_deficiency_note (sfpcl_credit.tests.test_portal_deficiency_response_api.PortalDeficiencyResponseApiTests.test_borrower_saves_response_draft_and_downloads_borrower_safe_deficiency_note)
backend-coverage-results.md:FAILED (failures=2, skipped=40)
diff-limits-results.md:- FAIL: changed-line count exceeds limits.max_lines_changed.
```

## Last 50 lines: backend-coverage-results.md

```
Approval configuration seeded: Demo Sanction Committee FY 2026 (seed-2026-1).
.Demo users seeded: demo.cfo@sfpcl.example, demo.director1@sfpcl.example, demo.director2@sfpcl.example, demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
Approval configuration seeded: Demo Sanction Committee FY 2026 (seed-2026-1).
.Demo users seeded: demo.cfo@sfpcl.example, demo.director1@sfpcl.example, demo.director2@sfpcl.example, demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
Approval configuration seeded: Demo Sanction Committee FY 2026 (seed-2026-1).
Demo users seeded: demo.cfo@sfpcl.example, demo.director1@sfpcl.example, demo.director2@sfpcl.example, demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
Approval configuration seeded: Demo Sanction Committee FY 2026 (seed-2026-1).
.Demo users seeded: demo.cfo@sfpcl.example, demo.director1@sfpcl.example, demo.director2@sfpcl.example, demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
Approval configuration seeded: Demo Sanction Committee FY 2026 (seed-2026-1).
...Demo users seeded: demo.cfo@sfpcl.example, demo.director1@sfpcl.example, demo.director2@sfpcl.example, demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
Approval configuration seeded: Demo Sanction Committee FY 2026 (seed-2026-1).
.Demo users seeded: demo.cfo@sfpcl.example, demo.director1@sfpcl.example, demo.director2@sfpcl.example, demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
Approval configuration seeded: Demo Sanction Committee FY 2026 (seed-2026-1).
.Demo users seeded: demo.cfo@sfpcl.example, demo.director1@sfpcl.example, demo.director2@sfpcl.example, demo.system_admin@sfpcl.example, demo.credit_manager@sfpcl.example, demo.compliance@sfpcl.example, demo.treasury@sfpcl.example, demo.internal_auditor@sfpcl.example, demo.tracer@sfpcl.example, demo.zero@sfpcl.example (predictable local/dev password set; do not use in production).
Approval configuration seeded: Demo Sanction Committee FY 2026 (seed-2026-1).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.Catalogue seeded: 183 permissions, 20 roles, 8 teams, 203 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
..Catalogue seeded: 183 permissions, 20 roles, 8 teams, 203 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.Catalogue seeded: 183 permissions, 20 roles, 8 teams, 203 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
...............................................................................sssssss.....ssssss........ssss..sssss.....ss.......sss........ssss.......sssssssss..........
======================================================================
FAIL: test_borrower_reads_open_deficiencies_without_internal_staff_notes (sfpcl_credit.tests.test_portal_deficiency_response_api.PortalDeficiencyResponseApiTests.test_borrower_reads_open_deficiencies_without_internal_staff_notes)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_073659_normal_run/sfpcl_credit/tests/test_portal_deficiency_response_api.py", line 149, in test_borrower_reads_open_deficiencies_without_internal_staff_notes
    self.assertEqual(body["data"]["application_reference_number"], "LA-RETURNED-L2")
AssertionError: None != 'LA-RETURNED-L2'

======================================================================
FAIL: test_borrower_saves_response_draft_and_downloads_borrower_safe_deficiency_note (sfpcl_credit.tests.test_portal_deficiency_response_api.PortalDeficiencyResponseApiTests.test_borrower_saves_response_draft_and_downloads_borrower_safe_deficiency_note)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_073659_normal_run/sfpcl_credit/tests/test_portal_deficiency_response_api.py", line 214, in test_borrower_saves_response_draft_and_downloads_borrower_safe_deficiency_note
    self.assertIn(b"LA-RETURNED-L2", note.content)
AssertionError: b'LA-RETURNED-L2' not found in b'SFPCL Application Deficiency Note\nApplication: 23eaa9ae-0cfd-449b-b11f-0462287e9fd7\n\n- Upload the missing six-month bank statement.\n'

----------------------------------------------------------------------
Ran 882 tests in 332.805s

FAILED (failures=2, skipped=40)
Destroying test database for alias 'default'...
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/008L2-member-portal-deficiency-response-and-resubmission.md
docs/slices/008M-documentation-hub-frontend-wiring.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/HANDOFF.md
docs/working/PROTOTYPE_GAP_REPORT.md
docs/working/PROTOTYPE_INVENTORY.md
docs/working/digests/epic-005-application-intake.md
sfpcl-lms/src/pages/borrower/portal/applications/MP10_ApplicationStatus.tsx
sfpcl-lms/src/services/portalApi.test.ts
sfpcl-lms/src/services/portalApi.ts
sfpcl_credit/applications/models.py
sfpcl_credit/config/urls.py
sfpcl_credit/documents/services.py
sfpcl_credit/members/portal_services.py
sfpcl_credit/members/portal_views.py
.ralph/runs/2026-07-15_073659_normal_run/
sfpcl-lms/src/pages/borrower/portal/applications/MP11_DeficiencyResponse.test.tsx
sfpcl-lms/src/pages/borrower/portal/applications/MP11_DeficiencyResponse.tsx
sfpcl_credit/applications/migrations/0015_applicationdeficiencyresponse.py
sfpcl_credit/processes/portal_deficiency_response.py
sfpcl_credit/tests/test_portal_deficiency_response_api.py
```
