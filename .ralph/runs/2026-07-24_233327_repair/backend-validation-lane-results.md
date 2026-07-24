# Backend Validation Lane Results

- Authoritative lane: full
- Classifier recommendation: full
- Selection reason: backend root defaults has no valid owner/contract test mapping
- Enforcement policy: selective
- Slice risk: medium
- Candidate completion ordinal: 351
- Impacted-test workers: 6

Backend changed paths:
- `sfpcl_credit/defaults/modules/default_workflow.py`
- `sfpcl_credit/recovery/modules/recovery_decision.py`
- `sfpcl_credit/tests/test_recovery_decision_api.py`

Impacted test labels:
- `sfpcl_credit.tests.test_recovery_decision_api`
- `sfpcl_credit.tests.test_auditor_epic_011_api`
- `sfpcl_credit.tests.test_default_case_opening_api`
- `sfpcl_credit.tests.test_default_grace_assessment_api`
- `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance`
- `sfpcl_credit.tests.test_extension_note_workflow_api`
- `sfpcl_credit.tests.test_non_payment_note_workflow_api`
