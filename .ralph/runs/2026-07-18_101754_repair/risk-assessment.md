# Risk Assessment

Risk level: High inherited slice risk; Low incremental repair risk

- Selected slice: 009G4-legal-checklist-migration-ownership-anchor
- Mode: repair
- Demonstrated failure: the retained pre-credit-ownership migration projection included the new
  current legal leaf, whose dependencies pulled `credit.0001` into a registry intended to stop at
  `applications.0010`; both historical fixture cases failed before creating rows.
- Repair scope: one test-only app-label exclusion and its explanatory comment. No production model,
  migration, schema, data, API, permission, checklist, aggregate, frontend, dependency, or external
  service changed.
- Regression risk: low. The exclusion matches the test's existing pattern for downstream ownership
  leaves and is verified against both forward and reverse ownership moves plus four adjacent
  migration boundaries.
- Controls passed: exact red/green reproduction, two repeat class runs, 15 impacted migration tests,
  Django check, migration sync, Python compilation, graph diagnosis, whitespace, protected-path,
  and debug-marker review.
- Residual risk: the complete 1,134-test coverage run is intentionally delegated to the independent
  orchestrator. No manual approval is required under the standing High-risk approval.
