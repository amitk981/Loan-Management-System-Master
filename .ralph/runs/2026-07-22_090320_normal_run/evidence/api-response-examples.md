# Default Case API Response Examples

Representative values are synthetic and contain no personal or financial fixture data.

## Successful open

```json
{
  "success": true,
  "data": {
    "default_case_id": "00000000-0000-4000-8000-000000000011",
    "default_case_status": "grace_period_active",
    "grace_period_start_date": "2026-06-22",
    "grace_period_end_date": "2026-09-22",
    "available_actions": []
  },
  "meta": {
    "request_id": "example-request",
    "timestamp": "2026-07-22T04:00:00Z",
    "api_version": "v1"
  }
}
```

## Fully allocated obligation

```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "The scheduled principal obligation is not missed.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": "example-request",
    "timestamp": "2026-07-22T04:00:00Z",
    "api_version": "v1"
  }
}
```
