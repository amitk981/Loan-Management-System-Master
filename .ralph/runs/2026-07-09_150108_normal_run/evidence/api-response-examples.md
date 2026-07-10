# 004I API Response Examples

## Successful PAN reveal

```json
{
  "success": true,
  "data": {
    "field_name": "pan",
    "value": "ABCDE1234F",
    "expires_at": "2026-06-22T10:35:00Z"
  },
  "meta": {
    "request_id": "req-pan-reveal",
    "timestamp": "2026-06-22T10:30:00Z",
    "api_version": "v1"
  }
}
```

Response headers include:

```text
Cache-Control: no-store
Pragma: no-cache
```

Success audit metadata shape:

```json
{
  "member_id": "member-uuid",
  "field_name": "pan",
  "reason": "KYC verification during loan application",
  "outcome": "success",
  "request_id": "req-pan-reveal",
  "expires_at": "2026-06-22T10:35:00Z"
}
```

## Denied Aadhaar reveal without field permission

```json
{
  "success": false,
  "error": {
    "code": "SENSITIVE_FIELD_ACCESS_DENIED",
    "message": "You do not have permission to reveal this sensitive field.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": "req-denied",
    "timestamp": "2026-06-22T10:30:00Z",
    "api_version": "v1"
  }
}
```

Denied audit metadata shape:

```json
{
  "member_id": "member-uuid",
  "field_name": "aadhaar",
  "reason": "KYC verification",
  "outcome": "denied",
  "denial_reason": "missing_field_permission",
  "request_id": "req-denied"
}
```

Audit rows intentionally exclude full PAN/Aadhaar values, encrypted token contents, hash values, and submitted identifier-derived values.
