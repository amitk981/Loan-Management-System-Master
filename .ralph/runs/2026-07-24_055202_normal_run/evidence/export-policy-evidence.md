# Export Policy Evidence

Run: `2026-07-24_055202_normal_run`

## Permission and Classification Matrix

| Decision | Required authority | Classification/scope | Result |
|---|---|---|---|
| Ordinary report read | Owning report read permission and canonical object/team scope | Report selector | Unchanged paginated read; no export authority |
| Masked export request | Owning report read + `reports.export` | Central report classification plus selector scope | Permitted selector columns only; sensitive families masked |
| Unmasked export request | Owning report read + `reports.export` + `reports.export_sensitive` + safe nonblank reason | Same classification/scope, frozen authority snapshot | Permitted sensitive values may be emitted |
| Bulk KYC unmasked export | Same request, but source highest authority unresolved | Restricted | Denied; no role/authority invented |
| Audit-log export | Would require audit read + `audit.export` and later 012D selector | Restricted | Unavailable; `audit.export` exists with no role grant |
| Recovery export | Owning read/scope + export authority | Critical Restricted | Default masked and independently re-authorised |

Every current exportable report code is present in the central classification map.
Unlisted source classifications use the conservative A-172 mapping recorded in
`docs/working/ASSUMPTIONS.md`; this mapping grants no access.

## Parsed Format Evidence

`test_requested_columns_mask_all_sensitive_families_in_every_format` parses CSV, JSON, XLSX,
and PDF output and proves:

- PAN becomes `ABCDE****F`.
- Aadhaar becomes `********9012`.
- Bank account and BO account become `************3456`.
- Cheque becomes `******78`.
- A server-absent requested column is omitted.
- No raw sensitive fixture value survives.

`test_unmasked_export_requires_separate_authority_and_safe_reason_audit` parses the same four
formats and proves all five raw families appear only when the exact sensitive permission and safe
reason are present. It also proves the job stores a 64-character reason digest rather than reason
text. The retained output is
`terminal-logs/authorised-sensitive-all-formats.log`; file bytes are deliberately ephemeral and
are not committed.

## Denial, Expiry, and Scope Evidence

`test_status_and_download_recheck_revocation_expiry_and_actor_ownership` proves:

| Attempt | HTTP result | Sanitised audit reason |
|---|---:|---|
| Tampered signed capability | 410 | `invalid_or_expired_grant` |
| Permission revoked after grant | 403 | `permission_or_scope_revoked` |
| Retention expired | 410 | `expired` |
| Cross-user/guessed job identity | 404 | `not_owner_or_unknown` |

The test also proves status and byte delivery re-run the current owning report selector, so current
object/team scope remains authoritative. `test_idempotency_replay_cannot_cross_masking_or_column_policy`
proves a key bound to sensitive output cannot be replayed as a masked or different-column request.

## Immutable Sanitised Audit Evidence

Focused tests prove the following append-only action rows:

- `report.export.requested`
- `report.export.denied`
- `report.export.sensitive_granted`
- `report.export.generated`
- `report.export.failed`
- `report.export.downloaded`
- `report.export.access_denied`
- `report.export.rate_limited`

Rows contain job/report/format/classification, permitted/requested column names, masking decision,
safe authority snapshot, safe reason or reason digest where applicable, outcome, and checksums.
They contain no exported rows, filter values, raw sensitive values, idempotency keys, storage keys,
or signed tokens. `terminal-logs/no-secret-scan.log` confirms production export paths and retained
evidence contain none of the raw sensitive fixtures.

## Test Evidence Index

- RED/GREEN cycles: `terminal-logs/red-*.log`, `terminal-logs/green-*.log`
- Final focused export module: `terminal-logs/final-focused-report-exports.log` — 15 tests green
- Adjacent reports/catalogue/audit/download: `terminal-logs/impacted-reverse-consumers.log` —
  78 tests green
- Existing PAN/Aadhaar/BO-account/cheque reveal audits:
  `terminal-logs/reverse-sensitive-reveal.log` — 4 tests green
- Django system check: `terminal-logs/backend-check.log`
- Migration sync: `terminal-logs/migrations-check.log`
- No-secret scan: `terminal-logs/no-secret-scan.log`
