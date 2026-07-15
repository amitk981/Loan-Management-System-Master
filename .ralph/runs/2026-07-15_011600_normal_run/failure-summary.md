# Failure Summary

- Run: 2026-07-15_011600_normal_run
- Mode: normal_run
- Slice: 008I4-sensitive-field-encryption-and-cdsl-null-contract-closure
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-coverage-results.md:FAILED (errors=4, skipped=36)
```

## Last 50 lines: backend-coverage-results.md

```
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
.Catalogue seeded: 183 permissions, 20 roles, 8 teams, 193 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
...............................................................................sssssss.....ssssss........ss..sssss............sss........ssss......sssssssss..........
======================================================================
ERROR: test_central_reveal_validates_reason_and_denies_lost_object_scope (sfpcl_credit.tests.test_cdsl_share_pledge_api.CDSLSharePledgeApiTests.test_central_reveal_validates_reason_and_denies_lost_object_scope)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_011600_normal_run/sfpcl_credit/tests/test_cdsl_share_pledge_api.py", line 484, in test_central_reveal_validates_reason_and_denies_lost_object_scope
    pledge_id = created.json()["data"]["cdsl_share_pledge_id"]
                ~~~~~~~~~~~~~~^^^^^^^^
KeyError: 'data'

======================================================================
ERROR: test_corrupt_ciphertext_fails_reveal_without_plaintext_or_success_audit (sfpcl_credit.tests.test_cdsl_share_pledge_api.CDSLSharePledgeApiTests.test_corrupt_ciphertext_fails_reveal_without_plaintext_or_success_audit)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_011600_normal_run/sfpcl_credit/tests/test_cdsl_share_pledge_api.py", line 587, in test_corrupt_ciphertext_fails_reveal_without_plaintext_or_success_audit
    pledge_id = created.json()["data"]["cdsl_share_pledge_id"]
                ~~~~~~~~~~~~~~^^^^^^^^
KeyError: 'data'

======================================================================
ERROR: test_explicit_company_secretary_reveal_is_one_time_and_separately_audited (sfpcl_credit.tests.test_cdsl_share_pledge_api.CDSLSharePledgeApiTests.test_explicit_company_secretary_reveal_is_one_time_and_separately_audited)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_011600_normal_run/sfpcl_credit/tests/test_cdsl_share_pledge_api.py", line 452, in test_explicit_company_secretary_reveal_is_one_time_and_separately_audited
    denial = AuditLog.objects.get(action="security.cdsl_pledge.bo_accounts_reveal_denied")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/manager.py", line 87, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/models/query.py", line 649, in get
    raise self.model.DoesNotExist(
sfpcl_credit.identity.models.AuditLog.DoesNotExist: AuditLog matching query does not exist.

======================================================================
ERROR: test_legacy_ciphertext_migration_reconciles_hash_last4_and_row_count (sfpcl_credit.tests.test_cdsl_share_pledge_api.CDSLSharePledgeApiTests.test_legacy_ciphertext_migration_reconciles_hash_last4_and_row_count)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_011600_normal_run/sfpcl_credit/tests/test_cdsl_share_pledge_api.py", line 632, in test_legacy_ciphertext_migration_reconciles_hash_last4_and_row_count
    pk=created.json()["data"]["cdsl_share_pledge_id"]
       ~~~~~~~~~~~~~~^^^^^^^^
KeyError: 'data'

----------------------------------------------------------------------
Ran 841 tests in 276.571s

FAILED (errors=4, skipped=36)
Destroying test database for alias 'default'...
```

## Changed files (git status)

```
.ralph/progress.md
.ralph/state.json
docs/slices/008I4-sensitive-field-encryption-and-cdsl-null-contract-closure.md
docs/slices/008J-blank-dated-cheque-and-cancelled-cheque-custody.md
docs/slices/008K-final-documentation-approval-sequence.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
docs/working/CONTEXT.md
docs/working/HANDOFF.md
docs/working/digests/epic-008-documentation-security-package.md
sfpcl_credit/config/settings.py
sfpcl_credit/members/protected_identity.py
sfpcl_credit/processes/security_instrument_evidence.py
sfpcl_credit/requirements.txt
sfpcl_credit/security_instruments/evidence_contract.py
sfpcl_credit/security_instruments/modules/cdsl_share_pledge.py
sfpcl_credit/security_instruments/modules/security_package.py
sfpcl_credit/security_instruments/request_contracts.py
sfpcl_credit/security_instruments/views.py
sfpcl_credit/tests/test_cdsl_share_pledge_api.py
sfpcl_credit/tests/test_security_instrument_boundary.py
.ralph/runs/2026-07-15_011600_normal_run/
sfpcl_credit/documents/modules/sensitive_data_access.py
sfpcl_credit/security_instruments/migrations/0004_migrate_cdsl_field_encryption.py
sfpcl_credit/shared/
sfpcl_credit/tests/test_field_encryption.py
```
