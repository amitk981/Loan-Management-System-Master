# API Response Examples — 002D Current User

## success

HTTP 200

```json
{
  "data": {
    "available_actions": [
      "approvals.case.create",
      "credit.appraisal.review"
    ],
    "email": "credit.manager@sfpcl.example",
    "full_name": "Credit Manager",
    "permissions": [
      "approvals.case.create",
      "credit.appraisal.review"
    ],
    "role_codes": [
      "credit_manager"
    ],
    "status": "active",
    "team_codes": [
      "credit_assessment"
    ],
    "user_id": "aec08d25-2177-4087-a116-e09ddbb3bf98"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-example-success",
    "timestamp": "2026-07-03T12:29:48.034696Z"
  },
  "success": true
}
```

## missing token

HTTP 401

```json
{
  "error": {
    "code": "AUTH_REQUIRED",
    "details": {},
    "field_errors": {},
    "message": "Bearer access token is required."
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-example-missing",
    "timestamp": "2026-07-03T12:29:48.034962Z"
  },
  "success": false
}
```

## expired access token

HTTP 401

```json
{
  "error": {
    "code": "TOKEN_EXPIRED",
    "details": {},
    "field_errors": {},
    "message": "Token has expired."
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-example-expired",
    "timestamp": "2026-07-03T12:29:48.035811Z"
  },
  "success": false
}
```

## refresh token misuse

HTTP 401

```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "details": {},
    "field_errors": {},
    "message": "Token type is invalid."
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-example-refresh",
    "timestamp": "2026-07-03T12:29:48.036124Z"
  },
  "success": false
}
```

## revoked session

HTTP 401

```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "details": {},
    "field_errors": {},
    "message": "Access session is not active."
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-example-revoked",
    "timestamp": "2026-07-03T12:29:48.038172Z"
  },
  "success": false
}
```

