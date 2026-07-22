# Risk Assessment

Risk level: Low

- Selected slice: 010O-header-notification-summary-wiring
- Mode: normal_run
- Change surface: one existing header component, one additive list-client query option, focused
  component/API tests, and the slice-owned Playwright spec. No backend, schema, permission, route,
  dependency, or API-contract change.
- Data/security: the header requests the existing current-user, permission-scoped unread inbox and
  does not build a client-side index or expose new fields. Unauthorized/error paths clear the list.
- Concurrency: mark-read sends the backend-owned `read_state_version`; `409 STALE_WRITE` reloads
  canonical unread truth and does not retry the mutation.
- Visual risk: existing header/dropdown classes, colours, typography, spacing, and row patterns are
  reused. The unsupported hard-coded “Mark all read” affordance was removed; each real row exposes
  the existing versioned action.
- Regression risk: final source regression prevents mock rows returning. All 411 frontend tests,
  typecheck, lint, build, Django check, and migration sync are green.
- Independent-validation item: local trusted-browser execution was blocked twice by the configured
  system Chrome aborting before page creation. The exact spec and both diagnostics are retained; no
  screenshots were fabricated. Trusted validation must rerun browser acceptance and create the
  three declared images before accepting the candidate.
