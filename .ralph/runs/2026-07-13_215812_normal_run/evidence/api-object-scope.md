# API Object-Scope Evidence

## Sanction decision

- Assigned/original/effective/conflicted/acted or persisted-scope reader +
  `approvals.sanction.read` + approved frozen cycle: `200`, source §25.8 projection.
- Same permission but unrelated case: `403 OBJECT_ACCESS_DENIED`.
- Attributable pending/rejected/returned cycle with no decision: `404 NOT_FOUND`.
- Attributable approved cycle followed by a newer coherent cycle: `200` for the immutable decision
  joined to its frozen terminal `approval_case`; application-latest state is ignored.
- Case scope without `approvals.sanction.read`: `403 FORBIDDEN`.

## Credit Sanction Register

- Canonical approval-case scope is applied before `financial_year`, `decision`, ordering, count,
  page normalization, and serialization.
- Each of two unrelated same-permission Directors receives only their attributable row and
  `total_count: 1`; a page beyond the scoped bound normalizes to page 1.
- An unrelated Director receives `data: []`, `total_count: 0`, and `total_pages: 1`, even though a
  terminal row exists outside their scope.
- Persisted legal/audit/management readers with the separate register permission see their defined
  read-only scope but receive no approval-case action or document authority.
- The real above-limit public case preserves `reasons: "Stored assessment requires exception
  approval."` separately from `exception_reference.business_reason: "Seasonal exception is
  commercially justified."` inside a two-terminal-case scoped page.

## Retained logs

- `terminal-logs/red-sanction-decision-object-scope.txt`
- `terminal-logs/green-sanction-decision-object-scope.txt`
- `terminal-logs/red-register-object-scope-pagination.txt`
- `terminal-logs/green-register-object-scope-pagination.txt`
- `terminal-logs/green-frozen-decision-cycle-scope.txt`
- `terminal-logs/green-above-limit-two-case-scope-matrix.txt`
- `terminal-logs/full-backend-gates-final.txt`
- `terminal-logs/full-frontend-gates.txt`
