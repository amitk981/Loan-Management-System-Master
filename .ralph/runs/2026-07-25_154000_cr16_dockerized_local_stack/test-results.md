# CR-016 Test Results

## TDD evidence

- RED command:
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_database_settings -v 2`
- RED assertion:
  `AssertionError: 'django.db.backends.sqlite3' != 'django.db.backends.postgresql'` in
  `test_explicit_postgres_environment_selects_postgres`.
- GREEN: both database-settings tests passed after adding the explicit PostgreSQL environment
  contract; the default-without-host test confirms existing SQLite development behavior remains.
- Review regression command:
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py test sfpcl_credit.tests.test_database_settings sfpcl_credit.tests.test_docker_stack_contract -v 2`
- Review regression result: 4 tests passed, covering both settings paths, the rendered Compose
  dependency/storage contract, and Nginx same-origin/history-fallback behavior.

## Backend

- Complete parallel backend suite: `Ran 1891 tests in 3570.454s`
- Result: `OK (skipped=176)`
- Coverage: `80603` statements, `8456` missed, `90%`
- Django system check: passed
- `makemigrations --check --dry-run`: no changes detected
- Backend image `pip check`: no broken requirements

## Frontend

- Vitest: 64 files, 515 tests passed
- TypeScript typecheck: passed
- ESLint: passed
- Production build: passed
- The existing bundle-size warning for a chunk larger than 500 kB remains; no UI code changed.

## Docker integration

- `docker compose --env-file docker.env.example config --quiet`: passed
- Backend and frontend image builds: passed
- PostgreSQL migrations and guarded demo seed: passed
- Long-running services healthy: PostgreSQL, Redis, backend, worker, beat, frontend
- One-shot `migrate` service: exited successfully with code 0
- Frontend HTML through Nginx: passed
- Proxied `/health/live/` response: `{"status":"live"}`
- Proxied `/health/ready/` response: `{"status":"ready"}`
- Staff login through Nginx, Django, and PostgreSQL: passed
- Celery worker connected to Redis and reported ready
- Celery beat started with the Redis broker
- Runtime identities: backend UID 10001 (`sfpcl`), frontend UID 101 (`nginx`)
- Persistence: demo login still passed after stopping and restarting application containers.
- Shared storage persistence: a marker written through the backend's document-storage mount remained
  readable from both newly recreated backend and worker containers.
- Browser check: the production SPA loaded and the synthetic system administrator reached the
  authenticated dashboard shell.

## Build-environment observations

- Docker Desktop's configured `desktop` credential helper failed while resolving public base-image
  metadata. Validation used an isolated temporary Docker CLI config without changing the owner's
  global Docker configuration.
- The first migration container was terminated during the initial large image/startup operation.
  The Compose definition now gives the one-shot migration service a bounded
  `restart: "on-failure:3"` policy. A clean subsequent start completed migrations before dependent
  services started.
