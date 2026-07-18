# Active Review Findings

This is the bounded, active architecture-review ledger. Reviews prepend new entries here and keep
only unresolved findings or the most recent closure evidence. The complete historical ledger
through 2026-07-18 is retained unchanged at
`docs/working/archive/REVIEW_FINDINGS-through-2026-07-18.md` and in Git history.

## Review admission and convergence

- Critical/High correctness, security, financial/data-integrity, or binding source-contract
  findings create immediate corrective slices.
- Medium findings are grouped into the owning slice or epic closure. Low findings remain recorded
  unless they naturally combine with higher-severity work.
- Related symptoms are grouped by root owner rather than creating one corrective slice per symptom.
- Every `review-packet.md` reports non-negative integer counts for findings closed, new findings by
  severity, and corrective slices added. Validation checks the reported additions against the
  candidate queue diff.
- Two consecutive reviews with no new Critical/High findings expand routine cadence from four to
  eight completed slices. Any new Critical/High resets cadence to four. Epic boundaries always
  trigger a review.

## Open findings from 2026-07-19_014802_architecture_review

Reviewed product commits: `35dd95ce` (009H9A), `4bdff96c` (009H9B), `9b1113af` (009H9C), and
`4bebe1af` (009I2), relative to the prior reviewed product boundary `e3d965ad`. The chronological
range also contains owner-maintenance commit `4fb0a5af`; it changed Ralph/docs preparation rather
than these product slices and is not attributed to them.

### 009H9D — communications provenance and operator boundary

- **High — incomplete provenance can be promoted:** communications migration 0008 treats required
  snapshot strings as complete when they are merely non-null. A queued row with a blank required
  template fact and a recomputed checksum becomes `verified / frozen_before_dispatch`, contrary to
  009H9A requirement 2. The review probe fails with `verified` instead of `legacy_partial`.
- **High — cross-kind exception authority:** the exception routes accept either generic-send or
  advice-send permission before returning every assigned exception. An assigned advice-only actor
  can read and resolve a generic exception, contrary to the exact job-kind authority documented in
  `API_CONTRACTS.md`; both read and resolution review probes return 200 instead of 403.
- **Medium — exception contract fidelity:** `provider_code` stores a dotted adapter class path
  instead of the source `email`/`sms` provider vocabulary, and the collection hard-codes its first
  100 rows instead of implementing standard pagination. Tests assert field presence but not
  provider semantics or reachability beyond the first batch.
- **Medium — communications boundary/test drift:** the process coordinator reads `Communication`
  to choose Email/SMS adapters and Celery calls underscore-prefixed dispatcher methods even though
  source §40.1 says the communications owner hides channel/adapter selection. A static test checks
  implementation strings while the required cross-channel idempotency behavior has no assertion.
- One root-owner corrective, `009H9D`, covers these related migration, permission, provider,
  pagination, module-boundary, and test-interface symptoms.

### Epic 009 closure — MP14 selection regression evidence

- **Medium:** 009I2 correctly passes the parent-selected application id and the real route selects
  a deterministic application, but its binding test requirement called for two finance-relevant
  applications in opposite list orders. The list test uses one finance-relevant and one returned
  application; the MP14 unit/browser tests request one selected id. Record this edge-coverage gap
  for Epic 009 closure rather than creating another immediate leaf correction.

## Closed in this review

- `009H9B` makes exact-cap stale recovery terminal, singular, fenced, and operator-reviewable; the
  retained tests and twice-run PostgreSQL race evidence cover exact/below/already-exhausted paths.
- `009H9C` separates Email and SMS adapters, rejects unsupported/unsafe channel requests before
  writes, and retains immutable generic provider acceptance with replay reconciliation.
- `009I2` removes client application ranking and consumes the explicit selected application id.
- `009I2` projects independent documentation, SAP, initiation, CFC, transfer, and advice times or
  honest nulls from their current owners.
- `009I2` restores the approved portal composition and supplies the three declared screenshots plus
  two independently passing trusted-browser runs.

## Review evidence

- Focused retained backend suites: 74 tests pass; six PostgreSQL-only races skip locally. The
  accepted slices retain their independent twice-run PostgreSQL evidence.
- Three review-only contract probes fail on the intended assertions: incomplete frozen provenance,
  cross-kind exception read authority, and cross-kind resolution authority.
- Evidence: `.ralph/runs/2026-07-19_014802_architecture_review/evidence/terminal-logs/` and the
  adjacent `evidence/review-probes/review_contract_probes.py`.
- No epic completed in the reviewed range, so no newly completed epic's M##-FR matrix required a
  closure audit. `CONTEXT.md` remains truthful, and no slice is currently marked `Blocked`.

Older findings and exact prior citations remain searchable in the historical ledger; they are not
repeated here unless current code reproduces them.
