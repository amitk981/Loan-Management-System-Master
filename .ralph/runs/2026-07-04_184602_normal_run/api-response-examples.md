# API Response Examples — 002K Demo Users

Generated from an isolated local SQLite database after guarded `seed_demo_users`.

## system_admin login (demo.system_admin@sfpcl.example)
```json
{
  "data": {
    "access_token": "<redacted>",
    "expires_in": 900,
    "refresh_token": "<redacted>",
    "token_type": "Bearer",
    "user": {
      "approval_authority_type": null,
      "email": "demo.system_admin@sfpcl.example",
      "full_name": "Demo System Administrator",
      "role_codes": [
        "system_admin"
      ],
      "status": "active",
      "team_codes": [
        "it"
      ],
      "user_id": "816da64e-1928-41d1-9370-6147ed5ec0a9"
    }
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:25:31.776260Z"
  },
  "success": true
}
```

## system_admin /auth/me
```json
{
  "data": {
    "available_actions": [
      "auth.session.read_all",
      "auth.session.revoke_any",
      "config.interest_rate.manage",
      "config.loan_policy.manage",
      "config.loan_policy.read",
      "config.scale_of_finance.manage",
      "config.share_valuation.manage",
      "users.permission.assign",
      "users.role.create",
      "users.role.update",
      "users.team.manage",
      "users.user.create",
      "users.user.disable",
      "users.user.update"
    ],
    "email": "demo.system_admin@sfpcl.example",
    "full_name": "Demo System Administrator",
    "mobile_number": "",
    "permissions": [
      "auth.session.read_all",
      "auth.session.revoke_any",
      "config.interest_rate.manage",
      "config.loan_policy.manage",
      "config.loan_policy.read",
      "config.scale_of_finance.manage",
      "config.share_valuation.manage",
      "users.permission.assign",
      "users.role.create",
      "users.role.update",
      "users.team.manage",
      "users.user.create",
      "users.user.disable",
      "users.user.update"
    ],
    "role_codes": [
      "system_admin"
    ],
    "roles": [
      {
        "role_code": "system_admin",
        "role_name": "System Administrator"
      }
    ],
    "status": "active",
    "team_codes": [
      "it"
    ],
    "teams": [
      {
        "team_code": "it",
        "team_name": "IT Team"
      }
    ],
    "user_id": "816da64e-1928-41d1-9370-6147ed5ec0a9"
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:25:31.787333Z"
  },
  "success": true
}
```

## tracer_only login (demo.tracer@sfpcl.example)
```json
{
  "data": {
    "access_token": "<redacted>",
    "expires_in": 900,
    "refresh_token": "<redacted>",
    "token_type": "Bearer",
    "user": {
      "approval_authority_type": null,
      "email": "demo.tracer@sfpcl.example",
      "full_name": "Demo Tracer User",
      "role_codes": [
        "sales_team_user"
      ],
      "status": "active",
      "team_codes": [
        "sales"
      ],
      "user_id": "e59daef6-7b3e-4810-ba04-ab2153cb4b3f"
    }
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:25:32.153387Z"
  },
  "success": true
}
```

## tracer_only /auth/me
```json
{
  "data": {
    "available_actions": [
      "tracer.lifecycle.run"
    ],
    "email": "demo.tracer@sfpcl.example",
    "full_name": "Demo Tracer User",
    "mobile_number": "",
    "permissions": [
      "tracer.lifecycle.run"
    ],
    "role_codes": [
      "sales_team_user"
    ],
    "roles": [
      {
        "role_code": "sales_team_user",
        "role_name": "Sales Team User"
      }
    ],
    "status": "active",
    "team_codes": [
      "sales"
    ],
    "teams": [
      {
        "team_code": "sales",
        "team_name": "Sales Team"
      }
    ],
    "user_id": "e59daef6-7b3e-4810-ba04-ab2153cb4b3f"
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:25:32.155328Z"
  },
  "success": true
}
```

## zero_permission login (demo.zero@sfpcl.example)
```json
{
  "data": {
    "access_token": "<redacted>",
    "expires_in": 900,
    "refresh_token": "<redacted>",
    "token_type": "Bearer",
    "user": {
      "approval_authority_type": null,
      "email": "demo.zero@sfpcl.example",
      "full_name": "Demo Zero Permission User",
      "role_codes": [
        "management_viewer"
      ],
      "status": "active",
      "team_codes": [],
      "user_id": "c4e43841-d7bd-4693-bc31-df469374947c"
    }
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:25:32.543159Z"
  },
  "success": true
}
```

## zero_permission /auth/me
```json
{
  "data": {
    "available_actions": [],
    "email": "demo.zero@sfpcl.example",
    "full_name": "Demo Zero Permission User",
    "mobile_number": "",
    "permissions": [],
    "role_codes": [
      "management_viewer"
    ],
    "roles": [
      {
        "role_code": "management_viewer",
        "role_name": "Management Viewer"
      }
    ],
    "status": "active",
    "team_codes": [],
    "teams": [],
    "user_id": "c4e43841-d7bd-4693-bc31-df469374947c"
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:25:32.545056Z"
  },
  "success": true
}
```
