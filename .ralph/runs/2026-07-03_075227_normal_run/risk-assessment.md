# Risk Assessment

Risk level: High

- Selected slice: 002B2-auth-hardening-jwt-library-and-packaging
- Mode: normal_run
- Manual review required: Yes, because this touches authentication token verification.

## Risks
- Auth token handling changed from custom HMAC verification to PyJWT verification. This is the intended security improvement, but it affects login/refresh/logout token paths.
- Local backend tests could not execute after the change because `PyJWT` is pinned but not installed in the sandbox venv.
- Local frontend gates could not execute because frontend dependencies are not installed in `node_modules`.

## Mitigations
- Preserved the existing claim set and configured token lifetimes.
- Preserved refresh token hash storage, rotation, replay rejection, logout revocation, and existing endpoint response envelopes.
- Added regression coverage for environment secret loading, wrong-secret rejection, and expired access-token rejection.
- Verified statically that no `hmac` references remain under `sfpcl_credit/identity/`.
- Recorded the missing dependency condition in final summary and handoff for orchestrator validation.

## Protected Paths
No protected files were edited. `docs/source/**`, scripts, config guardrails, and policy files were left unchanged.
