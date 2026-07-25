# Docker Local Application Stack

This stack is for local development and owner demonstrations with synthetic data. It is not a
production deployment.

## Services

| Service | Purpose |
|---|---|
| `frontend` | Existing React production build served by non-root Nginx on localhost |
| `backend` | Existing Django API served by Gunicorn |
| `postgres` | Local PostgreSQL application database |
| `redis` | Celery broker and result backend |
| `worker` | Celery background work, including communications and report exports |
| `beat` | Scheduled communications dispatch and export cleanup |
| `migrate` | One-shot migrations and optional guarded local demo seed |

PostgreSQL data, Redis data, and document/report-export storage are retained in named Docker
volumes. The backend and worker mount the same application-storage volume.

## Start

From the repository root:

```bash
cp docker.env.example .env.docker.local
docker compose --env-file .env.docker.local up --build -d
docker compose --env-file .env.docker.local ps
```

`.env.docker.local` is ignored by the repository's existing `*.local` rule. The committed example
contains only predictable local values. Do not place production credentials in it.

Open [http://localhost:8080](http://localhost:8080). When the example's guarded seed flag remains
enabled, a local staff login is:

```text
Email: demo.system_admin@sfpcl.example
Password: DemoStaff123!
```

All `demo.*@sfpcl.example` identities are synthetic and the command refuses to seed unless both
development/debug mode and the explicit demo-seed flag are enabled.

## Verify

```bash
curl --fail http://localhost:8080/
curl --fail http://localhost:8080/health/live/
curl --fail http://localhost:8080/health/ready/
curl --fail \
  --header 'Content-Type: application/json' \
  --data '{"email":"demo.system_admin@sfpcl.example","password":"DemoStaff123!"}' \
  http://localhost:8080/api/v1/auth/login/
docker compose --env-file .env.docker.local logs --tail=100 backend worker beat
```

The API and health URLs above travel through Nginx, proving the browser-facing same-origin proxy.
The worker log must show a Redis connection and `ready`; beat must show its scheduler starting
without a missing Redis transport.

## Operate

Status and logs:

```bash
docker compose --env-file .env.docker.local ps
docker compose --env-file .env.docker.local logs --follow backend worker beat
```

Apply migrations again:

```bash
docker compose --env-file .env.docker.local run --rm migrate \
  python sfpcl_credit/manage.py migrate --noinput
```

Run the guarded demo seed explicitly:

```bash
docker compose --env-file .env.docker.local run --rm \
  --env SFPCL_ALLOW_DEMO_SEED=true migrate \
  python sfpcl_credit/manage.py seed_demo_users
```

Stop while retaining data:

```bash
docker compose --env-file .env.docker.local down
```

Reset all local Docker data (destructive):

```bash
docker compose --env-file .env.docker.local down --volumes
```

## Production boundary

This stack deliberately does not claim production readiness. Production still requires unique
secret-store values, TLS/ingress controls, managed or hardened PostgreSQL/Redis, encrypted managed
document storage, provider credentials, monitoring and alerting, backups and restore exercises,
network policy, vulnerability/image scanning, immutable image promotion, staging soak evidence,
capacity evidence, disaster recovery, and business/security signoff.
