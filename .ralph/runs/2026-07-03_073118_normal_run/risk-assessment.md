# Risk Assessment

Risk level: High

- Selected slice: 002B2-auth-hardening-jwt-library-and-packaging
- Mode: normal_run
- Manual review required: yes, because backend runtime gates did not complete in this sandbox.

## Why High
- This slice changes authentication token signing and verification.
- A mistake could invalidate valid sessions, accept forged tokens, or weaken replay/expiry protections.

## Controls Applied
- Used approved dependency `PyJWT` pinned in `sfpcl_credit/requirements.txt`.
- Preserved existing auth endpoint handlers and response envelopes.
- Preserved refresh-token hash storage, rotation, replay rejection, and logout revocation paths.
- Added regression tests for wrong-secret refresh-token rejection and expired access-token rejection.
- Verified no `hmac` references remain under `sfpcl_credit/identity/`.
- Kept `SECRET_KEY` out of source-controlled configuration by reading `SFPCL_SECRET_KEY`, with only the existing local development value as fallback.

## Residual Risk
- Backend tests/checks/migration/coverage gates could not run because Python dependencies are not installed and pip install failed without package-index network access.
- PyJWT behavior is syntax-checked but not runtime-verified in this sandbox.
- The run must be repaired/revalidated before merge.
