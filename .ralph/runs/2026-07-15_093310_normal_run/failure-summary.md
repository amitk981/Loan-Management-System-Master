# Failure Summary

- Run: 2026-07-15_093310_normal_run
- Mode: normal_run
- Slice: 008K4-current-evidence-and-security-read-closure
- Failed checks: 4

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
artifact-quality-check.md:- FAIL: risk-assessment.md is still the unfilled template.
postgresql-acceptance-results.md:- FAIL: first independent run did not satisfy all acceptance predicates.
postgresql-acceptance-results.md:- FAIL: second independent run did not satisfy all acceptance predicates.
postgresql-acceptance-results.md:- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: postgresql-acceptance-results.md

```
# PostgreSQL Acceptance Results

- FAIL: first independent run did not satisfy all acceptance predicates.
- FAIL: second independent run did not satisfy all acceptance predicates.
- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: backend-migrations-results.md

```
# backend-migrations Results

Command: "/Users/amitkallapa/LMS/.ralph/venv/bin/python" sfpcl_credit/manage.py makemigrations --check --dry-run

Traceback (most recent call last):
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_093310_normal_run/sfpcl_credit/manage.py", line 17, in <module>
    main()
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-15_093310_normal_run/sfpcl_credit/manage.py", line 13, in main
    execute_from_command_line(sys.argv)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/__init__.py", line 442, in execute_from_command_line
    utility.execute()
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/__init__.py", line 436, in execute
    self.fetch_command(subcommand).run_from_argv(self.argv)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 413, in run_from_argv
    self.execute(*args, **cmd_options)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 459, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 107, in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/commands/makemigrations.py", line 213, in handle
    loader.project_state(),
    ^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/loader.py", line 361, in project_state
    return self.graph.make_state(
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/graph.py", line 329, in make_state
    project_state = self.nodes[node].mutate_state(project_state, preserve=False)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/migration.py", line 91, in mutate_state
    operation.state_forwards(self.app_label, new_state)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/operations/fields.py", line 93, in state_forwards
    state.add_field(
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/state.py", line 248, in add_field
    self.models[model_key].fields[name] = field
    ~~~~~~~~~~~^^^^^^^^^^^
KeyError: ('applications', 'checklistaction')
```

## Last 50 lines: backend-coverage-results.md

```
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/commands/test.py", line 24, in run_from_argv
    super().run_from_argv(argv)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 413, in run_from_argv
    self.execute(*args, **cmd_options)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 459, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/commands/test.py", line 68, in handle
    failures = test_runner.run_tests(test_labels)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 1061, in run_tests
    old_config = self.setup_databases(
                 ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/runner.py", line 959, in setup_databases
    return _setup_databases(
           ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/test/utils.py", line 203, in setup_databases
    connection.creation.create_test_db(
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/backends/base/creation.py", line 78, in create_test_db
    call_command(
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/__init__.py", line 194, in call_command
    return command.execute(*args, **defaults)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 459, in execute
    output = self.handle(*args, **options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/base.py", line 107, in wrapper
    res = handle_func(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/core/management/commands/migrate.py", line 356, in handle
    post_migrate_state = executor.migrate(
                         ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/executor.py", line 135, in migrate
    state = self._migrate_all_forwards(
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/executor.py", line 167, in _migrate_all_forwards
    state = self.apply_migration(
            ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/executor.py", line 252, in apply_migration
    state = migration.apply(state, schema_editor)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/migration.py", line 118, in apply
    operation.state_forwards(self.app_label, project_state)
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/operations/fields.py", line 93, in state_forwards
    state.add_field(
  File "/Users/amitkallapa/LMS/.ralph/venv/lib/python3.11/site-packages/django/db/migrations/state.py", line 248, in add_field
    self.models[model_key].fields[name] = field
    ~~~~~~~~~~~^^^^^^^^^^^
KeyError: ('applications', 'checklistaction')
Found 886 test(s).
```

## Changed files (git status)

```
docs/working/API_CONTRACTS.md
sfpcl_credit/applications/models.py
sfpcl_credit/applications/modules/document_checklist_facts.py
sfpcl_credit/applications/views.py
sfpcl_credit/config/urls.py
sfpcl_credit/legal_documents/models.py
sfpcl_credit/legal_documents/modules/checklist_actions.py
sfpcl_credit/legal_documents/modules/document_checklist.py
sfpcl_credit/legal_documents/modules/document_generation.py
sfpcl_credit/processes/document_checklist_actions.py
sfpcl_credit/processes/portal_documentation_actions.py
sfpcl_credit/security_instruments/modules/blank_dated_cheque.py
sfpcl_credit/security_instruments/modules/cdsl_share_pledge.py
sfpcl_credit/security_instruments/modules/power_of_attorney.py
sfpcl_credit/security_instruments/modules/security_package.py
sfpcl_credit/security_instruments/modules/sh4.py
sfpcl_credit/shared/masking.py
sfpcl_credit/tests/test_blank_dated_cheque_api.py
sfpcl_credit/tests/test_cdsl_share_pledge_api.py
sfpcl_credit/tests/test_final_documentation_approval_api.py
sfpcl_credit/tests/test_power_of_attorney_api.py
sfpcl_credit/tests/test_security_instrument_boundary.py
sfpcl_credit/tests/test_sh4_api.py
.ralph/runs/2026-07-15_093310_normal_run/
sfpcl_credit/applications/migrations/0016_bankverificationdecision_and_more.py
sfpcl_credit/applications/modules/bank_verification.py
```
