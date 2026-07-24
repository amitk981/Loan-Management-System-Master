# Risk Assessment

Risk level: Medium

- Selected slice: 012E-operational-dashboard-hardening
- Mode: normal_run
- Database/model impact: none; no migration or dependency changes.
- Permission risk: mitigated by server-derived active primary role, dedicated-route context checks,
  owner-read permission filtering, canonical actor/object selectors, and omission when archive team
  scope is unavailable. Caller role overrides and unknown roles are rejected.
- Data leakage risk: cards expose only stable code, label, integer count, and link; borrower/member/
  account values are not serialized. Dashboard reads create no business audit rows.
- Performance risk: Credit is capped at 10 queries and all supported cross-domain role catalogues
  at 24 fixed queries. Counts use aggregates or bounded owner selectors; no source rows are returned.
- Frontend risk: malformed counts fail closed, there is no mock fallback, scoped URLs are preserved
  across role families, and the application destination consumes its dashboard filters.
- Browser evidence risk: all four exact Playwright cases were attempted against the localhost
  servers, but Chromium aborted during launch. No screenshot was fabricated. Per the run contract,
  trusted independent validation must rerun browser acceptance and produce the four PNGs.
- Manual review required: independent validation should confirm the trusted-browser screenshots and
  the orchestrator-selected authoritative backend lane.
