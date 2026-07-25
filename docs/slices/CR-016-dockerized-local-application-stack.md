# Slice CR-016: Dockerized local application stack

## Status
Not Started

## Origin
Change request (maintenance stage), accepted 2026-07-25 from docs/change-requests/accepted/CR-016-dockerized-local-application-stack.md.

## Risk Level
High

## Change Request (verbatim)

# Dockerized local application stack

## Type
feature

## Severity
High

## What Is Requested
Provide one reproducible Docker Compose application stack for local development and owner
demonstration. It must run the React frontend, Django backend, PostgreSQL database, Redis broker,
Celery worker, and Celery beat scheduler, with a one-shot migration/bootstrap service and shared
persistent document/export storage. The stack is local/development infrastructure and must not
claim production readiness or fabricate the production evidence that remains missing.

## Expected Behaviour
1. The owner copies a committed non-secret Docker environment example to a local ignored environment
   file and runs one documented `docker compose up --build` command.
2. PostgreSQL and Redis start first and report healthy.
3. A one-shot backend bootstrap service connects to PostgreSQL, applies all Django migrations, and
   may seed the already-guarded local demo users only when the explicit local demo flag is enabled.
4. The Django API starts through Gunicorn, uses PostgreSQL rather than SQLite, and reports healthy
   through the existing liveness/readiness endpoints.
5. Separate Celery worker and beat services use the same backend image, PostgreSQL database, Redis
   broker/result backend, and persistent document/export storage as the API.
6. The React application is built into an Nginx image. Browser requests use same-origin `/api/` and
   health paths proxied to the backend, without hard-coded container-only hostnames in browser code.
7. Opening the documented localhost URL displays the frontend and the frontend can authenticate and
   call the real backend. Restarting the stack without deleting volumes retains PostgreSQL and
   document/export data.
8. Health checks and dependency ordering fail closed: an unhealthy database, Redis, failed
   migration, or unhealthy backend prevents dependent services from being reported ready.
9. Documentation explains start, status, logs, migration, guarded demo seed, stop, reset, and the
   distinction between this local stack and a production deployment.

## Where It Appears
Repository-level local runtime packaging. No approved product screen or styling changes are
requested. The existing frontend is served at a documented localhost URL and the existing backend
API remains under its current `/api/v1/` contract.

## Source Document Reference
`docs/source/deployment-ops.md` §§2, 4, 5.1, 7.1-7.4, 9, 11.4, and 20 recommends containerised
frontend/backend/worker/scheduler deployment, PostgreSQL, Redis-backed asynchronous work, health
checks, and explicit runtime configuration. The local Compose packaging and owner-demonstration
workflow are a new requirement — owner approved. This approval also covers the pinned Redis client
dependency required by Celery's Redis transport; Gunicorn is already pre-approved by
`docs/working/DEPENDENCY_POLICY.md`.

## Acceptance Criteria
- A checked-in Compose definition contains `frontend`, `backend`, `postgres`, `redis`, `worker`,
  `beat`, and one-shot migration/bootstrap services with bounded health checks and dependency order.
- Backend runtime settings select PostgreSQL from explicit `SFPCL_POSTGRES_*` variables while
  preserving the current isolated SQLite default when those variables are absent; focused tests
  prove both paths.
- Gunicorn and the Redis client are pinned in backend requirements; no dependency is hidden in a
  Dockerfile-only install.
- Frontend and backend images build from pinned project manifests, run as non-root where practical,
  use Docker ignore files, and contain no committed credentials or generated local data.
- Nginx serves the built single-page application, provides history fallback, and proxies API and
  health requests to the backend with safe forwarded headers and upload limits.
- PostgreSQL data and document/report-export storage use named volumes; API and worker share the
  application storage volume.
- `docker compose config` succeeds, every image builds, migrations complete against PostgreSQL, all
  long-running services become healthy/running, the frontend returns HTML, backend liveness and
  readiness return 200, and one real frontend-to-backend API request is demonstrated.
- Worker and beat connect to Redis without missing-transport errors; a bounded smoke check verifies
  their startup without claiming external email/SMS provider delivery.
- Existing backend tests, frontend tests, typecheck, lint, build, migration check, and configured
  Ralph gates remain green.
- Operator documentation includes exact commands and clearly states that production secrets,
  managed storage, TLS, monitoring, backups, real provider credentials, staging soak evidence, and
  business signoff remain separate production-readiness requirements.

## Mandatory First Step: Impact Analysis
Before changing ANY code, write impact-analysis.md in the run folder covering:
- Affected backend models/endpoints/services, with grep evidence.
- Affected frontend screens/components/routes.
- Blast radius: every OTHER module that consumes the affected pieces.
- Existing tests covering the affected pieces, and the regression tests to add in EACH affected module.
- FRONTEND_DESIGN_RULES compliance note for any UI change.
Validation fails this run if impact-analysis.md is missing.

## Acceptance Criteria
- The change request's own acceptance criteria are met.
- Regression tests added for every module named in the impact analysis.
- All quality gates pass.
