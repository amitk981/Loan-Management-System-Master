# CR-016 Risk Assessment

Risk remains **High** because the change packages every runtime lane and introduces PostgreSQL as
the Compose database.

The principal failure modes are database mis-selection, migrations racing service startup,
Redis/Celery transport failure, browser requests targeting an internal hostname, storage not being
shared or retained, and containers appearing ready when dependencies have failed.

Mitigations are focused settings tests, health-gated Compose dependencies, a one-shot migration
service with a bounded retry policy, same-origin Nginx proxying, named database/application-storage
volumes, backend/worker configuration reuse, complete backend and frontend regression suites, and
live integration checks recorded in `test-results.md`.

This change does not deploy externally, invoke real providers, store real personal/financial data,
or claim production readiness.
