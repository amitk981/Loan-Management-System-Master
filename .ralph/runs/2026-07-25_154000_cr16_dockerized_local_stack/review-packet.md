# CR-016 Review Packet

## Traceability

The accepted CR says the owner must be able to start one local stack containing the existing React
frontend, Django API, PostgreSQL, Redis, a Celery worker and beat, with migrations, persistent
storage, health-based ordering, and no claim of production readiness
(`docs/slices/CR-016-dockerized-local-application-stack.md`, Expected Behaviour 1-9).

The implementation provides those services in `docker-compose.yaml`, packages the existing
applications in `Dockerfile.backend` and `sfpcl-lms/Dockerfile`, selects PostgreSQL only when the
explicit `SFPCL_POSTGRES_HOST` runtime contract is present, and documents the local/production
boundary in `docs/working/DOCKER_LOCAL_STACK.md`.

Focused database-settings tests verify the SQLite and PostgreSQL branches. The complete backend and
frontend suites protect existing behavior. Compose configuration, image builds, PostgreSQL
migrations, service health, same-origin health/API calls, Celery Redis startup, persistence after a
restart, and a browser login verify the integrated local stack.

In source → code → test form:

- The CR says PostgreSQL must be selected only by explicit Docker runtime settings while isolated
  development remains on SQLite; `settings.py` implements the two branches, and
  `DatabaseSettingsTests` verifies both.
- The CR says migrations and healthy PostgreSQL/Redis must gate API, worker, beat, and frontend
  startup while all backend lanes share application storage; `docker-compose.yaml` implements that
  graph, and `DockerStackContractTests` plus the live healthy-service/recreation checks verify it.
- The CR says the existing SPA must reach the real backend through same-origin routes;
  `nginx.conf` implements API/health proxying and SPA fallback, and the Nginx contract test, proxied
  health/login calls, and authenticated browser check verify it.

## Scope check

- No product UI, route, component, styling, schema, migration, endpoint, or business rule changed.
- No protected workflow or source-document file changed.
- The implementation is local packaging only and explicitly lists the separate work still required
  before any production deployment.
