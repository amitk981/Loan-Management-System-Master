# Review Packet: 2026-07-24_055202_normal_run

## Result
Ready for independent validation

## Slice
012C-export-masking-and-permission-checks

## Outcome

Implemented one central export-policy module used before queueing, before file creation, and during
status/download access. It independently enforces report read/object scope, `reports.export`,
selector-owned columns, classification, sensitive authority/reason, default masking, actor
ownership, current scope, retention, and signed capability validity.

The API remains compatible with 012B and adds optional `columns` and `sensitive_reason`.
`reports.export_sensitive` and `audit.export` are Critical and have no role grants. Bulk KYC
unmasking and audit-log export remain fail closed.

## Source Traceability

- The source doc says screen read does not imply export and `reports.export` is required
  (`security-privacy.md` §32.1-32.2; `auth-permissions.md` §33). The code independently checks the
  owning selector and general export permission at request, generation, status, and download;
  verified by `test_export_permission_denial_is_audited_without_filter_values` and
  `test_status_and_download_recheck_revocation_expiry_and_actor_ownership`.
- The source doc says PAN, Aadhaar, bank, cheque, and BO account values are masked by default and
  sensitive export requires `reports.export_sensitive` plus a reason (`security-privacy.md`
  §§14.3-14.4/32.2). The code projects all renderer rows through the central policy and uses safe
  reason validation; verified in all four formats by
  `test_requested_columns_mask_all_sensitive_families_in_every_format` and
  `test_unmasked_export_requires_separate_authority_and_safe_reason_audit`.
- The source doc says only permitted columns may be emitted (`security-privacy.md` §32.2). The code
  intersects requested columns with actual server selector columns before rendering; verified by
  the forbidden-column assertion in the masking test.
- The source doc says export links expire and request/download are audited
  (`product-requirements.md` §11.31; `test-plan.md` §22.2). The code rechecks authority at byte
  delivery, audits expiry/revocation/tampering/cross-user denial, and preserves 012B retention;
  verified by the access-recheck and expired-cleanup tests.
- The source doc says audit data must be immutable and sanitised (`security-privacy.md` §24). The
  code records request, denial, sensitive grant, generation success/failure, download, denied
  access, and rate limit without rows or raw values; verified by audit assertions and
  `evidence/terminal-logs/no-secret-scan.log`.

## Standards Review

- Backend behavior is concentrated behind a deep central policy interface; views remain transport
  adapters and selectors remain object-scope owners.
- Tests exercise public request/status/download/file/audit behavior and follow retained RED/GREEN
  cycles.
- The additive migration is in sync and no new dependency was introduced.
- Protected/source paths, orchestrator-owned state/progress/status/handoff facts, and frontend
  files were not edited.
- The commit-range `review` skill was inapplicable because Ralph requires an uncommitted candidate;
  a bounded `git diff HEAD` standards/spec review found no unresolved correctness issue.

## Evidence

- `evidence/export-policy-evidence.md`
- `evidence/terminal-logs/red-*.log` and `green-*.log`
- `evidence/terminal-logs/final-focused-report-exports.log`
- `evidence/terminal-logs/impacted-reverse-consumers.log`
- `evidence/terminal-logs/reverse-sensitive-reveal.log`
- `evidence/terminal-logs/backend-check.log`
- `evidence/terminal-logs/migrations-check.log`
- `evidence/terminal-logs/no-secret-scan.log`

## Unresolved Decision

A-172 records conservative classifications for current reports not named in source §32.3.
Governance should confirm them prospectively; this does not block independent validation because
the mapping grants no access and applies at least Confidential protection.

## Recommended Next Action
Run the Ralph High-risk independent backend validation and coverage lane. Commit only if every
orchestrator-owned gate passes.
