# Risk Assessment

Risk level: High

- Selected slice: 002B2-auth-hardening-jwt-library-and-packaging
- Mode: normal_run
- Manual review required: no before autonomous completion; the owner has standing approval with veto controls.

## Risk Drivers
- Authentication token signing and validation are security-sensitive.
- The slice adds one backend dependency, `PyJWT==2.10.1`, from the approved dependency list.
- Login, refresh rotation, replay rejection, and logout revocation contracts must remain stable.

## Controls Applied
- Replaced custom HMAC/base64 JWT signing with PyJWT `jwt.encode` / `jwt.decode` using HS256.
- Kept token claims and lifetimes unchanged.
- Moved `SECRET_KEY` to `SFPCL_SECRET_KEY` with the existing local-dev fallback.
- Added regression tests for wrong-secret refresh rejection and expired access-token rejection.
- Verified no `hmac` references remain under `sfpcl_credit/identity/`.
- Ran backend and frontend quality gates; all passed after installing existing frontend lockfile dependencies.

## Residual Risk
- The local Python 3.11 installation has a broken optional `cryptography` architecture build. PyJWT HS256 does not require it; the implementation retries PyJWT import with that optional package disabled only when its import fails. This is recorded as A-007 in `docs/working/ASSUMPTIONS.md`.
- `/api/v1/auth/me/` is not implemented yet, so expired access-token rejection is tested at the backend token validation seam. The endpoint-level access-token rejection path belongs to 002D.
