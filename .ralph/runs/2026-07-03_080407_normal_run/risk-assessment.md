# Risk Assessment

Risk level: High

- Selected slice: 002B2-auth-hardening-jwt-library-and-packaging
- Mode: normal_run
- Manual review required: normal Ralph review only; all configured gates passed.

## Why High
- This slice changes authentication token signing and verification.
- A mistake could invalidate sessions incorrectly or accept forged tokens.
- A new backend security dependency was pinned.

## Risk Controls Applied
- Replaced custom HMAC JWT encode/decode with the maintained PyJWT library using HS256.
- Preserved the existing auth API fields for login, refresh, and logout.
- Preserved refresh-session storage as SHA-256 token hashes, refresh rotation, replay rejection, logout revocation, inactive-user rejection, and audit logging.
- Added tests for `SFPCL_SECRET_KEY` environment configuration, wrong-secret refresh-token rejection, and expired access-token rejection.
- Verified PyJWT import/version and no remaining `hmac` usage under `sfpcl_credit/identity/`.

## Residual Risk
- Existing access-token validation is only exercised through the shared decoder because `/api/v1/auth/me/` is not implemented until 002D.
- Production secret management remains outside this slice; the code supports `SFPCL_SECRET_KEY` with a local-dev fallback.
