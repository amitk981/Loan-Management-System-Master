# Diagnosis Evidence

## Feedback Loop

Command:

`/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_document_template_migration_state`

The corrected pre-fix run deterministically failed four subcases: approval-status and borrower-type
values were unordered sets in both current model constraints and the terminal documents migration
state. The command is fast, unattended, and asserts the reported serialization defect directly.

## Confirmed Cause

Hypotheses 1 and 2 were correct together. Current model sets made deconstruction nondeterministic,
and the last recorded state inherited the same sets from historical migration `0002`. Ordered model
tuples alone would leave model/state drift; a forward migration was therefore required. Both
constraints were vulnerable, confirming hypothesis 3. Exact-value and database-enforcement tests
falsified any runtime behavior change from the repair, addressing hypothesis 4.

## Fix Verification

- Focused test is green after the ordered current state and forward migration.
- The original full migration-check path is green under five hash-seed settings.
- Historical migration `0002` has no diff.
- No temporary instrumentation or throwaway harness remains.
