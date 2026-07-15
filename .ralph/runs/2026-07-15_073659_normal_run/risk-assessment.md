# Risk Assessment

Risk level: High

- Selected slice: 008L2-member-portal-deficiency-response-and-resubmission
- Mode: normal_run
- Standing approval: covered by `docs/working/HIGH_RISK_APPROVALS.md`; no revoked entry was found.
- Sensitive boundaries: authenticated borrower scope, document upload/download, immutable evidence,
  application state transition, audit/workflow records, and Stage-4 non-interference.
- Principal risks: cross-member disclosure, unsafe file acceptance, response-history rewriting,
  premature resubmission, and accidental mutation of documentation approval truth.
- Mitigations: active `PortalAccount` scope is the only authority; uploads enforce one file plus
  category/sensitivity/type/size validation; response rows are immutable successor chains; every
  open deficiency requires a current response; focused tests cover nondisclosure, invalid state,
  authenticated content reads, audit evidence, and zero Stage-4 side effects.
- Residual risk: High-impact workflow code remains subject to full independent Ralph validation and
  owner review before promotion from `staging` to `main`.
