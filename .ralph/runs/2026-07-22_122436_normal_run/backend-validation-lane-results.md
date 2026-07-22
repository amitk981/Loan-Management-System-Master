# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: periodic full-suite checkpoint at completed slice 320
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 320
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/defaults/migrations/0003_extension_note.py`
- `sfpcl_credit/defaults/models.py`
- `sfpcl_credit/defaults/modules/default_workflow.py`
- `sfpcl_credit/defaults/views.py`
- `sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py`
- `sfpcl_credit/tests/test_extension_note_workflow_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_extension_note_workflow_api`
- `sfpcl_credit.tests.test_default_case_opening_api`
- `sfpcl_credit.tests.test_default_grace_assessment_api`
