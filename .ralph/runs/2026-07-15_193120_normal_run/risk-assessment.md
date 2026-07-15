# Risk Assessment

Risk level: High

- Selected slice: 008L4-portal-production-boundary-and-browser-proof
- Mode: normal_run
- Standing approval: confirmed in `docs/working/HIGH_RISK_APPROVALS.md`; no revocation applies.

## Risk surface

- Authenticated borrower document upload/download authority and nondisclosing denials changed.
- Current published legal-document selection moved from a checklist pointer to the canonical latest
  renderer and now shares the application/checklist lock used by projection and upload.
- Retained audit vocabulary changed from generic document events to the source-defined single
  portal events; incorrect metadata or duplicate writes would damage the compliance ledger.
- Deficiency response state now derives from immutable workflow evidence and remains separate from
  staff-owned deficiency resolution.
- The browser harness creates a deterministic sanctioned fixture and handles real protected files.

## Controls and residual risk

- Every writer is transactional and fail-closed; application/checklist/current rows are locked in a
  consistent order. PostgreSQL-only threaded tests cover completion/upload and generation/content
  serialization; SQLite collects and skips them because it cannot prove row-lock semantics.
- Signed capabilities bind portal account, member, application, action, current loan document, and
  file. Tamper, expiry, replacement, cross-action, and cross-scope reads retain no success audit.
- The central audit writer injects the true document id and writes exactly one event; tests reject
  generic duplicates and checksum/storage disclosure.
- The E2E seed requires both debug and explicit seed guards, uses an isolated database/storage root,
  is idempotent, and creates no bank-verification decision.
- Residual browser risk remains until the orchestrator runs both specs twice outside the sandbox and
  verifies all four screenshots. Local Chromium failed before execution on the expected macOS
  Mach-port permission denial; screenshots were not fabricated.
- No schema migration, dependency, external network call, or production deployment is included.
