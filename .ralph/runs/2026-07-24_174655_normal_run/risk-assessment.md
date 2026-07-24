# Risk Assessment

Risk level: High

- Selected slice: 012F-security-privacy-regression-checks
- Mode: normal_run
- Database/model impact: none; no migrations.
- Frontend impact: none.
- External side effects: advisory lookups only. The command creates isolated Django test data and
  writes only the explicitly requested JSON output.

## Security-sensitive changes

- Production boot now requires explicit non-local hosts, HTTPS-only CORS/CSRF origins, a
  sufficiently long Django secret, a separate JWT signing secret, dedicated field/lookup secrets,
  HTTPS redirect, secure cookies, HSTS, content-type protection, referrer policy, and frame denial.
  Missing, malformed, reused, local, wildcard, or insecure settings fail during import.
- JWT encoding/decoding uses `SFPCL_JWT_SIGNING_KEY` in production. Development/test settings retain
  the historical Django-secret fallback so existing local sessions and tests remain compatible.
- Required scanner versions are pinned by the lane (`detect-secrets==1.5.0`,
  `pip-audit==2.10.1`, npm `10.8.2`) without adding packages outside the repository dependency
  allowlist. `npm audit` uses the existing lockfile and includes production and development
  dependencies.
- Scanner raw output is hashed and discarded from the machine summary; only scanner identity,
  version, status, error code, finding count, and SHA-256 are retained.

## Fail-closed results

- The real command ran 55 controls: 52 passed and 3 failed as exact product blockers.
- `SEC-AUTH-010`: no executable login throttle/lockout proof.
- `SEC-WEB-004`: public upload filename validation is incomplete.
- `SEC-WEB-005`: executable extension/MIME/content rejection is inconsistent.
- Required scanners did not silently skip. `detect-secrets` and `pip-audit` were unavailable in the
  pre-provisioned agent environment; npm 10.8.2 could not reach the registry advisory endpoint.
  Each produced a failing scanner record and report hash. Independent validation must provision
  the exact externally pinned scanner versions and run with advisory-service access.
- Production-settings positive/negative probes and the no-secret output check passed.

## Residual risk

- The three product findings block security/UAT readiness until normal prepared corrective slices
  implement and independently validate them. They were not repaired inside this test-focused slice.
- A successful advisory scan cannot be claimed from this network-restricted run. The executable
  lane correctly reports that environmental limitation as failure.
- Production deployment must provision the newly required `SFPCL_JWT_SIGNING_KEY` before using
  these settings. Missing rollout configuration intentionally prevents boot.

Manual independent review required: yes, because the slice is High risk and changes production
security configuration and token signing.
