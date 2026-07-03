# Risk Assessment

Run ID: 2026-07-03_071656_repair
Slice: 002B2-auth-hardening-jwt-library-and-packaging
Risk level: High

## Why High Risk
- Authentication token signing and verification are security-critical.
- A new backend dependency was added.
- Secret-key configuration changed from source-only to environment-variable-first.

## Controls Applied
- High-risk standing approval checked in `docs/working/HIGH_RISK_APPROVALS.md`; no veto exists for this slice.
- Dependency checked against `docs/working/DEPENDENCY_POLICY.md`; PyJWT is pre-approved and pinned as `PyJWT==2.10.1`.
- TDD evidence saved:
  - Red: `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/auth-tests-red.log`
  - Green: `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/auth-tests-green.log`
- Existing login, refresh rotation/replay rejection, logout revocation, inactive-user, and audit tests still pass.
- New regression tests cover wrong-secret token rejection and expired access-token rejection.
- `grep -R "hmac" sfpcl_credit/identity/` reports no matches.
- No frontend product code changed.

## Residual Risk
- The fresh repair worktree did not have Python or Node dependencies installed by default. Backend gates were run with `arch -arm64 /usr/local/bin/python3.11` because `/usr/bin/python3` lacks Django and the non-arm64 Python path cannot import PyJWT due to a broken optional `cryptography/cffi` wheel. Frontend dependencies were installed with `npm --prefix sfpcl-lms ci --prefer-offline --no-audit`.
- npm reports React Router 7 expects Node >=20 while this environment is Node 18.20.4. Existing frontend typecheck, tests, and build still pass.
- Commit may be blocked by sandbox write restrictions on `.git/worktrees/*/index.lock`; do not mark a commit created unless git confirms it.

## Decision
Proceed. The implementation removes hand-rolled token signing, keeps the existing auth API envelope and session behavior, and passes the configured gates in the available local environment.
