# Report Export Evidence

## Lifecycle API Examples

The implemented collection accepts:

```http
POST /api/v1/reports/exports/
Authorization: Bearer <access-token>
Idempotency-Key: register-export-1
Content-Type: application/json

{
  "report_code": "application-pipeline",
  "format": "csv",
  "filters": {
    "from_date": "2026-04-01",
    "to_date": "2026-06-30"
  }
}
```

The first request and a key-order-varied replay return the same job:

```json
{
  "success": true,
  "data": {
    "export_job_id": "<uuid>",
    "report_code": "application-pipeline",
    "format": "csv",
    "filters": {
      "from_date": "2026-04-01",
      "to_date": "2026-06-30"
    },
    "status": "queued",
    "failure_code": null,
    "idempotency_replayed": false
  }
}
```

The replay changes only `idempotency_replayed` to `true`. Status can expose
`queued`, `running`, `completed`, or `failed`. Completed status includes checksum, size, and a
short-lived application capability; it never exposes the storage key:

```json
{
  "export_job_id": "<uuid>",
  "status": "completed",
  "checksum_sha256": "<64 lowercase hex characters>",
  "file_size_bytes": "<positive integer>",
  "download_url": "/api/v1/reports/exports/<uuid>/download/?token=<signed-capability>",
  "expires_at": "<UTC timestamp>"
}
```

Failed status contains a stable code such as `STORAGE_ERROR` and no exception text or download
URL. Expired completed status retains lifecycle/checksum evidence, returns
`download_expired: true`, and returns no grant. Unknown jobs are `404`; absent authentication is
`401`; absent read/export authority is `403`; malformed report/format/filter/key inputs are the
standard `400 VALIDATION_ERROR`.

## Supported Format Matrix

| Report set | CSV | XLSX | PDF | JSON |
|---|---:|---:|---:|---:|
| Every runnable selector in the 012A registry | yes | yes | yes | yes |
| Restricted `audit-log-export` handoff | no | no | no | no |

Each file includes report code, generated-by user ID, generated-at UTC time, canonical applied
filters, and the exact selector rows. The file-level test parses CSV with `csv`, JSON with `json`,
XLSX as its standards-based ZIP/XML worksheet, and PDF with `pypdf`. Every parsed file contains
the same `application-pipeline` row `LR-EXPORT-001`, actor ID, and `from_date=2026-04-01`.
The completed job's SHA-256 is checked against the retained file bytes before download; the
five-worker PostgreSQL test independently recomputes the sole file's checksum and compares it with
the persisted job.

## Idempotency, Concurrency, Retry, and Retention

- Five simultaneous PostgreSQL requests with the same actor/report/filters/format/key return one
  UUID and persist one job.
- A blocked active worker commits `running` before file generation; four simultaneous duplicate
  workers observe `running` and do no generation.
- After completion, five simultaneous retries all return `completed`; the storage directory
  contains exactly one file and its SHA-256 matches the job.
- A storage failure moves the claimed job to terminal `failed` with `STORAGE_ERROR`; retry performs
  no second storage call and no stack/private exception detail reaches status.
- Expiry cleanup removes file bytes only, preserves the completed job/checksum/timestamps, stops
  issuing grants, and causes an old capability to return `410 DOWNLOAD_EXPIRED`.
- Request, denial, failure, and actual download audits contain only job/report/format/outcome/code/
  checksum references. Tests assert that filter/result value `LR-EXPORT-001`, denied filter value
  `2099-12-31`, and raw idempotency key are absent where prohibited.

## Retained Command Evidence

| Evidence | Result | SHA-256 |
|---|---|---|
| `01-request-replay-red.txt` | RED: collection was not implemented (`405`) | `48ae4172ebae8868b842afb394cac6f2c86c5608c652195c1d31e34705701a96` |
| `04-request-replay-green.txt` | GREEN: request/replay test passed | `4e3e5946e9c921331c0e2483cdcc51890d60ce4334017e33620634a5a9cc6c66` |
| `08-format-matrix-red.txt` | RED: JSON received non-JSON bytes | `02848ec5cb15f2ea15b06f60ee61fea07e675c5717f1f09ba28dfd79c2b71dda` |
| `09-format-matrix-green.txt` | GREEN: four parsed/reconciled formats passed | `4905eb6ff4107e13fe7799eb466d08d9b56afad190a624f2eaf83aac8f7005d9` |
| `22-running-lease-red.txt` | RED: worker state remained unobservable `queued` | `0f3e889c2c090526822b07128da3922e4b758a02f5a8f2d58ef82712d6915104` |
| `26-postgresql-final.txt` | GREEN: exact one-test PostgreSQL acceptance passed | `c0d67e943e6baa6048a2ffc1dab16de34cdd8c110bc7c93058df42243f73c30f` |
| `27-focused-export-final.txt` | GREEN: seven export API/service behaviours passed | `9c291e4904eea8158f58d9578a4ec9b702413d15553e49e1d85a3db303ae1ba5` |
| `30-focused-export-post-review.txt` | GREEN: final seven-behaviour rerun after operational settings | `9ebea9b385ded82d285d62bd7cecdda66206873c002cb6d89525a96aaca33434` |
| `33-focused-export-worker-registration.txt` | GREEN: final eight behaviours, including fresh-worker task registration | `af308c0386ad857a77e420b89afe352aa76280acf2eecbef59961414da908074` |
| `21-report-selector-regressions.txt` | GREEN: 33 unchanged 012A selector/catalogue tests passed | `cd2c6d7bfe901d017b51f6dd9d4aee32ec077b532e17a2b959572cee540b8265` |
