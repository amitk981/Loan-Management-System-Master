# Backend focused green evidence

Command used the mandated Ralph interpreter:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_loan_account_reads_api sfpcl_credit.tests.test_loan_account_creation_api.LoanAccountCreationApiTests.test_terminal_sanction_creates_unfunded_account_terms_and_evidence sfpcl_credit.tests.test_disbursement_transfer_success_api.DisbursementTransferSuccessApiTests.test_public_success_records_transfer_and_activates_exact_loan_atomically -v 1`

```text
Creating test database for alias 'default'...
Found 9 test(s).
System check identified no issues (0 silenced).
.........
----------------------------------------------------------------------
Ran 9 tests in 1.994s

OK
Destroying test database for alias 'default'...
```

Framework/schema checks:

```text
python manage.py check
System check identified no issues (0 silenced).

python manage.py makemigrations --check --dry-run
No changes detected
```
