# Risk Assessment

Risk level: High

- Selected slice: CR-012-epic-009-playwright-evidence-is-incomplete
- Mode: repair
- Standing approval: present; no CR-012 revocation is recorded.

## Risk analysis

- The browser proof crosses authentication, loan-account reads, readiness, initiation, CFC
  authorisation, transfer success, activation, advice availability, and a genuine safe error.
- The fixture command remains guarded by both `SFPCL_DEBUG=true` and
  `SFPCL_ALLOW_E2E_SEED=true`, uses an isolated database, and creates only synthetic actors/files.
- The added Senior Finance transfer grant exists only in the guarded E2E fixture. It exercises the
  production owner rule that an authorised initiating Senior Finance actor may record transfer;
  no production role catalogue or permission assignment changed.
- The CFC assertion now uses stable truth: a genuine HTTP 200 approved response followed by the
  pending-only queue's empty state. Transfer acceptance likewise uses the genuine response and
  stable successful/active projection rather than a transient alert.
- No production UI, styling, API shape, model, migration, dependency, money rule, workflow owner,
  external communication, real personal data, or real financial data changed.
- Residual risk is the outside-sandbox browser execution. Ralph mitigates it by clearing stale
  evidence and executing the exact nine-screenshot/hash contract twice before any commit.

## Outcome

Ready for independent validation. Do not commit unless both trusted browser runs retain nine valid,
pairwise-distinct screenshots and deterministic manifests and the complete backend coverage gate
passes.
