# Risk Assessment

Risk level: Medium.

- The change removes misleading client-owned workflow authority; it does not change backend data,
  APIs, permissions, financial rules, or persisted state.
- Blast radius is limited to `App.tsx` and its sole affected prop consumer,
  `SanctionWorkbench`. API-backed application, completeness, and appraisal screens retain their
  own service state.
- The shell now deliberately shows no sanction records until 007I. This is safer than presenting
  plausible mock cases, but users cannot use the prototype sanction queue from the routed app in
  the interim.
- SanctionWorkbench's own optional mock fallback is intentionally retained because the binding
  ownership table assigns its final removal and API wiring to 007I. The shell always passes an
  explicit empty array, so that fallback is not reachable from the production route.
- Regression controls: raw-source boundary assertion, real component static render, full frontend
  gates, full backend suite, and mock-surface audit.
- Residual evidence risk: the sandbox denied the Vite listener and the browser runtime exposed no
  browser backend, so screenshot acceptance is documented but unmet. The exact visual copy and
  absence of mock rows are asserted in rendered component markup.
