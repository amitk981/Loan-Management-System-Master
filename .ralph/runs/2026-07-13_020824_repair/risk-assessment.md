# Risk Assessment

Risk level: High (selected financial-authority slice); repair delta is browser-test-only.

- Selected slice: 006Z8-portal-limit-provenance-module-and-interaction-closure
- Mode: repair
- Demonstrated failure: both trusted runs timed out waiting for `New Application`; all four declared
  screenshots were absent because the fixture never mounted the authenticated borrower portal.
- Repair: replaced only the E2E storage shortcut with the repository's proven real member-login
  interaction and exact sidebar action. Production code, financial rules, response redaction,
  screenshot names, and the four limit assertions are unchanged.
- Mitigations: four-test collection, full frontend/backend gates, 93% backend coverage, and clean
  diff audit. The existing implementation and run-ahead 007A sharpening were preserved.
- Residual risk: Chromium cannot launch inside the coding sandbox. Ralph must still run the declared
  spec twice and verify all four non-empty screenshots before any commit.
