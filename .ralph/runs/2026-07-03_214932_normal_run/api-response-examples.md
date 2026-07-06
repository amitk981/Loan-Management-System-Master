# API Response Examples — 002D3

Source: `docs/source/api-contracts.md` §5.3, §6.1, §6.4, §11.4.

## Success

`GET /api/v1/auth/me/`

Request:

```http
Authorization: Bearer <access_token>
X-Request-ID: req-me-001
```

Response `200`:

```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "full_name": "Credit Manager",
    "email": "credit.manager@sfpcl.example",
    "mobile_number": "+919999999999",
    "status": "active",
    "roles": [
      {
        "role_code": "credit_manager",
        "role_name": "Credit Manager"
      }
    ],
    "teams": [
      {
        "team_code": "credit_assessment",
        "team_name": "Credit Assessment"
      }
    ],
    "role_codes": ["credit_manager"],
    "team_codes": ["credit_assessment"],
    "permissions": ["approvals.case.create", "credit.appraisal.review"],
    "available_actions": ["approvals.case.create", "credit.appraisal.review"]
  },
  "meta": {
    "request_id": "req-me-001",
    "timestamp": "2026-07-03T16:25:00Z",
    "api_version": "v1"
  }
}
```

## Missing Token

Response `401`:

```json
{
  "success": false,
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Bearer access token is required.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-03T16:25:00Z",
    "api_version": "v1"
  }
}
```

## Expired Access Token

Response `401`:

```json
{
  "success": false,
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Token has expired.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-03T16:25:00Z",
    "api_version": "v1"
  }
}
```

## Refresh Token Misuse

Response `401`:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Token type is invalid.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-03T16:25:00Z",
    "api_version": "v1"
  }
}
```

## Revoked Session

Response `401`:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Access session is not active.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-03T16:25:00Z",
    "api_version": "v1"
  }
}
```
