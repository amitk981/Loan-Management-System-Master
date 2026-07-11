# Trusted Browser Contract

- Spec: `sfpcl-lms/e2e/completeness-workbench.e2e.spec.ts`
- Portable root: required `RALPH_EVIDENCE_DIR`; the spec creates that directory.
- Declared outputs: `queue-detail.png`, `pass.png`, `deficiency.png`, `returned.png`,
  `resolved.png`, `rejected.png`, `denied.png`, `stale.png`, `api-error.png`.
- Interactions: exact pass, return, resolve, and reject bodies; one mutation call each; canonical
  checklist/completeness/deficiency reads after success; one stale call with no retry.
- Failure states: real routed `500 SERVICE_UNAVAILABLE` and `403 OBJECT_ACCESS_DENIED` envelopes.
- Local feedback: Playwright collection passed. The local Chromium attempt stopped at launch with
  `bootstrap_check_in ... Permission denied (1100)`, before page/test execution.
- Acceptance owner: Ralph's independent browser contract runner executes this spec twice outside
  the agent sandbox and collects the screenshots. This file is not a substitute for those runs.
