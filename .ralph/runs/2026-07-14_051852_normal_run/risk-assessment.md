# Risk assessment

Risk: **High**, proceeding under the owner's standing approval.

- Database: one additive migration adds/backfills immutable register JSON and source fields. The
  migration preserves existing rows and makes the generated entry number unique after backfill.
- Authorization: register reads retain existing object-scoped selectors and canonical permissions;
  document metadata does not create an action or download grant.
- Consistency: terminal communication and register generation remain in one transaction. Frozen
  JSON prevents later member/application/appraisal/decision/communication edits from rewriting the
  statutory projection.
- UI: existing table, badge, filter, and pagination patterns are reused. No styling system or new
  dependency was introduced.
- Browser evidence: local Chromium cannot launch because the sandbox denies macOS Mach-port
  rendezvous. No screenshots were fabricated; the declared contract is collected and independent
  validation must run it twice.
- External effects: no deployment, real notification, download, commit, merge, or push was run.

Residual risk is limited to independent browser rendering and production-database migration timing;
the orchestrator's migration and two-run trusted-browser gates are authoritative.
