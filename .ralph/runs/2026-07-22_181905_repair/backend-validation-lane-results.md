# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: high-risk slice
- Enforcement policy: selective
- Slice risk: high
- Candidate completion ordinal: 323
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/defaults/modules/default_workflow.py`
- `sfpcl_credit/identity/catalogue.py`
- `sfpcl_credit/legal_documents/modules/recovery_evidence.py`
- `sfpcl_credit/loans/modules/recovery_proceeds.py`
- `sfpcl_credit/recovery/migrations/0002_recovery_action_execution.py`
- `sfpcl_credit/recovery/models.py`
- `sfpcl_credit/recovery/modules/recovery_decision.py`
- `sfpcl_credit/recovery/modules/recovery_workflow.py`
- `sfpcl_credit/recovery/views.py`
- `sfpcl_credit/security_instruments/modules/recovery_invocation.py`
- `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_recovery_action_api.py`
- `sfpcl_credit/tests/test_recovery_decision_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_recovery_action_api`
- `sfpcl_credit.tests.test_recovery_decision_api`
- `sfpcl_credit.tests.test_default_case_opening_api`
- `sfpcl_credit.tests.test_default_grace_assessment_api`
- `sfpcl_credit.tests.test_extension_note_workflow_api`
- `sfpcl_credit.tests.test_non_payment_note_workflow_api`
