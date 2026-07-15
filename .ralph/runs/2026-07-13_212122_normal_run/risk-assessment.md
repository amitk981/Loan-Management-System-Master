# Risk Assessment

Risk level: High

- Selected slice: `007G2-general-meeting-current-evidence-and-document-scope-closure`
- Standing approval: active; no owner veto exists.
- Sensitive surfaces: Critical General Meeting record permission, legal document references,
  approval-case object scope, immutable sanction-cycle evidence, and the final sanction gate.
- Main risks: cross-application document disclosure, audit-only scope widening, historical evidence
  rewriting, gate-priority regression, exception-register mutation on denial, and hidden download
  authority/audit creation.
- Controls implemented: documents-owned typed reference context; exact public-upload application
  provenance; source §19.4 legal audience/category and sensitivity integrity; canonical case scope;
  per-field nondisclosing failures; atomic zero-write assertions; immutable case FK freezing for
  reject/return/conflict-block/final approval; real 007F2 public lifecycle regression.
- Residual risk: document category/relation remains reconstructed from immutable upload audit
  metadata because `DocumentFile` does not yet persist those columns. Missing or contradictory
  metadata fails closed. Future governance may define a narrower sensitivity/category matrix and
  must version the documents-owned policy without rewriting history.
- Database impact: none; migration sync is clean.
- Dependencies: none added.
- Diff limits: 657 tracked lines before Ralph bookkeeping, below 2,000; no protected paths changed.
- Manual review: independent Standards and Spec passes completed with no remaining findings;
  orchestrator independent validation remains required before commit/merge/push.
