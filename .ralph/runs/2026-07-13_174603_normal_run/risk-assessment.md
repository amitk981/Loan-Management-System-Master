# Risk Assessment

Risk level: Medium (slice-declared), with High/Critical control sensitivity.

- Approval and exception records affect sanction authority and immutable audit history.
- `approvals.exception.create` is Critical; it is granted to Credit Manager solely so the existing
  permission-gated case-enrichment system path can generate the row. There is no manual mutation API.
- Register reads require a dedicated permission and canonical approval-case object scope before
  count/pagination, preventing unused committee candidates from learning rows or counts.
- Entry status changes share the locked approval-action transaction. Denied/conflicted writes are
  zero-mutation; returned/conflict-blocked status handling follows the bounded source vocabulary.
- One migration adds a source-backed table and constraints; its cross-app dependency was narrowed
  to the earliest actual LoanApplication state after a full-suite migration regression exposed it.
- No external calls, deployments, protected-file edits, new dependencies, or frontend changes.
- Standing owner approval applies; no veto exists. Independent Standards and Spec reviews completed,
  and all substantive spec findings were repaired before final gates.
