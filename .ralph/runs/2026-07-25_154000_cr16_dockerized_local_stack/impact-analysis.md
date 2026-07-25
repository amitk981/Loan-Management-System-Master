# CR-016 Impact Analysis

## Changed backend modules

- `sfpcl_credit.config.settings`: currently defines SQLite unconditionally and reads the existing
  Celery/storage environment variables. CR-016 adds explicit PostgreSQL runtime selection while
  preserving SQLite when `SFPCL_POSTGRES_HOST` is absent.

## Unchanged backend integration points

- `sfpcl_credit.config.wsgi` and `sfpcl_credit.config.celery`: unchanged application entry points
  consumed by Gunicorn, the Celery worker, and Celery beat.
- `sfpcl_credit.ops` and `sfpcl_credit.config.urls`: unchanged `/health/live/` and
  `/health/ready/` endpoints consumed by container health checks and Nginx.
- `sfpcl_credit.identity.management.commands.seed_demo_users`: unchanged guarded local/demo seed.
  The bootstrap service runs it only when `SFPCL_ALLOW_DEMO_SEED=true`.
- `sfpcl_credit.processes.tasks`: unchanged Celery task catalogue imported by worker and beat.

Grep evidence:

```text
sfpcl_credit/config/settings.py: DATABASES, CELERY_BROKER_URL,
CELERY_RESULT_BACKEND, CELERY_BEAT_SCHEDULE, DOCUMENT_STORAGE_ROOT,
REPORT_EXPORT_STORAGE_ROOT
sfpcl_credit/config/urls.py: /health/live/, /health/ready/
sfpcl_credit/config/celery.py: sfpcl_credit.processes.tasks
sfpcl_credit/identity/management/commands/seed_demo_users.py:
SFPCL_DEBUG and SFPCL_ALLOW_DEMO_SEED guard
```

## Frontend integration points

- No React route, screen, component, styling, or business-behavior module changes.
- `sfpcl-lms/src/services/authSession.ts` already accepts `VITE_API_BASE_URL`; the production image
  builds with `/` so requests remain same-origin.
- Nginx serves the existing compiled SPA, provides history fallback, and proxies `/api/` and
  `/health/` to Django.

## Blast radius

- Every Django model/API uses the configured default database and therefore runs against PostgreSQL
  in Compose.
- Communications and report-export producers enqueue through Celery; the separate worker needs
  Redis and the same PostgreSQL/storage configuration as the API.
- Scheduled communications dispatch and export cleanup require Celery beat.
- Document and report-export modules require the API and worker to share the same persistent
  filesystem volume.
- Authentication is exercised through the frontend proxy to prove Nginx, Django, PostgreSQL, and
  seeded local identities agree.

## Regression tests and validation

- Add focused settings tests for default SQLite and explicit PostgreSQL selection.
- Add a packaging regression test for the rendered Compose dependency/storage graph and Nginx
  same-origin/history-fallback contract.
- Retain the existing health endpoint tests.
- Run Django migration checks and the complete backend suite.
- Run frontend unit tests, typecheck, lint, and production build.
- Run `docker compose config`, image builds, migrations against PostgreSQL, service health checks,
  frontend HTML, proxied health/API requests, and worker/beat Redis startup checks.

## Frontend design-rule compliance

No UI, component, route, styling, typography, color, spacing, or interaction change is made.
The container serves the existing production build unchanged.
