# Risk Assessment

Risk level: Medium slice; Low repair delta.

- Selected slice: 012E-operational-dashboard-hardening
- Mode: repair
- Validation domain: trusted browser acceptance only.
- Repair scope: one E2E helper locator changed from substring matching to exact accessible-name
  matching. No production code, API, permission, data, migration, dependency, or design change.
- Regression risk: low. The exact sidebar label remains `Dashboard`; exact matching removes
  ambiguity with buttons such as `Refresh dashboard` while preserving every existing `staffLogin`
  caller's intended readiness condition.
- Evidence risk: the coding-agent sandbox cannot complete macOS Chrome application registration.
  No screenshots were fabricated. The repair-run browser preflight passed outside that sandbox;
  independent validation must still run the exact spec twice and verify all four PNG manifests.
- Manual review required: independent validation must withhold commit if either trusted browser run
  or either screenshot manifest fails.
