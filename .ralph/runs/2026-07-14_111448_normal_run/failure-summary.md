# Failure Summary

- Run: 2026-07-14_111448_normal_run
- Mode: normal_run
- Slice: 008B3-document-renderer-and-output-proof-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_pdf_wraps_long_legal_text_across_bounded_pages (sfpcl_credit.tests.test_loan_document_generation_api.LoanDocumentGenerationApiTests.test_pdf_wraps_long_legal_text_across_bounded_pages)
backend-coverage-results.md:FAIL: test_sanctioned_application_generates_retained_pdf_from_exact_template (sfpcl_credit.tests.test_loan_document_generation_api.LoanDocumentGenerationApiTests.test_sanctioned_application_generates_retained_pdf_from_exact_template)
backend-coverage-results.md:FAILED (failures=2, skipped=22)
final-summary.md:failure, safe names, metadata-only lists, legal-document authority, and A-102 remain unchanged.
final-summary.md:fails there, this run must enter repair rather than be committed.
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
.Catalogue seeded: 182 permissions, 20 roles, 8 teams, 182 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
..Catalogue seeded: 182 permissions, 20 roles, 8 teams, 182 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.Catalogue seeded: 182 permissions, 20 roles, 8 teams, 182 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
......................................sssssss.....ssssss..........ssss......sss........ss..........
======================================================================
FAIL: test_pdf_wraps_long_legal_text_across_bounded_pages (sfpcl_credit.tests.test_loan_document_generation_api.LoanDocumentGenerationApiTests.test_pdf_wraps_long_legal_text_across_bounded_pages)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_111448_normal_run/sfpcl_credit/tests/test_loan_document_generation_api.py", line 265, in test_pdf_wraps_long_legal_text_across_bounded_pages
    self.assertEqual(response.status_code, 200, response.content)
AssertionError: 400 != 200 : b'{"success": false, "error": {"code": "VALIDATION_ERROR", "message": "Loan document generation failed validation.", "details": {}, "field_errors": {"borrower_name": "Merged authoritative text is not readable in the rendered PDF."}}, "meta": {"request_id": "req-generate-term-sheet", "timestamp": "2026-07-14T06:13:59.733359Z", "api_version": "v1"}}'

======================================================================
FAIL: test_sanctioned_application_generates_retained_pdf_from_exact_template (sfpcl_credit.tests.test_loan_document_generation_api.LoanDocumentGenerationApiTests.test_sanctioned_application_generates_retained_pdf_from_exact_template)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-14_111448_normal_run/sfpcl_credit/tests/test_loan_document_generation_api.py", line 175, in test_sanctioned_application_generates_retained_pdf_from_exact_template
    self.assertEqual(response.status_code, 200, response.content)
AssertionError: 400 != 200 : b'{"success": false, "error": {"code": "VALIDATION_ERROR", "message": "Loan document generation failed validation.", "details": {}, "field_errors": {"borrower_name": "Merged authoritative text is not readable in the rendered PDF."}}, "meta": {"request_id": "req-generate-term-sheet", "timestamp": "2026-07-14T06:13:59.802786Z", "api_version": "v1"}}'

----------------------------------------------------------------------
Ran 736 tests in 182.520s

FAILED (failures=2, skipped=22)
Destroying test database for alias 'default'...
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/008B3-document-renderer-and-output-proof-closure.md
docs/slices/008C-documentation-checklist-applicability.md
docs/slices/008D-stamp-duty-and-notarisation-tracking.md
docs/working/ASSUMPTIONS.md
docs/working/HANDOFF.md
docs/working/digests/epic-008-documentation-security-package.md
sfpcl_credit/legal_documents/modules/document_generation.py
sfpcl_credit/requirements.txt
sfpcl_credit/tests/test_loan_document_generation_api.py
.ralph/runs/2026-07-14_111448_normal_run/
sfpcl_credit/legal_documents/modules/document_renderer.py
```
