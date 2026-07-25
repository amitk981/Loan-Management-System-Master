# Deployment Health Response Examples

These are the exact public response shapes verified by
`sfpcl_credit/tests/test_health_api.py`.

## Liveness — 200

```json
{"status": "live"}
```

The liveness test wraps the request in `assertNumQueries(0)`.

## Readiness — 200

```json
{"status": "ready"}
```

## Readiness — 503 database unavailable

```json
{"status": "not_ready", "reason": "database_unavailable"}
```

The failure-path test raises a synthetic database error containing a password-like
value and proves that value is absent from the response.

## Readiness — 503 migrations pending

```json
{"status": "not_ready", "reason": "migrations_pending"}
```

## Readiness — 503 critical configuration missing

```json
{"status": "not_ready", "reason": "configuration_missing"}
```

Focused result: `terminal-logs/backend-focused-green.log`.

