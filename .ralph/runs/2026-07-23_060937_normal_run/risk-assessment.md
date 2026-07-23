# Risk Assessment

Risk level: High

- Selected slice: 011M-kyc-re-kyc-compliance-tracker
- Mode: normal_run
- Schema impact: one additive `kyc_reviews` table migration; no destructive or data-rewrite operation.
- Permissions: `compliance.kyc_review.manage` plus canonical member scope for writes; restricted
  Compliance/CFO task readers and Internal Auditor receive safe read-only summaries.
- Compliance/data integrity: cycle identity is derived from the canonical retained verification,
  due dates use exact calendar-year arithmetic, task/review/reminder identities are unique, and
  completion requires newer complete governed KYC evidence.
- Sensitive data: list/audit/scheduler payloads contain identifiers and safe status only. PAN,
  Aadhaar, file content, and recipient addresses are not copied into tracker/audit records. KYC
  document files remain owned by the existing restricted download/reveal controls.
- Communications: requests use approved effective templates and the existing durable dispatcher;
  API state is `queued` until retained provider evidence says `sent` or `failed`.
- Concurrency: the declared PostgreSQL acceptance ran one two-worker scheduler race and retained
  exactly one review, task, and due-reminder identity.
- Residual risk: production must provision approved effective `kyc_rekyc_request_email` and/or
  `kyc_rekyc_request_sms` templates. Missing templates/destinations fail closed (A-164).
- Independent validation: required because this is High risk and changes models, migration,
  routing, compliance permissions, scheduler behavior, and communications integration.
