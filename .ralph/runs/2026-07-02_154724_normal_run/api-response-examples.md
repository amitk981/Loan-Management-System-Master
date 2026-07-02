# API Response Examples

## Login

Status: `200`

```json
{
  "data": {
    "access_token": "<redacted-jwt>",
    "expires_in": 900,
    "refresh_token": "<redacted-jwt>",
    "token_type": "Bearer",
    "user": {
      "approval_authority_type": null,
      "email": "credit.manager@sfpcl.example",
      "full_name": "Credit Manager",
      "role_codes": [
        "credit_manager"
      ],
      "status": "active",
      "team_codes": [],
      "user_id": "0c092420-508b-4ed2-95eb-d217a8ca8359"
    }
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-example-login",
    "timestamp": "2026-07-02T10:25:47.075143Z"
  },
  "success": true
}
```

## Refresh

Status: `200`

```json
{
  "data": {
    "access_token": "<redacted-jwt>",
    "expires_in": 900,
    "refresh_token": "<redacted-jwt>",
    "token_type": "Bearer",
    "user": {
      "approval_authority_type": null,
      "email": "credit.manager@sfpcl.example",
      "full_name": "Credit Manager",
      "role_codes": [
        "credit_manager"
      ],
      "status": "active",
      "team_codes": [],
      "user_id": "0c092420-508b-4ed2-95eb-d217a8ca8359"
    }
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-example-refresh",
    "timestamp": "2026-07-02T10:25:47.077849Z"
  },
  "success": true
}
```

## Logout

Status: `200`

```json
{
  "data": {
    "logged_out": true
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-example-logout",
    "timestamp": "2026-07-02T10:25:47.079154Z"
  },
  "success": true
}
```

## Audit Evidence

```json
[
  "auth.login.succeeded",
  "auth.refresh.succeeded",
  "auth.logout.succeeded"
]
```
