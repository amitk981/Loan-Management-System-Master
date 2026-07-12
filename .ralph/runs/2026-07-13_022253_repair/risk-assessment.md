# Risk Assessment

Risk level: High (inherited slice classification); repair delta is test-only and Low risk.

- Selected slice: 006Z8-portal-limit-provenance-module-and-interaction-closure
- Mode: repair
- Change: one Playwright navigation action; no production/backend/data/API change.
- Primary risk: a synchronous native click could mask a genuinely absent navigation handler.
- Mitigation: the control must first be visible, the click executes the real React handler, and the
  test then requires the routed `New Loan Application` screen plus all server-projection assertions.
- Residual risk: local Chromium cannot execute inside the sandbox. The two independent trusted runs
  and four non-empty screenshots remain the authoritative residual-risk gate.
- Protected files, source documents, dependencies, migrations, and styling are unchanged.
