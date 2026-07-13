# Risk Assessment

Risk level: High

- Selected slice: `007N-register-matrix-settings-contract-and-browser-closure`.
- Mode: normal_run. Standing owner approval applies; no 007N veto is recorded.
- Primary risks: client-derived approval authority drifting from the routing configuration,
  duplicated auth/error handling disclosing stale rows after permission loss, sidebar/direct-route
  permission drift, a policy-screen redesign presenting misleading live values, and register ids
  becoming action/download authority.
- Controls: display authority/count are projected by the configuration owner; all register/matrix
  calls use one shared authenticated envelope/pagination boundary; each panel retains canonical
  permission checks and clears denied data; one navigation manifest serves both consumers; S70
  uses real retained versions in the approved card/field composition; raw-source and behavior tests
  reject duplicate transport, React cardinality rules, fixtures, and inferred download controls.
- Browser risk: the exact six-screenshot Playwright contract collects, and Django/Vite reached
  readiness locally, but Chromium was denied its macOS Mach port by the sandbox. No screenshots
  were fabricated. The orchestrator's required two trusted browser runs are authoritative.
- Residual risk: S72 says `active` while §16.2/§26.3 use `approved` and define no activation route.
  A-095 records the conflict for 008A/008B; no lifecycle business rule was invented in this slice.
- No schema migration, dependency, external service, communication, deployment, or financial write
  was introduced.
