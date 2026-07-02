# Dependency Policy

Up to `limits.max_new_dependencies` (see `.ralph/config.yaml`) new packages may be added per run, but only from the pre-approved list below. Never hand-roll a replacement for security-critical functionality (cryptography, token signing, password hashing, SQL) because a library is not yet installed — request the library instead. A hand-rolled substitute is always worse than stopping the run.

## Pre-approved packages

Backend (add to `sfpcl_credit/requirements.txt`, pinned):
- Django, djangorestframework, djangorestframework-simplejwt, PyJWT
- psycopg[binary], python-dotenv, gunicorn, whitenoise
- pytest, pytest-django

Frontend (add to `sfpcl-lms/package.json`, dev dependencies unless noted):
- vitest, @testing-library/react, @testing-library/jest-dom, jsdom
- eslint and @typescript-eslint packages (when the lint gate is introduced)

## Rules for any addition
- Pin the version (`package==x.y.z` / lockfile entry).
- Record the reason in the run's final summary.
- Anything not on the list requires an entry in `docs/working/HIGH_RISK_APPROVALS.md` or explicit human approval in the slice file.
- Large frameworks, payment libraries, or production infrastructure packages always require human review.
