# Section 41.4 Contract Examples

## Create proposal

`POST /api/v1/config/interest-rates/` with `config.interest_rate.manage`:

```json
{
  "version_number": "RATE-2026-01",
  "rate_type": "floating",
  "effective_rate": "9.2500",
  "effective_from": "2026-08-01",
  "effective_to": null,
  "benchmark_name": null,
  "spread_rate": null,
  "reset_frequency": null,
  "communication_required": true,
  "board_approval_reference": "BOARD-RATE-2026-01"
}
```

Success returns the same governed rate facts plus the server-owned id, `proposed` status, creator,
nullable approver/activation time, and zeroed notice summary. Optional benchmark/spread/reset fields
do not derive or override `effective_rate`.

## Activate

`POST /api/v1/config/interest-rates/{id}/activate/` requires a different maker/checker,
`config.interest_rate.manage`, `communications.communication.send`, and `Idempotency-Key`.
Success freezes the version, records activation/version/audit evidence, resolves the predecessor
period, and atomically creates active-loan history and required notice obligations. Exact replay
returns the retained response. Changed key binding, overlap/history insertion, gap after an explicitly
closed predecessor, or reactivation returns `409 CONFLICT` without partial writes.

## Notice truth

Per affected active floating-rate loan, activation creates one loan-level obligation linked to one
email and one SMS communication. A queued communication is `pending`; only provider-accepted
evidence is `sent`; an exhausted job or missing address is `failed`. The rate response returns
separate obligation/channel aggregate counts only and never contact addresses or message bodies. The
delivery transition exercised in the focused test is
`pending → retrying/pending → sent` for email and `pending → failed` for SMS.

Evidence: `terminal-logs/create-list-red.log`, `terminal-logs/create-list-green.log`,
`terminal-logs/activation-resolution-red.log`, `terminal-logs/activation-resolution-green.log`,
`terminal-logs/notices-red.log`, `terminal-logs/notice-delivery-truth-green.log`, and
`terminal-logs/permission-conflict-matrix.log`.
