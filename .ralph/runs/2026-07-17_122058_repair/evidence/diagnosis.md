# Repair Diagnosis

The deterministic regression command was:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_final_documentation_approval_api --verbosity 1`

Before the repair it collected 70 tests and failed the same three inherited checklist assertions on
two runs. The original `DocumentChecklistApiTests` class independently passed 13/13. Inspection then
confirmed a new module-level subclass with loan-owner-specific `_application_case` and `_decision`
overrides. Django's unittest loader collected that subclass even though its name did not begin with
`Test`.

The concrete subclass is now local to a fixture factory. After the repair, the same command collects
57 intended tests and passes twice. This isolates test fixtures without weakening production
checklist, loan-owner, readiness, initiation, or authorisation behavior.
