# API Contract Harness Response Examples

Generated from Django test client for slice 002J.

## auth_me_success
```json
{
  "data": {
    "available_actions": [
      "tracer.lifecycle.run"
    ],
    "email": "credit.manager.contract.example@sfpcl.example",
    "full_name": "Credit Manager",
    "mobile_number": "+917111111111",
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
    "team_codes": [],
    "teams": [],
    "user_id": "d94aa043-b762-48cf-b8e8-e4869d5907f0"
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:10:34.776134Z"
  },
  "success": true
}
```

## admin_users_pagination
```json
{
  "data": [
    {
      "email": "contract.user.creator@sfpcl.example",
      "full_name": "Contract User Creator",
      "mobile_number": "+917111111111",
      "roles": [
        {
          "role_code": "contract_user_creator",
          "role_name": "Contract User Creator"
        }
      ],
      "status": "active",
      "teams": [],
      "user_id": "3b504080-0090-4c4e-90ae-d72c40978dda"
    },
    {
      "email": "credit.manager.contract.example@sfpcl.example",
      "full_name": "Credit Manager",
      "mobile_number": "+917111111111",
      "roles": [
        {
          "role_code": "credit_manager",
          "role_name": "Credit Manager"
        }
      ],
      "status": "active",
      "teams": [],
      "user_id": "d94aa043-b762-48cf-b8e8-e4869d5907f0"
    },
    {
      "email": "system.admin.contract.example@sfpcl.example",
      "full_name": "System Admin",
      "mobile_number": "+917111111111",
      "roles": [
        {
          "role_code": "system_admin",
          "role_name": "System Administrator"
        }
      ],
      "status": "active",
      "teams": [],
      "user_id": "d1e7b882-bef1-4ecd-9c9b-3d8df6fad713"
    },
    {
      "email": "target.contract.example@sfpcl.example",
      "full_name": "Target User",
      "mobile_number": "+917111111111",
      "roles": [
        {
          "role_code": "credit_manager",
          "role_name": "Credit Manager"
        }
      ],
      "status": "active",
      "teams": [],
      "user_id": "8f69c45f-6276-4af9-bd73-da173cbfb9bc"
    }
  ],
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:10:34.780731Z"
  },
  "pagination": {
    "has_next": false,
    "has_previous": false,
    "page": 1,
    "page_size": 20,
    "total_count": 4,
    "total_pages": 1
  },
  "success": true
}
```

## admin_users_401_auth_required
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
    "request_id": null,
    "timestamp": "2026-07-04T13:10:34.781057Z"
  },
  "success": false
}
```

## admin_users_403_permission_denied
```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "details": {},
    "field_errors": {},
    "message": "You do not have permission to perform this user-management action."
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:10:34.782261Z"
  },
  "success": false
}
```

## partial_admin_create_only_403_update_denied
```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "details": {},
    "field_errors": {},
    "message": "You do not have permission to perform this user-management action."
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:10:34.783623Z"
  },
  "success": false
}
```

## tracer_409_invalid_state_transition
```json
{
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "details": {},
    "field_errors": {},
    "message": "Expected status sanctioned, found draft."
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T13:10:34.791015Z"
  },
  "success": false
}
```

## auth_me_401_invalid_token
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
    "request_id": null,
    "timestamp": "2026-07-04T13:10:34.793017Z"
  },
  "success": false
}
```
