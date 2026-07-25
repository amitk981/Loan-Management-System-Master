# Risk Assessment

Risk level: Medium

- Selected slice: 012G-critical-e2e-uat-smoke-scenarios
- Mode: repair
- Validation domain: deterministic critical-UAT seed and source-role browser contract.
- Product impact: no production business logic, endpoint, permission policy, schema, migration,
  visual design, or provider behavior changed.
- Financial integrity: the seed uses existing immutable configuration/rate owners and the public
  interest-invoice API; the focused test proves the server-owned FY behavior.
- Permission integrity: invoice generation now runs as the source Accounts role. The additional
  activation permission exists only on the deterministic E2E System Administrator role in the
  guarded local seed database.
- Isolation: `seed_critical_uat_e2e_fixture` remains blocked unless demo surfaces and both explicit
  local E2E guards are enabled. Production-isolation regressions pass.
- Idempotency: the fixture command is executed twice in the focused test; exactly one approved
  rate and one invoice configuration remain.
- Browser evidence: two post-fix local attempts ended before page creation because Chrome closed
  during launch. No screenshot evidence was manufactured; independent trusted validation owns the
  final browser verdict and declared screenshot manifests.
- Manual review required: independent validation must run the trusted browser contract.
