# Risk Assessment

Risk level: High (inherited from CR-012)

- Selected slice: CR-012-epic-009-playwright-evidence-is-incomplete
- Mode: repair
- Change boundary: one Playwright chronology derivation/assertion on top of the preserved CR
  implementation; no production code or schema change in this repair.
- Financial/workflow risk: the browser proof executes real initiation, CFC authorisation, transfer,
  account activation, and advice availability. The repair does not weaken any money, permission,
  state, idempotency, or chronological validation.
- Data risk: fixture data remains synthetic, isolated, double-guarded, and idempotent. No real personal
  or financial data is used.
- Security risk: real form login remains required. Owned auth, Loan Account, and disbursement APIs are
  not intercepted or fulfilled in the browser.
- Evidence risk: local Chrome cannot launch inside the sandbox. Ralph must run the exact declared spec
  twice, freshly produce nine PNGs per run, and validate nine distinct hashes before acceptance.
- Rollback: revert the spec-only timestamp derivation/assertion from this repair; the preserved CR
  implementation remains independently reviewable.
- Residual risk: if the outside-sandbox run reveals a different real-boundary product defect, validation
  must fail closed rather than changing product rules within this evidence repair.
