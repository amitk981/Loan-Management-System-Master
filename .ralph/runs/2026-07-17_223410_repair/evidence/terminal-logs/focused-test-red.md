# Focused Repair Test — RED

Command:

```text
"/Users/amitkallapa/LMS/.ralph/venv/bin/python" manage.py test sfpcl_credit.tests.test_final_documentation_approval_api.FinalDocumentationApprovalApiTests.test_public_post_disbursement_signature_binds_current_transfer_evidence --verbosity 2
```

Result: exit code 1; 1 test ran in 0.842 seconds.

Exact demonstrated failure:

```text
ERROR: test_public_post_disbursement_signature_binds_current_transfer_evidence
Traceback (most recent call last):
  File "sfpcl_credit/tests/test_final_documentation_approval_api.py", line 2535, in test_public_post_disbursement_signature_binds_current_transfer_evidence
    register.delete()
django.db.models.deletion.ProtectedError: ("Cannot delete some instances of model 'LoanRegisterUpdate' because they are referenced through protected foreign keys: 'Disbursement.register_update'.", {<Disbursement: Disbursement object (...)>})

Ran 1 test in 0.842s
FAILED (errors=1)
```

This is red on the precise full-coverage failure: the legacy test expects deletion to create missing
register evidence, while 009G3 intentionally makes that evidence undeletable.
