# Failure Summary

- Run: 2026-07-17_112800_normal_run
- Mode: normal_run
- Slice: 009E3-disbursement-amount-and-source-bank-governance-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_non_approved_or_incoherent_cases_create_nothing (sfpcl_credit.tests.test_final_documentation_approval_api.LoanReadyDocumentChecklistFixture.test_non_approved_or_incoherent_cases_create_nothing) (status='approved', coherent=False)
backend-coverage-results.md:FAIL: test_non_approved_or_incoherent_cases_create_nothing (sfpcl_credit.tests.test_final_documentation_approval_api.LoanReadyDocumentChecklistFixture.test_non_approved_or_incoherent_cases_create_nothing)
backend-coverage-results.md:FAIL: test_share_mode_variants_and_missing_or_conflicting_facts_do_not_guess (sfpcl_credit.tests.test_final_documentation_approval_api.LoanReadyDocumentChecklistFixture.test_share_mode_variants_and_missing_or_conflicting_facts_do_not_guess)
backend-coverage-results.md:FAILED (failures=3, skipped=58)
```

## Last 50 lines: backend-coverage-results.md

```
Approval configuration seeded: Demo Sanction Committee FY 2026 (seed-2026-1).
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.Catalogue seeded: 184 permissions, 20 roles, 8 teams, 203 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
..Catalogue seeded: 184 permissions, 20 roles, 8 teams, 203 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.Catalogue seeded: 184 permissions, 20 roles, 8 teams, 203 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.Catalogue seeded: 184 permissions, 20 roles, 8 teams, 203 role-permission links.
Portal E2E fixture seeded for e2e.portal@sfpcl.example: LO000008L4, LO000008L4-R.
Portal E2E fixture already exists.
................................................................................sssssss.....ssssss.........ssss..sssssssssss.....ssssssss.........ssss........sssssssss...........ssss.....sssss..........
======================================================================
FAIL: test_non_approved_or_incoherent_cases_create_nothing (sfpcl_credit.tests.test_final_documentation_approval_api.LoanReadyDocumentChecklistFixture.test_non_approved_or_incoherent_cases_create_nothing) (status='approved', coherent=False)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_112800_normal_run/sfpcl_credit/tests/test_document_checklist_api.py", line 744, in test_non_approved_or_incoherent_cases_create_nothing
    with self.assertRaises(document_checklist.InvalidChecklistState):
AssertionError: InvalidChecklistState not raised

======================================================================
FAIL: test_non_approved_or_incoherent_cases_create_nothing (sfpcl_credit.tests.test_final_documentation_approval_api.LoanReadyDocumentChecklistFixture.test_non_approved_or_incoherent_cases_create_nothing)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_112800_normal_run/sfpcl_credit/tests/test_document_checklist_api.py", line 750, in test_non_approved_or_incoherent_cases_create_nothing
    self.assertEqual(DocumentChecklist.objects.count(), 0)
AssertionError: 1 != 0

======================================================================
FAIL: test_share_mode_variants_and_missing_or_conflicting_facts_do_not_guess (sfpcl_credit.tests.test_final_documentation_approval_api.LoanReadyDocumentChecklistFixture.test_share_mode_variants_and_missing_or_conflicting_facts_do_not_guess)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-17_112800_normal_run/sfpcl_credit/tests/test_document_checklist_api.py", line 217, in test_share_mode_variants_and_missing_or_conflicting_facts_do_not_guess
    self.assertFalse(items[code].applicable_flag)
AssertionError: True is not false

----------------------------------------------------------------------
Ran 1086 tests in 790.565s

FAILED (failures=3, skipped=58)
Destroying test database for alias 'default'...

Duration milliseconds: 813454
Exit code: 1
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/009E3-disbursement-amount-and-source-bank-governance-closure.md
docs/slices/009F2-cfc-authorisation-integrity-and-bank-evidence-closure.md
docs/slices/009G-utr-capture-and-transfer-success.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/HANDOFF.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/configurations/models.py
sfpcl_credit/configurations/modules/source_bank_governance.py
sfpcl_credit/disbursements/modules/disbursement_authorisation.py
sfpcl_credit/disbursements/modules/disbursement_initiation.py
sfpcl_credit/disbursements/modules/disbursement_scope.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/loans/modules/loan_account_lifecycle.py
sfpcl_credit/tests/test_disbursement_authorisation_api.py
sfpcl_credit/tests/test_disbursement_initiation_api.py
sfpcl_credit/tests/test_final_documentation_approval_api.py
.ralph/runs/2026-07-17_112800_normal_run/
sfpcl_credit/configurations/migrations/0004_source_bank_governance_history.py
```
