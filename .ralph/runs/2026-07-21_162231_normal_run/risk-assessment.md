# Risk Assessment

Risk level: High

- Selected slice: `010MB-interest-and-monitoring-frontend-wiring`
- Standing approval: applicable; no revocation was found.
- Financial correctness: the browser displays backend Money, invoice, accrual, and capitalisation projections without local calculation. Capitalisation posting is disabled unless the preview matches the selected loan, financial year, and date and the backend marks it eligible.
- Authorisation: mutations use exact permission predicates and backend enforcement remains authoritative. DPD and reminders require `monitoring.dpd.read` plus canonical loan-object scope.
- Data disclosure: the scoped reminder read excludes recipient, contacted-person, message, template, and provider-sensitive content; tests verify safe retained delivery/follow-up/call evidence.
- Completeness: the monitoring page consumes one canonical scoped reminder collection independent of current DPD pointers and exhausts every pagination page. Any DPD or reminder failure fails the whole dashboard visibly.
- Replay/concurrency: interest mutations send caller-stable idempotency keys. This slice adds no new high-contention write behavior or schema migration.
- UI drift: existing tabs, banners, single-card compositions, tables, badges, and alerts are retained; fixtures and role-string policy were replaced with canonical projections and permission visibility.
- Browser acceptance: the required four-test Playwright contract collects and names both screenshots, uses real backend login/current-user authority, and has no auth mock. Chromium and the twice-run screenshots are intentionally deferred to the orchestrator's trusted environment.
- Residual risk: the production bundle retains the repository's existing >500 kB chunk warning. Independent complete backend coverage and trusted-browser execution remain authoritative orchestrator gates.

Manual review required: independent validation and the declared trusted-browser gate.
