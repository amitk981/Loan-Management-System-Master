# Risk Assessment

Risk level: Medium (slice declaration).

- Selected slice: CR-006-register-date-time-timezone-determinism
- Mode: normal_run
- Production delta: one explicit `Intl.DateTimeFormat` timezone option and one public rendered-UI
  assertion.
- Data/API impact: none; UTC storage and ISO API values remain unchanged.
- Authorization/audit impact: none.
- UI-design impact: none; layout, typography, colours, spacing, and components are unchanged.
- Blast radius: the local shared formatter affects S23/S25 approval-action timestamps and a sent
  sanction communication timestamp when present, all of which require business-time display.
- Primary regression risk: an invalid or unavailable IANA timezone could break formatting. The
  standard `Asia/Kolkata` identifier is exercised by both focused host environments, the full
  browser-like jsdom suite, typecheck, lint, and production build.
- Rollback: revert the formatter option and regression assertion; no migration or stored-data
  rollback exists.
- Manual review required: no beyond independent orchestrator validation and normal staging CI.
