# Standards axis

- **High — hard authorization violation:** `quarterly_mis.py` returns generation replays after only
  the generate permission, before portfolio-read scope; submission/review replay likewise precedes
  report scope and exact submitted-CFO authority. This violates `CONTEXT.md` backend/current-authority
  direction and the repository CFO MIS contract.
- **High — hard cutoff/owner-seam violation:** 010K rebuilds the snapshot from other owners' private
  live models. A reminder created after cutoff for an older quarter enters historical MIS, invoice
  status is live, and separate READ COMMITTED prefetches can mix concurrent source states. The two
  PostgreSQL tests cover duplicate report generation/review, not source mutation.
- **High — carried reminder root:** serviceability commits before provider execution. Repayment,
  scope, recipient, or template state can change in the unprotected gap; the accepted race class does
  not exercise that boundary.
- **High — carried DPD root:** the DPD source sums allocation/reversal evidence but ignores interest
  capitalisation schedule evidence, reporting already reclassified interest overdue again.

No judgment-only findings.
