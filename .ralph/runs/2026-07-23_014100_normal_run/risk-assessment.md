# Risk Assessment

Risk level: Medium (slice-declared), with schema and scheduler concurrency sensitivity.

- Persistence: one initial compliance migration; uniqueness/check constraints cover control/period,
  maker-checker, review status, financial-year/state, and version identity.
- Concurrency: tasks and notification pointers are database-unique/locked; the exact one-test
  PostgreSQL race class is present for Ralph's authoritative capability gate.
- Authority: mutations require exact permissions and owner/reviewer scope; list results are scoped.
- Evidence: restricted files remain document-owned, cross-owner references retain validated source
  identity/period, accepted reviews are immutable through the public interface, and access is audited.
- Residual: the R7 catalogue is source-mapped rather than auto-created because production assignee,
  reviewer, and statutory due-date facts are not source-defined; controls must be provisioned explicitly.
