# Risk Assessment — 002EYA

## Risk Level
Medium.

## Changes
- Guarded `seed_e2e_users` behind explicit local/E2E flags: `SFPCL_DEBUG=true` and `SFPCL_ALLOW_E2E_SEED=true`.
- Updated Playwright web-server config to require `E2E_DJANGO_PYTHON` and pass the seed flag only for the isolated E2E sqlite database.
- Documented that deterministic E2E credentials are not production seed data.
- Confirmed the six expected Playwright snapshot PNGs are tracked.

## Risks and Mitigations
- Known-password E2E users: mitigated by runtime guard and isolated `SFPCL_DB_PATH`.
- Wrong backend interpreter in E2E: mitigated by fail-fast config error when `E2E_DJANGO_PYTHON` is unset.
- Visual-regression proof cannot complete in this sandbox: local run with the required interpreter is blocked by `EPERM`; evidence is saved, and non-E2E gates are green.

## Protected Paths
No protected files or `docs/source/**` were modified.
