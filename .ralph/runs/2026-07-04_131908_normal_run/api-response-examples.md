# 002G Admin User API Response Examples

## List users

HTTP 200

```json
{
  "data": [
    {
      "email": "plain.staff@sfpcl.example",
      "full_name": "Plain Staff",
      "mobile_number": "",
      "roles": [
        {
          "role_code": "credit_manager",
          "role_name": "Credit Manager"
        }
      ],
      "status": "active",
      "teams": [],
      "user_id": "a33b1a1e-8332-4819-8272-4d9c58468433"
    },
    {
      "email": "system.admin@sfpcl.example",
      "full_name": "System Admin",
      "mobile_number": "+919999999999",
      "roles": [
        {
          "role_code": "system_admin",
          "role_name": "System Administrator"
        }
      ],
      "status": "active",
      "teams": [],
      "user_id": "13b5fc93-c91e-40b9-a5cd-6686cd395378"
    },
    {
      "email": "target.user@sfpcl.example",
      "full_name": "Target User",
      "mobile_number": "+918888888888",
      "roles": [
        {
          "role_code": "credit_manager",
          "role_name": "Credit Manager"
        }
      ],
      "status": "active",
      "teams": [],
      "user_id": "1809410b-a5f1-4b7d-9f9a-30e22cd0ed57"
    }
  ],
  "meta": {
    "api_version": "v1",
    "request_id": "req-002g-example",
    "timestamp": "2026-07-04T08:00:42.790329Z"
  },
  "pagination": {
    "has_next": false,
    "has_previous": false,
    "page": 1,
    "page_size": 20,
    "total_count": 3,
    "total_pages": 1
  },
  "success": true
}
```

## Detail user

HTTP 200

```json
{
  "data": {
    "email": "target.user@sfpcl.example",
    "full_name": "Target User",
    "mobile_number": "+918888888888",
    "roles": [
      {
        "role_code": "credit_manager",
        "role_name": "Credit Manager"
      }
    ],
    "status": "active",
    "teams": [],
    "user_id": "1809410b-a5f1-4b7d-9f9a-30e22cd0ed57"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-002g-example",
    "timestamp": "2026-07-04T08:00:42.792973Z"
  },
  "success": true
}
```

## Successful role assignment

HTTP 200

```json
{
  "data": {
    "email": "target.user@sfpcl.example",
    "full_name": "Target User",
    "mobile_number": "+918888888888",
    "roles": [
      {
        "role_code": "accounts_head",
        "role_name": "Accounts Head"
      }
    ],
    "status": "active",
    "teams": [],
    "user_id": "1809410b-a5f1-4b7d-9f9a-30e22cd0ed57"
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-002g-example",
    "timestamp": "2026-07-04T08:00:42.796998Z"
  },
  "success": true
}
```

## 401 missing bearer token

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
    "request_id": null,
    "timestamp": "2026-07-04T08:00:42.797341Z"
  },
  "success": false
}
```

## 403 missing manage-users permission

HTTP 403

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "details": {},
    "field_errors": {},
    "message": "User management permission is required."
  },
  "meta": {
    "api_version": "v1",
    "request_id": null,
    "timestamp": "2026-07-04T08:00:42.798539Z"
  },
  "success": false
}
```

## Validation failure unknown role

HTTP 400

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "details": {},
    "field_errors": {
      "role_code": "Existing active role is required."
    },
    "message": "Admin user request failed validation."
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-002g-example",
    "timestamp": "2026-07-04T08:00:42.799972Z"
  },
  "success": false
}
```

## Last system-admin lock-out

HTTP 400

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "details": {},
    "field_errors": {
      "status": "Cannot suspend the last active system_admin user."
    },
    "message": "Admin user request failed validation."
  },
  "meta": {
    "api_version": "v1",
    "request_id": "req-002g-example",
    "timestamp": "2026-07-04T08:00:42.802378Z"
  },
  "success": false
}
```

