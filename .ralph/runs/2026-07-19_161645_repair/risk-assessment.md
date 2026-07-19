# Risk Assessment

Risk level: High (inherited from CR-012's cross-stack trusted-evidence boundary)

- Selected slice: CR-012-epic-009-playwright-evidence-is-incomplete
- Mode: repair
- Demonstrated failure: Playwright strict mode rejected an unscoped `Sanctioned` text locator because
  Loan Account 360 legitimately renders both the account-status badge and the sanctioned KPI label.
- Repair scope: one test-only locator is scoped to the exact account heading's header container. No
  backend, API, permission, money, workflow, fixture, production UI, or styling behavior changes.
- Primary residual risk: a full Chromium run cannot execute in the coding sandbox. The orchestrator's
  required two trusted runs must prove that the locator advances the workflow and that all nine
  screenshots and nine unique hashes are produced freshly in each run.
- Regression risk: low for other browser specs because no shared helper or Playwright configuration
  changes were made during repair. The quarantined normal-run implementation is preserved intact.
- Data/security: the retained seed remains doubly guarded and synthetic; this repair adds no data,
  credentials, route fulfilment, token injection, logging, or external communication.
- Protected/forbidden paths: none modified by the repair. `git diff --check`, focused ESLint,
  Playwright collection, and forbidden-stub/auth-injection scans pass.
- Reversal: revert the single locator-scoping line pair if independent validation reveals a different
  DOM boundary; no schema or persisted production state is involved.
- Manual review required: yes, through Ralph's full independent validation and trusted browser gate.
