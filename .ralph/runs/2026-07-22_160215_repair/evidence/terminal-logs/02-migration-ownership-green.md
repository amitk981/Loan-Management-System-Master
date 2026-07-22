# Focused GREEN — historical credit ownership migration

Command (from `sfpcl_credit/`):

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_credit_model_ownership_migration.CreditAssessmentModelOwnershipMigrationTests --verbosity 2
```

Result: `OK`, exit code `0`, 2 tests run in 189.946 seconds.

Passing behaviors:

- `test_forward_move_preserves_rows_relationships_and_evidence_references`
- `test_reverse_move_restores_application_state_without_changing_rows`

The pre-move projection now excludes the downstream `recovery` leaf, so it retains the historical
`applications` credit models and does not pull the post-move `credit` owner into that state.
