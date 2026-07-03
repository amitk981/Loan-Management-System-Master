# API Response Samples — 002EX Tracer

## POST /api/v1/auth/login/

HTTP 200

```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwidXNlcl9pZCI6ImMwNzg5NDg2LTRjZDAtNDYxMC1hZjQzLTA3MzQ4NGI0ZmFiNiIsInNlc3Npb25faWQiOiI5NWY0MzY1Mi00YmIyLTQzYmUtOTg3Mi00ZmRkOGEzMDU0OTAiLCJlbWFpbCI6InRyYWNlci5zdGFmZkBzZnBjbC5leGFtcGxlIiwicm9sZV9jb2RlcyI6WyJjcmVkaXRfbWFuYWdlciJdLCJ0ZWFtX2NvZGVzIjpbImNyZWRpdF9hc3Nlc3NtZW50Il0sInBlcm1pc3Npb25zX3ZlcnNpb24iOiIyMDI2LTA3LTAzVDE4OjIyOjEwLjM3NDY1NVoiLCJpYXQiOjE3ODMxMDI5MzEsImV4cCI6MTc4MzEwMzgzMX0.ade7XoZGJVii4u7Pooau0e8-lL0sBRdeXfk8lAm7IlI",
    "expires_in": 900,
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsInVzZXJfaWQiOiJjMDc4OTQ4Ni00Y2QwLTQ2MTAtYWY0My0wNzM0ODRiNGZhYjYiLCJzZXNzaW9uX2lkIjoiOTVmNDM2NTItNGJiMi00M2JlLTk4NzItNGZkZDhhMzA1NDkwIiwianRpIjoiYmI0M2Q1MmEtNzUwOS00YTg0LTliZmEtZjc3YTczYjY4YWI3IiwiaWF0IjoxNzgzMTAyOTMxLCJleHAiOjE3ODMxODkzMzF9.iP6pSrhKaWfEBQUaObAtxW6k2ODK1uc-TgJI7l4PIhU",
    "token_type": "Bearer",
    "user": {
      "approval_authority_type": null,
      "email": "tracer.staff@sfpcl.example",
      "full_name": "Tracer Staff",
      "role_codes": [
        "credit_manager"
      ],
      "status": "active",
      "team_codes": [
        "credit_assessment"
      ],
      "user_id": "c0789486-4cd0-4610-af43-073484b4fab6"
    }
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-03T18:22:11.080382Z"
  },
  "success": true
}
```

## GET /api/v1/auth/me/

HTTP 200

```json
{
  "data": {
    "available_actions": [
      "tracer.lifecycle.run"
    ],
    "email": "tracer.staff@sfpcl.example",
    "full_name": "Tracer Staff",
    "mobile_number": "",
    "permissions": [
      "tracer.lifecycle.run"
    ],
    "role_codes": [
      "credit_manager"
    ],
    "roles": [
      {
        "role_code": "credit_manager",
        "role_name": "Credit Manager"
      }
    ],
    "status": "active",
    "team_codes": [
      "credit_assessment"
    ],
    "teams": [
      {
        "team_code": "credit_assessment",
        "team_name": "Credit Assessment"
      }
    ],
    "user_id": "c0789486-4cd0-4610-af43-073484b4fab6"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-tracer-smoke",
    "timestamp": "2026-07-03T18:22:11.090981Z"
  },
  "success": true
}
```

## POST /api/v1/tracer/members/

HTTP 200

```json
{
  "data": {
    "display_name": "Smoke Tracer Member",
    "member_id": "a1e9a7d6-154c-45b3-9db2-60d1aa27dcf6",
    "reference": "MEM-000001",
    "status": "active"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-tracer-smoke",
    "timestamp": "2026-07-03T18:22:11.095511Z"
  },
  "success": true
}
```

## POST /api/v1/tracer/members/{member_id}/loan-applications/

HTTP 200

```json
{
  "data": {
    "amount": "400000.00",
    "loan_application_id": "9a63fef0-5d0d-4933-bac7-f9d2297b38e8",
    "member_id": "a1e9a7d6-154c-45b3-9db2-60d1aa27dcf6",
    "reference": "APP-000001",
    "status": "draft"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-tracer-smoke",
    "timestamp": "2026-07-03T18:22:11.100331Z"
  },
  "success": true
}
```

## POST /api/v1/tracer/loan-applications/{loan_application_id}/sanction/

HTTP 200

```json
{
  "data": {
    "available_actions": [],
    "entity_id": "9a63fef0-5d0d-4933-bac7-f9d2297b38e8",
    "entity_type": "loan_application",
    "new_status": "sanctioned",
    "previous_status": "draft",
    "workflow_event_id": "74d9d118-4150-49ae-92d1-c7d0eb01b43d"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-tracer-smoke",
    "timestamp": "2026-07-03T18:22:11.103324Z"
  },
  "success": true
}
```

## POST /api/v1/tracer/loan-applications/{loan_application_id}/loan-account/

HTTP 200

```json
{
  "data": {
    "amount": "400000.00",
    "loan_account_id": "42c1ee8f-240b-445a-9d98-63c86bc2b0fc",
    "loan_application_id": "9a63fef0-5d0d-4933-bac7-f9d2297b38e8",
    "member_id": "a1e9a7d6-154c-45b3-9db2-60d1aa27dcf6",
    "reference": "LAC-000001",
    "status": "pending_disbursement"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-tracer-smoke",
    "timestamp": "2026-07-03T18:22:11.106998Z"
  },
  "success": true
}
```

## POST /api/v1/tracer/loan-accounts/{loan_account_id}/disburse/

HTTP 200

```json
{
  "data": {
    "available_actions": [],
    "entity_id": "42c1ee8f-240b-445a-9d98-63c86bc2b0fc",
    "entity_type": "loan_account",
    "new_status": "active",
    "previous_status": "pending_disbursement",
    "workflow_event_id": "de13b542-63d0-4be2-b092-9c3f9916841f"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-tracer-smoke",
    "timestamp": "2026-07-03T18:22:11.109796Z"
  },
  "success": true
}
```

## POST /api/v1/tracer/loan-accounts/{loan_account_id}/repayments/

HTTP 200

```json
{
  "data": {
    "amount": "400000.00",
    "loan_account_id": "42c1ee8f-240b-445a-9d98-63c86bc2b0fc",
    "reference": "REP-000001",
    "repayment_id": "983da42f-9099-469a-8d43-5491529acbb5",
    "status": "posted"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-tracer-smoke",
    "timestamp": "2026-07-03T18:22:11.113158Z"
  },
  "success": true
}
```

## POST /api/v1/tracer/loan-accounts/{loan_account_id}/close/

HTTP 200

```json
{
  "data": {
    "available_actions": [],
    "entity_id": "42c1ee8f-240b-445a-9d98-63c86bc2b0fc",
    "entity_type": "loan_account",
    "new_status": "closed",
    "previous_status": "active",
    "workflow_event_id": "f4e3015b-e364-4441-84e7-998d68599cef"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-tracer-smoke",
    "timestamp": "2026-07-03T18:22:11.116171Z"
  },
  "success": true
}
```

## Persistent SQLite Counts

```json
{
  "closed_loan_accounts": 1,
  "loan_accounts": 1,
  "loan_applications": 1,
  "members": 1,
  "repayments": 1,
  "workflow_events": 7
}
```
