# Risk Assessment

Risk level: Medium

- Selected slice: 011PC-closure-frontend-wiring
- Mode: normal_run
- Declared slice risk: Medium
- Product diff: 2,000 changed lines including the new focused test and the required design
  assumption; at the configured limit, with no dependency or migration change.
- Primary controls: server readiness and canonical `available_actions` own action eligibility;
  permission checks hide mutations; every write uses a stable idempotency header; NOC and archive
  actions are followed by canonical GET; no client money or prerequisite calculation remains.
- Verification: 10 focused request/action/render tests, 34 reverse-consumer tests, and the full
  477-test frontend suite pass. Lint, typecheck, build, and `git diff --check` pass.
- Browser risk: trusted screenshot acceptance remains unexecuted because Chromium exited during
  launch twice. The exact scenario/output are present and the failure is preserved without
  fabricated evidence.
- Residual integration risk: the prior backend contract has no staff closure collection/detail
  read, no security-return GET, and projects archive creation while NOC/security are pending.
  Reloaded workflows, canonical security-return refetch, and prerequisite-correct archive UI gating
  cannot be completed by this frontend-only slice. This is a High acceptance risk requiring an
  independently selected backend corrective, not an invented client cache or scope expansion.
- Manual review required: yes, specifically for those backend seams and trusted browser evidence.
