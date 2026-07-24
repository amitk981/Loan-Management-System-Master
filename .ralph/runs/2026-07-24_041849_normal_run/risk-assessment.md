# Risk Assessment

Risk level: Medium

- Selected slice: 012B-register-exports
- Mode: normal_run
- Manual review required: independent validation per Ralph.

## Scope and Change Risk

- Adds one non-destructive `report_export_jobs` table and registers the existing reports package as
  a Django app. No business-domain row or source selector is rewritten.
- Adds one public request/status seam plus a signed application download capability. The storage
  adapter never returns its permanent key.
- Adds a Celery worker and bounded cleanup task; both wrappers delegate to the report-export
  module.
- Reuses every 012A selector and its current object/read permission. `reports.export` is an
  additional required permission; `audit-log-export` remains default-denied for 012C/012D.

## Principal Risks and Mitigations

| Risk | Mitigation and evidence |
|---|---|
| Duplicate jobs/files under request or worker races | Composite database uniqueness, PostgreSQL row claims, five-minute leases, deterministic storage keys, and the exact five-request/five-worker acceptance leave one job/file/checksum. |
| `running` is not observable or a crashed worker is stranded | Claim state commits before generation; active claims deduplicate; expired leases may be resumed. PostgreSQL acceptance observes `running` while storage is blocked. |
| Export diverges from live report scope/filters | Request and status recheck the owning selector; workers paginate that same selector to exhaustion. Four parsed formats reconcile to the same fixture row and canonical filter. |
| Permanent/raw URL or stale file exposure | Signed actor/job capability, current permission recheck, 15-minute grant, 24-hour retention, checksum/size verification, and hourly cleanup. Expiry and old-grant negatives are green. |
| Sensitive/audit data bypasses later policy | The registry's selector-less `audit-log-export` is unsupported. This slice exports only the already masked/scoped 012A selector projections. 012C remains owner of sensitive reason/unmasking policy. |
| Exception/filter/result leakage through audit/status | Stable failure codes only; request/download/denial/failure audits carry references and outcomes, not rows. Negative tests assert representative values and raw idempotency keys are absent. |
| Migration or report regression | `manage.py check`, `makemigrations --check --dry-run`, eight focused export tests, 33 existing report tests, and the exact PostgreSQL acceptance are green. |

## Operational Defaults

Assumptions A-170 and A-171 record the uniform runnable-report format matrix and configurable
five-minute claim / 15-minute grant / 24-hour retention / hourly cleanup defaults. These are
prospective operational policy and do not rewrite retained jobs or files.

## Residual Risk

Independent validation still needs to run the orchestrator-selected backend lane and protected-path/
diff checks. Sensitive unmasking, audit-log export, and frontend progress wiring are intentionally
deferred to 012C/012D/012DA.
