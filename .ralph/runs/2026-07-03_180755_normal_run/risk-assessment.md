# Risk Assessment

Risk level: Medium

- Selected slice: 002D2-backend-dev-infrastructure
- Mode: normal_run
- Manual review required: no, but backend runtime validation requires orchestrator dependency installation.

## Risk Drivers
- Backend settings changed from hardcoded/in-memory defaults to env-driven configuration and a persistent dev SQLite database.
- CORS middleware added to support React Vite development origin.
- Backend tests were refactored from manual table creation to Django migrations/TestCase.
- New dependency pinned: `django-cors-headers==4.4.0`.

## Controls
- TDD RED evidence saved before implementation.
- `rg "schema_editor.create_model|ensure_.*tables" sfpcl_credit/tests` evidence is clean after refactor.
- `compileall` passed for backend Python files.
- Frontend typecheck, vitest, and build all passed.
- Backend runtime commands were attempted with the required Ralph venv interpreter and failed only because the newly pinned package is not installed locally.

## Residual Risk
- `manage.py check`, backend tests, migration check, coverage, dev DB migration, CORS runtime response, and auth smoke cannot complete in this offline venv until `django-cors-headers` is installed from the pinned requirements.
- Once installed, the new CORS middleware is expected to provide `Access-Control-Allow-Origin: http://localhost:5173` for the new test.
