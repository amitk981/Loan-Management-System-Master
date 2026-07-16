# Failure Summary

- Run: 2026-07-16_224541_normal_run
- Mode: normal_run
- Slice: 009B3C-sap-current-evidence-and-adapter-contract-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAIL: test_disbursement_readiness_real_owners_reach_a126_then_all_pass (sfpcl_credit.tests.test_final_documentation_approval_api.FinalDocumentationApprovalApiTests.test_disbursement_readiness_real_owners_reach_a126_then_all_pass)
backend-coverage-results.md:FAILED (failures=1, skipped=52)
```

## Last 50 lines: backend-coverage-results.md

```
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
.Catalogue seeded: 183 permissions, 20 roles, 8 teams, 203 role-permission links.
Portal E2E fixture seeded for e2e.portal@sfpcl.example: LO000008L4, LO000008L4-R.
Portal E2E fixture already exists.
................................................................................sssssss.....ssssss.........ssss..sssss.....ssssssss.........ssss........sssssssss...........ssss.....sssss..........
======================================================================
FAIL: test_disbursement_readiness_real_owners_reach_a126_then_all_pass (sfpcl_credit.tests.test_final_documentation_approval_api.FinalDocumentationApprovalApiTests.test_disbursement_readiness_real_owners_reach_a126_then_all_pass)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-16_224541_normal_run/sfpcl_credit/tests/test_final_documentation_approval_api.py", line 3065, in test_disbursement_readiness_real_owners_reach_a126_then_all_pass
    self.assertEqual(
AssertionError: Lists differ: ['sap_customer_code_present', 'source_bank_account_configured'] != ['source_bank_account_configured']

First differing element 0:
'sap_customer_code_present'
'source_bank_account_configured'

First list contains 1 additional elements.
First extra element 1:
'source_bank_account_configured'

- ['sap_customer_code_present', 'source_bank_account_configured']
+ ['source_bank_account_configured']

----------------------------------------------------------------------
Ran 1033 tests in 601.028s

FAILED (failures=1, skipped=52)
Destroying test database for alias 'default'...

Duration milliseconds: 620192
Exit code: 1
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/009B3C-sap-current-evidence-and-adapter-contract-closure.md
docs/slices/009E-payment-initiation-by-senior-manager-finance.md
docs/working/CONTEXT.md
docs/working/HANDOFF.md
docs/working/digests/epic-009-sap-loan-account-disbursement.md
sfpcl_credit/sap_workflow/adapters.py
sfpcl_credit/sap_workflow/modules/sap_customer_code.py
sfpcl_credit/sap_workflow/modules/sap_customer_profile.py
sfpcl_credit/tests/test_sap_customer_profile_repair.py
.ralph/runs/2026-07-16_224541_normal_run/
```
