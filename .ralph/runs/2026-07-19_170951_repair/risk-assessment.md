# Risk Assessment

Risk level: High (inherited from CR-012)

- Selected slice: CR-012-epic-009-playwright-evidence-is-incomplete
- Mode: repair
- Manual review required: no; independent validation is required before commit.

## Risk Review

- The acceptance flow crosses authentication, SAP, loan-account, disbursement-readiness,
  initiation, CFC authorisation, transfer, advice, and notification boundaries. False-positive
  evidence could conceal a financial workflow defect, so the trusted browser contract must remain
  fail-closed and execute twice.
- This repair changes no production model, API, selector, permission, money rule, workflow rule,
  adapter, component, style, or layout. It only assigns each browser state to an actor already
  authorised by the canonical owner contract.
- The fixture remains isolated behind both `SFPCL_DEBUG=true` and
  `SFPCL_ALLOW_E2E_SEED=true`, uses synthetic data, and is idempotent. No real communication or
  external provider call is made.
- The spec still clears stale evidence, asserts each intended state immediately before capture,
  computes SHA-256 for all nine basenames, and rejects any duplicate hash within a run.
- The residual risk is browser-environment-only: local Chromium is not authoritative in the coding
  sandbox. Ralph's two independent outside-sandbox executions must produce all screenshots and both
  manifests before commit.

## Rollback

The repair is reversible by restoring only the actor sequence and its fixture-scope regression.
No database migration or persisted production state is introduced.
