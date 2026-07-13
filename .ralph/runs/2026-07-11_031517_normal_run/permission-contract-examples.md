# Permission Contract Examples

## Before 002J2

```json
{"success":false,"error":{"code":"PERMISSION_DENIED","message":"You do not have permission to manage users.","details":{},"field_errors":{}},"meta":{"request_id":null,"timestamp":"<timestamp>","api_version":"v1"}}
```

## After 002J2

```json
{"success":false,"error":{"code":"FORBIDDEN","message":"You do not have permission to manage users.","details":{},"field_errors":{}},"meta":{"request_id":null,"timestamp":"<timestamp>","api_version":"v1"}}
```

Only `error.code` changed. HTTP status remains 403. Messages, authorization checks, check order,
side effects, object-scope behavior, and success payloads are unchanged.

## Preserved specialized examples

- Same-permission actor outside an application scope: `403 OBJECT_ACCESS_DENIED`.
- Unauthorized full sensitive-value reveal: `403 SENSITIVE_FIELD_ACCESS_DENIED`.
- Actor who is not an eligible approver: `403 APPROVAL_AUTHORITY_REQUIRED`.
- Missing/revoked bearer credentials: existing 401 auth/token codes.

The representative 168-test log and full 389-test coverage log verify these contracts and their
existing zero-write/audit/workflow assertions.
