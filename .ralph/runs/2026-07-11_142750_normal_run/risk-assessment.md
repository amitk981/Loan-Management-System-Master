# Risk Assessment

Risk level: High.

- Selected slice: 005FA3-portal-auth-interaction-and-demo-flag-proof
- Mode: normal_run
- Standing approval: active; no owner veto exists.
- Auth impact: the only production change removes native `required` interception from the two
  portal credential inputs so the existing component validation message can render. The form still
  requires both values before its sole `onSubmitLogin` callback and adds no bypass or fallback.
- Permission/session impact: no permission mapping or backend session code changed. New rendered
  tests prove protected content is absent pre-login and local auth is cleared after failed logout.
- Demo impact: no demo production behavior changed. Isolated tests prove only the existing staff
  demo controls appear when `VITE_ENABLE_DEMO_AUTH=true`; unset/false remains closed.
- Residual risk: sandbox policy denied Playwright web-server startup, so real-browser assertions and
  the required validation screenshot await independent orchestrator execution. Failure evidence is
  saved; no visual evidence was fabricated.
- Protected/source paths: untouched.
