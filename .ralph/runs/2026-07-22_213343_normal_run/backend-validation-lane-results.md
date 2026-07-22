# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root closure has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 325
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/closure/migrations/0002_noc_issuance.py`
- `sfpcl_credit/closure/models.py`
- `sfpcl_credit/closure/modules/loan_closure.py`
- `sfpcl_credit/closure/modules/noc_document_facts.py`
- `sfpcl_credit/closure/views.py`
- `sfpcl_credit/communications/modules/communication_dispatcher.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/legal_documents/modules/document_generation.py`
- `sfpcl_credit/legal_documents/modules/noc_document.py`
- `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_loan_document_generation_api.py`
- `sfpcl_credit/tests/test_noc_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_loan_document_generation_api`
- `sfpcl_credit.tests.test_noc_api`
- `sfpcl_credit.tests.test_closure_api`
