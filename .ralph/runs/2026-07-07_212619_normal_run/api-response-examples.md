# API Response Examples — 004A Member Directory

Synthetic data only. These examples reflect `GET /api/v1/members/` from `docs/source/api-contracts.md` §13.1 and the standard envelopes from §6-7.

## Success

Request:

```http
GET /api/v1/members/?search=Ramesh&page=1&page_size=20
Authorization: Bearer <access_token>
X-Request-ID: req-members-list
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "member_id": "00000000-0000-4000-8000-000000000001",
      "member_number": "MEM-00125",
      "member_type": "individual_farmer",
      "legal_name": "Ramesh Patil",
      "display_name": "Ramesh Patil",
      "folio_number": "FOL-456",
      "membership_status": "active",
      "kyc_status": "verified",
      "rekyc_due_date": "2027-06-22",
      "default_status": "no_default",
      "mobile_number": "******7890",
      "email": "ramesh@example.com",
      "share_summary": {
        "number_of_shares": 100,
        "holding_mode": "physical",
        "available_share_count": 100
      },
      "active_member_status": {
        "status": "active",
        "verified_at": "2026-06-22T10:30:00Z"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "meta": {
    "request_id": "req-members-list",
    "timestamp": "2026-07-07T16:10:00Z",
    "api_version": "v1"
  }
}
```

## Validation Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Member directory query failed validation.",
    "details": {},
    "field_errors": {
      "member_type": "Unsupported filter value."
    }
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-07T16:10:00Z",
    "api_version": "v1"
  }
}
```

## Auth Errors

Missing bearer token returns `401 AUTH_REQUIRED`; an authenticated user without `members.member.read` returns:

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to read members.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-07T16:10:00Z",
    "api_version": "v1"
  }
}
```
